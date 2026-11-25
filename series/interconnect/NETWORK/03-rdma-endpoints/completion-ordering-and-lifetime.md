---
search:
  exclude: true
---

# RDMA 排序、完成与缓冲区复用（原章节入口）

原文的完成时序已并入《同样发 4 KiB，TCP 和 RDMA 什么时候能复用缓冲区？》。可以从下列入口回到原先阅读的段落。

<div markdown="1" data-article-redirect="true">

- <span id="排序完成与缓冲区复用哪个事件允许程序继续"></span>[查看发送方、接收方和目标缓冲区的交接时刻](../01-foundations/host-nic-data-path.md#completion)
- <span id="四个阶段分别允许什么"></span>[区分提交、发送完成、接收通知和消费结束](../01-foundations/host-nic-data-path.md#completion)
- <span id="排队顺序不等于任意可见顺序"></span>[为什么另一条队列上的通知可能先到](../01-foundations/host-nic-data-path.md#queues)
- <span id="通知之后还有本地消费者"></span>[接收方何时能读，何时能让下一轮覆写](../01-foundations/host-nic-data-path.md#completion)

</div>
