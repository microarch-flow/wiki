# AXI Burst、对齐与边界

上级：[03 片上总线协议族](./README.md)

相关：[位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md)、[AXI 五通道与 VALID/READY](./axi-five-channels-handshake.md)、[AXI Narrow Transfer 与 WSTRB](./axi-narrow-transfer-wstrb.md)、[AXI Response 与错误路径](./axi-response-error-path.md)

## 这页在回答什么问题

为什么 AXI burst 不只是“连续多拍数据”，而是由长度、beat 大小、地址递增规则、对齐和边界共同约束的一组事务语义。

## Burst 把多个 beat 绑定成一笔事务

AXI burst 用一次地址请求描述多个 data beat。地址 channel 里会给出起始地址、burst length、每 beat 大小和 burst 类型；数据 channel 逐 beat 传 payload，并用 last 标记结束。这样可以摊薄地址开销，也让 interconnect、slave 和 memory controller 提前知道后续数据规模。

三个字段是理解 burst 的入口：

| 字段 | 含义 | 建模时保留什么 |
|---|---|---|
| `AxLEN` | burst 里有多少 beat，编码值对应 beat 数减一 | beat count、last beat 位置 |
| `AxSIZE` | 每个 beat 传输多少 byte | beat bytes、byte lane 选择 |
| `AxBURST` | 地址如何随 beat 变化 | FIXED / INCR / WRAP 的地址序列 |

`FIXED` burst 的地址不随 beat 变化，适合 FIFO 类寄存器窗口；`INCR` burst 的地址按 beat size 递增，是连续内存访问的主要形态；`WRAP` burst 用在 cache line 这类环绕边界场景。实现者不能只看“有几个 beat”，还要知道每个 beat 的地址如何被推导。

容易误解：burst 只是把多次访问合并起来。实际上，burst 是一笔带有地址生成规则、last beat、response 和边界约束的 transaction。

## 对齐决定 byte lane 和拆分压力

`AxSIZE` 定义每个 beat 的传输大小。若一次 4-byte transfer 从 4-byte 对齐地址开始，byte lane 选择简单，地址递增也直观；若起始地址不对齐，数据可能跨越自然边界，master、interconnect、adapter 或 slave 就要处理 byte lane 选择、WSTRB、重组或拆分。

一个 64-bit data path 上的例子：

| 起始地址 | Transfer size | 覆盖 byte lane | 实现含义 |
|---:|---:|---|---|
| `0x1000` | 4 byte | lane 0-3 | 对齐半宽访问 |
| `0x1004` | 4 byte | lane 4-7 | 对齐半宽访问 |
| `0x1003` | 4 byte | lane 3-6 | 非自然对齐，需要更小心的 lane/strobe 处理 |

读路径上，非对齐访问可能要求 slave 返回包含目标 byte 的 beat，再由 master 或 adapter 选择有效 byte。写路径上，`WSTRB` 必须准确表达哪些 byte lane 被更新；如果经过 width adapter，还可能被拆成多个下游 beat。

对齐不是格式洁癖，而是决定硬件是否能用简单地址生成器和固定 lane 映射完成访问。对齐差会增加 adapter 逻辑、buffer、响应合并和验证 corner case。

容易误解：地址连续就能形成高效 burst。实际上，连续地址还要满足 transfer size、lane 映射、下游宽度和边界规则；否则 burst 可能被拆分，或者变成高成本窄访问。

## 边界限制保护 decode 和下游语义

AXI burst 不能跨越协议规定的 4KB address boundary。这个规则的目的不是性能优化，而是让一次 burst 不跨越可能不同 decode 目标、保护属性、page 属性或 slave 归属的区域。若一个 burst 能跨过 4KB 边界，interconnect 就可能在同一笔事务中途改变目标或属性，response 和 ordering 语义都会变复杂。

判断 4KB 边界可以用这个口径：

`start_address[31:12] == end_address[31:12]`

其中 `end_address` 来自起始地址、beat count 和 beat size 推导出的最后一个 byte 地址。构造例子：

| 起始地址 | Beat 数 | 每 beat | 最后 byte | 是否跨 4KB |
|---:|---:|---:|---:|---|
| `0x0FC0` | 8 | 8 byte | `0x0FFF` | 否 |
| `0x0FE0` | 8 | 8 byte | `0x101F` | 是 |

第二行必须在 master 或上游生成逻辑里拆成两个合法 burst，例如先覆盖 `0x0FE0-0x0FFF`，再从 `0x1000` 继续。拆分后，事务数量、address handshake 次数、outstanding 占用、response 数量和 backpressure 形态都会改变。

除了 AXI 的协议级 4KB 边界，SoC 还会有自己的 decode window、bridge 限制、memory controller 行粒度、IOMMU/SMMU 映射和外设寄存器窗口。协议合法只说明通过了第一层约束，不说明下游一定愿意按原始 burst 接收。

容易误解：跨界拆分只是地址生成细节。实际上，拆分会改变 transaction 数量和 completion 组织，进而影响性能、错误定位和软件等待时机。

## Burst 长度不是越长越好

长 burst 的收益来自摊薄地址开销和提高连续 payload 利用率。对连续、对齐、可合并的 memory traffic，它可以让 data path 和 memory controller 更容易保持忙碌。

长 burst 的代价来自资源占用时间。按 burst 保持 grant 的路径上，一个长 burst 会让短请求等待更久；经过 narrow adapter 或 CDC 时，长 burst 可能占用更多 buffer；遇到错误时，系统还要回答哪个 beat 出错、response 如何组织、master 如何恢复。

下面是一个简化对比，假设地址/响应固定开销合计 3 cycle，data path 每 cycle 接 1 beat：

| Burst | Payload beat | 固定开销 | 总 cycle | 单 beat 平均成本 |
|---|---:|---:|---:|---:|
| 1 beat | 1 | 3 | 4 | 4.00 cycle |
| 4 beat | 4 | 3 | 7 | 1.75 cycle |
| 16 beat | 16 | 3 | 19 | 1.19 cycle |

这张表只展示固定开销摊薄，不包含仲裁等待、回压、边界拆分和下游服务时间。若 16-beat burst 在目标端口前等待，或者中途被 adapter 拆成更多下游访问，真实尾延迟可能比表格更差。

容易误解：burst 越长越高效。实际上，burst 长度是在 payload 利用率、占路时间、buffer 压力、边界拆分和错误诊断之间做交易。

## 一句话理解

AXI burst 用 `AxLEN/AxSIZE/AxBURST` 把多个 beat 组织成一笔事务；对齐和 4KB 边界决定这笔事务能否被简单、合法、低成本地送到同一个目标。

## 建模启示

建模 AXI burst 时，不能只保存 payload bytes。至少要保存起始地址、beat count、beat size、burst type、last beat、是否跨 4KB 边界、是否经过 width adapter、每个 beat 的有效 byte lane，以及拆分后形成的子事务数量。

性能模型要把 burst 拆分对系统状态的影响算进去：一个非法跨界 burst 会变成多个 address handshake 和多个 response；一个非对齐或 narrow burst 可能增加 beat 数、adapter buffer 占用和 WSTRB 处理；一个长 burst 可能提高 payload 利用率，也可能放大仲裁尾延迟。

功能模型要检查地址序列是否合法、`WLAST/RLAST` 是否和 `AxLEN` 一致、`AxSIZE` 是否匹配 byte lane、`WRAP` 地址是否按规则环绕、4KB 边界是否被遵守、错误 response 是否能对应到正确事务。省略这些规则，会把 burst 从协议语义误降成“连续 N 个 beat”，从而漏掉最容易出错的边界条件。
