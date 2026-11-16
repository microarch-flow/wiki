# BUS 高频问题

上级：[07 术语与检查清单](./README.md)

相关：[术语表](./glossary.md)、[BUS 一页版总览](./bus-one-page.md)、[Timeout、Fault 与 Hang 定位框架](../05-performance-debug/timeout-fault-hang-debug-framework.md)

说明：本 wiki 正文优先使用 `master / slave`。在跨协议或抽象语境里，会补充 `initiator / target` 作为同义表述。

## 1. BUS 和 NoC 是不是一回事

不是。BUS 像城市里的**公交系统**——强调站点、时刻表、乘客能看到的到站信息。NoC 像**高铁网络**——强调大规模节点、分布式调度、包裹分拣和可扩展运力。

设计判断：门禁、配置、状态查询这类"市内通勤"用 BUS；tile 间大批量数据搬运这类"城际货运"用 NoC。

## 2. AXI 是不是一条“总线”

AXI 是事务协议，不是传统意义上的一根共享线。AXI 可以接在 crossbar、bus matrix、bridge 或更复杂 fabric 上。

调试判断：看到 AXI 信号时，不要只问“总线忙不忙”，要问 AR/AW/W/R/B 哪个 channel 没闭环，ID/outstanding 哪个 slot 没释放。

## 3. AXI 比 AHB 新，是不是所有地方都应该用 AXI

不是——就像不能因为高铁比公交新，就在小区里修高铁。AXI 提供更强并发和多 channel 能力，也带来 ID、outstanding、return path、验证和时序复杂度。

设计判断：大货量长距离用高速公路（AXI）；小区内通勤用自行车道（APB）或公交（AHB-Lite），够用、便宜、好维护。

## 4. APB 慢，是不是就不重要

不是——消防报警器不需要跑得快，但如果它不响，整栋楼都有危险。APB 承载大量配置、状态、interrupt clear、timer、watchdog、debug/status 路径。它不追求高吞吐，但它直接影响软件控制闭环。

调试判断：APB PREADY 长等待、PSLVERR、bridge timeout 就像消防通道被堵——平时没事，关键时刻要命。

## 5. Address handshake 成功，是不是事务就完成了

不是——快递公司说"已揽收"不等于"已送达"。地址握手只表示 request 被接收（揽收）。读事务要看到最后一个 R beat 和 RLAST（签收）；写事务要看到所有 W beat、WLAST 和 B response（确认送达回执）。

波形判断：维护 transaction ledger，就像快递追踪系统——记录每个包裹的揽收、在途、签收状态。

## 6. Coherent 系统是不是就不需要 barrier

不是。Coherence 解决 cache 副本可见性，不替代 MMIO 顺序、doorbell 顺序、interrupt/completion 顺序和设备协议。

设计判断：descriptor -> doorbell、completion -> interrupt、clear/EOI 这些顺序仍要由 barrier、属性和设备状态机共同保证。

## 7. DMA 完成数据搬运，是不是软件一定看到 completion

不是——外卖送到你家门口不等于你知道了。骑手还得拍照确认（writeback）、系统要同步状态（cache/coherence）、给你发"已送达"通知（interrupt）、你要点"确认收货"（clear/EOI）。

调试判断：先区分 `data_done`（货到了）和 `completion_visible_to_cpu`（你知道了），再看通知是不是比实际送达还早。

## 8. IOMMU fault 是不是 memory controller 问题

不是——海关拒签不等于目的地城市有问题。IOMMU fault 发生在翻译和权限层（签证审核），data request 可能根本没到达 memory controller（旅客还没出海关）。

调试判断：看护照号（stream ID）、签证类型（context）、目的地（IOVA）、出行目的（access type）和在哪个窗口被拒的（fault stage）。

## 9. 平均带宽够，是不是 BUS 就没问题

不是。平均带宽掩盖 tail latency、局部热点、return path 争用、write drain 和 completion latency。

性能判断：看 latency histogram、p99/max、queue high watermark、arbiter wait、response wait，而不是只看 aggregate bandwidth。

## 10. 波形里 READY 拉低，是不是一定有 bug

不是。READY 拉低是合法 backpressure。关键是它是否长期不恢复，以及下游哪个 queue、slot、slave、bridge 或 return path 导致不能接收。

反过来，READY 高也不等于路径空闲；source 可能因为 outstanding 满、ID 保序或上游状态没发 VALID。

## 11. CPU 读 MMIO 卡死，是不是软件 bug

不一定。常见根因包括 decode 没闭环、外设 clock/reset/power 未 ready、APB PREADY 不来、bridge response 丢失、timeout/error 机制缺失。

调试判断：先分 timeout/fault/hang，再追 `CPU request -> bridge/APB -> slave -> response return`。

## 12. DDR 带宽高，是不是 AXI master 体验好

不是。DDR 总吞吐高时，单个 master 仍可能被 row conflict、read/write turnaround、return arbiter、R FIFO 或 RREADY 反压拖出长尾。

性能判断：把 DDR data ready 和 AXI R channel returned 分开观测。

## 13. Crossbar 是不是无阻塞

不是。Crossbar 只能让不冲突的 input/output 组合并行。同一 slave、同一 DDR controller、同一 APB bridge、共享 return path 和 ID slot 仍会形成阻塞。

设计判断：画并发矩阵，不要只看框图上有没有 crossbar。

## 14. Barrier 能不能让 DMA 看到脏 cache line

不能。Barrier 约束顺序，不执行 cache clean。non-coherent DMA 需要显式 clean/invalidate 或使用 coherent path。

设计判断：descriptor 可见性靠 clean/coherence，doorbell 顺序靠 barrier/device ordering，两者不能互相替代。

## 15. Debug read 是不是无害观察

不是。Debug read 也是 BUS transaction，可能触发 MMIO read side effect、FIFO pop、read-clear status，也会与正常流量争用。

设计判断：关键状态应提供 snapshot、shadow register 或只读 debug alias。

## 一句话理解

BUS 高频误区的共同根源，是把协议、互连实现、内存属性、软件语义和调试现象混成一层。把 request、service、response、completion、error 分开后，大多数判断会更清楚。

## 建模启示

FAQ 里的每个问题都对应一个建模边界：BUS/NoC 是 Topology 边界，AXI/AHB/APB 是 Interaction/Capability 边界，MMIO/memory 是 Software Model 边界，timeout/fault/hang 是终态边界，debug/counter/waveform 是 Observability 边界。

事件模型建议用 `request_accept`、`response_return`、`completion_visible`、`barrier_order_point`、`cache_clean_done`、`timeout_fire`、`fault_recorded`、`debug_read_side_effect` 来回答这些高频问题，而不是只用协议名称回答。
