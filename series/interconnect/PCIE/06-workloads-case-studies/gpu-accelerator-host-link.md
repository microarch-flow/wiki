---
title: "GPU 主机链路何时成为瓶颈？"
---

<div id="gpu-加速器-host-link-视角" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# GPU 主机链路何时成为瓶颈？

上级：[工作负载与案例](README.md)

GPU 或加速器的 HBM 很快，并不说明主机链路不重要。关键是每轮工作有多少数据必须经过主机链路，以及这些传输能否与计算重叠。本文是构造模型，不引用某款产品的实测吞吐。

<div id="它通常承担什么角色" class="pcie-legacy-anchor"></div>

## 先列出主机链路上的工作

包括输入传入、结果回读、命令提交、初始化与状态访问。设备内部 HBM、NoC 和 copy engine 是其他资源；若数据已驻留设备，后续复用可能不再经过 PCIe。

<div id="但为什么仍然必须理解它" class="pcie-legacy-anchor"></div>

## 无重叠时，服务时间相加

设每批输入 D<sub>in</sub>、输出 D<sub>out</sub>，两个方向的有效传输率分别为 B<sub>in</sub>、B<sub>out</sub>，计算时间为 T<sub>compute</sub>。在串行执行、无重叠的教学模型中：

> T<sub>batch</sub> = T<sub>submit</sub> + D<sub>in</sub>/B<sub>in</sub> + T<sub>compute</sub> + D<sub>out</sub>/B<sub>out</sub>。

例如输入 256 MB、输出 16 MB、两向均假设可持续达到 16 GB/s、计算 10 ms，忽略提交成本，则需要 16 + 10 + 1 = **27 ms**。这里 MB、GB 均采用十进制，16 GB/s 是模型输入。

## 理想流水重叠改变的是稳态间隔

若不同批次独立，具备足够缓冲和可并发的传输/计算资源，理想稳态批次间隔下界是各独立阶段服务时间的最大值。上述例子为 max(16, 10, 1)=16 ms。它不是第一批的完成延迟，也不是自动可达的实测结果。

若输入和输出共用不可并发的 copy engine，或与计算竞争同一内存服务，必须合并共享资源的工作量或显式建模竞争，不能继续使用独立阶段的最大值。

<div id="为什么它常常不是全局性能上限" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 驻留与复用减少哪些字节

若输入只传一次，在设备内复用 K 轮，最后回读一次，则主机传输成本按该组工作摊薄。不能在每轮又发生输出或数据更新时，仍把所有传输都除以 K。

小批次还可能由提交、同步和启动成本主导。应记录实际传输字节、依赖、重叠区间及资源占用，分别判断是减少数据移动、增加批量还是改善流水更有效。

协议带宽边界见[性能参数](../05-performance-debug/bandwidth-latency-credit-mps-mrrs.md)，设备内路径见 [NoC](../../NOC/README.md)和[存储系统](../../../storage/README.md)。
