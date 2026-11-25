# 协议与控制器：把权限规则变成执行过程

<!-- nav-title: 02 协议与控制器 -->

基础篇用[一笔 MSI 读写](../01-foundations/coherence-invariants.md)跟踪了目录怎样撤销共享副本的读权限、最新值怎样从缓存回到内存。本章沿着这条路径继续：如果一条刚读入的缓存行没有其他副本，下次写入可以省掉哪条消息？

先看增加状态能省掉哪些通信，再考虑目录容量、消息乱序和有限资源怎样影响控制器。

本章中 GetS、GetM 等是教学消息名。真实 CHI 的字段、操作码和完成规则放在下一章。NoC 的路由与传输细节继续由片上网络专题负责。

## 阅读顺序

1. [MESI 与 MOESI](mesi-moesi-extensions.md)
2. [目录与探查过滤](directory-snoop-filter.md)
3. [瞬态状态与竞争](transient-states-and-races.md)
4. [前进与资源依赖](forward-progress.md)

返回[专题导读](../README.md)，选择 CHI、CXL 或其他章节的阅读路线。
