# 参数与配置参考：数值、单位和边界怎样对应？

<span id="parameter-reference"></span>

上级：[09 模拟器构建与验证](../SUMMARY.md#08-simulator-construction)；原章节：[08 Simulator Construction](./README.md)

相关：[模拟器设计规格](./simulator-design-spec.md)、[Credit 与反压](../02-router-microarchitecture/credit-based-flow-control.md)、[验证与校准](./verification-and-calibration.md)

## 使用规则

每次实验记录参数值、单位、来源、消费者和模型版本。下表中的数字只是教学配置，不是行业规格。区分配置合法性、性能建议和是否已校准。

| 组 | 示例参数 | 单位和条件 |
| --- | --- | --- |
| 拓扑／路由 | `rows=4, cols=4`，固定路由 | 节点、端口和有向邻接要能复原；端点位置单独记录。 |
| flit 与链路 | `flit_bytes=16, link_width_bits=128` | 基线一次传输一个同宽 flit；不同宽度需定义 phit 和串行化。 |
| 时钟 | `frequency_hz=1e9` | 本章基线使用单时钟；多时钟及 CDC 是另行建模的扩展。 |
| 正反向延迟 | `forward_latency=1, return_latency=1` | 各为正整数 cycle；到期在拍末提交。返回延迟不是完整信用往返时间。 |
| input VC | `vcs_per_input=4, depth_per_vc=8` | VC 数／input、slot／VC；总容量与每 VC 深度不能混用。 |
| 端点 | 注入与 ejection 深度、`consumer_rate` | 标明 packet 或 flit 单位、服务规则和完成点。 |
| 仲裁 | 策略、每 input/output 允许的 grant 数 | 若建模流水 allocator，还要记录 latency、启动间隔和 pointer 更新。 |
| 任务 | `release_time`、依赖、源目的、payload、class、compute 时长 | 单位与第八章 v1 一致；资源和消费者需另行定义。 |
| 实验 | seed、测量窗口、模型和配置版本 | 记录未完成对象；有限 workload 与稳态实验的窗口不同。 |

## 派生量与合法性

若每个 link cycle 恰好传一个完整的 W-bit 物理传输单位，链路频率为 f，则原始速率为 W×f/8 B/s；有效 payload 还受 header、padding、空拍及重传影响。链路和内部 flit 的位宽可以不同；基线固定同宽，扩展模型需给出 phit 打包和时钟规则。

令 **T<sub>credit</sub>** 为从某次发送到其返还 credit 首次可参与发送决策的完整间隔，不与仅表示返程传输的 `return_latency` 混用。若固定反馈间隔为 T<sub>credit</sub>，单 VC、连续供数且其他资源不阻塞，要维持目标平均速率 r，可先按 ⌈r×T<sub>credit</sub>⌉ 个 slot 估算必要窗口。这个容量不保证任意突发、仲裁、包间 VC 许可等待或下游停顿下都能保持该速率。

例如本章快照中，正向和返回延迟均为 1：拍 0 发送，拍 1 末到达，拍 2 移出下游 FIFO，拍 3 末返回 credit，拍 4 才能使用，故此例 T<sub>credit</sub>=4 cycle。深度 1 是合法配置，但不足以让该单 VC 在以上条件下每拍持续发送。

负容量、未知端口、不可达 route 和非法依赖应按模型契约报错。较浅 buffer 或多个 class 共用 VC 可以是合法设计；是否满足性能、隔离和前进要求需另外验证。

## 外部工具的可追溯对照

[gem5 Garnet 2.0 文档](https://www.gem5.org/documentation/general_docs/ruby/garnet-2/)给出默认 1-cycle router、`vcs_per_vnet=4` 和 control/data VC 深度 1/4 flit。这里的 4 是每个 vnet 的 VC 数，不能直接当作本模型每个 input 的总 VC 数。

固定版本的 [BookSim 配置源码](https://github.com/booksim/booksim2/blob/54e2e6d2608297e4374a9a5f9b3baa0ca2c5d687/src/booksim_config.cpp)给出 `num_vcs=16`、`vc_buf_size=8`；实际配置文件可以覆盖它们。比较工具时还需对齐拓扑、路由、buffer、VC 释放、时间和统计边界。

## 验证与 sweep

保存完整配置、来源、单位和随机种子；记录未完成任务与适用范围。先用[逐拍场景](./verification-and-calibration.md)检查模型，再用独立参考校准。扫描 link、VC 或 buffer 时，同时说明频率、端点服务和固定的面积／容量预算。
