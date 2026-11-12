# Tile 微架构与 NoC 接口

上级：[AI Dataflow 系统视角](./README.md)

相关：[NI / DMA / 存储接口](./ni-dma-memory-interface.md)、[SRAM Bank Conflict / Local Memory System](./sram-bank-conflict-local-memory-system.md)、[从 NoC 知识到 DSL 设计](../06-reference/noc-to-dsl-bridge.md)

## 读这页前先统一几个词

- `tile`：AI 加速器中最基本的计算+存储单元，通常包含 MAC 阵列、local SRAM、NI
- `NI`：Network Interface，tile 与 NoC 之间的协议转换层
- `injection port`：tile 向 NoC 发送数据的出口
- `ejection port`：tile 从 NoC 接收数据的入口
- `local SRAM`：tile 内部的片上存储，通常分 bank 组织

## 为什么需要从 tile 侧看 NoC

前面的 wiki 主要从 NoC 内部向外看（router → link → endpoint）。但你的 DSL 要描述的是完整的片上架构，tile 是一等公民。如果不理解 tile 内部结构与 NoC 的接口关系，DSL 就无法准确描述：

- tile 能以多快的速率向 NoC 注入数据
- tile 能以多快的速率从 NoC 消费数据
- tile 内部的存储组织如何影响 NoC 流量模式
- tile 的计算流水线何时会因 NoC 延迟而 stall

## 典型 AI Tile 内部结构

```text
┌─────────────────────────────────────────┐
│                  Tile                    │
│                                         │
│  ┌──────────┐    ┌──────────────────┐   │
│  │  Compute │    │   Local SRAM     │   │
│  │  Engine  │◄──►│  (多 bank 组织)   │   │
│  │ (MAC/ALU)│    │                  │   │
│  └──────────┘    └────────┬─────────┘   │
│       │                   │             │
│       │          ┌────────┴─────────┐   │
│       │          │  SRAM Controller │   │
│       │          └────────┬─────────┘   │
│       │                   │             │
│  ┌────┴───────────────────┴──────────┐  │
│  │       Network Interface (NI)      │  │
│  │  ┌─────────┐  ┌────────────────┐  │  │
│  │  │Injection│  │   Ejection     │  │  │
│  │  │  Queue  │  │Queue + Reassem.│  │  │
│  │  └────┬────┘  └───────┬────────┘  │  │
│  └───────┼───────────────┼───────────┘  │
└──────────┼───────────────┼──────────────┘
           │               │
     ┌─────┴───────────────┴─────┐
     │        NoC Router         │
     └───────────────────────────┘
```

### 各组件的 NoC 相关角色

| 组件 | 与 NoC 的关系 | DSL 中需要描述什么 |
|---|---|---|
| Compute Engine | 产生数据需求（读 weight/activation）、产生输出（partial sum / output） | 计算吞吐（TOPS）、pipeline 深度 |
| Local SRAM | 数据的暂存和复用点，决定何时需要从 NoC 搬入/搬出 | 容量、bank 数、bank width、端口数 |
| SRAM Controller | 仲裁 compute 和 NI 对 SRAM 的竞争访问 | 端口数、仲裁策略 |
| NI Injection | 将 tile 产生的数据打包成 packet 注入 NoC | 注入带宽、队列深度 |
| NI Ejection | 从 NoC 接收 packet，重组后写入 SRAM | 弹出带宽、重组 buffer 深度 |

## Tile 的 NoC 端口模型

一个 tile 与 NoC 的接口可以抽象为若干端口，每个端口有方向和带宽约束：

```text
Tile 的 NoC 端口视图：

  ┌──── injection_port[0]: data_noc, width=256bit, max_rate=32GB/s
  ├──── injection_port[1]: control_noc, width=64bit, max_rate=8GB/s
  │
  ├──── ejection_port[0]: data_noc, width=256bit, max_rate=32GB/s
  └──── ejection_port[1]: control_noc, width=64bit, max_rate=8GB/s
```

### 端口数量的影响

| 配置 | injection 端口数 | ejection 端口数 | 对 NoC 的影响 |
|---|---|---|---|
| 最简单 | 1 | 1 | injection/ejection 成为瓶颈，所有 traffic class 共享 |
| 按网络分 | N（每张网络一个） | N | 不同 traffic class 物理隔离 |
| 按功能分 | 2（data + control） | 2 | data 和 control 不互相阻塞 |
| 多端口 | 2+ data | 2+ data | 提高注入/弹出带宽，但 router radix 增加 |

DSL 需要能描述每个 tile 有几个端口、每个端口连接哪张网络。

## 注入与弹出的带宽约束

### 注入侧

tile 能向 NoC 注入数据的速率受三个因素共同约束：

```text
实际注入带宽 = min(
  NI injection queue 排空速率,      ← NI 硬件约束
  router local port 接受速率,       ← NoC 侧约束
  tile 产生数据的速率               ← compute/SRAM 侧约束
)
```

典型瓶颈场景：

| 瓶颈位置 | 表现 | 原因 |
|---|---|---|
| NI injection queue 满 | tile compute stall（tile 无法写出结果） | NoC 拥塞导致 backpressure |
| Router local port 忙 | injection queue 排不空 | router SA 竞争激烈 |
| SRAM read port 忙 | NI 拿不到要发的数据 | compute 和 NI 争 SRAM 读端口 |

