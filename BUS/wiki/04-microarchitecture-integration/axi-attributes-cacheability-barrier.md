# AXI 属性、Cacheability 与 Barrier

上级：[04 微架构与系统集成](./README.md)

相关：[MMIO、Cache 与 Interrupt 视角](./mmio-cache-interrupt-view.md)、[DMA Descriptor Fetch、Data Move 与 Writeback](./dma-descriptor-fetch-data-move-writeback.md)、[Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md)、[Coherent Bus vs Non-Coherent Bus](../03-on-chip-protocol-families/coherent-bus-vs-noncoherent-bus.md)、[缓存一致性、IOMMU 与地址空间](../../../DMA/wiki/02-fundamentals/consistency-cache-coherency.md)

## 这页在回答什么问题

AXI transaction 不只携带"去哪里、搬什么"，还携带一张**旅行须知卡**——写着"这件行李能不能寄存（cache）？能不能和别人的行李合并（combine）？能不能调换顺序（reorder）？需不需要安检（secure）？走 VIP 通道还是普通通道（QoS）？有没有'必须等前面的人到了再出发'这种约束（barrier）？"

这些属性决定一笔访问的处理方式。DMA descriptor、data buffer、completion、MMIO doorbell 和 interrupt clear 虽然都是地址访问，但它们需要的"旅行须知"完全不同——就像普通旅客和外交信使走同一个机场，规则天差地别。

## AXI 属性在表达系统意图

不同 AXI 版本和系统会使用不同字段组合表达属性，例如 AxCACHE、AxPROT、AxQOS、AxUSER、shareability/attribute sideband 或由 MMU/MPU/IOMMU 生成的内部属性。建模时不必绑定某一组信号名，但必须保留语义。

| 属性语义 | 系统意图 | 错误配置后果 |
| --- | --- | --- |
| cacheable / non-cacheable | 是否允许进入 cache hierarchy | DMA 看不到 CPU 写入，或 CPU 看不到 DMA 写回 |
| bufferable / gatherable | 是否允许缓冲、合并、延后写入 | MMIO 写被延后或合并，改变设备行为 |
| device / normal memory | 是否有 side effect 和强顺序需求 | 寄存器被预取、重排或按普通 memory 优化 |
| shareable / non-shareable | 是否参与 coherence 或共享域 | 多 master 可见性错误 |
| secure / non-secure | 是否能访问安全资源 | 权限绕过或合法访问被拒绝 |
| privileged / user | 访问权限级别 | 用户态或设备访问越权 |
| QoS / priority | 调度优先级 | 实时流被饿死，或 debug/DMA 干扰 CPU |

属性的设计动机是让互连、cache、bridge、memory controller 和设备用一致方式理解访问。代价是属性要在多个层级保持一致：CPU 页表、DMA/IOMMU mapping、AXI sideband、bridge 映射、目标寄存器语义都要对齐。

## Memory 与 MMIO 的属性不能混用

同一个 load/store 形式，落到 memory 和 MMIO 上的语义不同。

| 访问对象 | 推荐语义 | 不应发生的优化 |
| --- | --- | --- |
| normal cacheable memory | 可 cache、可预取、可合并，受 coherence/order 规则约束 | 不能忽略权限和 shareability |
| non-coherent DMA buffer | 软件显式 clean/invalidate 或使用 non-cacheable mapping | 不能只靠 barrier 建立数据可见性 |
| coherent DMA buffer | 参与 coherence domain | 仍不能忽略 descriptor/doorbell 顺序 |
| MMIO register | device/non-cacheable，保留访问顺序和 side effect | 不能预取、合并、缓存或随意拆写 |
| completion/status memory | CPU 和 DMA 都要有明确可见性规则 | 不能让 interrupt 早于 completion 可见 |

把 MMIO 标成 cacheable，会让寄存器访问进入完全错误的优化空间；把普通 memory 标成 device，会牺牲吞吐并破坏合理的 burst/merge；把 DMA buffer 标错，会让软件和设备看到不同版本的数据。

## Cacheability 如何影响 DMA 三段链路

DMA 提交和完成路径里，descriptor、data buffer、completion buffer 的属性要分别看。

| 阶段 | 访问对象 | 属性与维护要求 | 错误症状 |
| --- | --- | --- | --- |
| descriptor fetch | CPU 写，DMA 读 | CPU 写后要对 DMA 可见；non-coherent 需要 clean | DMA 使用旧地址、旧长度 |
| source data read | CPU/设备准备，DMA 读 | 源数据要对 DMA 可见 | DMA 搬旧数据 |
| destination data write | DMA 写，CPU/设备读 | CPU 读取前要看到 DMA 写入；non-coherent 需要 invalidate | CPU 读旧目的 buffer |
| completion writeback | DMA 写，CPU 读 | completion 先于 interrupt 可见 | ISR 看到空队列或旧状态 |
| MMIO doorbell/clear | CPU 写 device register | device/non-cacheable，不能缓存或合并 | DMA 未启动或中断未清 |

cacheability 是正确性问题，不只是性能问题。一个 non-coherent DMA buffer 若缺少 clean/invalidate，BUS 上可能没有任何错误 response；系统只是静默地使用旧数据。

## Barrier 约束顺序，不制造可见性

barrier 的作用是约束访问顺序和可见点，不是把错误属性修正成正确属性，也不是自动把脏 cache line 写回给 DMA。

