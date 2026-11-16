# 第二阶段资料入口

上级：[SerDes 术语、资料与自测](./README.md)

下表记录本阶段的主要一手资料。设备文档与应用说明只适用于各自描述的产品、版本和条件；协议要求仍应查对应规范正文。数值教学例子是本专题的推导，不是资料中的产品测试结果。

| 主题 | 资料与使用范围 |
| --- | --- |
| 比特、符号与 UI | [Keysight：Understanding Signal Parameters](https://helpfiles.keysight.com/scopes/FlexDCA-UG/Content/Topics/Quick-Start/FlexDCA-fact-6.htm)，用于区分 bit、symbol、baud、UI；数值换算按正文的单位自行计算。 |
| PAM4 | [TI：Understanding clocking needs for high-speed 56G PAM-4 serial links](https://www.ti.com/lit/an/snaa325a/snaa325a.pdf)，用于理解四电平及相关接收余量；不把理想电平间距比当作通用系统 BER 罚损。 |
| 64b/66b 格式 | [Altera：64B/66B Encoder and Transmitter State Machine](https://docs.altera.com/r/docs/683621/current/l-and-h-tile-transceiver-phy-user-guide/b/66b-encoder-and-transmitter-state-machine-tx-sm)，限定为该 10GBASE-R 实现的同步头和加扰处理。 |
| 眼图与时钟恢复 | [Tektronix：Clock Recovery Primer](https://download.tek.com/document/65W_26023_0_Letter.pdf) 与 [PAM4 信号测试、分析与调试](https://download.tek.com/document/PAM4-Signaling-in-High-Speed-Serial-Technology_55W-60273.pdf)，用于理解测量设置、时钟参考与眼图。 |
| 误码与 FEC | [Keysight：BER 的含义](https://www.keysight.com/blogs/en/tech/2019/03/10/ber-is-it-bit-error-rate-or-bit-error-ratio)；[IEEE 802.3：FEC 与误码指标讨论](https://www.ieee802.org/3/B400G/public/21_03/wang_b400g_01a_210315.pdf)。置信上界的公式在正文列出假设并推导。 |
| PCIe 编码与带宽 | [Intel 500 系列 PCH 数据手册](https://cdrdv2-public.intel.com/635218/635218-008.pdf)，包含 Gen3 x4 的编码效率与理论带宽例子。 |
| 复位与初始化 | [AMD Versal GTM：Reset and Initialization](https://docs.amd.com/r/en-US/am017-versal-gtm-transceivers/Reset-and-initialization)，用于指定器件的 TX / RX 初始化和状态。 |
| 训练与自适应 | [TI TLK10031 数据手册](https://www.ti.com/lit/ds/symlink/tlk10031.pdf)第 7.3.14—7.3.15 节，适用于该器件的 10GBASE-KR / 1GBASE-KX 模式。 |
| 多 lane 对齐 | [Altera Stratix V 收发器手册：Deskew FIFO](https://docs.altera.com/r/docs/683779/current/stratix-v-device-handbook-volume-2-transceivers/deskew-fifo?contentId=cO~VnJWtO05NxONKzLfrpQ)，用于该器件的 XAUI 对齐机制；不是其他协议的通用 skew 预算。 |
| PCIe 建链与测试 | [PCI-SIG：PCIe 5.0 测试问答](https://pcisig.com/blog/pcie%C2%AE-50-protocol-and-electrical-compliance-testing-deep-dive-webinar-qa)；[PCI-SIG：PCIe 5.0 系统实现](https://pcisig.com/sites/default/files/files/PCI-SIG-Seamless_Transition_to_PCIe_5.0_in_System_Implementations_FINAL.pdf)。完整状态机以对应版本规范为准。 |
