# Chiplet 与 Die-to-Die 互连

上级：[AI Dataflow 系统视角](./README.md)

相关：[NoC 分类框架](../01-overview/taxonomy.md)、[多网络组织](./multi-network-organization.md)、[Physical Realization 与 Floorplan-Aware NoC](./physical-realization-floorplan-aware-noc.md)

## 读这页前先统一几个词

- `chiplet`：一个完整的、可独立制造的小芯片（die），多个 chiplet 通过封装互连组成系统
- `die-to-die (D2D)`：跨越两个独立 die 之间的互连接口
- `interposer`：芯片之间的中间层基板（硅中介层或有机基板），提供 die 间的短距离高密度互连
- `UCIe`：Universal Chiplet Interconnect Express，新兴的 chiplet 互连标准
- `package-level interconnect`：封装层面的互连，带宽和延迟介于片上 NoC 和板级 PCIe 之间

## 为什么 chiplet 对 NoC DSL 重要

AI 加速器越来越多采用 multi-die 架构：

- 单 die 面积受光罩（reticle）限制（~800 mm²），大规模加速器必须用多 die
- HBM 本身就是独立 die，通过 interposer 与计算 die 连接
- Chiplet 方案允许不同工艺混合（compute die 用先进工艺，IO die 用成熟工艺）

你的 DSL 如果只能描述单 die 内的 NoC，就无法描述：
- compute chiplet 之间的数据搬运
- compute die 到 HBM die 的访问路径
- 跨 die 的延迟和带宽约束

## Die-to-Die 互连与片上 NoC 的关键差异

| 维度 | 片上 NoC link | Die-to-Die link |
|---|---|---|
| 延迟 | 1-3 cycle (1-3 ns @ 1GHz) | 10-50 ns |
| 带宽密度 | 极高（金属层内布线） | 中等（受 bump/μbump 密度限制） |
| 典型带宽 | 32-128 GB/s per link | 64-256 GB/s per D2D interface |
| 线长 | 0.5-5 mm | 1-10 mm（interposer）或更长 |
| 能效 | ~0.1-0.5 pJ/bit | ~0.5-2 pJ/bit |
| 错误率 | 极低（可忽略） | 需要 CRC / retry 机制 |
| 协议 | NoC flit | D2D 协议（如 UCIe, BoW） |

### 关键影响：延迟不对称

```text
片上 NoC 内（同 die）：     1-3 ns per hop
Die-to-Die 穿越：          10-50 ns（协议+物理+序列化）
HBM 访问（compute die → HBM die → DRAM）：50-150 ns

跨 die 延迟是片上的 10-50 倍。
这意味着跨 chiplet 通信的调度必须与片上 NoC 区别对待。
```

## 典型 AI 加速器 Chiplet 架构

### 架构一：Compute + HBM（最常见）

```text
┌─────────────────────────────────────────────┐
│               Interposer / Package          │
│                                             │
│  ┌─────────┐                 ┌─────────┐   │
│  │  HBM 0  │                 │  HBM 1  │   │
│  │  (DRAM   │                 │  (DRAM   │   │
│  │   die)  │                 │   die)  │   │
│  └────┬────┘                 └────┬────┘   │
│       │ D2D (μbump)               │        │
│  ┌────┴───────────────────────────┴────┐   │
│  │         Compute Die                 │   │
│  │  ┌────────────────────────────┐     │   │
│  │  │       On-chip NoC          │     │   │
│  │  │  T0──T1──T2──T3           │     │   │
│  │  │  │   │   │   │            │     │   │
│  │  │  T4──T5──T6──T7           │     │   │
│  │  │  │   │   │   │            │     │   │
│  │  │  T8──T9──T10─T11          │     │   │
│  │  │  │   │   │   │            │     │   │
│  │  │  T12─T13─T14─T15          │     │   │
│  │  └────────────────────────────┘     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────┐                 ┌─────────┐   │
│  │  HBM 2  │                 │  HBM 3  │   │
│  └─────────┘                 └─────────┘   │
└─────────────────────────────────────────────┘

HBM 通过 interposer μbump 连接到 compute die 边缘的 PHY。
PHY 后面接 memory controller，再接入 NoC。
```

NoC 视角：HBM port 是 NoC 边缘节点，但它的"最后一跳"延迟远大于片上 hop。

### 架构二：Multi-Compute Chiplet

```text
┌──────────────────────────────────────────────────┐
│                    Package                        │
│                                                   │
│  ┌──────────────┐   D2D    ┌──────────────┐      │
│  │ Compute Die 0│◄────────►│ Compute Die 1│      │
│  │  (NoC 0)     │  64GB/s  │  (NoC 1)     │      │
│  │  16 tiles    │  ~20ns   │  16 tiles    │      │
│  └──────┬───────┘          └───────┬──────┘      │
│         │                          │              │
│    ┌────┴────┐                ┌────┴────┐        │
│    │  HBM 0  │                │  HBM 1  │        │
│    └─────────┘                └─────────┘        │
└──────────────────────────────────────────────────┘

两个 compute die 各有独立的片上 NoC。
Die 间通过 D2D link 连接。
```

