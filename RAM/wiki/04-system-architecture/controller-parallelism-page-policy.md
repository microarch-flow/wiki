# 控制器、并行度与页策略

上级：[04 系统架构视角](./README.md)

相关：[DRAM 命令与时序](../03-ddr-protocol-families/dram-commands-timing.md)、[地址映射与层级结构](./channel-rank-bank-address-mapping.md)

## 为什么控制器决定了“理论带宽能用出多少”

DRAM 设备本身只提供命令接口和阵列资源，真正把这些资源编排起来的是内存控制器。

控制器至少要处理：

- 请求排序
- bank 冲突规避
- row hit 利用
- read/write 切换
- refresh 干扰
- QoS 和尾延迟约束

所以系统性能很大程度上不是由 DRAM 颗粒单独决定，而是由控制器和 workload 共同决定。

## 三种关键并行资源

### Channel-level parallelism

多个 channel 可以并行搬数据，最直接提高峰值带宽。

### Bank-level parallelism

多个 bank 可以交错工作，用来隐藏 activate/precharge 开销。

### Row locality

如果后续访问持续命中 `同一个 bank 中已经打开的同一行`，单次访问代价会明显降低。

这三者常常互相牵制：

- 过度追求 row locality，可能降低 bank 打散
- 过度打散到不同 bank，可能损失行命中

控制器就是在这些矛盾之间找平衡。

## Page policy 在解决什么

常见直觉可以分成两类：

- `open-page`：假设后续还会访问当前行，尽量保留已打开 row
- `close-page`：假设后续局部性不强，尽快关行，减少冲突

没有哪一种永远更好，关键看 workload：

- 后续访问若常回到同一 bank、同一 row，更可能受益于 open-page
- 随机访问和高冲突场景，更可能受益于 close-page

## Refresh 为什么会影响真实性能

refresh 不是后台自动忽略的细节。

它会：

- 占用 bank 或更大范围资源
- 打断原有调度节奏
- 拉高尾延迟

容量越大、负载越重，refresh 的干扰越值得单独建模。

## 架构分析时最该看什么

如果你在做 CPU / GPU / AI 芯片的内存分析，优先看：

- 工作负载访问是否连续
- 是否有足够 bank/channel 并行
- 请求粒度和 burst 是否匹配
- 是否容易形成 row hit
- refresh 和写回是否在关键路径上

## 一句话理解

`内存控制器的工作，不是“把请求发出去”，而是把一堆带物理约束的阵列资源，调度成尽量接近理论峰值的系统吞吐。`
