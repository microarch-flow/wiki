# 第一阶段自测：从发送到接收

上级：[SerDes 术语、资料与自测](./README.md)

先独立判断，再展开参考答案。每题都依赖题设条件；正确回答不代表已验证真实芯片。

1. 每个 `312.5 MHz` 周期输入一个 `32 bit` 字。什么条件下串行线速率是 `10 Gb/s`？
2. `VP = 0.65 V`、`VN = 0.45 V`。差模和共模各是多少？若两线都增加 `0.1 V` 呢？
3. 两条 lane 的对应数据相差 `240 ps`，UI 是 `100 ps`。相差多少 UI？能否仅据此确定缓冲深度？
4. 某频点 `Sdd21` 为 `−20 dB` 时，需要哪些参考条件？能否由此直接得到 BER？
5. 在 `r[k] = 0.7a[k] + 0.2a[k−1]` 中，当前符号为 `+1`，两种历史分别得到什么？是否必然误码？
6. TX FFE、RX CTLE 和 RX DFE 各处在哪里？为什么均衡不能无限增强？
7. 长时间没有可用跳变时，CDR 会遇到什么问题？CDR 锁定是否意味着字边界已对齐？
8. DFE 使用了错误的上一判决，下一次是否一定错？
9. 一条 lane 采对每一位后，为什么并行字或多 lane 数据仍可能错位？
10. 一张示意图、一次仿真、一次样片测量和完整产品验证，能否支持同样的结论？

<details markdown="1">
<summary>查看参考判断</summary>

1. 需要每周期有一个有效字、无额外编码或空闲等假设：`32 × 312.5 MHz = 10 Gb/s`。有空周期或额外传输位时需重新计算。[速率换算](../01-overview/rates-clocks-and-ui.md)
2. 差模 `0.20 V`，共模 `0.55 V`；两线各加 `0.1 V` 后差模仍为 `0.20 V`，共模为 `0.65 V`。[差分示例](../02-signal-channel/differential-and-return.md)
3. 相差 `2.4 UI`。缓冲还取决于对齐标记、时钟域、字宽和协议要求。[skew 与 jitter](../02-signal-channel/timing-skew-and-jitter.md)
4. 至少明确频率、端口、参考阻抗、参考面和去嵌条件。BER 还依赖信号、噪声、接收器和测量条件。[通道损耗](../02-signal-channel/loss-db-and-s-parameters.md)
5. 前一符号为 `+1` 时得 `+0.9`，为 `−1` 时得 `+0.5`。在零门限和无噪声的假设下两次均正确。[ISI 示例](../02-signal-channel/isi-noise-and-eye.md)
6. FFE 在此例的发送侧改变输出；CTLE 在线性接收前端调整频率响应；DFE 利用接收端的历史判决。输出范围、噪声、系数误差和反馈时序限制效果。[发送均衡](../03-transmitter/tx-equalization-ffe.md)、[CTLE](../04-receiver/analog-frontend-and-ctle.md)、[DFE](../04-receiver/dfe-and-error-propagation.md)
7. 依赖跳变的检测器在该区间没有新的边沿信息，要依靠已有状态和本地时钟；频差会带来相位漂移。锁定与字边界对齐是不同状态。[CDR](../04-receiver/cdr-and-timing-recovery.md)
8. 不一定。无扰动示例得到 `+0.3`，仍在零门限上方；加上题文所述扰动后才可能翻转。[DFE 反例](../04-receiver/dfe-and-error-propagation.md)
9. 位序、单 lane 字边界与多 lane 相对位置分别需要约定和检查。[解串与对齐](../04-receiver/deserializer-and-alignment.md)
10. 不能。示意图表达关系；仿真受模型和条件限制；测量覆盖所测样片与条件；产品验证还需相应的互通、工作条件和可靠性证据。[RX 案例的边界](../04-receiver/rx-cooperation-example.md)

</details>
