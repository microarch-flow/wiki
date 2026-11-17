# 加速器互连专题补齐记录

日期：2026-11-17。实施前基线：`cfdf01ab76ce7cf1c6f92bd5e4831b00b78f58ad`。

## 范围与职责

按确认方案将一页导读补齐为六章、30 页：保留并扩充专题导读，新增六篇章节导读和 23 篇正文。新增三张仓内 SVG。没有移动既有文章，没有改写相邻专题正文。

访问语义定义对象、地址、权限、操作与完成；交换结构解释请求窗口、拓扑、拥塞和失败边界；协议案例分别介绍 UALink 组件、GB200 NVL72 和 MI350X／MI355X；软件章节解释对端访问、NVSHMEM 和通信库；性能章节从并行切分得到通信；最后一章贯通矩阵预算、诊断和资料查阅。

NoC 的集体通信定义、环形归约推导、通信矩阵与信用机制，PCIe 的 P2P 和链路重放，以及一致性、D2D、SerDes、CPO 的基础职责均通过链接复用。推理运行时的 TP 草稿仍保留原状；新专题不采用其“必须节点内 NVLink”作为通用条件。

## 技术依据与限制

关键来源为联盟规范目录、NVIDIA／AMD 官方接口和架构文档、NCCL／RCCL 测试项目及 Megatron、DeepSeek 原始论文。24 个外部链接均通过 HTTP 可访问性检查；可访问性不代替逐条事实核查。

UALink 以 200G 1.0 解释分层，同时区分 Common 2.0、200G DL/PL 2.0、128G DL/PL 1.0、Chiplet 1.01 和 Manageability 1.0。目录信息不冒充完整规范字段或已上市产品认证。

NVLink 数字固定到 GB200 NVL72 第五代接口，明确双向聚合口径；xGMI 固定到指定八 GPU 平台。NCCL、RCCL、CUDA、HIP、NVSHMEM 的在线文档版本会变化，实际实验须固定安装版本。

所有窗口、TP、MoE、重叠和矩阵数字都是构造算例。本次没有执行 GPU 性能测试、硬件故障注入、互操作认证或形式化协议证明。未公开的设备内部状态机、重试策略与恢复时限仍需产品资料及硬件验证。

## 路径与导航

源码继续位于 `series/interconnect/SCALEUP/`，公开前缀继续为 `SCALEUP/wiki/`。根导读的原标题和三个原小节标题保留，对应四个旧锚点。六个编号目录与侧栏章节对应，各章阅读列表维护顺序及短标题。未改变来源映射，也未引入第二套正文。

## 本地验证

- `python website/prepare.py`、`mkdocs build --strict` 和全站 unittest；最终结果以提交前日志及交付说明为准。
- 增加专题检查，覆盖 30 页、六章阅读列表、源码链接、网页标题、搜索标题、短导航、面包屑、当前项、图形资源和四个旧锚点。
- 浏览器在 1280 × 900 和 390 × 900 下遍历全部 30 页，共 60 组检查：无整页横向溢出、无图片加载失败、均有正文标题。
- 人工检查桌面导读与访问时序图，390 × 844 手机结构图、重叠图、矩阵横向滚动、菜单与当前项。手机 UALink 搜索返回新协议文章。
- 独立复算：64 × 256 B / 1 μs = 16.384 GB/s；100 GB/s × 1 μs 的窗口需要至少 391 个 256 B 请求；TP 示例为 36.70016 μs 纯序列化预算；MoE 逻辑分发为 16 MiB；AllReduce 示例 busbw 为 117.440512 GB/s；矩阵跨域与端点下界分别为 2.9296875 ms 和 0.9765625 ms。
- 原有 18 个未跟踪文件按 SHA-256 基线检查，内容保持不变。临时脚本、构建产物和验收日志不加入提交。

公开部署及线上验收结果以交付说明中的提交和 Actions 链接为准。

## 页面清单

