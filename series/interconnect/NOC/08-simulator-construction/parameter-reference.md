# Parameter Reference

上级：[08 Simulator Construction](./README.md)

相关：[Core Data Structures](./core-data-structures.md)、[Credit Based Flow Control](../02-router-microarchitecture/credit-based-flow-control.md)、[Allocator Design](../02-router-microarchitecture/allocator-design-vc-switch.md)、[Topology Design Metrics](../03-topology/topology-design-metrics.md)、[NOC Meets Memory System](../05-system-integration/noc-meets-memory-system.md)

## 使用规则

每次实验记录参数值、单位、来源、模型消费者和版本。以下仅给**教学起点**，不是行业规格或法定区间；实际值由拓扑、接口、工艺或校准决定。协议合法性、性能建议和实现假设必须分开。

| 组 | 参数及示例 | 单位与消费者 | 条件 |
| --- | --- | --- | --- |
| 拓扑 | `topology=mesh`, `rows=4`, `cols=4`, `concentration=1` | 节点数、邻接、routing | 不规则、fat-tree、dragonfly 需显式邻接和端口；N 不能唯一决定图 |
| 数据粒度 | `flit_bytes=16`, `link_width_bits=128` | flit/slot；物理 phit bits | 两者独立；若 flit 宽于 link，按配置串行化 phit |
| 时钟 | `router_frequency_hz=1e9`, `link_frequency_hz=1e9` | 每个域独立 | 不同时钟域需显式 CDC 与时间换算 |
| 正反链路 | `forward_latency=1`, `return_latency=1` | 各自 clock cycle；link pipes | 本章基线为正整数，采样规则见下文 |
| Router | `vcs_per_input=4`, `depth_per_vc=8` | 每 input 的 VC 数、flit slot 数 | 按 routing、class、依赖与资源预算验证 |
| 队列 | `injection_depth`, `ejection_depth` | 指明 packets 或 flits | 不得混用；容量根据到达、消费和反压实验确定 |
| 分配器 | `policy=round_robin`, `latency`, `II` | cycle、grant 规则 | 若用 iSLIP 还须说明 iteration 在同拍还是跨拍；效率由相同负载测得 |
| Endpoint | `consumer_rate`、`max_outstanding` | flit/cycle、请求数 | 说明资源释放点及端点时钟 |
| Workload | `release_time`, `src_node`, `dst_set`, `payload_bytes`, `depends_on`, `traffic_class` | cycle、节点、B | 依赖以 consumer 完成为准或显式声明其他边界 |
| Memory | channel 数、每 pin 数据率、数据位宽、bank/port、服务和 RTT 分布 | B/s、req/s、秒 | burst 是传输量，不再乘每 pin 数据率；单位见 [memory 边界](../05-system-integration/noc-meets-memory-system.md) |
| 实验 | warmup、measurement、drain、seed、模型版本 | cycle 和整数 | 保存未完成样本与所有 sweep 输入 |

## 派生量与合法性

单链路物理字节速率是 `link_width_bits × link_frequency_hz / 8` B/s；有效 payload 还要扣 header、padding、空拍及重传。序列化拍数在每拍可传一个完整 phit 时为 `ceil(flit_bits / phit_bits)`，跨域须按两个时钟和具体握手处理。不能把线长除以一个虚构的统一信号速度直接决定 pipeline 数；应由物理实现和时序约束校准正反延迟。

固定 R cycle、单 VC 目标速率 r flit/cycle 的稳态窗口估算为 `ceil(r×R)` slot；`depth<R` 是合法配置，只是独占满速可能出现气泡。队列深度还取决于突发、仲裁和采样规则，不存在通用 `max(R,burst+2)` 下界。多个 class 可以共享 VC；若要做隔离或死锁证明，按真实依赖与服务规则决定 VC 数，而不是强制 `VC数≥class数`。allocator η 是工作负载下实测的匹配统计，不能只由算法名推导。

基线的时间定义：跨 router 发送时即扣 credit，表示预留下游 slot；下游移出 slot 后生成返回 credit，返回事件拍末提交，下一拍才可用。单播时间、TAIL 本地释放及下游许可见 [快照契约](./router-pipeline-pseudocode.md#时间与快照契约)。

## 外部工具的可追溯对照

- [gem5 Garnet 2.0 官方文档](https://www.gem5.org/documentation/general_docs/ruby/garnet-2/)描述默认 router 为 1-cycle、`vcs_per_vnet=4`、control/data VC 深度分别为 1/4 flit；默认 flit 16 B。它的具体实现、vnet 数和拓扑仍取决于配置，不能把这些值直接当本模型规格。
- BookSim 的 [固定版本 `54e2e6d2608297e4374a9a5f9b3baa0ca2c5d687` 配置源码](https://github.com/booksim/booksim2/blob/54e2e6d2608297e4374a9a5f9b3baa0ca2c5d687/src/booksim_config.cpp) 中 `num_vcs=16`、`vc_buf_size=8`；配置文件可能覆盖默认值。跨实验应保存 commit 和完整配置。
- 产品名称不能推断拓扑、控制器在途深度或实际瓶颈；没有同一工作负载和测量边界的证据，不把 NVSwitch 称为 dragonfly，也不由一个 OS 数推断 HBM 不会成为瓶颈。

## 验证与 sweep

启动时拒绝负容量、未知端口、无效 route、环形 trace 依赖和单位错误。`depth<R`、多个 class 共用 VC 等是可运行的设计选择，最多提示性能或安全条件需要验证。扫描时共同记录 topology/placement、宽度/频率、allocator 的综合频率、buffer/R、流量/端点服务和内存映射；每组结果附配置、种子与来源。先以 [逐拍手算表](./verification-and-calibration.md) 验证，再用目标实现校准。
