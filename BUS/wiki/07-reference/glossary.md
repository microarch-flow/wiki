# 术语表

上级：[07 术语与检查清单](./README.md)

## BUS

片上事务互连层。`shared bus / bus matrix / crossbar / 分层互连` 都可以看成这个抽象下的具体组织方式，而不是只有“一根共享总线”才叫 BUS。

## Master / Initiator

发起读写请求的一侧，例如 CPU、DMA。

本 wiki 默认正文优先使用 `master`，在更抽象或跨协议语境里会补充 `initiator` 作为同义词。

## Slave / Target

接收请求并提供数据或状态的一侧，例如 SRAM、DDR controller、peripheral block。

本 wiki 默认正文优先使用 `slave`，在更抽象或更中性的语境里会补充 `target` 作为同义词。

## Transaction

一次完整访问行为。从系统视角看，通常要把地址、控制、数据和完成/错误闭环组织起来；但不同协议不一定都把响应做成独立通道。

## Outstanding

已经发出但尚未完成的事务数量。

## Ordering

请求和响应是否必须按某种顺序出现的规则。

## Arbitration

多个请求竞争共享资源时的选择规则。

## Backpressure

下游无法继续接收流量时，向上游传播的节流机制。

## Bridge

在不同协议、位宽或时钟域之间做转换的互连模块。

## CDC

Clock Domain Crossing。跨时钟域传输和同步的逻辑与缓冲结构。

## Width Adaptation

在不同总线位宽之间做拆分、拼接、byte lane 重组或窄宽适配的过程。

## Crossbar

允许多个输入和多个输出并发匹配的一类互连组织方式。

## Coherent / Non-Coherent

是否提供 cache coherence 相关语义的区分。`coherent` 关注缓存副本一致性；`non-coherent` 不自动保证这件事。

## MMIO

通过内存映射地址空间访问设备寄存器的方式；语义上不同于普通可缓存内存。

## Barrier

约束访问顺序和可见性的机制。它不等于 cache maintenance，本身不会凭空让脏缓存对 non-coherent DMA 可见。

## Doorbell

软件或上游模块用于通知 device / DMA“有新任务可取”的控制面写操作或寄存器机制。

## Completion

把“硬件任务已完成”传回软件或上游模块的记录、状态或事件机制。

## Write Response

协议级写事务完成返回，例如 AXI `B` 通道；不要和软件层面的 completion record 混成一层。

## Response Path

请求完成后，数据或状态从 target 返回到 initiator 的路径；本 wiki 默认优先使用这个词。

## Return Path

`Response Path` 的同义别名。

## Control Plane / Data Plane

控制面更强调配置、状态、doorbell、管理和软件可见性；数据面更强调大吞吐数据搬运。

## Fabric

比“单条总线”更宽泛的互连统称，可包含 shared bus、bus matrix、crossbar、桥接和相关仲裁结构。

## Observability

系统对计数器、trace、错误状态和关键内部事件的可观测能力。

## Software Model

软件对一条访问路径的预期语义，例如是否可缓存、是否允许副作用、何时需要 barrier、何时结果可见。

## Timeout

事务最终可能会返回，但已经明显超过系统预期时限的现象。

## Fault

事务被明确判定为错误，例如 decode error、slave error、translation fault 或 permission fault。

## Hang

事务既没有成功完成，也没有明确报错，而是长时间失去 forward progress 的状态。
