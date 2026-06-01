# PCIE 分类框架

上级：[01 概览与问题定义](./README.md)

相关：[链路、分层与事务基础](../02-link-transaction-basics/README.md)、[高级主题](../07-advanced-topics/README.md)、[PCIe 建模参数与公式速查](../08-reference/pcie-modeling-params.md)

## 这页在回答什么问题

学 PCIE 时，应该按什么维度切分问题，才不容易把协议、拓扑、软件和性能搅在一起。

## 一个实用的五层分类法

### 1. 系统角色层

- Root Complex
- Switch
- Endpoint
- Host software
- Device DMA engine

### 2. 协议分层

- Transaction Layer
- Data Link Layer
- Physical Layer

### 3. 资源与寻址层

- config space
- BAR / MMIO
- bus number / device / function
- DMA address
- IOMMU translation

### 4. 数据路径层

- MMIO control path
- DMA read/write data path
- completion path
- interrupt / MSI-X notification path

### 5. 系统能力层

- virtualization
- isolation
- reliability / AER
- performance tuning
- P2P / switch topology

## 6. 量化 / 可建模维度

如果学 PCIE 的目的是建性能模型，上面五层各自对应一组可量化参数，建模时按这个映射取数（完整表见 [PCIe 建模参数与公式速查](../08-reference/pcie-modeling-params.md)）：

| 分类层 | 对应的可建模量 |
| --- | --- |
| 系统角色层 | switch 级数（每级加延迟）、RC 往返延迟 |
| 协议分层 | 编码效率（8b/10b、128b/130b、FLIT/FEC）、TLP 固定开销 |
| 资源与寻址层 | IOMMU 翻译命中率、hit/miss 延迟 |
| 数据路径层 | MPS / MRRS / RCB、Tag 数、credit 池深度 |
| 系统能力层 | 多 VF 共享带宽、P2P 路径、AER 引发的 replay 开销 |

这样切分的好处是：**模型的每个参数都能落到一个明确的层**，调参时知道动的是协议开销、并发上限还是路径延迟，而不是笼统地调一个「带宽系数」。

## 为什么这样切分有用

因为很多常见混淆都来自跨层混用：

- 把 `PCIe completion` 和 `软件 completion queue` 当成同一个概念
- 把 `BAR 可见地址` 和 `DMA 地址` 当成天然同一套地址
- 把 `链路速率问题` 和 `软件排队问题` 混成一个瓶颈

## 一句话理解

学 PCIE 最有效的方式，是先把 `角色`、`分层`、`寻址`、`数据路径`、`系统能力` 这五类问题拆开。
