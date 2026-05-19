# 术语表

上级：[08 术语与检查清单](./README.md)

## 常见术语

- `Root Complex`：主机侧进入 PCIE fabric 的根
- `Endpoint`：承载设备功能的终端节点
- `Switch`：扩展拓扑的中间节点
- `TLP`：事务层包
- `DLLP`：链路层控制包
- `Completion`：对 read 或某些 non-posted 请求的返回
- `BAR`：设备向主机申请的地址窗口
- `MMIO`：CPU 通过地址访问设备寄存器或窗口
- `DMA`：设备直接访问主机内存
- `MSI-X`：常见的消息型中断机制
- `IOMMU`：DMA 地址翻译与隔离组件
- `MPS`：Max Payload Size
- `MRRS`：Max Read Request Size
- `AER`：Advanced Error Reporting
- `SR-IOV`：单物理设备导出多个虚拟功能的能力

## 最常见误区

- `completion` 不只指软件完成队列
- `BAR` 不是 DMA buffer
- `DMA address` 不等于用户态虚拟地址