- [01 访问语义](../../series/interconnect/SCALEUP/01-access-semantics/README.md)
- [远端地址、映射与权限：怎样让对端资源可访问](../../series/interconnect/SCALEUP/01-access-semantics/address-mapping-and-permissions.md)
- [加速器互连的对象与边界：先确定谁与谁通信](../../series/interconnect/SCALEUP/01-access-semantics/objects-and-domains.md)
- [读写、原子操作与完成：哪些事件允许继续执行](../../series/interconnect/SCALEUP/01-access-semantics/operations-ordering-and-completion.md)
- [02 交换结构](../../series/interconnect/SCALEUP/02-fabric-architecture/README.md)
- [背压与拥塞：缓冲不溢出以后，请求能否继续前进](../../series/interconnect/SCALEUP/02-fabric-architecture/backpressure-and-progress.md)
- [一次远端读取：请求、返回和在途状态怎样配合](../../series/interconnect/SCALEUP/02-fabric-architecture/remote-read-path.md)
- [链路重试与事务失败：恢复了传输，是否恢复了操作](../../series/interconnect/SCALEUP/02-fabric-architecture/retry-and-failure.md)
- [直连与交换：怎样计算可供任务使用的带宽](../../series/interconnect/SCALEUP/02-fabric-architecture/topology-and-bandwidth.md)
- [03 协议与系统案例](../../series/interconnect/SCALEUP/03-protocols-and-systems/README.md)
- [AMD xGMI：八 GPU 直连系统怎样分配链路](../../series/interconnect/SCALEUP/03-protocols-and-systems/amd-xgmi.md)
- [NVLink 与 NVSwitch：从 GPU 链路到机架通信域](../../series/interconnect/SCALEUP/03-protocols-and-systems/nvlink-nvswitch.md)
- [UALink 200G 1.0：一次内存事务怎样穿过协议栈](../../series/interconnect/SCALEUP/03-protocols-and-systems/ualink-200g-transactions.md)
- [UALink 规范组件：Common、DL/PL 与系统管理怎样分工](../../series/interconnect/SCALEUP/03-protocols-and-systems/ualink-specification-family.md)
- [04 软件与集体通信](../../series/interconnect/SCALEUP/04-software-and-collectives/README.md)
- [集体通信怎样映射到链路、分块和交换归约](../../series/interconnect/SCALEUP/04-software-and-collectives/collective-mapping-and-offload.md)
- [GPU 发起通信：数据传输、通知和等待怎样配合](../../series/interconnect/SCALEUP/04-software-and-collectives/gpu-initiated-communication.md)
- [NCCL 与 RCCL：通信组、执行依赖和底层路径怎样连接](../../series/interconnect/SCALEUP/04-software-and-collectives/nccl-rccl-contracts.md)
- [CUDA 与 HIP 对端访问：先查询能力，再建立有效路径](../../series/interconnect/SCALEUP/04-software-and-collectives/peer-access-setup.md)
- [05 负载与性能](../../series/interconnect/SCALEUP/05-workloads-and-performance/README.md)
- [多卡通信怎样测试：正确性、路径和计时边界一起记录](../../series/interconnect/SCALEUP/05-workloads-and-performance/benchmarking.md)
- [带宽与时延指标：先统一字节、方向和观察边界](../../series/interconnect/SCALEUP/05-workloads-and-performance/metrics-and-units.md)
- [MoE 分发与回收：平均流量为何掩盖热点](../../series/interconnect/SCALEUP/05-workloads-and-performance/moe-dispatch-and-combine.md)
- [通信与计算重叠：怎样计算没有被隐藏的时间](../../series/interconnect/SCALEUP/05-workloads-and-performance/overlap-and-critical-path.md)
- [TP、PP、DP：从计算切分得到通信事件](../../series/interconnect/SCALEUP/05-workloads-and-performance/parallelism-traffic.md)
- [06 建模、诊断与查阅](../../series/interconnect/SCALEUP/06-modeling-and-reference/README.md)
- [多卡通信异常定位：先找失败边界，再改变配置](../../series/interconnect/SCALEUP/06-modeling-and-reference/diagnosis-and-recovery.md)
- [加速器互连术语、版本与一手资料](../../series/interconnect/SCALEUP/06-modeling-and-reference/glossary-and-sources.md)
- [从通信矩阵到性能下界：一个四端点预算例子](../../series/interconnect/SCALEUP/06-modeling-and-reference/traffic-budget-example.md)
- [加速器互连：多颗加速器怎样访问对端资源？](../../series/interconnect/SCALEUP/README.md)
