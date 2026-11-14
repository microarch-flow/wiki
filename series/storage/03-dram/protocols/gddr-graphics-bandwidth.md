# GDDR：高速数据接口与带宽预算

上级：<span id="gddr为带宽放弃了什么"></span>[DRAM 命令与接口](./README.md)

相关：[接口家族比较](./ddr-lpddr-gddr-hbm-tradeoff-map.md) · [HBM 宽接口](./hbm-stacked-wide-io.md)

## 这页在回答什么问题

GDDR 如何通过较高的每引脚数据率提供带宽？“为带宽放弃了什么”需要结合实际接口、板级设计与工作负载回答，不能预设它总比其他家族更耗电。

## 高带宽目标与 I/O 代价

典型系统使用多颗 GDDR 器件组成更宽的外部内存总线。提高引脚数据率需要控制器、PHY、封装和板级走线满足相应的信号完整性、训练和时序要求。器件组织、命令与功耗模式随代际变化。

例如 [Micron GDDR7 产品资料](https://www.micron.com/content/dam/micron/global/public/products/product-flyer/gddr7-product-brief.pdf)列出 32 Gb/s 数据率；若某 x32 器件的 32 根数据线均以此速率承载有效数据，理论峰值为 `32 Gb/s × 32 / 8 = 128 GB/s`。这不计协议、刷新、方向切换和其他损失；系统总线上的多颗器件也必须先确认独立有效位宽。

信号编码会影响符号率与位率之间的关系。Micron 的 GDDR6X 采用 PAM4，GDDR7 采用 PAM3；具体编码及换算以相应接口为准。上述 32 Gb/s 已是每数据引脚的位率，不能再按 PAM 电平数乘一次。[Micron 对 GDDR7 的说明](https://www.micron.com/products/memory/graphics-memory/gddr7)列出了 PAM3 及代际兼容性。

## 一句话理解

GDDR 通过高速数据引脚和系统总线组织获取带宽，实际性能还受协议和物理实现限制。

## 建模启示

区分符号率、每引脚数据率、有效 DQ 数和器件数量；再引入控制器、队列和信号实现限制。功耗与能效使用同条件下的产品数据或测量。
