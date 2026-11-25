---
search:
  exclude: true
---

# SRAM 宏接口与读写语义（原入口）

本页已并入[SRAM 在哪一拍接纳请求，读数据又在哪一拍可用？](./read-write-cycle-timing.md)。原文各小节可直接在新文中阅读。

<div markdown="1" data-storage-redirect="true">

- <span id="sram-宏接口地址时序与访问语义"></span>[宏向系统提供哪些信号](./read-write-cycle-timing.md#macro-pins)
- <span id="sram-宏接口怎样正确发起读写"></span>[怎样发起一次读或写](./read-write-cycle-timing.md#macro-pins)
- <span id="1-宏向外提供什么"></span>[读宏接口的引脚和控制条件](./read-write-cycle-timing.md#macro-pins)
- <span id="2-从一个-64-32-bit-的宏读接口"></span>[读一个 64 × 32 bit 宏的地址](./read-write-cycle-timing.md#word-address)
- <span id="byte-地址怎样对应-word-地址"></span>[把字节地址换算成字地址](./read-write-cycle-timing.md#word-address)
- <span id="写掩码改变哪些位"></span>[哪些数据位会被改写](./read-write-cycle-timing.md#write-mask)
- <span id="部分写入需要读改写时"></span>[部分写为什么可能产生一读一写](./read-write-cycle-timing.md#read-modify-write)
- <span id="3-数据有效时间与下一次接纳间隔"></span>[区分数据何时可用与下一次何时可接纳](./read-write-cycle-timing.md#pipeline)
- <span id="4-两个端口可以同时做什么"></span>[两个端口有哪些并发组合](./read-write-cycle-timing.md#ports)
- <span id="5-宏接口与系统接口在哪里分界"></span>[系统与宏之间怎样转换请求](./read-write-cycle-timing.md#wrapper)
- <span id="一句话理解"></span>[沿时钟边沿读一次访问](./read-write-cycle-timing.md#timeline)
- <span id="建模启示"></span>[模型应当记录哪些事件](./read-write-cycle-timing.md#model)
- <span id="接下来怎么读"></span>[继续读端口与阵列组织](./read-write-cycle-timing.md#next)

</div>
