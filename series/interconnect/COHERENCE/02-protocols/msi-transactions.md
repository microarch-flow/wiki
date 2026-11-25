---
search:
  exclude: true
---

# MSI 读写事务（原章节入口）

《内存里还是 0，为什么 B 能读到 A 写的 1？》把原来的 MSI 事务和一致性约束放在同一条时间线上。按原来读到的位置，可以直接查看每一步的值、权限和等待的消息。

<div markdown="1" data-article-redirect="true">

- <span id="用-msi-走完读写事务数据和权限怎样转移"></span>[从 A、B 都读到 0 开始](../01-foundations/coherence-invariants.md)
- <span id="本文采用的教学模型"></span>[写回缓存、目录与 MSI 状态](../01-foundations/coherence-invariants.md#model)
- <span id="从无人缓存到共享"></span>[A、B 怎样各自取得一份只读副本](../01-foundations/coherence-invariants.md#shared)
- <span id="从共享到独占写入"></span>[B 何时失效，A 何时取得写权限](../01-foundations/coherence-invariants.md#write-permission)
- <span id="脏-owner-遇到另一个读取"></span>[内存仍为 0 时，B 的新读取从哪里取数](../01-foundations/coherence-invariants.md#read-again)
- <span id="回收不是直接删掉缓存行"></span>[回收缓存行时谁接下最新值](../01-foundations/coherence-invariants.md#evict)

</div>
