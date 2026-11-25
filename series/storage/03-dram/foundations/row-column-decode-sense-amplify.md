---
search:
  exclude: true
---

# DRAM 行列解码：感测、恢复与列选择

这篇文章已并入[《只读几个字节，DRAM 为什么先打开一整行？》](./1t1c-cell-destructive-read.md)。原小节对应以下段落。

<div markdown="1" data-storage-redirect="true">

- <span id="行列解码与读出放大为什么-dram-必须先开行"></span>[开行怎样引发感测和恢复](./1t1c-cell-destructive-read.md#sense-restore)
- <span id="这页在回答什么问题"></span>[读几个字节为什么要先选一行](./1t1c-cell-destructive-read.md#access-granularity)
- <span id="位线感测整行恢复与列选择"></span>[位线感测与整行恢复](./1t1c-cell-destructive-read.md#sense-restore)
- <span id="位线电荷共享与整行感测"></span>[存储电容与位线怎样共享电荷](./1t1c-cell-destructive-read.md#charge-sharing)
- <span id="行选通与列选择"></span>[列选择怎样取出其中一部分](./1t1c-cell-destructive-read.md#column-select)
- <span id="一句话理解"></span>[一次内部开行与一次外部传输的大小](./1t1c-cell-destructive-read.md#access-granularity)
- <span id="建模启示"></span>[模型需要记录哪些状态](./1t1c-cell-destructive-read.md#model)

</div>