### 多 die 系统的互连层次

```text
层级              延迟       带宽         范围
─────────────────────────────────────────────────
L0: Cluster 内    1 ns      128 GB/s     ~1mm
L1: Die 内 NoC    3-5 ns    32 GB/s/link  ~10mm
L2: Die-to-Die    20-50 ns  64-256 GB/s  ~10mm (interposer)
L3: Board-level   100+ ns   32-64 GB/s   ~100mm (PCIe/CXL)
```

## D2D 对 NoC 设计的影响

### 1. 需要 D2D bridge 或 gateway

```text
片上 NoC 的 flit 不能直接跨 die 传输，需要：

  NoC flit → D2D TX (序列化+编码+CRC)
           → 物理传输
           → D2D RX (解码+CRC 检查+反序列化)
           → 远端 NoC flit

这个 bridge/gateway 需要：
  - TX/RX FIFO（吸收延迟差异）
  - 协议转换（NoC flit ↔ D2D packet）
  - 流控桥接（NoC credit ↔ D2D credit/ACK）
  - 可选：压缩/解压（减少 D2D 带宽需求）
```

### 2. 跨 die 流量应尽量最小化

```text
原则：尽量让通信发生在 die 内，跨 die 通信只走必要的流量。

编译器 placement 应该：
  - 紧密耦合的算子放在同一个 die
  - 跨 die 只传递必须共享的数据（如 all-reduce 的 partial sum）
  - 利用层次化 schedule：先 die 内 reduce，再 die 间 reduce
```

### 3. 延迟不对称要求 NoC 感知

```text
编译器在做 scheduling 时必须区分：

  同 cluster 内通信：~1 ns     → 可以 pipeline 紧密衔接
  同 die 跨 cluster：~3-5 ns   → 需要小量 prefetch
  跨 die 通信：~20-50 ns       → 需要显著的 prefetch / double-buffering
  HBM 访问：~50-150 ns         → 需要 DMA outstanding window 覆盖

如果 DSL 不区分这些层级，编译器无法做出正确的 scheduling 决策。
```

## DSL 中 Chiplet 互连的描述

```yaml
system:
  name: dual_die_accelerator
  
  dies:
    - id: die_0
      tiles: [T0, T1, ..., T15]
      noc:
        type: mesh
        rows: 4
        cols: 4
        link_width: 256
        link_latency: 1
      hbm_ports: [HBM0, HBM1]
      
    - id: die_1
      tiles: [T16, T17, ..., T31]
      noc:
        type: mesh
        rows: 4
        cols: 4
        link_width: 256
        link_latency: 1
      hbm_ports: [HBM2, HBM3]
  
  d2d_links:
    - name: d2d_0
      die_a: die_0
      die_b: die_1
      gateway_a: T3            # die_0 边缘 tile
      gateway_b: T16           # die_1 边缘 tile
      bandwidth: 128 GB/s      # 双向
      latency: 25 ns           # 单程
      protocol: ucie
      fifo_depth: 64           # flit

  hbm:
    - id: HBM0
      die: die_0
      bandwidth: 128 GB/s
      latency: 80 ns           # 含 D2D + DRAM access
      channels: 8
```

### 关键：层次化距离模型

```yaml
distance_model:
  # DSL 应该支持层次化的距离/延迟查询
  
  same_cluster:
    hop_latency: 1 ns
    bandwidth: 128 GB/s
    
  same_die_cross_cluster:
    hop_latency: 1 ns          # per hop
    bandwidth: 32 GB/s         # per link
    
  cross_die:
    latency: 25 ns             # fixed D2D 穿越
    bandwidth: 128 GB/s        # D2D link
    
  hbm_access:
    latency: 80 ns             # 含 controller + DRAM
    bandwidth: 128 GB/s        # per HBM stack
```

## 对编译器 Placement 的影响

```text
Placement cost model 需要扩展为层次化：

cost(mapping) = 
    α₁ × Σ intra_die_comm_cost(f)       # die 内通信代价（低权重）
  + α₂ × Σ cross_die_comm_cost(f)       # 跨 die 通信代价（高权重）
  + α₃ × Σ hbm_access_cost(f)           # HBM 访问代价

其中 α₂ >> α₁，反映跨 die 延迟远大于 die 内。

编译器应该先做 die-level partition（哪些算子放在哪个 die），
再做 die 内的 tile-level placement。
```

## 本页结论

Chiplet 和 die-to-die 互连引入了一个新的互连层次，其延迟是片上 NoC 的 10-50 倍。DSL 必须能描述多 die 系统的层次化互连（die 内 NoC + D2D link + HBM 接口），并且距离/延迟模型必须感知层次差异。对编译器而言，跨 die 通信的最小化是 placement 的首要目标，scheduling 必须用 prefetch 和 double-buffering 来掩盖 D2D 延迟。
