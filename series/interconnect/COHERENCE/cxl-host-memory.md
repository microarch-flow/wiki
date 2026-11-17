# CXL：从设备发现到内存访问

<!-- nav-title: 04 CXL 内存访问 -->

CXL（Compute Express Link）把 I/O、缓存和内存访问协议组织在同一系统互连体系中。读懂一条路径时，先确认内存在哪里、谁发起访问、谁缓存数据，再检查设备类型、拓扑和软件配置。

本页是第四章导读。先读过[基础概念](01-foundations/README.md)即可进入本章，不要求先掌握 CHI。

## 三类协议各做什么

| 协议 | 基本职责 | 阅读时要区分的路径 |
| --- | --- | --- |
| CXL.io | 发现、配置、寄存器访问等 I/O 功能 | 管理设备不等于已经配置好设备内存 |
| CXL.cache | 设备一致性访问并缓存主机内存 | 设备保存主机数据的副本 |
| CXL.mem | 主机访问设备内存，支持相应缓存与协调语义 | 主机保存设备数据的副本 |

Type 1 支持 io 与 cache，Type 2 支持三类子协议，Type 3 支持 io 与 mem。更复杂事务方向和模式需要按版本核查；这张表不是所有事务的完整清单。基础定义见 [Linux CXL 设备与协议文档](https://docs.kernel.org/driver-api/cxl/devices/device-types.html)。

## 一次内存扩展访问

假设 Type 3 设备已就绪，主机完成地址与内存资源配置。应用访问该区域，CPU 经过地址转换并查询缓存。若请求需要访问设备内存，主机依据地址路由到设备，端点把主机地址转换为设备地址，设备内存控制器返回数据。

这条路径需要分别回答“访问去哪里”和“软件何时可以使用”。前者由窗口、decoder 和设备内存映射决定，后者还涉及 region、DAX 或 System RAM 的接入。[地址路径](04-cxl/cxl-type3-address-path.md)与 [Linux 路径](04-cxl/cxl-linux-regions-and-memory.md)分别展开。

## 扩展、池化与共享

扩展增加容量，池化管理容量分配，共享允许多个参与者访问同一数据区域。共享能力及其一致性条件不能从“有交换机”推导出来，也不能把 CXL 2.0 的分配约束推广成所有后续版本的限制。

本章用 2.0 解释池化边界，以 3.0 说明增强共享与 Back-Invalidate，并指出 3.x、4.0 的能力需要按具体配置核查。Linux 接入路径固定采用 6.16 文档基线；规范能力和软件支持不是一回事。

## 阅读顺序

1. [Type 3 地址路径](04-cxl/cxl-type3-address-path.md)：HPA、DPA 与交织。
2. [缓存方向与设备内存](04-cxl/cxl-cache-and-device-memory.md)：CXL.cache、CXL.mem 与探查。
3. [池化、共享与 Fabric](04-cxl/cxl-pooling-sharing-fabric.md)：分配、同时访问和管理面。
4. [Linux 内存接入](04-cxl/cxl-linux-regions-and-memory.md)：从发现设备到应用使用。

性能分析继续读[CXL 延迟、带宽与放置](05-performance-reliability/cxl-latency-bandwidth-and-placement.md)。PCIe 背景见[两者的边界](../PCIE/07-advanced-topics/cxl-and-pcie-boundary.md)；系统层选型见[存储集成文章](../../storage/06-system-integration/future-packaging-cxl-near-memory.md)。
