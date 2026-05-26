# 地址空间与路由映射

上级：[AI Dataflow 系统视角](./README.md)

相关：[Routing 与 Arbitration](../03-topology-routing/routing-arbitration.md)、[Source Routing 与 Compiler-Driven NoC](../03-topology-routing/source-routing-compiler-driven-noc.md)、[Memory-Centric NoC](./memory-centric-noc.md)、[NI / DMA / 存储接口](./ni-dma-memory-interface.md)

## 读这页前先统一几个词

- `address map`：地址空间到物理资源的映射表，定义"访问地址 X 应该路由到哪个物理节点"
- `address decode`：在 NI 或 router 中，根据地址判断目的节点的硬件逻辑
- `interleaving`：将连续地址交替分配到不同 bank/port/node，分散访问压力
- `striping`：类似 interleaving，强调按固定粒度轮转分配
- `address region`：地址空间中一段连续范围，映射到同一类物理资源

## 为什么 address map 对 NoC 架构至关重要

NoC 的路由决策最终依赖一个基本问题：**给定一个目的地址，数据应该发往哪个物理节点？**

如果不理解 address map：

- 无法确定 DMA transfer 的路由目标
- 无法分析 HBM 访问的流量分布
- 无法理解为什么某些 link 成为热点
- 编译器无法为 placement 和 routing 做正确决策

## AI 加速器典型地址空间布局

```text
地址空间总览：

0x0000_0000 ┌──────────────────────┐
            │  Global Control Regs │  ← 控制寄存器（CSR），通过 control NoC 访问
0x0010_0000 ├──────────────────────┤
            │  Tile 0 Local SRAM   │  ← 每个 tile 有独立的 SRAM 地址段
0x0020_0000 ├──────────────────────┤
            │  Tile 1 Local SRAM   │
            │       ...            │
0x0100_0000 ├──────────────────────┤
            │  Tile 15 Local SRAM  │
0x0110_0000 ├──────────────────────┤
            │  Shared SRAM Pool    │  ← 如有共享 SRAM，独立地址段
0x1000_0000 ├──────────────────────┤
            │  HBM Channel 0      │  ← HBM 各 channel 的地址段
0x2000_0000 ├──────────────────────┤
            │  HBM Channel 1      │
            │       ...            │
0x8000_0000 ├──────────────────────┤
            │  HBM Channel 7      │
0xFFFF_FFFF └──────────────────────┘
```

### 地址 → 物理节点的映射规则

| 地址范围 | 物理目标 | 连接的 NoC | 路由行为 |
|---|---|---|---|
| `0x001n_xxxx` | Tile n 的 local SRAM | data NoC | 地址高位 decode 出 tile_id |
| `0x1000_0000 + ch × 0x1000_0000` | HBM channel ch | DMA/data NoC | 地址高位 decode 出 channel_id |
| `0x0000_xxxx` | Global CSR | control NoC | 固定路由到 control hub |

## Address Decode 的两种模式

### 模式一：NI 侧 decode（常见于 AI 加速器）

```text
Tile 发出请求 → NI 根据目的地址查表 → 确定目的 node_id → 注入 NoC

NI address decode table:
  地址 [0x0010_0000, 0x001F_FFFF] → node_id = 0  (Tile 0)
  地址 [0x0020_0000, 0x002F_FFFF] → node_id = 1  (Tile 1)
  ...
  地址 [0x1000_0000, 0x1FFF_FFFF] → node_id = 16 (HBM port 0)
```

优点：router 不需要理解地址，只做 node_id 路由，设计简单。

缺点：NI 必须知道完整 address map。

### 模式二：Router 侧 decode（常见于 CPU SoC）

```text
请求携带原始地址进入 NoC → 每个 router 根据地址判断转发方向

适用于：地址空间与拓扑结构对齐（如地址高位 = 行号，次高位 = 列号）
```

优点：支持灵活的地址映射。

缺点：router 需要 address decode 逻辑，面积和延迟增加。

**AI 加速器绝大多数采用模式一**，因为流量模式由编译器确定，NI 侧 decode 足够。

## HBM Address Interleaving

HBM 的地址映射对 NoC 流量分布影响巨大。

### 无 interleaving（按 channel 连续分配）

```text
HBM Channel 0: 地址 [0, 256MB)
HBM Channel 1: 地址 [256MB, 512MB)
...

问题：连续访问一段大 tensor 时，流量全部压到同一个 HBM port
→ 该 port 附近的 NoC link 成为热点
→ 其他 HBM port 空闲
```

### Channel-level interleaving

