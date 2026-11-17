---
title: "AER 与链路计数器：错误在哪里被观察到？"
---

<div id="aer计数器与链路调试路径" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# AER 与链路计数器：错误在哪里被观察到？

上级：[性能与调试](README.md)

AER（Advanced Error Reporting）扩展 PCIe 的错误记录和报告能力。报错端口是观察点，不必然是故障源。要定位问题，应同时记录事务、链路状态、设备状态及平台日志。

## AER 在做什么

错误分为 Correctable 与 Uncorrectable；后者再按严重性分 Non-Fatal 与 Fatal。分类不是固定的恢复脚本。某些错误由硬件机制纠正，其他错误可能需要驱动恢复、复位或隔离。

操作系统是否收到报告还受硬件能力、使能、掩码、固件控制和平台处理影响。Linux 的 AER 使用与恢复流程见[官方指南](https://docs.kernel.org/PCI/pcieaer-howto.html)。

## 常见观测点

| 观察点 | 记录内容 | 注意事项 |
| --- | --- | --- |
| 目标 Function 及每跳端口 | BDF、LnkCap/LnkSta、速率和宽度 | 端点能力不能替代沿途实际状态 |
| AER 状态与日志 | 错误类型、源身份、可用头部日志、时间 | 掩码和日志限速会影响可见数量 |
| 设备或控制器计数器 | replay、信用等待、吞吐、请求状态 | 定义、清零方式和方向依实现 |
| 驱动与平台 | 命令超时、IOMMU fault、恢复动作 | 对齐时间线，保留恢复前证据 |

<div id="调试时先分三层" class="pcie-legacy-anchor"></div>

## 调试时先分观察层次

链路未建立或协商宽度异常，先查复位、配置和训练路径；重放增加，查传输可靠性及对应链路；UR、CA 或 Completion Timeout，则结合原始请求和路由检查事务路径。AER 可能记录不同层次的错误，不能把“AER 报错”直接归为某一层。

例如同一窗口吞吐下降、重放计数增加，但没有新的 AER 日志。它支持“发生了控制器定义的重放事件”，不支持“没有错误”或“打开 AER 导致重放”。反过来，多条 AER 日志也不能直接换算为同样数量的重发包。

<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 从只读记录开始

在 Linux 上可用以下命令收集拓扑与解码后的配置状态，具体输出依权限和 pciutils 版本变化：

```sh
lspci -t
lspci -s 0000:03:00.0 -vv
```

BDF 只是示例，使用目标设备及其上游端口。清状态、写配置、强制重训练和复位会改变证据与设备状态，不属于这两个只读步骤。

事务错误的判别见 [UR、CA 与 Timeout](common-failures-ur-ca-timeout.md)；速率问题见[链路降速案例](../06-workloads-case-studies/link-downgrade-case-card.md)。
