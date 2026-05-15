# NoC 功耗与面积建模

上级：[建模与评估](./README.md)

相关：[Topology 量化对比](../03-topology-routing/topology-layout.md)、[Physical Realization 与 Floorplan-Aware NoC](../04-ai-dataflow-system/physical-realization-floorplan-aware-noc.md)、[Buffer Depth / Credit Sizing / Allocator Policy](../02-router-microarchitecture/buffer-depth-credit-sizing-allocator-policy.md)

## 读这页前先统一几个词

- `dynamic power`：电路实际切换活动产生的功耗，与数据流量成正比
- `leakage power`：即使不切换也会因漏电流消耗的功耗，与面积和工艺相关
- `wire energy`：信号在长线上传播消耗的能量，与线长和负载电容成正比
- `router area`：一个 router 占用的硅面积，主要由 buffer 和 crossbar 决定

## 为什么架构探索需要功耗和面积维度

前面的 wiki 所有分析维度都是 latency / throughput / utilization / stall。但芯片设计中，**面积和功耗往往是最终的硬约束**：

- 面积限制了能放多少 router、多宽的链路、多深的 buffer
- 功耗限制了能同时驱动多少链路、能跑多高的频率
- 架构探索如果不考虑这些约束，可能选出一个性能最优但物理上不可实现的方案

## NoC 功耗的组成

```text
NoC 总功耗 = Router 功耗 + Link 功耗 + NI 功耗

Router 功耗组成（按占比排序）：
  ┌────────────────────────────────────┐
  │  Buffer (SRAM/register)  40-60%   │  ← 最大头
  │  Crossbar (mux/demux)    20-30%   │
  │  Arbiter / Allocator      5-15%   │
  │  Route compute            2-5%    │
  │  Control logic            3-5%    │
  └────────────────────────────────────┘

Link 功耗：
  wire driver + repeater 功耗，与线长和翻转率成正比
  长线（跨 cluster）功耗可能与 router 本身相当

NI 功耗：
  packetization / depacketization + injection/ejection queue
  通常占 NoC 总功耗的 10-15%
```

### Buffer 为什么占最大头

```text
Buffer 功耗 ∝ buffer_depth × flit_width × vc_count × access_rate

示例：
  4 VC × 8 flit deep × 256 bit wide = 8192 bit SRAM per port
  5-port router = 40960 bit = 5 KB buffer
  
  每次 flit 读写 = 一次 SRAM access
  每周期可能多个 port 同时 access → 高 access rate
```

这就是为什么增加 VC 数量和 buffer 深度的代价不仅是面积，还有功耗。

## NoC 面积的组成

### Router 面积模型

```text
Router 面积 ≈ Buffer 面积 + Crossbar 面积 + Control 面积

Buffer 面积:
  A_buffer = vc_count × buffer_depth × flit_width × SRAM_bit_cell_area
  
Crossbar 面积:
  A_crossbar ∝ port_count² × flit_width
  （全交叉开关面积随端口数平方增长）
  
Control 面积:
  A_control ∝ vc_count × port_count  （相对较小）
```

### 具体数值估算（7nm 工艺参考）

| 组件 | 参数 | 面积估算 |
|---|---|---|
| Buffer (SRAM) | 4 VC × 8 deep × 256 bit × 5 port | ~0.015 mm² |
| Crossbar | 5×5 × 256 bit | ~0.005 mm² |
| Arbiter + Control | 4 VC × 5 port | ~0.002 mm² |
| **单个 Router 总计** | | **~0.02-0.03 mm²** |

### 不同拓扑的面积对比（N=16 tiles）

| 拓扑 | Router 数 | Router radix | 总 Router 面积 | Link 面积 | 总互连面积估算 |
|---|---|---|---|---|---|
| 4×4 mesh | 16 | 5 | ~0.4 mm² | ~0.2 mm² | ~0.6 mm² |
| 4×4 torus | 16 | 5 | ~0.4 mm² | ~0.35 mm²（长 wrap 线） | ~0.75 mm² |
| 2×2 concentrated mesh | 4 | 8 | ~0.2 mm² | ~0.1 mm² | ~0.3 mm² |
| 16-port crossbar | 1 | 16 | ~0.15 mm² | ~0.05 mm² | ~0.2 mm² |
| 4×(4-port crossbar) + mesh | 4 xbar + 4 router | 4+5 | ~0.25 mm² | ~0.15 mm² | ~0.4 mm² |

注意：这些是量级估算，实际值随工艺、频率目标和具体实现差异很大。关键是**相对比较**。

### 面积占比参考

```text
典型 AI 加速器面积分配：

  ┌─────────────────────────────────────────────┐
  │  Compute (MAC array)            50-65%      │
  │  SRAM (local + shared)          20-35%      │
  │  NoC (router + link + NI)        2-8%       │
  │  IO / PHY / misc                 5-10%      │
  └─────────────────────────────────────────────┘

NoC 面积通常只占 2-8%，但它的设计决策影响系统性能的 20-40%。
这就是为什么 NoC 架构探索的 ROI 很高。
```

## 关键参数对功耗和面积的影响

### Buffer 深度

```text
面积: A ∝ buffer_depth           （线性）
功耗: P ∝ buffer_depth           （线性，每深一级多一份 SRAM）
性能: 存在拐点——超过 credit RTT 后收益递减

推荐：buffer_depth = credit_round_trip_latency + 2-4 margin
  典型值：4-8 flit（单 hop），8-16 flit（多 hop 或跨 cluster）
```

### VC 数量

