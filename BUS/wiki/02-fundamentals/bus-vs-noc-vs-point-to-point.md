# BUS vs NoC vs Point-to-Point

上级：[02 基础对象与事务语义](./README.md)

相关：[BUS 在解决什么问题](../01-overview/problem-statement.md)、[BUS 分类框架](../01-overview/taxonomy.md)、[NoC Wiki 首页](../../../NOC/wiki/README.md)、[PCIE Wiki: PCIE vs AXI / NoC：边界与分工](../../../PCIE/wiki/06-workloads-case-studies/pcie-vs-axi-noc-boundary.md)

## 这页在回答什么问题

为什么 BUS、NoC 和 point-to-point 都能被叫作“互连”，但它们解决的约束不同，不能按“谁更高级”来排序。

## 三者的分界不是线多线少

想象你要解决三种不同的通信需求：

- **给隔壁同事递文件**：你直接走过去交给他就行。这就是 **Point-to-point**——一个发起端和一个接收端直接连起来。简单、快速、可预测。但如果突然有第三个人也要这份文件，你就得多跑一趟或者找人帮忙转交。
- **公司内部的收发室**：十个部门都需要寄文件、领物资，统一交给收发室调度。这就是 **BUS**——多个 master 对多个 slave 的访问被组织成 transaction。收发室负责登记（地址）、排队（仲裁）、送达确认（响应）和纠错（错误处理）。它不一定只有一个窗口；可以有多个窗口（crossbar）、分层柜台（bridge）。
- **全国快递网络**：当节点多到几十上百、分布在芯片各个角落时，一个收发室忙不过来了。这就是 **NoC**——用分布式的中转站（router）和线路（link）组成网络，每个包裹被切成小份（flit），沿着路由跳转。扩展性强，但端到端延迟更难预测，死锁、QoS 和 buffer sizing 都成了新问题。

所以这三者不是”谁更高级”的代际替换关系，而是不同规模下的最优解。一个 SoC 可以同时用 point-to-point 做局部专线（递文件），用 BUS 做控制和事务骨架（收发室），用 NoC 做大规模数据交换（快递网络）。

## Point-to-Point 适合固定关系

Point-to-point 就像两栋楼之间的**专用天桥**——只连接固定的两端，没有红绿灯、没有岔路口、不用排队。两个模块之间的带宽、时序和协议语义都可以量身定制：producer 到 consumer 的 streaming path、固定 DSP pipeline、一个 controller 到专用 SRAM，都可以不引入全局地址 decode 和复杂仲裁。

它的设计交易很明确：用低通用性换低延迟、低面积和可预测行为。只要天桥两端的用户不变，就不需要回答”第三栋楼的人怎么过来””回程怎么走””多个目的地怎么选”这些问题。

问题会在需求变化时出现。一个本地 SRAM 如果后来既要被 CPU 配置，又要被 DMA 搬运，又要被 debug master 访问——就像天桥突然要服务三栋楼——点到点连接就会开始堆 mux、arbiter 和地址窗口。此时它已经在向 BUS 的问题域移动，只是没有显式承认自己需要事务组织层。

容易误解：点到点一定低级。实际上，在固定低延迟路径中，点到点可以是性能最强的局部专线——专用天桥比挤公交快得多；它不弱，只是不负责共享访问和软件可见地址空间。

## BUS 适合共享事务语义

BUS 就像**公司的收发室**——它的强项是把多人共享的访问变成有序的、可追踪的事务。CPU、DMA、debug master、外设控制器都要访问同一批 memory-mapped slave，就像十个部门都要用收发室寄件收件。系统需要统一编号（地址空间）、验证身份（权限）、排队（仲裁）、送达确认（响应）、退件处理（错误）和超时提醒（timeout）。

这也是 BUS 长期存在的原因——只要有”多人共享”的场景，就需要规则。点到点链路就像同事之间直接递文件，很快，但没有追踪记录；NoC 就像快递网络，能承载更大规模通信，但最终包裹到了你手上，你还是需要一个签收确认（事务语义）。

BUS 的代价来自集中管理。收发室让一切有序，但所有人都得排队过同一个窗口。master/slave 数量上升后，单窗口会变成瓶颈；多窗口（crossbar/matrix）可以释放并行度，但柜台、场地和人员成本也随之上升。

容易误解：BUS 就是低性能共享线。实际上，BUS 是事务语义的组织方式；收发室可以小到一个人一张桌（APB），也可以大到一整层楼的自动分拣系统（AXI crossbar），差异来自系统角色和并发压力。

## NoC 适合大规模空间分布

NoC 就像**全国高铁网络**——当城市（节点）数量多、距离大、人流分布在多个区域时，继续扩建单一的中央火车站（集中 fabric）会遇到站台不够、轨道塞满、调度崩溃的问题。NoC 用分布式的车站（router）和轨道（link）把全局调度拆成一站一站的局部转发。

这种拆分换来可扩展性，也引入新的复杂度。一个包裹（packet）会被切成小件（flit），经过多个中转站，受车次（virtual channel）、车票（credit）、候车室容量（buffer）和线路规划（routing policy）影响。一趟旅程的延迟不再只由一个车站决定，而是由每一站的换乘等待、路线选择、下一站座位余量和终点服务共同决定。

