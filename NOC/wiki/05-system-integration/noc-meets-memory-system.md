# NOC Meets Memory System

上级：[05 System Integration](./README.md)

相关：[RAM: npu memory hierarchy](/mnt/e/wiki/RAM/wiki/09-ai-chip-memory-architecture/npu-memory-hierarchy.md)、[RAM: why mc is the real bottleneck](/mnt/e/wiki/RAM/wiki/06-memory-controller/why-mc-is-the-real-bottleneck.md)、[RAM: qos multi-master arbitration](/mnt/e/wiki/RAM/wiki/06-memory-controller/qos-multi-master-arbitration.md)

## 这页在回答什么问题

这页回答：为什么 NoC 和 memory system 不能分开优化，以及为什么很多“网络瓶颈”最终其实是 local SRAM、HBM port 或 memory controller 在定义上限。

## NoC 不是独立的数据海关

NoC 只负责把流量送到 memory system 边界，真正的数据服务能力来自：

- tile 本地 SRAM / scratchpad
- cluster memory
- shared SRAM pool
- HBM / DRAM port
- memory controller 调度

所以网络吞吐的有效上限不只是 `link_bw`，而是：

```text
effective_bw <= min(network_path_bw, endpoint_bw, bank_port_bw, controller_service_bw)
```

这条关系听起来简单，但被忽略得非常频繁。

## 参数化展开 effective_bw

为了让上式不停留在概念，把四项每项都展开成可测量的参数：

```text
network_path_bw       = min over all links on path of (link_width · frequency)
endpoint_bw           = NI_width · frequency
bank_port_bw          = bank_width · frequency / bank_conflict_factor
controller_service_bw = num_active_channels · channel_bw · controller_efficiency
```

四项的典型量级（1 GHz 系统）：

| 项 | 典型范围 | 决定因素 |
|----|---------|---------|
| `network_path_bw` | 16~128 GB/s | link 宽、router 频率 |
| `endpoint_bw` | 32~128 GB/s | NI 宽度、tile 端口数 |
| `bank_port_bw` | 8~64 GB/s | bank 数、port 数、conflict |
| `controller_service_bw` | 12~600 GB/s | HBM stack 数、queue 深度、调度 |

**关键观察**：四项的典型范围不重合。`network_path_bw` 与 `endpoint_bw` 通常是同量级，但 `bank_port_bw` 可低一个数量级，`controller_service_bw` 在小尾端会成为系统天花板。所以"网络是不是瓶颈"问题，等价于"上式 min 的产生位置在哪一项"。

## 本地 SRAM 会反向定义 ejection 能力

当数据到达 tile 或 cluster 端时，还要经过：

- ejection FIFO
- local write port
- SRAM bank / port arbitration
- compute 与 DMA / NoC 的共享访问

如果这些局部资源吃不动，NoC 看到的就会是：

- credit 回不来
- ejection blocked
- 上游 injection 被迫放缓

这说明某些所谓的"网络 backpressure"，本质是 local memory consumption backpressure。

### bank conflict 参数化

local SRAM 的 `bank_port_bw` 等效公式：

```text
bank_port_bw_effective = num_banks · port_per_bank · bank_width · freq
                       / max(1, conflict_factor)

conflict_factor = E[同周期请求同一 bank 的请求数]
                = (num_concurrent_requests)^2 / num_banks   (uniform 随机访问下)
                + access_pattern_skew_term
```

对 AI workload 的两种典型访问模式：

| 访问模式 | conflict_factor 估计 | 影响 |
|---------|---------------------|------|
| GEMM tile-major（顺序，按 bank stripe）| ≈ 1 | bank_port_bw 接近峰值 |
| Attention head-major 写 KV cache | ≈ 1.5~3 | bw 降 30~70% |
| 多 DMA + compute 并发访问 | ≈ 3~8 | bw 退到 1/3 以下 |

这就是 NoC 看上去带宽够、系统跑不满 的最常见根因之一：ejection 端的 SRAM 因为 bank conflict 服务速率不够，credit 链堵在 last hop。

### 从 SRAM 反推 ejection 最大稳态吞吐

```text
max_sustainable_ejection_flit_per_cycle
  = bank_port_bw_effective · bytes_per_flit_inverse
  = (num_banks · port · width · freq / conflict_factor) / flit_bytes
```

例：4 banks × 1 port × 32 B × 1 GHz / conflict=2 = 64 GB/s ÷ 32 B/flit = 2 flits/cycle。若 NoC link 能力 = 4 flits/cycle，**链路自然只能利用一半**——再优化 router 也没用。

这条公式应该作为 simulator 的 endpoint 配置项，让 `ejection_drain_rate` 反映真实 SRAM 服务能力，而不是无限快。

## HBM / memory controller 则定义 request-response 节奏

对外部 memory 路径，决定系统节奏的通常不是 NoC hop 数，而是：

- HBM channel 数量
- address interleaving
- controller scheduling
- row / bank / write-drain 行为
- 返回路径的聚合形状

如果 memory controller 本身已经是主瓶颈，那么单纯改善 NoC topology 的收益会迅速变小。

### HBM 与 NoC 注入率的耦合公式

设：
- `C_HBM` = HBM channel 数（HBM2e 通常 8/stack、HBM3 16/stack）
- `B_HBM` = 单 channel 带宽（HBM3 ≈ 800 MB/s 物理 × burst = 51.2 GB/s effective）
- `T_HBM` = 单请求 round-trip latency（含 row activate + read + return），典型 80~120 ns
- `OS_max` = 控制器最大 outstanding request 数

