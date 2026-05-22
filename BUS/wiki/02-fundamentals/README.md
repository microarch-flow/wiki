# 02 基础对象与事务语义

上级：[BUS Wiki](../README.md)

相关：[BUS 在解决什么问题](../01-overview/problem-statement.md)、[BUS 分类框架](../01-overview/taxonomy.md)、[AXI / AHB / APB 对照](../03-on-chip-protocol-families/axi-ahb-apb-comparison.md)、[互连组件与数据路径分解](../04-microarchitecture-integration/interconnect-components.md)

## 这一章在回答什么问题

当系统已经确定需要片上事务互连之后，BUS 到底在组织什么对象，哪些规则决定一笔访问能不能完成，哪些参数决定它跑得快不快。

01 章给出的是问题定义：BUS 不是一根线，而是共享资源上的事务组织层。02 章把这个判断拆成四个基础对象：连接关系、transaction 生命周期、共享约束、时序粒度。后面的 AXI、bridge、crossbar、性能调试都建立在这四个对象之上。

## 本章阅读顺序

1. [BUS vs NoC vs Point-to-Point](./bus-vs-noc-vs-point-to-point.md)
2. [地址、数据、响应与事务语义](./transaction-address-data-response.md)
3. [仲裁、顺序性与 Backpressure](./arbitration-ordering-backpressure.md)
4. [位宽、时钟、Burst 与延迟](./width-clock-burst-latency.md)

这个顺序不是按协议字段展开，而是按建模依赖展开。先判断连接关系，再定义一次访问的生命周期，然后讨论多笔访问共享资源时的约束，最后把位宽、频率、burst 和 latency 放进同一个时间模型。

## 四个基础判断

第一，互连选型从连接关系开始。Point-to-point 适合固定专线，BUS 适合共享地址和事务语义，NoC 适合大规模分布式通信。这个边界能防止把固定 accelerator 内部流水建成完整 BUS，也能防止把高并发 tile 数据面压成单共享仲裁点。

第二，transaction 不是“地址 + 数据”的二元组，而是一段生命周期。地址决定路由和合法性，控制属性决定处理规则，数据阶段消耗带宽，response 证明事务闭环。`request accepted` 和 `transaction completed` 之间的时间差，是 outstanding、timeout、backpressure 和性能尾部问题的共同起点。

第三，共享系统必须显式定义仲裁、顺序性和 backpressure。仲裁决定谁先获得资源，顺序性决定哪些完成结果可以先被看见，backpressure 决定下游压力如何传回上游。三者组合后，平均带宽充足的系统仍可能出现尾延迟、starvation、hang 或软件可见性错误。

第四，位宽、时钟和 burst 只给出服务能力，不自动等于有效吞吐。位宽决定每个 beat 承载多少 byte，频率决定每秒有多少服务窗口，burst 决定固定开销如何被 payload 平摊；真实延迟还要扣除仲裁等待、CDC、width adapter、边界拆分、response 和排队时间。

## 和后续章节的关系

03 章会把这些基础对象落到具体片上协议族里。读 AXI 五通道时，要带着“地址、数据、响应为什么分离”的问题；读 ID/outstanding 时，要带着“response 如何匹配 request”的问题；读 burst、WSTRB 和 response error 时，要带着“transaction 生命周期如何被拆分和闭合”的问题。

04 章会把这些对象放进实现结构。decoder、arbiter、crossbar、bridge、FIFO、CDC 和 width adapter，不是孤立组件，而是在实现本章定义的路由、仲裁、顺序、回压和时序适配。

05 章会把这些对象转成性能和调试口径。带宽、延迟、利用率、拥塞、QoS、timeout、fault 和 waveform debug，核心都是在追踪 transaction 从请求被接受到 completion 被消费之间，卡在了哪个资源、哪个队列、哪条顺序边或哪段 backpressure 链上。

06 章会用系统案例检验这些判断。MCU、SoC、AI 芯片和 AXI crossbar 的差异，不只是协议名字不同，而是连接规模、共享语义、事务能力、仲裁压力和时序参数的组合不同。

## 常见误解

- “BUS、NoC、point-to-point 是性能等级”：它们是不同约束下的组织方式，不是代际替换关系。
- “一次访问就是发地址拿数据”：一次访问至少要区分请求头、payload、completion 和 completion consumption。
- “平均带宽够就不会堵”：仲裁粒度、顺序约束和 backpressure 传播会把问题集中到尾延迟和 forward progress 上。
- “位宽和频率越大越好”：更宽和更快会带来布线、时序、adapter、CDC 和固定延迟代价。

## 一句话总纲

BUS 的复杂度不在“连线数量”，而在连接关系、transaction 生命周期、共享资源约束和时序粒度这些规则如何共同决定访问能否闭环、能否并行、会在哪里排队。

## 建模启示

02 章给性能模型和功能模型提供最小状态集合。性能模型至少要记录端点连接关系、目标地址、读写方向、payload size、burst beat、固定开销、仲裁点、outstanding slot、顺序约束、FIFO/credit/backpressure、response 返回时间。功能模型还要保留地址合法性、访问属性、byte enable/strobe、错误响应和可见顺序。

不要用“BUS/NoC/AXI/APB”这些名字直接推出行为。名字只能提供默认假设，真正决定模型的是连接关系、事务拆分、共享资源和时序参数。一个 AXI 路径可能被低速 slave 或 bridge FIFO 限住；一个简单 point-to-point 专线可能比复杂 fabric 更适合固定低延迟数据流；一个 NoC 边缘的 MMIO 访问仍然需要软件可见 completion。

本章结束后，读者应该能把一次访问拆成事件，把一条路径拆成资源，把一个性能现象拆成排队、顺序或回压问题。做到这一步，再进入 03 章协议细节，字段和通道才会变成有意义的设计选择，而不是孤立术语。
