# 02 基础对象与事务语义

上级：[BUS Wiki](../README.md)

相关：[BUS 在解决什么问题](../01-overview/problem-statement.md)、[BUS 分类框架](../01-overview/taxonomy.md)、[AXI / AHB / APB 对照](../03-on-chip-protocol-families/axi-ahb-apb-comparison.md)、[互连组件与数据路径分解](../04-microarchitecture-integration/interconnect-components.md)

## 这一章在回答什么问题

01 章回答了"为什么需要 BUS"——就像理解了"为什么城市需要交通系统"。02 章要回答的是：这个交通系统到底由哪些基本零件组成，什么规则决定一辆车（一笔访问）能不能到达目的地，什么参数决定它跑得快不快。

具体来说，02 章把 BUS 拆成四个基础对象：连接关系（路网结构）、transaction 生命周期（一次出行的全过程）、共享约束（交通规则）、时序粒度（车道宽度和限速）。后面的 AXI、bridge、crossbar、性能调试都建立在这四个对象之上。

## 本章阅读顺序

1. [BUS vs NoC vs Point-to-Point](./bus-vs-noc-vs-point-to-point.md)
2. [地址、数据、响应与事务语义](./transaction-address-data-response.md)
3. [仲裁、顺序性与 Backpressure](./arbitration-ordering-backpressure.md)
4. [位宽、时钟、Burst 与延迟](./width-clock-burst-latency.md)

这个顺序不是按协议字段展开，而是按建模依赖展开。先判断连接关系，再定义一次访问的生命周期，然后讨论多笔访问共享资源时的约束，最后把位宽、频率、burst 和 latency 放进同一个时间模型。

## 四个基础判断

用一个物流系统的类比来串起这四个判断：

**第一，先看路网结构（连接关系）。** 两个仓库之间固定走专线卡车（point-to-point），多个仓库共享配送网络需要调度中心（BUS），全国性物流需要分布式中转网络（NoC）。这个边界能防止给两个相邻仓库建一整套物流网络（过度设计），也能防止让全国快递都挤一个配送站（设计不足）。

**第二，理解一次配送的完整生命周期（transaction）。** 一次配送不是”写个地址贴上就完了”。地址决定路由和合法性（包裹寄往哪里），控制属性决定处理规则（加急？冷链？保价？），数据阶段消耗带宽（实际搬运），response 证明事务闭环（签收确认）。快递公司说”已揽收”（`request accepted`）和收件人说”已签收”（`transaction completed`）之间的时间差，是 outstanding、timeout、backpressure 和性能尾部问题的共同起点。

**第三，共享系统必须有交通规则（仲裁、顺序性、backpressure）。** 仲裁决定谁先上高速（谁先获得资源），顺序性决定包裹能不能乱序送达（哪些完成结果可以先被看见），backpressure 决定下游仓库爆仓后压力如何传回上游（下游压力如何传回上游）。三者组合后，理论运力充足的物流系统仍可能出现个别包裹迟迟送不到（尾延迟）、某些路线永远排不上（starvation）、整个系统卡死（hang）。

**第四，卡车大小、行驶速度和批量发车只是运力上限（位宽、时钟、burst）。** 位宽决定每趟卡车能装多少货，频率决定每天能发多少趟车，burst 决定固定装卸开销如何被大批量货物平摊。但真实送达效率还要扣除排队等装车、过收费站、换小车进城、拆分超重包裹、等签收回单的时间。

## 和后续章节的关系

03 章会把这些基础对象落到具体片上协议族里。读 AXI 五通道时，要带着“地址、数据、响应为什么分离”的问题；读 ID/outstanding 时，要带着“response 如何匹配 request”的问题；读 burst、WSTRB 和 response error 时，要带着“transaction 生命周期如何被拆分和闭合”的问题。

04 章会把这些对象放进实现结构。decoder、arbiter、crossbar、bridge、FIFO、CDC 和 width adapter，不是孤立组件，而是在实现本章定义的路由、仲裁、顺序、回压和时序适配。

05 章会把这些对象转成性能和调试口径。带宽、延迟、利用率、拥塞、QoS、timeout、fault 和 waveform debug，核心都是在追踪 transaction 从请求被接受到 completion 被消费之间，卡在了哪个资源、哪个队列、哪条顺序边或哪段 backpressure 链上。

06 章会用系统案例检验这些判断。MCU、SoC、AI 芯片和 AXI crossbar 的差异，不只是协议名字不同，而是连接规模、共享语义、事务能力、仲裁压力和时序参数的组合不同。

## 常见误解

- “BUS、NoC、point-to-point 是性能等级”：就像说”自行车 < 汽车 < 飞机”——它们是不同约束下的组织方式，不是代际替换关系。骑自行车去楼下买菜比开飞机合适得多。
- “一次访问就是发地址拿数据”：就像说”网购就是下单收货”——实际上至少要区分请求头（下单）、payload（发货）、completion（签收）和 completion consumption（拆包验货）。
- “平均带宽够就不会堵”：就像说”这条高速每天能通过 10 万辆车，所以不会堵”——早高峰的仲裁粒度、不能变道的顺序约束和出口匝道的 backpressure 会把问题集中到尾延迟和 forward progress 上。
- “位宽和频率越大越好”：就像说”把所有路都修成 8 车道高速”——更宽和更快会带来布线面积、时序收敛、adapter 转接、CDC 同步和固定延迟代价。

## 一句话总纲

BUS 的复杂度不在”有多少根线”（有多少条路），而在连接关系（路网怎么连）、transaction 生命周期（一趟配送从接单到签收）、共享资源约束（交通规则）和时序粒度（车道宽度和限速）这些规则如何共同决定每笔访问能否送达、能否并行、会在哪里排队。

## 建模启示

02 章给性能模型和功能模型提供最小状态集合。性能模型至少要记录端点连接关系、目标地址、读写方向、payload size、burst beat、固定开销、仲裁点、outstanding slot、顺序约束、FIFO/credit/backpressure、response 返回时间。功能模型还要保留地址合法性、访问属性、byte enable/strobe、错误响应和可见顺序。

不要用“BUS/NoC/AXI/APB”这些名字直接推出行为。名字只能提供默认假设，真正决定模型的是连接关系、事务拆分、共享资源和时序参数。一个 AXI 路径可能被低速 slave 或 bridge FIFO 限住；一个简单 point-to-point 专线可能比复杂 fabric 更适合固定低延迟数据流；一个 NoC 边缘的 MMIO 访问仍然需要软件可见 completion。

本章结束后，读者应该能把一次访问拆成事件，把一条路径拆成资源，把一个性能现象拆成排队、顺序或回压问题。做到这一步，再进入 03 章协议细节，字段和通道才会变成有意义的设计选择，而不是孤立术语。
