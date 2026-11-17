# 术语表

上级：[08 研究模板与术语](./README.md)

## 核心术语

- `CPO`：Co-Packaged Optics，光电共封装
- `NPO`：Near-Packaged Optics，近封装光学
- `OBO`：On-Board Optics，板载光学。
- `Optical I/O`：光输入/输出功能，可以在板上或封装内实现。`OIO` 的展开随来源而异，应核对原文，不将它直接等同于 OBO。
- `Pluggable optics`：可插拔光模块
- `PIC`：Photonic Integrated Circuit，光子集成芯片
- `Silicon photonics`：硅光子技术平台
- `Driver`：调制器驱动电路
- `TIA`：Transimpedance Amplifier，跨阻放大器，将光探测器输出电流转换为电压
- `SerDes`：Serializer/Deserializer，高速串并转换接口
- `Laser`：激光器，提供光载波；位置可在封装内或外
- `Modulator`：调制器，用电信号改变光载波以承载数据
- `Photodetector / PD`：光探测器，将接收光转换为电流
- `External laser source`：外置激光源
- `KGD`：Known Good Die，按指定测试条件和判据筛选通过的裸片，仍可能有漏检或后续装配损伤
- `TCO`：Total Cost of Ownership，总拥有成本

## 易混术语提醒

- `硅光` 不是 `CPO`
- `CPO` 不是 `所有板上光学`
- `外置激光` 不是 `非 CPO`
- `功耗更低` 不等于 `系统更便宜`

## 接口资料怎么查

- [OIF 已发布实施协议](https://www.oiforum.com/technical-work/implementation-agreements-ias/)列有 3.2T 共封装模块、ELSFP 光源和管理接口等文件。使用时核对具体版本和适用的电、光、机械与管理边界。
- [OIF 当前项目](https://www.oiforum.com/technical-work/current-work/)列出仍在制定的工作；2026-11-17 核阅时，12.8T / 6.4T NPO 模块接口仍作为项目列示。项目、演示和已发布实施协议应分开记录。
- 协议规定接口，不证明任意两个产品已经过互通验证。产品是否符合某版本，应查看该产品的符合性与互通证据。
