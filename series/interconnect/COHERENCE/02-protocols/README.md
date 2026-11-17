# 协议与控制器：把权限规则变成执行过程

<!-- nav-title: 02 协议与控制器 -->

本章以教学用目录式、写失效 MSI 为起点。请求者发出读写，目录协调副本，缓存根据消息改变权限并承担数据责任。每项事务都要给出初始状态、执行条件和结束条件。

先读无竞争的完整流程，再研究增加状态能省掉哪些通信；随后加入目录容量、消息乱序和有限资源。不要在第一遍就把一个简化流程当作可实现的完整控制器。

本章中 GetS、GetM 等是教学消息名。真实 CHI 的字段、操作码和完成规则放在下一章。NoC 的路由与传输细节继续由片上网络专题负责。

## 阅读顺序

1. [MSI 读写事务](msi-transactions.md)
2. [MESI 与 MOESI](mesi-moesi-extensions.md)
3. [目录与探查过滤](directory-snoop-filter.md)
4. [瞬态状态与竞争](transient-states-and-races.md)
5. [前进与资源依赖](forward-progress.md)

返回[专题导读](../README.md)，选择 CHI、CXL 或其他章节的阅读路线。
