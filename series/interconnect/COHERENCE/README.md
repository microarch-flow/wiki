# 一致性与内存互连：缓存副本如何协调，设备内存如何接入？

<span id="一致性与内存互连谁持有最新的缓存行"></span>

多个处理器或设备共享数据时，缓存减少了重复访问，也引入了副本和权限管理。设备内存接入以后，还要解决地址映射、协议选择和软件资源管理。本专题分六章，分别从缓存副本的协调和设备内存的接入讲起。

## 从一次写入看职责

假设 A、B 都缓存了同一行，A 要修改它。A 先请求写权限，协调节点处理冲突副本，所需响应完成后 A 才能写入。最新值可以留在缓存中，不必立即写回 DRAM，但协议必须持续跟踪数据责任。

从[《内存里还是 0，为什么 B 能读到 A 写的 1？》](01-foundations/coherence-invariants.md)跟着两份副本逐步看：B 在什么时候失去旧副本的读权限，A 在什么时候可以写，B 再读时数据从哪里回来。再把场景扩大到两个地址，讨论[内存顺序与原子性](01-foundations/coherence-consistency-atomicity.md)。

| 层次 | 本专题要回答的问题 | 相邻专题的主要职责 |
| --- | --- | --- |
| 语义 | 谁可以读写，读到什么值？ | 内存访问与软件同步的具体使用接口 |
| 控制器 | 怎样取得权限、保存脏数据、结束事务？ | 缓存阵列及存储器件实现 |
| CHI / CXL | 真实接口怎样表达访问与协调？ | NoC 传输、PCIe I/O、封装链路 |
| 系统接入 | 设备地址怎样成为可用内存？ | 存储层次规划与数据放置策略 |

## 一致性与 CXL 的关系

CHI 用于描述一致性接口事务；CXL 组织主机与设备之间的 I/O、缓存和内存访问。它们不是同一协议的两个名称，也不意味着所有参与者自动属于同一个一致性域。

主机缓存设备内存，与设备缓存主机内存，是不同方向。CXL 的协议、设备类型、内存模式和软件配置共同决定实际路径，见[CXL 内存访问](cxl-host-memory.md)。

## 阅读顺序

1. [01 基础概念](01-foundations/README.md)：MSI 的值与权限、内存顺序和一致性域。
2. [02 协议与控制器](02-protocols/README.md)：状态扩展、目录、竞争和前进。
3. [03 CHI](03-chi/README.md)：节点、事务、信用和完成。
4. [04 CXL 内存访问](cxl-host-memory.md)：地址映射、设备缓存、池化共享和 Linux 接入。
5. [05 性能与可靠性](05-performance-reliability/README.md)：共享流量、并发带宽、错误和容量生命周期。
6. [06 查阅与验证](06-reference/README.md)：术语、资料、模型检查和调试。

第一次学习建议先读前两章，再分别进入 CHI 或 CXL。关注内存扩展的读者可在第一章后先读 CXL，遇到权限与探查问题再回第二章。CHI 不是 CXL 的必修前置章节。

## 与其他专题怎么配合

- [BUS 的一致性路径概览](../BUS/03-on-chip-protocol-families/coherent-bus-vs-noncoherent-bus.md)解释接口边界；这里展开权限和控制器。
- [NoC 的一致性流量案例](../NOC/07-workload-cases/coherent-access-and-noc.md)统计消息传输；这里解释消息为什么产生。
- [PCIe 与 CXL 的边界](../PCIE/07-advanced-topics/cxl-and-pcie-boundary.md)解释链路与 I/O 背景；这里展开设备内存访问。
- [CHI C2C](../D2D/02-interfaces/chi-c2c.md)解释跨 die 承载；这里解释 CHI 基本事务。
- [存储系统集成](../../storage/06-system-integration/future-packaging-cxl-near-memory.md)讨论数据放置；这里提供协议与配置条件。

本专题用[资料与版本页](06-reference/glossary-and-sources.md)区分规范、教学模型和实现。构造算例不是产品实测，模型检查也不等于完整硬件合规验证。
