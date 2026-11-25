---
search:
  exclude: true
---

# 一次跨芯粒通信（原章节入口）

[《一次跨芯粒的寄存器读，什么时候才算完成？》](../ucie-pcie-read.md)跟随同一笔读取，从两颗裸片之间的封装通道，一直走到发起方收齐返回的 4 个字节。原文各节可从下列位置接着读。

<div markdown="1" data-article-redirect="true">

- <span id="一次跨芯粒通信怎样完成"></span>[从这笔寄存器读开始](../ucie-pcie-read.md)
- <span id="先约定一个读取"></span>[两颗裸片、一个地址和返回值](../ucie-pcie-read.md#先约定一次读取)
- <span id="请求经过哪些边界"></span>[顺着图找到两端的接口和封装通道](../ucie-pcie-read.md#read-path)
- <span id="怎样判断已经完成"></span>[寄存器已给出数据，发起方为什么还在等](../ucie-pcie-read.md#return-wait)
- <span id="为什么连接线接通还不够"></span>[读之前，两端要准备什么](../ucie-pcie-read.md#ready)
- <span id="接下来怎么读"></span>[封装、接口与系统设计的延伸阅读](../ucie-pcie-read.md#next)

</div>
