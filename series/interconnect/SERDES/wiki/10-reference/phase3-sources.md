# 第三阶段资料入口

上级：[SerDes 术语、资料与自测](./README.md)

以下是本阶段所用的一手资料及适用范围。标准组织的公开摘要不代替规范全文；厂商产品页和数据手册描述其产品与声明，不是独立验收报告。网络页面会变化，访问日期为 `2026-11-11`。

| 主题 | 来源与使用边界 |
| --- | --- |
| IBIS-AMI | [IBIS 6.1 规范](https://ibis.org/ver6.1/ver6_1.pdf)第 10.2.2 节：统计和时域算法模型的能力与假设。是否适用于具体模型，还要看其文件和仿真器。 |
| 参考面与夹具 | [Keysight：Reference Plane Adjustment](https://helpfiles.keysight.com/csg/N1930xB/ToolsAndUtilities/Reference_Plane_Adjustment.htm)：参考面、夹具表征和去嵌；不代表校正没有不确定度。 |
| 接收器架构 | [AMD GTY / GTYP 接收均衡](https://docs.amd.com/r/en-US/am002-versal-gty-transceivers/RX-Equalizer-DFE-and-LPM)：指定器件的均衡模式与权衡。 |
| PCIe 测试 | [PCI-SIG 合规项目](https://pcisig.com/developers/compliance-program)和[系统实现问答](https://pcisig.com/blog/seamless-transition-pcie%C2%AE-50-technology-system-implementations-webinar-qa)：合规项目及电气测试与互通的区别；实际版本判据以相应测试文档为准。 |
| 以太网训练实例 | [TI TLK10031 数据手册](https://www.ti.com/lit/ds/symlink/tlk10031.pdf)第 7.3.14—7.3.15 节：该器件的 10GBASE-KR 自动协商和训练。 |
| D2D / UCIe | [UCIe 联盟规范入口](https://www.uciexpress.org/specifications/ucie-3-0)和[早期问答](https://www.uciexpress.org/post/introduction-to-ucie-webinar-q-a-recap)：封装级接口范围和问题背景；使用条件以目标版本规范为准。 |
| HBM | [Micron HBM 基础](https://www.micron.com/products/memory/hbm)、[AMD Versal HBM 接口](https://docs.amd.com/r/en-US/am011-versal-acap-trm/HBM-Interface)：堆叠概念和指定器件的接口宽度实例；不同 HBM 代际与产品不可混同。 |
| 光接口 | [OIF Co-Packaging Framework](https://www.oiforum.com/wp-content/uploads/OIF-Co-Packaging-FD-01.0.pdf)：共封装光学接口与架构术语，具体模块与协议仍需查相关版本。 |
| 产品声明 | [Synopsys 224G Ethernet PHY IP](https://www.synopsys.com/designware-ip/interface-ip/ethernet/224g-ethernet-phy-ip.html)：厂商公开声明的阅读案例；不据此推断未公开的完整测试条件或量产数据。 |

更早阶段的详细资料见[第一阶段资料入口](./sources.md)和[第二阶段资料入口](./phase2-sources.md)。模型中的计算例子由本文自设条件推导，不是上述厂商的性能数据。
