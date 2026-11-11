# 第一阶段资料入口

上级：[SerDes 术语、资料与自测](./README.md)

本专题优先采用规范组织、器件厂商和测量设备厂商的原始资料。厂商手册描述指定产品；其数字和框图不能不加条件地推广到所有 SerDes。

| 资料 | 本阶段使用范围 |
| --- | --- |
| [TI：SerDes 软件与接口说明](https://software-dl.ti.com/jacinto7/esd/processor-sdk-linux-am67/latest/exports/docs/linux/Foundational_Components/Kernel/Kernel_Drivers/SERDES/SERDES.html) | TI 指定 SoC 的串并转换与协议能力边界。 |
| [AMD：Versal GTY Receiver](https://docs.amd.com/r/en-US/am002-versal-gty-transceivers/Receiver) | 指定器件的 RX 前端、均衡、CDR 和对齐模块。 |
| [AMD：1000BASE-X PCS/PMA](https://docs.amd.com/r/en-US/pg138-axi-ethernet/PCS/PMA) | 特定以太网接口的物理层功能划分。 |
| [Keysight：信号参数](https://helpfiles.keysight.com/scopes/FlexDCA-UG/Content/Topics/Quick-Start/FlexDCA-fact-6.htm) | NRZ、PAM4、bit、symbol 与 UI 的关系。 |
| [TI：高速差分连接](https://www.ti.com/lit/an/slla104a/slla104a.pdf) | 差分、终端和连接中的阻抗问题。 |
| [Intel：SFI-5.1 SerDes Framer](https://cdrdv2-public.intel.com/654332/an571.pdf) | 特定实现的 lane 间 skew 和 deskew。 |
| [TI：反射和高速系统](https://www.ti.com/document-viewer/lit/html/SSZTAX3/GUID-2D2CAEAA-D7FA-43E3-8CAD-78D810632034) | 阻抗不连续与反射。 |
| [Keysight：测量参数](https://helpfiles.keysight.com/csg/pxivna/S1_Settings/Measurement_Parameters.htm) | S 参数、前向传输与反射。 |
| [Analog Devices：PLL 基础](https://www.analog.com/media/en/training-seminars/tutorials/MT-086.pdf) | 反馈、VCO、分频与锁相的基础模型。 |
| [AMD：UltraScale 收发器](https://docs.amd.com/api/khub/documents/qoVxLVymW4dP6eFnjYnZCA/content) | 指定收发器的 TX FIR 与接收均衡实例。 |
| [Analog Devices：ADRV904x 调参](https://www.analog.com/cn/resources/app-notes/an-2594.html) | 指定器件的发送与接收均衡。 |
| [Analog Devices：CDR 参考时钟](https://www.analog.com/en/resources/technical-articles/hfta070-precision-reference-clock-usage-in-clock-and-data-recovery-circuits.html) | 串行链路中的时钟恢复与参考时钟。 |
| [Keysight：眼图](https://helpfiles.keysight.com/csg/N1930xB/Analyzing/Analyzing_Data_using_Eye_Diagrams.html) | 眼高、眼宽与 NRZ / PAM4 波形。 |
| [Intel：接收数据重新对齐](https://www.intel.com/content/www/us/en/docs/programmable/813929/24-1/data-realignment-block-bit-slip.html) | 特定接收器的 bit slip 实现。 |
