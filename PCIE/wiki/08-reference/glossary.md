# 术语表

上级：[08 术语与检查清单](./README.md)

相关：[PCIe 建模参数与公式速查](./pcie-modeling-params.md)

## 常见术语

带「量纲」的术语给出建模时直接取数的单位与典型/合法取值；完整表见 [PCIe 建模参数与公式速查](./pcie-modeling-params.md)。

- `Root Complex`：主机侧进入 PCIE fabric 的根
- `Endpoint`：承载设备功能的终端节点
- `Switch`：扩展拓扑的中间节点；量纲：每多一级，往返延迟 +百 ns 量级
- `TLP`：事务层包；量纲：固定开销约 24 字节（framing 4 + seq 2 + header 12/16 + LCRC 4，ECRC 可选 +4）
- `DLLP`：链路层控制包（ACK/NAK、FC update），占用少量链路带宽
- `Completion`：对 read 或某些 non-posted 请求的返回；量纲：按 RCB 边界拆分
- `BAR`：设备向主机申请的地址窗口
- `MMIO`：CPU 通过地址访问设备寄存器或窗口
- `DMA`：设备直接访问主机内存
- `MSI-X`：常见的消息型中断机制
- `IOMMU`：DMA 地址翻译与隔离组件；量纲：IOTLB hit ~几十 ns，miss（page walk）数百 ns ~ µs
- `GT/s`：每 lane 每秒传输的 symbol 数（Giga-Transfers）；Gen1=2.5、Gen2=5、Gen3=8、Gen4=16、Gen5=32、Gen6=64
- `lane / x N`：差分对数量；名义带宽 = 每 lane 带宽 × N，N ∈ {1,2,4,8,16}
- `MPS`：Max Payload Size；量纲：单 TLP 最大 payload，合法值 128/256/512/1024/2048/4096 字节，常见实际 128/256
- `MRRS`：Max Read Request Size；量纲：单 read 最多请求字节数，合法值 128…4096 字节
- `RCB`：Read Completion Boundary；量纲：completion 拆分边界，64 或 128 字节
- `Tag`：标识 outstanding 请求的 ID；量纲：并发上限，默认 32（5-bit）/ Extended 256（8-bit）/ 10-bit 768~1024
- `Credit`：flow control 信用；量纲：header credit = 1 个 TLP 头，data credit = 16 字节（4DW）；分 P/NP/CPL 三类独立池
- `AER`：Advanced Error Reporting
- `SR-IOV`：单物理设备导出多个虚拟功能的能力

## 最常见误区

- `completion` 不只指软件完成队列
- `BAR` 不是 DMA buffer
- `DMA address` 不等于用户态虚拟地址
