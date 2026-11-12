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
- 源注入 flit 和重复的全网 flit-hop 数
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

记录源注入 flit、每条边的 flit-hop、复制 buffer、branch 状态和每个目的地的唯一投递。例：一次 fork 到 A/B，A 有 credit、B 无 credit。原子 fork 必须两分支都能接收才发送；逐分支 fork 可先发 A，并记录 `sent={A}`，B 恢复后只发 B，避免向 A 重复发送。packet 在所有必需分支被接收后才释放复制状态；fork 的持有/等待关系还需纳入死锁证明。

在相同路由资源且忽略 fork 额外成本时，可比较多份 unicast 与理想共享树的总 flit-hop；multiple-unicast 不是任意实现的延迟或吞吐上界，实际 fork 排队、复制和反压可能更慢。
