# AXI Narrow Transfer 与 WSTRB

上级：[03 片上总线协议族](./README.md)

相关：[AXI Burst、对齐与边界](./axi-burst-alignment-boundary.md)、[位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md)、[Bridge、CDC 与 Width Adapter](../04-microarchitecture-integration/bridge-cdc-width-adaptation.md)、[MMIO、Cache 与 Interrupt 视角](../04-microarchitecture-integration/mmio-cache-interrupt-view.md)

## 这页在回答什么问题

为什么 AXI 数据总线很宽时，一次只访问几个 byte 会把地址低位、byte lane、WSTRB、width adapter 和 MMIO 副作用都卷进来。

## Narrow transfer 描述的是 beat 粒度

想象一条 8 车道的高速公路（128-bit data path），现在只有一辆摩托车（4 byte 数据）要通过。这就是 narrow transfer——**货物比车道窄得多**。

在 AXI 里，`AxSIZE` 描述每个 data beat 传输多少 byte。如果传输大小小于数据总线物理宽度，这个 beat 就是 narrow transfer。例如 128-bit data path 有 16 个 byte lane，但 `AxSIZE=2` 表示每个 beat 只传 4 byte。

Narrow transfer 的重点不是”货少”，而是”**摩托车占哪条车道**”。系统必须回答：这 4 byte 走的是第 1-4 车道还是第 5-8 车道？没有货物的车道怎么处理？地址低位、`AxSIZE`、burst 类型和 beat index 会共同决定车道选择。

一个 128-bit data path 上的构造例子：

| 地址 | `AxSIZE` | 每 beat byte | 覆盖 lane | 语义 |
|---:|---:|---:|---|---|
| `0x1000` | 2 | 4 byte | lane 0-3 | 低 32-bit lane |
| `0x1004` | 2 | 4 byte | lane 4-7 | 中间 32-bit lane |
| `0x100C` | 2 | 4 byte | lane 12-15 | 高 32-bit lane |
| `0x1003` | 2 | 4 byte | lane 3-6 | 非自然对齐，lane 处理更复杂 |

容易误解：narrow transfer 只是“数据少一点”。实际上，它改变的是每个 beat 的 lane 映射和访问粒度，直接影响 adapter、slave 和验证状态。

## WSTRB 描述的是写 lane 有效性

`WSTRB` 就像**货物装卸单上的勾选框**——8 个车道，哪几个车道上有实际货物需要卸下来，在单子上打勾。没打勾的车道（`WSTRB=0`），目标仓库不应该动那个位置的存货。

Narrow transfer 和 WSTRB 有关联，但不是同一件事：

| 概念 | 由什么定义 | 作用 |
|---|---|---|
| Narrow transfer | `AWSIZE/ARSIZE` 小于 data bus 宽度 | 定义这次 beat 的传输大小 |
| WSTRB | `W` channel 上的 byte strobe | 定义写 beat 中哪些 byte lane 真正更新 |
| Partial write | WSTRB 只打开部分 lane | 定义写入掩码，可能发生在窄写或宽写里 |

一个 128-bit data path 上，4-byte narrow write 到 `0x1004`，合理的 `WSTRB` 可能只打开 lane 4-7。若实现错误地打开 lane 0-15，就会把不属于这次访问的 byte 一起写掉；若 lane 偏移算错，就会把数据写进错误字段。

读路径没有 `RSTRB`。读 narrow transfer 的有效 byte 由地址和 `ARSIZE` 推导，slave 或 adapter 返回的数据必须让 master 能取到对应 byte。建模时不能把“写有 WSTRB”推广成“读也有 strobe”；读侧的关键是 data alignment、lane extraction 和 response。

容易误解：WSTRB 就等于 narrow transfer。实际上，WSTRB 只描述写 lane 是否更新；narrow transfer 描述 beat 传输粒度。在小粒度写入宽数据通路时，两者会同时影响同一个 beat，但语义边界不同。

## Width adapter 会把 lane 语义重写成子访问

宽窄适配是 narrow transfer 最容易出错的位置。宽 master 访问窄 slave 时，一个上游 beat 可能被拆成多个下游 beat；窄 master 访问宽 slave 时，adapter 可能把多个窄访问合并，或者用 byte strobe 在宽 slave 上执行局部写。

例如，128-bit AXI master 对 32-bit APB 寄存器子树写 4 byte。上游看起来是一笔 128-bit data path 上的窄写，下游却可能变成一次 32-bit APB 写。adapter 必须把地址低位、WSTRB、write data lane 和 response 重新组织。如果 WSTRB 指示的 lane 与目标 APB 字对不齐，adapter 要么拒绝/报错，要么拆分成更小粒度访问，具体取决于系统支持的语义。

