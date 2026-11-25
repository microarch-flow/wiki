---
search:
  exclude: true
---

# Row buffer 与 DRAM 行状态

这篇文章已并入[《只读几个字节，DRAM 为什么先打开一整行？》](./1t1c-cell-destructive-read.md)。原小节对应以下段落。

<div markdown="1" data-storage-redirect="true">

- <span id="row-bufferdram-内部的小-cache"></span>[行缓冲与 bank 的打开行](./1t1c-cell-destructive-read.md#row-state)
- <span id="这页在回答什么问题"></span>[感测放大器怎样保留打开行的数据](./1t1c-cell-destructive-read.md#sense-restore)
- <span id="打开行的工作副本"></span>[用三次请求区分行命中、关闭行和行冲突](./1t1c-cell-destructive-read.md#row-state)
- <span id="一句话理解"></span>[下一笔请求能否使用已打开的行](./1t1c-cell-destructive-read.md#row-state)
- <span id="建模启示"></span>[为每个 bank 记录状态与可用时刻](./1t1c-cell-destructive-read.md#model)

</div>
