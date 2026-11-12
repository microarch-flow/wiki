# 术语表

上级：[08 术语与检查清单](./README.md)

相关：[PCIe 建模参数与公式速查](./pcie-modeling-params.md)

## 常见术语

带「量纲」的术语给出建模时直接取数的单位与典型/合法取值；完整表见 [PCIe 建模参数与公式速查](./pcie-modeling-params.md)。

- `Root Complex`：主机侧进入 PCIE fabric 的根
- `Endpoint`：承载设备功能的终端节点
- `Switch`：扩展拓扑的中间节点；转发延迟与实现、负载和路径有关，需对目标平台标定
- `TLP`：事务层包；开销依包类型、字段和链路模式变化。24 B 只能是特定 Non-Flit 估算假设。
- `DLLP`：传统 Non-Flit 模式下相邻链路的控制包，如 ACK/NAK 和 FC update；不等于事务完成。
- `Completion`：对 non-posted 请求的事务返回 TLP。读返回可含数据，成功配置写返回无数据 Cpl；读数据可在合法 RCB 边界拆分，不必在每个边界拆分。
- `BAR`：设备向主机申请的地址窗口
- `MMIO`：CPU 通过地址访问设备寄存器或窗口
- `DMA`：设备直接访问主机内存
- `MSI-X`：设备向配置的目的地址发送中断消息，通知 CPU 服务；不直接证明某个 CQE 已被软件消费。
- `IOMMU`：DMA 地址翻译与隔离组件；IOTLB 命中与 miss 的延迟依平台和负载而变，需标定
- `GT/s`：PCIe 对单方向、每 lane 原始数据传输速率的标注，不应无条件等同于每秒物理 symbol 数。Gen1–5 使用 NRZ，每 symbol 承载 1 bit；Gen6 的 64 GT/s 使用 PAM4，每 symbol 承载 2 bit，对应 32 GBd（每秒 320 亿 symbol），原始速率仍是 64 Gb/s。Gen1 至 Gen6 依次标为 2.5、5、8、16、32、64 GT/s。见 [PCI-SIG PAM4 说明](https://pcisig.com/why-does-pcie-60-specification-utilize-pam4-signaling-over-nrz-signaling)。
- `lane / xN`：一条全双工 lane 含一对发送差分线及一对接收差分线。xN 有 N 条 lane、每方向 N 对差分线；常见宽度为 x1、x2、x4、x8、x16。单向名义带宽 = 单向每 lane 带宽 × N；双向合计要另行说明。
- `MPS`：Max Payload Size；量纲：单 TLP 最大 payload，合法值 128/256/512/1024/2048/4096 字节，常见实际 128/256
- `MRRS`：Max Read Request Size；量纲：单 read 最多请求字节数，合法值 128…4096 字节
- `RCB`：Read Completion Boundary；允许拆分的自然对齐边界，常为 64 或 128 B，并非 CplD 长度上限。
- `Tag`：标识 outstanding 请求的 ID；通常 5-bit 最多 32，Extended 已启用最多 256；10-bit 已启用且目标支持时，单个 completer 最多 768，实际还受实现资源限制。
- `Credit`：flow control 信用；传统 Non-Flit 模式分 P/NP/CPL，header 和 data 分开，data credit 单位为 16 B；有限或无限依协议和配置而定。
- `AER`：Advanced Error Reporting，PCIe 扩展错误记录与报告机制；分 Correctable 和 Uncorrectable，后者再区分 Non-Fatal/Fatal。
- `SR-IOV`：单物理设备导出多个虚拟功能的能力

## 最常见误区

- `completion` 不只指软件完成队列
- `BAR` 不是 DMA buffer
- `DMA address` 不等于用户态虚拟地址
