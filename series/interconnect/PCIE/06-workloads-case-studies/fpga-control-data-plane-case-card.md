---
title: "FPGA 采集卡：BAR 可访问，为什么 DMA 仍不工作？"
---

<div id="fpga-采集卡控制面与数据面案例卡" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>
<div id="典型系统位置" class="pcie-legacy-anchor"></div>

# FPGA 采集卡：BAR 可访问，为什么 DMA 仍不工作？

上级：[工作负载与案例](README.md)

教学设备通过 BAR 暴露控制寄存器，DMA 引擎把采集数据写入主机缓冲区。寄存器布局与计数器是示例，不代表任何现成 IP。

<div id="最关键的两条路径" class="pcie-legacy-anchor"></div>
<div id="为什么它特别适合拿来学" class="pcie-legacy-anchor"></div>

## 分开验证控制面与数据面

| 路径 | 输入 | 应观察的输出 |
| --- | --- | --- |
| 控制面 | CPU 对 BAR 寄存器的合法访问 | 可预期的标识、配置与状态 |
| 数据面 | 已发布描述符、有效 DMA 地址、采集数据 | 主机缓冲区中正确的载荷 |
| 完成路径 | 设备结束条件 | 可匹配的状态/CQE，以及可选通知 |

配置读与 BAR 访问成功，只能证明相应路径可用，不能证明 Bus Master、DMA 映射或设备引擎已配置正确。

<div id="最常见问题" class="pcie-legacy-anchor"></div>

## 一组构造观察

驱动能读设备版本；启动后描述符消费计数增加，发出的写事务计数也增加；主机没有得到预期数据，同时 IOMMU 报告写权限错误。

这组证据优先指向 DMA 映射、方向或权限。它不支持“因为没有 MSI-X，所以数据没有传到”。接下来应核对描述符中的 DMA 地址、长度、映射所属设备及映射生命周期。未取得实际错误地址和上下文前，不能认定唯一根因。

## 另一组观察会改变判断

如果描述符消费计数始终为零，应先查队列地址、发布顺序、Doorbell 和启动状态；如果数据与有效完成项已经正确，而应用仍等待，则查通知、同步和软件命令匹配。相同的“应用超时”可以来自完全不同阶段。

<div id="最值得抄走的判断" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 最小验证顺序

先用设备允许的无副作用寄存器确认控制路径；再用小型、已映射且边界明确的缓冲区验证一次 DMA；检查数据和完成状态后，再增加长度、并发和持续时间。错误恢复中先停止并确认 DMA 不再访问，再撤销映射和释放页面。

主机地址依据见[地址视角](../03-configuration-enumeration-addressing/mmio-config-dma-address-view.md)，所有权依据见[缓冲区生命周期](../04-data-path-dma-interrupts/host-memory-pinned-buffer-visibility.md)和 [Linux DMA 指南](https://docs.kernel.org/core-api/dma-api-howto.html)。
