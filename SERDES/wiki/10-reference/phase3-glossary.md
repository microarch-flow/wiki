# 第三阶段术语表

上级：[SerDes 术语、资料与自测](./README.md)

本表补充设计验证、系统场景和建模术语。链路模块、指标与训练术语分别见[第一阶段术语表](./glossary.md)和[第二阶段术语表](./phase2-glossary.md)。

| 术语 | 本专题含义及入口 |
| --- | --- |
| PVT / 角点 | 工艺、电压、温度 / 按指定模型选出的条件组合；有限角点不自动覆盖全部真实变化。[电路与 PVT](../07-design-and-validation/circuit-layout-and-pvt.md) |
| 参考面 / 去嵌 | 定义信号或测量的位置 / 用已表征的模型数学移除夹具等影响；去嵌仍有模型和测量不确定度。[实验室测试](../07-design-and-validation/lab-compliance-interop.md) |
| S 参数 / `Sdd21` | 按参考阻抗定义的频率域散射参数 / 一项差分传输参数；完整通道仍需其他端口和频率信息。[通道模型](../07-design-and-validation/system-and-channel-models.md) |
| IBIS-AMI | 用于高速收发器算法模型的接口；统计与时域方法对模型有不同假设。它不是实物测试数据。 |
| 合规 / 互通 | 对指定规范项目的测试 / 在指定对端和条件下的互操作。各自的范围与判据必须记录。 |
| D2D / UCIe | die-to-die，芯粒间连接 / 一组封装级互连规范；D2D 不指定唯一协议或 PHY。[Chiplet 与 D2D](../08-system-applications/chiplet-and-d2d.md) |
| HBM / TSV | 堆叠式高带宽 DRAM / 硅通孔；TSV 是物理连接手段，不独自定义主机协议。[HBM 与 3D](../08-system-applications/hbm-and-3d.md) |
| CPO / 光引擎 | 共封装光学 / 实现电光转换等功能的组件；具体边界、激光源和信号处理依架构而异。[CPO](../08-system-applications/cpo-electrical-optical.md) |
| 事件模型 / 背压 | 以定义的状态和事件推进系统的抽象 / 接收方暂不接受新请求的流控行为；需明确容量和重试责任。[状态模型](../09-modeling/link-state-and-failure.md) |
| 串行化 / 传播延迟 | 消息占用链路服务所需时间 / 信号沿通道传播及抽象管线的时间；在可流水模型中两者可能重叠。 |
| 模型校准 / 模型验证 | 按参考数据调整模型参数 / 用预先明确的输入和判据检查模型预测；匹配校准数据不自动证明其他场景有效。它与芯片电路的参数校准不是同一项工作。 |
