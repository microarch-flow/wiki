# Row Locality、Return Path 与 AXI 体验

上级：[04 微架构与系统集成](./README.md)

相关：[RAM Row Locality 与 Page Policy 深化](../../../RAM/wiki/04-system-architecture/row-locality-page-policy-deep-dive.md)、[AXI Burst、对齐与边界](../03-on-chip-protocol-families/axi-burst-alignment-boundary.md)

## 这页在回答什么问题

为什么软件或 AXI master 看到的是“某些读特别慢、某些 burst 很顺”，而背后常常是 row locality 和 return path 一起在起作用。

## Row locality 会直接改变返回节奏

如果一串请求持续命中同一 row：

- DDR 侧更容易连续出数
- AXI `R` channel 更可能形成平滑返回流

如果频繁 row conflict：

- 返回会出现空洞
- outstanding 虽然很多，但 `RVALID` 不连续
- master 端会感觉系统“时快时慢”

## Return path 不是天然无限宽

即使 DDR 侧已经准备好数据，返回路径还可能受限于：

- interconnect return arbiter
- response FIFO 深度
- 与其他 master 的共享返回端口

所以 row locality 好，不一定自动等于最终 AXI 体验好；中间路径也可能再次打散。

## 一个有用的判断方式

如果你看到：

- DDR 吞吐不错
- 但某个 master 的 `R` channel 抖动很大

要同时排查两层：

1. DDR 侧是否有 row conflict / read-write turnaround
2. AXI return path 是否有共享争用

## 一句话理解

AXI 读体验是“DDR 是否顺利出数”与“返回路径是否顺利回流”两层因素叠加的结果。