NoC 更适合大规模数据面，不代表它只搬”无语义数据”。AI tile 间 activation 交换、DMA 到 HBM、SRAM bank 间数据搬运，都可能需要 NoC。区别在于 NoC 的核心问题变成分布式运输和流控，而不是单一收发室里的事务管理。

一个实用边界是：当收发室（bus matrix/crossbar）的窗口数、长距离走廊、统一排班已经成为主要成本负担，而流量又能被拆成多个区域的局部转发时，NoC 才开始比继续扩大收发室更有吸引力。若部门数量有限、访问仍围绕少数 memory-mapped slave，matrix 或 crossbar 可能仍是更低成本的答案。

容易误解：有高铁就不需要公交了。实际上，在 NoC 系统中，边缘仍需要 BUS/MMIO 风格接口来完成配置、状态读取、doorbell、interrupt 和 debug——高铁站里也得有出租车和公交接驳。NoC 负责大规模传输，BUS 负责软件可见事务边界。

## 选型要看三类约束

**第一类：你要连谁？** 固定的一对一关系（同事之间递文件），point-to-point 更直接。多个部门共用资源（收发室场景），BUS 的事务语义更合适。几十上百个节点分布在各处（全国物流），NoC 才开始体现价值。

**第二类：软件需不需要看到？** 如果访问对象是寄存器、状态位、doorbell、interrupt controller——软件需要清楚地知道"我写了什么地址、成功没有、出了什么错"——BUS 更容易表达（就像收发室有签收单）。如果通信主要是编译器调度的数据流、tile 间消息或大块数据搬运，NoC 或专用链路可以把软件语义放在更高层（就像快递网络的内部中转对发件人透明）。

**第三类：扩展到什么规模会变贵？** Point-to-point 就像专线——两条没问题，二十条就满地是线；BUS 就像收发室——五个部门很轻松，五十个部门就要排长队；NoC 就像路网——每多一个站点就要多建路由器、缓冲区和防死锁机制。没有一种方式免费扩展，只是成本曲线不同。

一个 SoC 内部分工可以写成这个构造示例：

| 路径 | 更自然的组织 | 主约束 | 主要风险 |
|---|---|---|---|
| CPU 配置外设寄存器 | BUS | 软件可见地址和错误语义 | 低速外设拖慢控制路径 |
| DMA 搬运连续内存块 | BUS / NoC | 持续带宽和 outstanding | 长 burst 压制短请求 |
| AI tile 间 activation 交换 | NoC | 多节点并发和空间分布 | credit、buffer、热点和死锁 |
| 固定 accelerator 内部流水 | Point-to-point | 低延迟和固定带宽 | 后续共享需求导致重构 |
| Debug / boot 可达性 | BUS / 简单专线 | 初始化前可访问 | 依赖复杂 fabric 导致 bring-up 困难 |

这张表不是选型规则表，而是提醒：同一芯片里不同路径可以有不同答案。把所有通信统一成一种互连，会让低复杂度路径承担过度设计成本，也会让高并发路径缺少扩展空间。

## 和板级 I/O 互连的边界

BUS、NoC 和 point-to-point 在这里讨论的是片内连接。它们关注的是 SoC 内部 agent、slave、地址空间、事务响应、片上流控和微架构实现。

如果问题变成 host 与 device 之间的板级或封装外 I/O，例如 PCIe endpoint、CXL device、NVMe、NIC、GPU 与 CPU host 的连接，核心约束就会变成链路训练、packet/TLP、枚举、BAR、DMA、cache coherency 或 I/O memory model。此时应该切到 [PCIE Wiki](../../../PCIE/wiki/README.md) 或对应 I/O 互连视角，而不是把片内 BUS 经验直接套过去。

## 一句话理解

Point-to-point 解决固定专线问题，BUS 解决共享地址和事务语义问题，NoC 解决大规模分布式通信问题；三者不是谁替代谁，而是在同一系统里承担不同约束。

## 建模启示

建模时不要先问“这是 BUS 还是 NoC”，而要先记录连接关系：端点数量、是否共享目标、是否需要统一地址空间、是否有返回匹配、是否存在多跳路径、是否需要软件可见 completion。连接关系决定模型里要放 mux、arbiter、queue、router、credit，还是简单 service edge。

Point-to-point 模型可以压得很轻：在固定端点、固定服务路径和局部流控条件下，固定 latency、固定吞吐、局部 backpressure、少量 buffer 就能表达主要行为。只要没有共享目标和可变路由，就不需要引入全局仲裁和 response matching。

BUS 模型至少要保留 transaction 状态：address decode、仲裁点、burst beat、outstanding、ordering、response 和 backpressure。它的性能风险来自共享资源和事务闭环之间的等待时间。

NoC 模型必须显式保留网络状态：packet/flit、router pipeline、link 带宽、buffer/credit、routing policy、virtual channel 或 deadlock avoidance 约束。它的性能风险来自每跳争用、热点、路径选择和分布式流控。

最危险的简化是用名称替代约束。例如把 NoC 边缘的 MMIO 配置路径当作普通数据包流，会丢掉软件可见 completion；把一个固定 accelerator 内部专线建成完整 BUS，会把模型复杂度放错地方；把高并发 tile 数据面压成单共享 BUS，会低估热点、路径和多跳 backpressure。
