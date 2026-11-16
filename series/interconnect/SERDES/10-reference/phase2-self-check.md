# 第二阶段自测：指标与训练

上级：[SerDes 术语、资料与自测](./README.md)

先写出假设，再展开参考答案。以下题目和计算是教学例子，不代表真实链路的测量结果。

## 问题

1. 在线路比特率 `20 Gb/s`、未计编码开销时，NRZ 与 PAM4 的符号率和 UI 各是多少？为什么这不等于应用带宽？
2. 一个 `8b/10b` 链路连续发送数据字符，线路速率 `10 Gb/s`。只扣除该编码开销后，上限是多少？控制字符和空闲会怎样影响结果？
3. 若同一信号使用不同 CDR 参考测量眼图，为什么结果可能不同？仅知道眼宽能否确定 BER？
4. 在独立、固定误码概率模型中，检查 `3 × 10^12 bit` 且零错误，如何估算单侧 `95%` 上界？它为什么不是“误码概率为零”？
5. 两次测试的 pre-FEC BER 相同，但一组错误集中成突发。为什么不能直接断定 post-FEC 结果也相同？
6. 功率 `0.2 W`，线路速率 `10 Gb/s`，有效载荷速率 `4 Gb/s`。两种口径的 `pJ/bit` 各是多少？
7. PLL 锁定后，为什么仍需要观察接收对齐和协议状态？本地 RX 自适应与请求对端调整 TX 有什么区别？
8. 两条 lane 的对应标记相差 `2 UI`，每 UI 为 `100 ps`。到达偏差是多少？为什么这个数不能单独决定 FIFO 深度？
9. 一个 PCIe 链路最终读到 `8 GT/s x4`。这能否证明设备只支持 Gen3，或者证明通道一定有问题？

<details markdown="1">
<summary>查看参考判断</summary>

1. NRZ：`20 GBd`、`50 ps`；PAM4：`10 GBd`、`100 ps`。编码、FEC、空闲及协议开销尚未扣除。[NRZ 与 PAM4](../05-signaling-and-metrics/nrz-and-pam4.md)
2. `10 × 8/10 = 8 Gb/s` 是只扣除编码比例的上限；控制和空闲占用线路时间时，业务数据速率更低。[编码与加扰](../05-signaling-and-metrics/coding-and-scrambling.md)
3. 不同时钟恢复模型跟踪的相位变化可能不同；有限眼图不能单独给出尾部错误概率。还需明确参考面、码型和测量方法。[眼图和抖动](../05-signaling-and-metrics/eye-and-jitter.md)
4. `2.996/(3 × 10^12) ≈ 1.0 × 10^−12`。零错误仅是有限样本结果；结论依赖独立与概率恒定等假设。[BER 与置信度](../05-signaling-and-metrics/ber-confidence-and-fec.md)
5. FEC 按码字和译码算法工作。错误如何分布在各码字内会改变能否纠正；还需知道交织和计数口径。[FEC 前后](../05-signaling-and-metrics/ber-confidence-and-fec.md)
6. 线路口径 `20 pJ/bit`，有效载荷口径 `50 pJ/bit`。应说明同一时间窗及功率包含的模块。[带宽和能耗](../05-signaling-and-metrics/bandwidth-power-efficiency.md)
7. 本地 PLL、CDR、边界恢复和协议状态不是同一层的条件。RX 自适应调整本地接收参数；双端训练中的 TX 请求只有协议支持时才存在。[训练与自适应](../06-link-operation/training-and-adaptation.md)
8. 偏差为 `200 ps`。还需考虑标记、时钟容差、动态偏差、读写时序和规范限值，才能设计实际缓冲。[lane 对齐](../06-link-operation/lane-alignment.md)
9. 不能。它只是该时刻的工作状态；根因和双方能力需结合配置、日志和测试确定。[PCIe 案例](../06-link-operation/pcie-training-case.md)

</details>

通过自测只说明回答覆盖了这些问题，不证明任何硬件或协议实现符合规范。
