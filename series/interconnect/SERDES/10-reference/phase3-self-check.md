# 第三阶段自测：设计、系统与模型

上级：[SerDes 术语、资料与自测](./README.md)

先写出条件和推理，再展开参考判断。例子是教学假设，不代表硬件测量或产品规格。

1. 一份需求只写“单 lane 10G、通道损耗 12 dB、BER 合格”。至少还缺少哪些会影响验收的条件？
2. 一次接收眼图仿真通过，能否直接证明芯片对所有 PVT、噪声与对端都可用？为什么？
3. ADC-DSP 接收器是否不再需要模拟前端和时钟？增加均衡抽头是否一定改善整个系统？
4. 某器件通过了一项电气测试。为什么仍需要检查其他合规项目与指定对端互通？
5. `4 × 10 Gb/s` 和 `2 × 20 Gb/s` 的单方向 NRZ 链路都使用 `8b/10b`。在无其他开销时，它们的数据上限各是多少？两者功耗是否必然相同？
6. HBM 堆栈内部的 TSV 连接与主机到堆栈的 HBM 接口，是不是同一段通道？`1024` 条数据线各以 `2 Gb/s` 传输时，峰值是多少？
7. 输入光功率为 `0 dBm`，光纤损耗 `3 dB`，其他连接损耗 `2 dB`。输出功率是多少？为什么还不能仅据此认定链路达标？
8. 一条标为 `224G PAM4` 的产品链路，在什么额外假设下可以计算为 `112 GBd`、约 `8.93 ps/UI`？
9. 事件模型的队列容量计入在服务数据；一个请求比总容量更大时，模型需要明确什么？
10. 在[教学事件模型](../09-modeling/worked-model-and-limits.md)中，A、B 何时完成？如果没有定义恢复触发和时长，能否自行加入 `2 μs` 停顿？
11. 同一 `4 μs` 窗口内，`200 mW` 持续 `2 μs`、`80 mW` 持续 `2 μs`，能量与平均功率是多少？交付 `16000 bit` 时是多少 `pJ/bit`？
12. 事件模型与某次系统吞吐量测量吻合。它能否证明眼图、BER、器件互通和量产可靠性？

<details markdown="1">
<summary>查看参考判断</summary>

1. 至少需要协议 / 模式、调制与编码、损耗频率和参考面、PVT、对端、误码观察点、测试码型 / 时间及判据。[需求契约](../07-design-and-validation/requirements-and-contract.md)
2. 不能。它只覆盖所选模型和条件；未包含或未覆盖的效应仍需其他分析与测量。[通道模型](../07-design-and-validation/system-and-channel-models.md)
3. 不是。ADC 前仍有模拟输入与采样时钟限制；抽头带来的收益也受噪声、时序、功耗和范围约束。[架构取舍](../07-design-and-validation/architecture-tradeoffs.md)
4. 电气、协议和互通是不同观察；一项通过不覆盖其他测试、对端或环境。[测试分工](../07-design-and-validation/lab-compliance-interop.md)
5. 各为 `32 Gb/s`；功耗取决于各 lane、共享模块、状态和测量边界，不能只由总速率确定。[lane 数与速率](../08-system-applications/lane-count-vs-rate.md)
6. 不是。按题设算为 `256 GB/s` 的单方向数据位峰值，还未扣除控制器和存储行为的影响。[HBM 与 3D](../08-system-applications/hbm-and-3d.md)
7. `−5 dBm`。还需要接收灵敏度对应的速率 / BER、其他损耗、余量和完整电光条件。[CPO 预算](../08-system-applications/cpo-electrical-optical.md)
8. 需假设实际线路比特率精确为 `224 Gb/s`，且每个 PAM4 符号映射 `2 bit`；产品名称本身不保证全部模式都满足该数值。[产品声明](../08-system-applications/product-claims-and-evidence.md)
9. 必须定义拆分、拒绝或其他明确处理。仅背压且永不拆分，会导致该请求在队列清空后仍无法进入。[状态与失败](../09-modeling/link-state-and-failure.md)
10. 无恢复时 A 为 `1 μs`、B 为 `2 μs`；指定恢复时 A 为 `1 μs`、B 为 `4 μs`。不能凭空加入停顿；需给触发、时长和排队规则。[事件模型](../09-modeling/worked-model-and-limits.md)
11. 能量 `0.56 μJ`，平均功率 `0.14 W`，每交付比特 `35 pJ/bit`；分子分母要位于同一窗口。[事件模型](../09-modeling/worked-model-and-limits.md)
12. 不能。吻合只说明所比较条件和指标下的模型表现；其他结论需要相应证据。[模型层次](../09-modeling/modeling-scope.md)

</details>

通过自测只说明这些问题得到检查，不代表已验证实际芯片或产品。