```text
面积: A ∝ vc_count               （线性，每 VC 一份独立 buffer）
功耗: P ∝ vc_count               （线性）
      allocator 功耗 ∝ vc_count²  （VA 仲裁复杂度）
性能: 2→4 VC 提升明显，4→8 VC 收益递减

推荐：AI NoC 通常 2-4 VC 足够（按 traffic class 数决定）
```

### Link width

```text
面积: A ∝ link_width             （线性，每 bit 一根线）
功耗: P ∝ link_width × activity  （线性，但活动率通常 < 50%）
性能: 带宽线性提升

推荐：匹配 tile 的注入/弹出速率即可，过宽的链路是浪费
  典型值：128-512 bit
```

### Router radix（端口数）

```text
面积: crossbar A ∝ radix²        （平方增长，这是面积杀手）
功耗: crossbar P ∝ radix²
      arbiter P ∝ radix × vc_count
性能: radix 越大，单 router 连接越多节点，hop 越少

4-port → 5-port: 面积增加 ~36%
5-port → 8-port: 面积增加 ~156%

这就是为什么 concentrated mesh（高 radix 少 router）和 flat mesh（低 radix 多 router）
之间存在面积-延迟取舍。
```

## 功耗面积与性能的取舍框架

```text
                    性能
                     ▲
                     │        ★ 理想点（不存在）
                     │       /
                     │      /
                     │     / ← Pareto 前沿
                     │    /
                     │   ●  ← concentrated mesh（少 router，中等性能）
                     │  / 
                     │ ●   ← flat mesh（多 router，高性能）
                     │/
                     ●───── crossbar（极端面积换极低延迟）
                     └──────────────────────► 面积/功耗
```

### 架构探索中的典型取舍

| 决策 | 性能方向 | 面积/功耗代价 | 何时值得 |
|---|---|---|---|
| 加宽链路 | 带宽↑ | 面积线性↑ | 当链路是瓶颈时 |
| 加深 buffer | 吞吐↑（到拐点） | 面积线性↑ | buffer < credit RTT 时 |
| 加 VC | HOL blocking↓ | 面积线性↑，allocator ↑² | traffic class ≥ 3 且互相干扰时 |
| 升 radix | hop↓ | crossbar 面积 ↑² | 小规模 cluster 内 |
| 加 pipeline stage | 频率↑ | 面积小↑，延迟 +1 cycle/stage | 长线无法 1 cycle 穿越时 |
| 加一张物理网络 | 隔离↑ | 面积翻倍 | control 被 data 严重干扰时 |

## 功耗估算的实用公式

### Per-flit 能量估算

```text
E_flit = E_buffer + E_crossbar + E_link

E_buffer ≈ 2 × flit_width × E_SRAM_access    （读 + 写各一次）
E_crossbar ≈ flit_width × E_mux              （穿越 crossbar）
E_link ≈ flit_width × wire_length × E_per_bit_per_mm

参考值（7nm）：
  E_SRAM_access ≈ 0.5 fJ/bit
  E_mux ≈ 0.1 fJ/bit
  E_per_bit_per_mm ≈ 0.2 fJ/bit/mm

示例（256-bit flit, 1mm link）：
  E_buffer = 2 × 256 × 0.5 fJ = 256 fJ
  E_crossbar = 256 × 0.1 fJ = 25.6 fJ
  E_link = 256 × 1 × 0.2 fJ = 51.2 fJ
  E_flit ≈ 333 fJ per hop
```

### 总 NoC 功耗估算

```text
P_noc = E_flit × flit_rate × hop_count_avg + P_leakage

示例：
  E_flit = 333 fJ/hop
  flit_rate = 1 Gflit/s（256-bit flit, 32 GB/s 有效带宽）
  hop_count_avg = 2.67（4×4 mesh）
  
  P_dynamic = 333 fJ × 1G × 2.67 = 0.89 W
  P_leakage ≈ 0.3 W（16 router）
  P_noc ≈ 1.2 W

  对比芯片总功耗 ~50-100W → NoC 功耗占 1-2%
```

## 对 DSL 的影响

### DSL 应该支持的功耗/面积查询

```yaml
evaluate:
  mode: analytical
  metrics:
    # 面积估算
    total_router_area:
      formula: Σ router_area(radix, vc_count, buffer_depth, flit_width)
    total_link_area:
      formula: Σ link_width × link_length × wire_pitch
    noc_area_ratio:
      formula: noc_area / chip_area
      
    # 功耗估算
    energy_per_flit:
      formula: E_buffer + E_crossbar + E_link(wire_length)
    noc_power:
      formula: energy_per_flit × traffic_rate × avg_hop + leakage
    noc_power_ratio:
      formula: noc_power / chip_power
```

### 架构探索中的面积/功耗约束

```yaml
constraints:
  noc_area_budget: 5%          # NoC 面积不超过芯片面积的 5%
  noc_power_budget: 3 W        # NoC 功耗不超过 3W
  
  # 这些约束会限制可探索的参数空间：
  # buffer_depth, vc_count, link_width, router_count
  # 编译器和架构探索器应该在约束内搜索最优解
```

## 本页结论

功耗和面积不是 NoC 设计的"第二优先级"，而是与性能同等重要的硬约束。buffer 占 router 功耗的 40-60%，crossbar 面积随 radix 平方增长——这两个事实直接约束了 VC 数量、buffer 深度和 router radix 的上限。DSL 的评估器应该能在性能仿真之外，同时输出面积和功耗估算，让架构探索在 Pareto 前沿上做选择而不是单维度追求性能。