| 软件意图 | 需要的动作 | barrier 的作用 |
| --- | --- | --- |
| CPU 写 descriptor 后启动 DMA | clean descriptor cache line，然后 barrier，再写 doorbell | 保证 doorbell 不早于 descriptor 可见 |
| DMA 写 completion 后 CPU 读取 | coherent completion 或 invalidate 后读取 | 保证读取不越过同步点 |
| 多个 MMIO 配置寄存器按顺序生效 | 使用 device 属性和必要 barrier | 防止后续 start 早于配置写可见 |
| 清中断后退出 ISR | clear/EOI write 到达目标 | 防止后续动作早于 clear |
| 更新 IOMMU page table 后启用 DMA | 页表写入可见、TLB invalidation 完成 | 保证 DMA 不使用旧 translation |

barrier 的设计取舍是局部限制重排来换取确定性。过少 barrier 会让正确性依赖微架构偶然顺序；过多 barrier 会让 CPU、store buffer、interconnect 和 memory system 失去可用并行度。

## 例子：Descriptor、Doorbell、Completion 的顺序

一条 non-coherent DMA 提交到完成路径可以这样建模：

| 阶段 | 软件/硬件动作 | 属性与顺序要求 |
| --- | --- | --- |
| T0 | CPU 写 descriptor memory | normal memory，CPU cache 中可能是脏数据 |
| T1 | CPU clean descriptor cache line | descriptor 写入 memory 或 coherent 可见点 |
| T2 | CPU 执行 barrier | 后续 MMIO doorbell 不能越过 T1 |
| T3 | CPU 写 MMIO doorbell | device/non-cacheable，触发 DMA |
| T4 | DMA 读 descriptor | 读取到 T0/T1 的内容 |
| T5 | DMA 写 destination buffer 和 completion | completion 不早于 data write 完成语义 |
| T6 | DMA 触发 interrupt | interrupt 不早于 completion 可见 |
| T7 | CPU ISR invalidate/read completion | CPU 看到 DMA 写入的 completion |
| T8 | CPU 写 clear/EOI | device/non-cacheable，清除通知状态 |

这里的关键不是“是否用了 barrier”四个字，而是每个动作建立了什么可见关系。T2 不能替代 T1；T6 不能替代 T5；T8 不能被普通 cacheable write 替代。

## Bridge 与 Attribute Propagation

属性经过 bridge、width adapter、clock crossing 或 protocol conversion 时可能被保留、转换或丢弃。

| 转换位置 | 风险 | 建模要求 |
| --- | --- | --- |
| AXI -> APB bridge | APB 没有完整 AXI 属性字段 | MMIO/device 语义要由 bridge/地址窗口保证 |
| width adapter | 拆写或合并可能改变 side effect | MMIO 区域禁止不安全合并 |
| SMMU/IOMMU | 输入属性与页表属性结合 | 输出 cache/shareability/security 要明确 |
| interconnect firewall | 权限检查依赖 master ID 和属性 | secure/privileged 错误要返回可诊断响应 |
| DDR controller | QoS/cache hints 影响调度 | 属性不等于强制性能保证 |

属性传播的设计动机是让系统语义跨层保持一致。若某个 bridge 把 device 访问当成 normal memory，或者把 secure 属性丢掉，错误可能不在 bridge 处暴露，而是在软件流程里表现为乱序、缓存旧值或安全漏洞。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| coherent 系统不需要 barrier | coherence 解决 cache 可见性，不替代 doorbell、MMIO、interrupt 的顺序约束 |
| barrier 能让 DMA 看到脏 cache line | barrier 约束顺序，cache clean/coherence 才建立数据可见性 |
| cacheability 只影响性能 | 错误 cacheability 会造成旧数据、错误 completion 和 MMIO side effect |
| MMIO 访问自带所有顺序保证 | 还要看 CPU memory model、bridge、store buffer 和目标设备语义 |
| AXI 属性只是附加位 | 属性定义系统如何处理事务，是软件契约的一部分 |

## 一句话理解

AXI 属性定义一笔访问应被系统如何对待，barrier 定义多笔访问之间哪些顺序不能被打破；两者共同决定 DMA、MMIO 和 interrupt 流程是否成立。

## 继续阅读

- 如果你在追 `descriptor、data、writeback 三段为什么语义不同`：看 [DMA Descriptor Fetch、Data Move 与 Writeback](./dma-descriptor-fetch-data-move-writeback.md)
- 如果你在追 `MMIO 和普通内存的软件模型差别`：看 [MMIO、Cache 与 Interrupt 视角](./mmio-cache-interrupt-view.md)
- 如果你在追 `doorbell 前后为什么要小心顺序`：看 [Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md)
- 如果你在追 `coherent / non-coherent DMA 的系统前提`：看 [缓存一致性、IOMMU 与地址空间](../../../DMA/wiki/02-fundamentals/consistency-cache-coherency.md)

## 建模启示

AXI 属性、cacheability 和 barrier 要按软件契约建模。性能模型要记录不同属性对 cache、write buffer、bridge、interconnect、SMMU/IOMMU 和 memory controller 的影响。功能模型要记录 memory type、cacheability、shareability、secure/privileged、QoS、MMIO side effect、cache maintenance、barrier、attribute propagation 和 completion 可见性。

事件模型建议显式表达 `cache_line_clean_done`、`attribute_assign`、`barrier_order_point`、`mmio_write_observed`、`descriptor_visible_to_dma`、`completion_visible_to_cpu`、`attribute_drop_or_map`、`interrupt_after_completion`。这些事件能把“用了 barrier 但仍然错”“coherent 但中断顺序错”“DMA 读旧数据”拆成具体的属性、可见性或顺序问题。
