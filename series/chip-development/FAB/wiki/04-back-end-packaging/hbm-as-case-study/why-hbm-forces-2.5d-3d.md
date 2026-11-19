# HBM 为什么常与高密度封装配合

<span class="micro-legacy-anchor" id="hbm-如何把产业逼向-25d-和-3d"></span>

上级：[HBM 制造与集成](README.md)
相关：[硅中介层](../2.5d-routes/si-interposer-fundamentals.md) · [供电完整性](../../06-cross-cutting-engineering/power-delivery-pi-pdn-decap.md)

## 这页在回答什么问题

HBM 堆栈内部怎样获得容量？逻辑芯片怎样连接堆栈的宽接口？这两个问题分别指向垂直堆叠和封装内互连。

## 传统外部内存的瓶颈

跨板高带宽要求同时考虑 I/O 数、时序、通道损耗和供电。HBM 使用宽的并行接口，在近距离连接下获得较高总带宽。要比较不同接口的能效，分别注明测到的功耗、流量包含的范围以及速率，再用 W 除以 bit/s 得到 J/bit。 [Micron HBM4 规格与 pJ/bit 比较条件](https://www.micron.com/products/memory/hbm/hbm4)

## HBM 的两层封装含义

堆栈内，多层 DRAM 裸片采用垂直互连，堆层和单片容量影响堆栈容量。封装内，计算芯片通过高密度近距互连访问 HBM 的外部接口。以 TSMC CoWoS 为例，可采用硅中介层、RDL 中介层或带局部硅互连的 RDL 平台。 [HBM 堆栈制造](hbm-stack-manufacturing.md) · [TSMC CoWoS](https://3dfabric.tsmc.com/schinese/dedicatedFoundry/technology/cowos.htm)

## 为什么 logic 和 HBM 必须近

接口宽度会产生大量封装连线。可用层、线宽、间距、路径长度、电源与时序都要满足接口要求。选型应记录用到的堆栈与通道、连接密度、实际工作点和封装边界。原始峰值带宽的算式和协议读法见[HBM 代际与封装约束](hbm-evolution-hbm2-hbm3-hbm4.md)及[存储系统 HBM](../../../../../storage/03-dram/protocols/hbm-stacked-wide-io.md)。

## 为什么还会继续走向 3D

计算、缓存或 I/O 若采用垂直堆叠，可在一些方案中缩短连接并提高连接密度。同时需要处理热路径、键合和测试访问。HBM 内部的垂直堆叠，与计算芯片和 HBM 的横向封装，可以在同一系统中同时存在。 [3D 路线](../3d-routes/README.md)

<span class="micro-legacy-anchor" id="架构师启示"></span>

## 一句话理解

HBM 内部的堆叠决定存储结构。计算芯片到 HBM 的宽接口决定封装内连线、供电和散热要求。分别确定对象和条件后再估算系统带宽。