### 弹出侧

```text
实际弹出带宽 = min(
  router ejection port 速率,        ← NoC 侧约束
  NI ejection queue + reassembly,   ← NI 硬件约束
  SRAM write port 接受速率          ← tile 侧约束
)
```

弹出侧更容易成为瓶颈，因为：
- 多个远端 tile 可能同时向同一个 tile 发送数据（fan-in）
- 弹出被阻塞时，flit 会堵在 router output buffer，进而 backpressure 蔓延到 NoC 内部
- 这是 `EJECTION_BLOCKED` stall 的根源

## Local SRAM 组织对 NoC 流量的影响

### 容量决定 NoC 流量频率

```text
SRAM 容量大 → 更多数据可以本地复用 → NoC 流量更少
SRAM 容量小 → 频繁从外部搬入/搬出 → NoC 流量更多

量化关系（以 weight-stationary GEMM 为例）：
  tile SRAM = 256 KB → 可容纳完整 weight tile → 运行时 weight NoC 流量 = 0
  tile SRAM = 64 KB  → 需要分 4 次加载 weight → 运行时 weight NoC 流量 = 3 × 64KB
```

### Bank 组织决定并发能力

```text
SRAM 典型组织：

  ┌──────┬──────┬──────┬──────┐
  │Bank 0│Bank 1│Bank 2│Bank 3│  ← 每 bank 独立可访问
  └──┬───┴──┬───┴──┬───┴──┬───┘
     │      │      │      │
  ┌──┴──────┴──────┴──────┴──┐
  │      SRAM Controller     │
  │  (仲裁 compute 和 NI)     │
  └──────────┬───────────────┘
             │
    To Compute / To NI
```

bank 数影响 NoC 的方式：
- bank 数多 → compute 和 NI 可以并行访问不同 bank → NI 注入/弹出更少被 compute 阻塞
- bank 数少 → compute 和 NI 频繁冲突 → NI 有效带宽下降 → 从 NoC 角度看像是端点变慢了

### DSL 需要描述的 SRAM 参数

| 参数 | 含义 | 对 NoC 的影响 |
|---|---|---|
| `capacity` | 总容量 | 决定数据复用率，间接决定 NoC 流量总量 |
| `bank_count` | bank 数 | 决定 compute 和 NI 的并发访问能力 |
| `bank_width` | 单 bank 单周期读写位宽 | 约束 NI 单周期最大搬运量 |
| `read_ports` | 读端口数 | compute 和 NI 的读竞争 |
| `write_ports` | 写端口数 | NI ejection 写入和 compute 写入的竞争 |

## Tile 对 NoC 的需求总结

从 tile 的视角看，它对 NoC 有以下核心需求：

| 需求 | 描述 | 对应 DSL 层 |
|---|---|---|
| 注入带宽 | 每周期能向 NoC 发多少数据 | L2 Network Resources |
| 弹出带宽 | 每周期能从 NoC 收多少数据 | L2 Network Resources |
| 多网络接入 | 同时连接 data/control/reduction 等多张网络 | L1 Physical Topology |
| 延迟要求 | 关键 response 的最大可容忍延迟 | L4 Traffic Specification |
| 流量模式 | 什么时候发什么、发给谁 | L5 Scheduled Communication |

## 对 DSL 设计的影响

### Tile 在 DSL 中的描述

```yaml
tile:
  id: T0
  compute:
    type: mac_array
    throughput: 1 TOPS           # FP16
    pipeline_depth: 8            # cycles
  sram:
    capacity: 256 KB
    bank_count: 8
    bank_width: 256              # bit
    read_ports: 2
    write_ports: 2
  noc_ports:
    - name: data_port
      network: data_noc
      injection_width: 256       # bit
      ejection_width: 256        # bit
      injection_queue_depth: 4   # flits
      ejection_queue_depth: 8    # flits
    - name: control_port
      network: control_noc
      injection_width: 64
      ejection_width: 64
      injection_queue_depth: 2
      ejection_queue_depth: 2
```

### 为什么 tile 必须是 DSL 一等公民

如果 DSL 只描述 NoC（router + link），不描述 tile 内部参数：

| 缺什么 | 会导致什么 |
|---|---|
| 缺 SRAM 容量 | 无法推算 NoC 流量总量和时序 |
| 缺 bank 组织 | 无法建模 NI 有效带宽（实际受 bank conflict 约束） |
| 缺 compute 吞吐 | 无法计算 compute/communication ratio |
| 缺端口描述 | 无法知道 tile 连了几张网络、每张网络的注入弹出约束 |

## 本页结论

NoC 的性能上界不取决于 router 有多快，而取决于端点能以多快的速率注入和消费数据。DSL 必须将 tile 的 compute 吞吐、SRAM 组织、NI 端口配置作为一等公民来描述，否则仿真和架构探索的结论会脱离真实约束。对 AI 加速器而言，最常见的系统瓶颈不在 NoC 内部，而在 tile 的 ejection port 和 SRAM write port。