反方向也有风险。32-bit master 写 128-bit slave 的一个字段，如果 slave 原生支持 byte strobe，adapter 可以直接转发 lane 掩码；如果 slave 只支持 128-bit 全宽写，adapter 可能需要 read-modify-write。只有在目标不能直接做 byte-lane 写，或者必须保持更宽粒度原子更新时，read-modify-write 才是合理路径；它会增加读延迟、临时 buffer 和错误处理复杂度。

容易误解：width adapter 只是改变数据线宽。实际上，它还要维护地址偏移、WSTRB、response、ordering 和副作用边界。

## MMIO 副作用让局部写变得敏感

普通仓库（memory）很好理解：你说往第 3 格放货，就放第 3 格，其他格不动。但 MMIO 寄存器更像一个**充满机关的控制面板**——有些按钮按一下就会触发动作，有些开关读一下就会自动复位，有些保留位碰都不能碰。

这会让”先读出来、改一部分、再写回去”（read-modify-write）变得危险——就像为了按面板上的一个按钮，你先把整个面板拍了张照，改了一个像素，然后把整张照片印回面板上。读的动作可能已经触发了 read-to-clear（你拍照时有些灯灭了）；如果你不小心碰到了保留按钮，可能触发意想不到的动作；如果 slave 忽略 WSTRB，你本来只想改一个字段，结果整个面板都被重写了。

因此，MMIO slave 必须明确自己接受哪些访问粒度。只接受 32-bit 对齐写的寄存器，不应该默默吞掉 8-bit narrow write；支持 byte write 的寄存器，必须让 WSTRB 和副作用规则一致。bridge 也要决定非法粒度是返回错误、拆分、还是转成受控的下游访问。

容易误解：WSTRB 能自动保护寄存器副作用。实际上，WSTRB 只是写掩码信号；是否保护副作用，取决于 slave 和 bridge 是否按寄存器语义正确解释它。

## 对齐、WSTRB 和 burst 必须一起看

Narrow transfer 可以出现在 burst 中。此时每个 beat 的地址递增、lane 选择和 WSTRB 都要随 beat 变化。一个 4-beat、每 beat 4 byte 的 INCR burst，在 128-bit data path 上可能依次覆盖 lane 0-3、4-7、8-11、12-15；若起始地址不是自然对齐，lane 变化会更复杂，还可能跨越下游 word 或 adapter 边界。

对写 burst，`WSTRB` 还要和 `WLAST`、`AxLEN`、`AxSIZE` 一起验证。最后一个 beat 不是特殊豁免，仍然必须正确标记有效 byte lane。对读 burst，模型要知道每个 beat 的有效 byte 位于哪里，不能只记录“返回了 N 个 beat”。

下面是一个对齐的 4-beat narrow write 示例：

| Beat | 地址 | 有效 byte | 128-bit lane | 期望 WSTRB |
|---:|---:|---:|---|---|
| 0 | `0x1000` | 4 byte | lane 0-3 | `0x000F` |
| 1 | `0x1004` | 4 byte | lane 4-7 | `0x00F0` |
| 2 | `0x1008` | 4 byte | lane 8-11 | `0x0F00` |
| 3 | `0x100C` | 4 byte | lane 12-15 | `0xF000` |

这张表只覆盖简单对齐场景。经过 width adapter、跨 4KB 边界、跨寄存器窗口或非对齐起点时，系统必须重新判断是否允许原始 burst，还是拆成多个合法子事务。

## 一句话理解

Narrow transfer 用 `AxSIZE` 定义 beat 粒度，WSTRB 用 byte strobe 定义写 lane 有效性；两者共同决定宽 AXI 数据通路上的小粒度访问是否能被正确、安全地落到目标 byte 或寄存器字段上。

## 建模启示

建模 narrow transfer 时，不能只记录 payload size。至少要记录 data bus width、`AxSIZE`、起始地址低位、beat index、每个 beat 的有效 byte lane、写路径 WSTRB、是否经过 width adapter、以及目标 slave 支持的最小访问粒度。

性能模型要把窄访问的额外成本算进去：lane extraction、adapter 拆分或合并、read-modify-write、额外 response、buffer 占用和 backpressure。一个 4-byte 写在 128-bit fabric 上不一定等价于“宽总线里传了 4 byte”；它可能在下游变成一次 32-bit APB 写，也可能触发更复杂的 RMW。

功能模型必须检查 WSTRB 和地址是否一致，未打开 lane 是否保持不变，MMIO 副作用是否只发生在被允许的字段，非法访问粒度是否返回错误或被明确定义地转换。对读路径，模型要检查返回数据的有效 byte 如何被提取，不能假设读侧也有 strobe 帮忙标记有效 lane。

最危险的简化是把 WSTRB 当作“写几个 byte”的普通掩码，而忽略目标寄存器语义。对普通 memory，它主要是 byte lane 更新问题；对 MMIO，它可能直接决定是否误清状态、误触发动作或扩大副作用范围。
