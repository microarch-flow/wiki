# BUS 分类框架

上级：[01 概览与问题定义](./README.md)

相关：[AXI / AHB / APB 对照](../03-on-chip-protocol-families/axi-ahb-apb-comparison.md)、[分层总线与协议分工](../03-on-chip-protocol-families/hierarchical-bus-and-protocol-roles.md)

## 这页在回答什么问题

面对各种 BUS 名称时，应该用什么维度做分类，而不是只背协议缩写。

## 可以按 5 个维度分类

### 1. 按拓扑结构分

- 单共享总线
- 多主仲裁总线
- crossbar
- 分层互连

### 2. 按事务能力分

- 单拍寄存器访问
- burst 访问
- 支持多个 outstanding 的 split transaction
- 支持独立读写通道

### 3. 按顺序模型分

- 严格顺序
- 同 ID 内保序、跨 ID 可乱序
- 需要软件或 barrier 明确约束顺序

### 4. 按适用层级分

- 高性能 memory-mapped 主干总线
- 外设配置总线
- coherent interconnect
- bridge 后的低速外设子总线

### 5. 按系统角色分

- CPU 发起主干访问
- DMA 数据搬运路径
- peripheral 控制与状态路径
- debug / test / boot 访问路径

## 常见协议放在哪

- `APB`：低复杂度、低带宽、外设寄存器访问
- `AHB/AHB-Lite`：中等复杂度、顺序更强、适合中低复杂度 SoC
- `AXI`：高吞吐、独立通道、多 outstanding、生态最广
- `TileLink`：强调模块化、参数化和一致性扩展能力

## 一句话理解

分类 BUS 最有效的方式不是按名字，而是按 `拓扑 + 事务能力 + 顺序模型 + 适用层级 + 系统角色` 来判断。
