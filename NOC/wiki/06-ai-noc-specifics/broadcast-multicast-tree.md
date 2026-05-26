# Broadcast Multicast Tree

上级：[06 AI NOC Specifics](./README.md)

相关：[Reduction And Collective Networks](./reduction-and-collective-networks.md)、[Multiple Physical Networks](../05-system-integration/multiple-physical-networks.md)

## 这页在回答什么问题

这页回答：为什么 AI 芯片里的 broadcast / multicast 不应该只被当作“多份 unicast”，以及什么时候值得用树形或硬件复制支持。

## 软件复制的代价

最直接的做法是：

- 源端复制多份 packet
- 每个目的地各走一条 unicast

这在功能上没问题，但会带来两个典型代价：

- 靠近源端的链路被重复占用
- 相同 payload 在网络里反复走相近路径

当目标数一大，这种重复占用会很快变成热点根因。

## 树形分发的核心价值

理想的 multicast / broadcast 做法是：

- 上游共享路径
- 在网络中某些分叉点复制
- 每条上游链路尽量只承载一份数据

这会直接减少：

- 源端出口压力
- 总 flit 数
- 某些主干路径的重复占用

## 哪些 AI 场景最需要它

最典型的是：

- weight broadcast
- activation fan-out
- 某些配置 / control 广播

这些模式的共同点是：同一份数据确实要发给多个 consumer，而不是“内容不同但目的多”。

## 它和 topology 的关系

broadcast/multicast 的收益和 topology 强相关。

在 mesh 上，multiple-unicast 更容易重复踩源端附近链路。
在分层或树状 overlay 上，更容易利用共享上游路径。

这就是为什么某些 AI 设计会额外引入：

- router 内 multicast 支持
- 预配置 multicast group
- 单独的 broadcast tree / control tree

## 什么时候不值得硬件化

如果某类 broadcast：

- 频率很低
- 数据量不大
- 重复占用还没成为瓶颈

那么软件复制往往就够了。硬件 multicast 不是越早上越好，而是应当建立在“重复占用已是结构性问题”之上。

## 一句话理解

multicast 的价值不在“少发几条命令”，而在“别让同一份数据把靠近源端的路径重复压很多遍”。

## 建模启示

第一版建模最实用的方法是做上下界：

- 上界：multiple-unicast
- 下界：理想 shared-path multicast tree

只要这两者的差距足够大，就说明硬件 multicast 可能有架构价值；如果差距很小，说明问题不在这里。
