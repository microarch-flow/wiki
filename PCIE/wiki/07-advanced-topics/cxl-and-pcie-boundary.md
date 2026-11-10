# CXL 和 PCIE 的边界

上级：[07 高级主题](./README.md)

相关：[PCIE 在解决什么问题](../01-overview/problem-statement.md)

## 这页在回答什么问题

为什么学 CXL 之前最好先学 PCIE，以及两者边界应该怎么理解。

## 一个最实用的判断

CXL 不是绕开 PCIE 凭空出现的新世界，它建立在 PCIE 物理和部分链路基础之上，但目标比传统 PCIE 更靠近内存语义和一致性扩展。

## 为什么先学 PCIE

因为很多前置概念都来自这里：

- 拓扑和链路训练
- 配置和枚举
- host-device 资源组织
- 基本错误处理与可管理性

## 两者边界怎么抓

- 传统 PCIE 更偏 `设备互连和 DMA 契约`。
- `CXL.io` 提供发现、配置和 I/O 管理；`CXL.cache` 支持设备一致地访问和缓存主机内存；`CXL.mem` 支持主机访问设备连接的内存。各自的请求对象与方向不同。
- 例如 Type 3 内存扩展设备使用 CXL.io 和 CXL.mem，主机可按配置访问其设备内存；不能因此假定该设备用 CXL.cache 缓存主机内存。

仅有普通 PCIe 物理连接不足以产生 CXL 一致性事务。主机和设备必须支持相应 CXL 协议与设备类型，链路须协商进入支持的模式，软件还要配置可访问资源。参见 [CXL 3.0 规范](https://computeexpresslink.org/wp-content/uploads/2024/02/CXL-3.0-Specification.pdf) 的设备类型和协议说明。

## 一句话理解

PCIE 是理解现代设备互连的地基，CXL 是在这块地基上往更强内存语义继续延展。
