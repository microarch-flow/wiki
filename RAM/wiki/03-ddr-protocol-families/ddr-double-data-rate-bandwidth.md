# DDR、数据率与带宽

上级：[03 DDR 协议与家族](./README.md)

相关：[为什么不能只靠提频](./why-frequency-cannot-scale-forever.md)、[地址映射与层级结构](../04-system-architecture/channel-rank-bank-address-mapping.md)

## DDR 到底是什么意思

这里先区分两层含义：

- 狭义 `DDR`：`Double Data Rate` 这种传输方式
- 广义 `DDR`：JEDEC 主存路线里的 `DDR SDRAM` 家族

本页先讲前者，也就是“为什么一个接口能在一个周期里传两次数据”。

核心含义是：

- 一个时钟周期里
- 在上升沿和下降沿各传一次数据

因此，在相同基础时钟下，DDR 的数据传输次数可以是 SDR 的两倍。

## 为什么常见标称不是 MHz 而是 MT/s

内存宣传里更常见的是 `3200 MT/s`、`6400 MT/s` 这类写法，而不是简单写 MHz。

原因是：

- 物理时钟频率只是内部节奏的一部分
- 系统真正关心的是单位时间发生多少次数据传输

所以像 `DDR5-6400`，通常更应理解为 `6400 MT/s`，而不是单纯 `6400 MHz`。

如果用最粗略的时钟直觉去看，它对应的外部数据节奏大约可联想到 `3200 MHz` 级别的双沿传输，但工程讨论里更稳妥的写法仍然是 `MT/s`。

## 带宽公式从哪来

理论峰值带宽可以近似写成：

`Bandwidth = Transfer Rate x Bus Width / 8`

也就是：

- `Transfer Rate` 决定一秒传多少次
- `Bus Width` 决定一次能传多少 bit
- 除以 `8` 是把 bit 转成 Byte

## 例子

这里的 `Bus Width` 必须说明比较单位。下面例子都指 `单 64-bit channel` 的理论峰值，不是在比较整个平台、整条 DIMM 链路或整块板卡的总带宽。

### DDR4-3200，单 64-bit 通道

理论峰值：

`3200 x 10^6 x 64 / 8 = 25.6 GB/s`

### DDR5-6400，单 64-bit 通道

理论峰值：

`6400 x 10^6 x 64 / 8 = 51.2 GB/s`

### 双通道 DDR5-6400

理论峰值：

`51.2 x 2 = 102.4 GB/s`

## 为什么“理论带宽”不等于“有效带宽”

这个公式只描述 `理论峰值带宽`，不代表应用总能跑到这个值。

跨页比较时，最好显式写清楚自己在说：

- `per pin`
- `per channel`
- `per DIMM`
- `per stack`
- `per package`
- `per board`
- `per platform`

实际带宽还受：

- row hit / row conflict
- bank 并行度
- 控制器调度
- refresh
- read/write 切换
- 请求粒度和访问模式

影响。

所以真正的工程问题不是“公式会不会算”，而是“系统能否把理论峰值转成有效/可持续吞吐”。

## 一句话理解

带宽公式解释了 `为什么位宽和速率重要`，但要把公式变成真实系统能力，必须同时看阵列结构、控制器和封装约束。