NoC 注入率上限：

```text
hbm_service_bw       = C_HBM · B_HBM · scheduling_efficiency
                     # scheduling_efficiency ≈ 0.7~0.85（含 row miss / write turnaround）

hbm_request_rate_max = OS_max / T_HBM
                     # Little's Law：在途数 = 速率 × 延迟

noc_injection_rate_to_hbm = min(hbm_service_bw / avg_response_size,
                                hbm_request_rate_max)
```

例：HBM3、16 channels、800 GB/s 峰值、`scheduling_efficiency=0.75`、`OS_max=64`、`T_HBM=100ns`：

- `hbm_service_bw = 600 GB/s`
- `hbm_request_rate_max = 64 / 100ns = 640 M req/s`
- 若 avg response = 256 B：服务速率 = 600 GB/s / 256 B ≈ 2.34 G req/s（被 OS_max 限到 640 M req/s）

**关键结论**：`OS_max` 不够大时，HBM 物理峰值带宽根本用不上。这是 NoC 端常被怪罪的"瓶颈"，根因是上游 DMA / endpoint 的 outstanding 配置不足。

### 返回路径的 burst 形状

HBM 响应返回时是 burst 模式（典型 32 B × 8 burst = 256 B 一次性返回）。这意味着：

```text
ejection 端在 burst window 内瞬时压力
  = burst_size / NI_width
  flits 在 1~2 cycle 内涌入 ejection queue
```

如果 ejection_depth 没考虑这个 burst，会在每个 HBM response 到达时短暂触发 `EJECTION_BLOCKED`，造成 bursty stall。这条经验值：

```text
ejection_depth >= max(buffer_R_requirement, max_burst_flits + 2)
```

第一项来自 [credit-based-flow-control](../02-router-microarchitecture/credit-based-flow-control.md#推导使链路饱和的最小-buffer_depth)，第二项来自 HBM burst。两者取大。

## 为什么 AI 工作负载特别容易暴露这件事

因为 AI 工作负载经常会同时触发：

- 大量规则 bulk read/write
- 局部 SRAM 高频复用
- 某些阶段性的 gather / reduce / writeback
- 对 HBM 返回路径的强依赖

这样一来，NoC 与 memory system 之间几乎没有清晰分界线。流量是否“跑得起来”，很大程度上取决于 memory hierarchy 是如何配平的。

## 一个常见误诊模式

常见误诊是：

- 看到 link 利用率不高
- 又看到系统总吞吐不佳
- 就怀疑 router、routing 或 topology

但更常见的根因其实是：

- DMA outstanding 太小，memory latency 没隐藏住
- HBM port 端口数或调度成了瓶颈
- local SRAM bank conflict 把 ejection 拖住

也就是说，网络“没满”不代表网络“不是系统瓶颈链的一部分”，它可能只是被 memory system 另一端卡住了。

## NoC 和 memory hierarchy 的耦合方式

最关键的耦合有四种：

- `placement coupling`：数据放在哪里，决定流量打向哪里
- `port coupling`：memory port 数量和位置决定热点出口
- `timing coupling`：controller 返回节奏决定 response burst 形状
- `local-consume coupling`：本地 SRAM / compute 消费能力决定终点 backpressure

这四种耦合里，前两种偏结构，后两种偏动态；都必须被建进系统模型。

## deterministic NPU 的典型处理思路

较稳妥的思路通常不是让 NoC 独自兜底，而是同时做：

- 数据布局与 address interleaving
- DMA 节奏控制
- local SRAM bank/port 规划
- 必要时 control/data/memory fabric 分离

这比单纯在 router 里加更多动态智能更贴近 deterministic 设计目标。

## 一句话理解

NoC 决定“数据怎么走到 memory 边界”，memory system 决定“数据到了以后能不能被服务和消化”；两者共同定义有效带宽。

## 建模启示

建模时，NoC 和 memory system 至少要通过这些状态连起来：

- ejection FIFO occupancy
- local bank / port service rate
- memory controller queue / service rate
- HBM channel mapping
- request-response return latency distribution

完整参数化对象建议：

```text
LocalSRAMModel {
  num_banks; port_per_bank; bank_width; freq
  conflict_factor(access_pattern)    # 由 placement / workload phase 派生
  effective_bw -> drives endpoint.consumer_rate_flits_per_cycle
}

HBMModel {
  num_channels; channel_bw; T_RT
  OS_max
  scheduling_efficiency
  burst_size; bursts_per_response
  effective_bw  -> drives source-endpoint injection_rate cap
  burst_shape  -> drives ejection_depth requirement
}

NocMemoryCoupling {
  injection_rate_cap = min(noc_link_bw,
                            hbm_service_bw / avg_response_size,
                            OS_max / T_RT)
  ejection_rate_cap  = local_sram.effective_bw / flit_bytes
}
```

如果模型只给 memory 一个固定延迟常数，会错过：

- burst 返回峰值
- bank / port 局部热点
- request / response 互相拖累
- effective bandwidth 明显低于 peak 的真实原因

正确的链路：**workload phase → access pattern → conflict_factor → SRAM effective bw → endpoint consumer rate → ejection backpressure → credit 链 → injection 端口反压 → injection_rate cap**。任何一环用常数代替，链上后续都会失真。`from-workload-to-traffic-trace.md` 里 `placement_ctx` 字段就是为了把 access pattern 显式传到这里。