```text
按 4KB page 交替分配：
  Page 0 → Channel 0
  Page 1 → Channel 1
  ...
  Page 7 → Channel 7
  Page 8 → Channel 0  (wrap around)

地址 decode: channel_id = (addr >> 12) % 8

效果：连续 tensor 的访问被均匀分散到所有 HBM port
→ NoC 流量均衡
→ bisection BW 被充分利用
```

### Interleaving 粒度的取舍

| 粒度 | 特性 | 适用场景 |
|---|---|---|
| 64B（cache line 级） | 极度均匀分散 | CPU coherent NoC |
| 256B-4KB | 均匀且 DMA 友好 | AI 加速器主流 |
| 1MB+（大块） | 保持空间局部性 | 需要利用 row locality |
| 无 interleaving | 编译器完全控制 | 编译器显式管理 placement |

### 对 NoC 流量的量化影响

```text
16 tile 的 4×4 mesh，8 个 HBM port 分布在 mesh 边缘

场景：所有 tile 同时读取一个 32MB tensor

无 interleaving（tensor 在 Channel 0）：
  Channel 0 port 流量 = 32 MB
  其他 channel 流量 = 0
  Channel 0 附近 link 利用率 ≈ 100%（饱和）
  总完成时间 = 32 MB / 32 GB/s = 1 ms

有 interleaving（4KB 粒度，8 channel）：
  每个 channel 流量 = 32 MB / 8 = 4 MB
  link 利用率 ≈ 12.5%（均匀分散）
  总完成时间 = 4 MB / 32 GB/s = 125 μs（8× 加速）
```

## 地址空间与多网络的关系

不同地址范围的访问可能路由到不同的物理网络：

```text
NI address decode 不仅决定 node_id，还决定走哪张网络：

地址 [0x0010_xxxx, 0x010F_xxxx] → data_noc     (tile SRAM 访问)
地址 [0x0000_xxxx]              → control_noc   (CSR 访问)
地址 [0x1000_xxxx, 0x8FFF_xxxx] → dma_noc       (HBM 访问)
```

这意味着 address map 和多网络设计是紧密耦合的——DSL 必须能描述"哪段地址走哪张网络"。

## 地址空间对编译器的影响

编译器在做 placement 和数据分配时，实际上是在做 address map 的上层决策：

```text
编译器决策链：

1. 算子 placement → 哪个 tile 执行哪个算子
2. 数据 placement → weight 放在哪些 tile 的 SRAM / 哪些 HBM channel
3. 地址分配 → 数据在地址空间中的具体位置
4. 通信生成 → 基于源和目的地址，生成 DMA descriptor / NoC packet
5. 路由决策 → NI 根据目的地址 decode 出 node_id + network

所以编译器必须知道 address map，才能做出不产生热点的 placement。
```

## DSL 中 address map 的描述方式

```yaml
address_map:
  regions:
    - name: tile_sram
      base: 0x0010_0000
      size_per_node: 1 MB        # 每个 tile 1MB SRAM
      node_type: tile
      node_count: 16
      network: data_noc
      decode: linear             # node_id = (addr - base) / size_per_node

    - name: global_csr
      base: 0x0000_0000
      size: 1 MB
      node_type: control_hub
      node_id: 0
      network: control_noc

    - name: hbm
      base: 0x1000_0000
      size_per_channel: 256 MB
      channel_count: 8
      network: dma_noc
      interleaving:
        granularity: 4 KB
        decode: modulo           # channel_id = (addr >> 12) % 8

  # 编译器可查询的接口
  queries:
    - resolve(addr) → (node_id, network, channel_id)
    - list_nodes(region_name) → [node_id, ...]
    - bandwidth(node_id) → injection_bw, ejection_bw
```

## 常见 address map 错误与 NoC 后果

| 错误 | NoC 后果 | 正确做法 |
|---|---|---|
| HBM 不做 interleaving | 单 channel 热点，bisection BW 浪费 | 按 workload 特性选择 interleaving 粒度 |
| 地址 decode 不区分网络 | control 消息走 data NoC 被堵 | 地址范围与网络绑定 |
| 编译器不知道 address map | placement 产生不必要的跨 cluster 流量 | 将 address map 暴露给编译器 |
| 共享 SRAM 地址集中 | 多 tile 同时访问同一 bank 产生冲突 | 按 bank 做 interleaving |

## 本页结论

address map 是连接 NoC 路由、编译器 placement 和系统流量分布的关键桥梁。DSL 必须能描述地址空间到物理节点的映射规则（包括 interleaving 策略和网络绑定），编译器必须能查询 address map 来做出避免热点的 placement 决策。对 AI 加速器而言，HBM 的 interleaving 策略是影响 NoC 流量分布最大的单一因素。
