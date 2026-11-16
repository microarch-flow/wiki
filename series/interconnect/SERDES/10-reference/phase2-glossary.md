# 第二阶段术语表

上级：[SerDes 术语、资料与自测](./README.md)

本表帮助查找概念；测量和适用条件以对应正文为准。基础术语见[第一阶段术语表](./glossary.md)。

| 术语 | 本专题含义与边界 |
| --- | --- |
| 符号 / Bd | 一个符号周期内选择的信号状态 / 每秒符号数；不等于应用有效比特数。见 [NRZ 与 PAM4](../05-signaling-and-metrics/nrz-and-pam4.md)。 |
| 线路编码 / 加扰 / 调制 | 分别组织码组或块、变换比特序列、把比特映射为符号；不是同一操作。见[编码与加扰](../05-signaling-and-metrics/coding-and-scrambling.md)。 |
| 眼高 / 眼宽 | 在指定采样时刻 / 指定门限处观察到的电压 / 时间开口；必须说明参考与测量条件。见[眼图和抖动](../05-signaling-and-metrics/eye-and-jitter.md)。 |
| BER | 可指观察错误比特占比，或语境中的误码概率；必须注明观察位置和测试条件。见 [BER、置信度与 FEC](../05-signaling-and-metrics/ber-confidence-and-fec.md)。 |
| 单侧置信上界 | 由样本和统计模型计算的参数上界；`3/N` 是零错误、独立同分布和约 95% 置信度下的近似。 |
| pre-FEC / post-FEC | FEC 解码前 / 后的观察位置。码字失败率与比特 BER 不能直接互换。 |
| 有效带宽 / pJ per bit | 某一层或时间窗内交付的数据速率 / 每个指定口径比特分摊的能量；分子与分母边界需一致。见[带宽和能耗](../05-signaling-and-metrics/bandwidth-power-efficiency.md)。 |
| 校准 / 训练 / 自适应 | 校准处理规定的电路参数；训练按接口规则建立工作条件；自适应依据观察调整参数。实现中可能相互配合。见[训练与自适应](../06-link-operation/training-and-adaptation.md)。 |
| lane skew / deskew | 对应数据在 lane 间的到达差异 / 按协议对齐的处理；允许范围和缓存机制依实现而异。见 [lane 对齐](../06-link-operation/lane-alignment.md)。 |
| LTSSM / Recovery / L0 | PCIe 的链路训练与状态机 / 其中的恢复相关状态 / 工作状态；不能用作所有 SerDes 的通用状态名。见 [PCIe 案例](../06-link-operation/pcie-training-case.md)。 |
