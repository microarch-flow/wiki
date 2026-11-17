# 一致性与内存互连专题补齐记录

日期：2026-11-17。实施前基线：`3679e85974340afd1690b9d5e330c85df21f0d52`。

## 范围与职责

按确认方案将两页框架补齐为六章、28 页：专题导读一页、章节导读六页、正文和查阅文章二十一页。现有两页扩充，新增二十六页。没有移动既有文章，没有改写相邻专题正文。

基础概念定义权限、数据值、内存顺序和作用域；协议与控制器解释 MSI、状态扩展、目录、竞争和前进；CHI 展开真实接口的节点、事务与信用；CXL 展开地址、缓存方向、池化共享与 Linux；性能与可靠性连接流量、并发、故障和容量退出；查阅与验证维护术语、证据和调试方法。

NoC 的消息承载和字节跳数、PCIe 的 I/O 事务、DMA 的软件 API、CHI C2C 的封装承载以及存储系统的数据放置策略均通过链接复用。

## 技术基线与边界

- 基础协议采用显式定义的教学用目录式写失效模型；MSI 消息名不冒充 CHI 操作码。
- CHI 固定 IHI 0050E.b，核查 ReadShared 的 DMT/DCT 示例、CompAck 和 RetryAck/PCrdGrant 依赖；不声称涵盖后续规范全部扩展。
- CXL 区分 io/cache/mem 的访问方向、设备类型、HDM 地址路径、2.0 池化与 3.0 增强共享及 BI，并列出 3.x/4.0 的版本边界。
- Linux 内存接入固定 6.16 文档基线；没有开展真实 CXL 硬件或 cxl-cli 容量修改实验。
- 数值均为带条件的构造算例，不是产品测量。没有声称完成协议形式化证明或硬件合规验证。

## 兼容与导航

保留 `COHERENCE/wiki/` 与 `COHERENCE/wiki/cxl-host-memory/`，保留原有八个锚点。第四章沿用旧 CXL 文件作为章节导读，通过 MkDocs Page 的导航角色识别为章节首页，不改变 File 路径和 canonical URL。

各章阅读列表维护文章顺序与短标题。构建拒绝未列入阅读列表的页面。新增三张仓内 SVG，避免运行时 Mermaid 未渲染时暴露图源码；图中箭头、状态和正文同步核查。

## 本地验证

- `python website/prepare.py` 与 `mkdocs build --strict`。
- 全站 60 项 unittest：包含 28 页搜索标题、导航顺序、归属、面包屑、canonical URL、源码生成链接、图形资源及旧锚点。
- 1440 × 1000 与 390 × 844 浏览器检查覆盖全部 28 页：无整页横向溢出，当前导航项唯一，图形加载正常；另人工检查首页、三张图、手机菜单和表格。
- 独立复算：目录位图 128 MiB；二路交织四组地址；64 个在途请求、64 B、300 ns 对应约 13.65 GB/s；假设 32 GB/s 时需要平均 150 个在途请求。
- 四事件完成条件练习枚举 24 种顺序；验证范围仅限该谓词，不外推为 MSI 完整证明。
- 原有 18 个未跟踪文件建立 SHA-256 基线，提交前复核。构建产物和临时验收文件不加入版本控制。

公开部署及线上验收结果以本次交付说明中的提交和 GitHub Actions 链接为准。

## 页面清单

- [基础概念：先确定一致性保证的对象](../../series/interconnect/COHERENCE/01-foundations/README.md)
- [缓存一致性、内存顺序与原子性：分别保证什么？](../../series/interconnect/COHERENCE/01-foundations/coherence-consistency-atomicity.md)
- [一致性域与 I/O：谁参与副本协调？](../../series/interconnect/COHERENCE/01-foundations/coherence-domains-and-io.md)
- [缓存一致性要保持什么约束？](../../series/interconnect/COHERENCE/01-foundations/coherence-invariants.md)
- [协议与控制器：把权限规则变成执行过程](../../series/interconnect/COHERENCE/02-protocols/README.md)
- [目录、Home 与 Snoop Filter：谁知道缓存行在哪里？](../../series/interconnect/COHERENCE/02-protocols/directory-snoop-filter.md)
- [一致性事务如何保证前进？](../../series/interconnect/COHERENCE/02-protocols/forward-progress.md)
- [MESI 与 MOESI：增加状态解决了什么问题？](../../series/interconnect/COHERENCE/02-protocols/mesi-moesi-extensions.md)
- [用 MSI 走完读写事务：数据和权限怎样转移？](../../series/interconnect/COHERENCE/02-protocols/msi-transactions.md)
- [瞬态状态与并发竞争：收到数据以后，还在等什么？](../../series/interconnect/COHERENCE/02-protocols/transient-states-and-races.md)
- [CHI：从节点职责到事务完成](../../series/interconnect/COHERENCE/03-chi/README.md)
- [CHI 的流控、重试与完成：三种“可以继续”](../../series/interconnect/COHERENCE/03-chi/chi-flow-control-retry-completion.md)
- [CHI 节点与通道：把协议角色放到访问路径中](../../series/interconnect/COHERENCE/03-chi/chi-nodes-and-channels.md)
- [CHI 的读取与写权限：数据到达和事务完成怎样区分？](../../series/interconnect/COHERENCE/03-chi/chi-read-and-ownership.md)
- [CXL.cache 与设备内存：两个方向的一致性](../../series/interconnect/COHERENCE/04-cxl/cxl-cache-and-device-memory.md)
- [Linux CXL：从发现设备到应用可用内存](../../series/interconnect/COHERENCE/04-cxl/cxl-linux-regions-and-memory.md)
- [内存扩展、池化与共享：容量怎样分配，数据怎样协调？](../../series/interconnect/COHERENCE/04-cxl/cxl-pooling-sharing-fabric.md)
- [Type 3 内存访问：从主机地址到设备地址](../../series/interconnect/COHERENCE/04-cxl/cxl-type3-address-path.md)
- [性能与可靠性：从访问过程到系统代价](../../series/interconnect/COHERENCE/05-performance-reliability/README.md)
- [共享、伪共享与一致性流量：程序改了几个字节，网络搬了多少？](../../series/interconnect/COHERENCE/05-performance-reliability/coherence-traffic-and-false-sharing.md)
- [CXL 延迟、带宽与数据放置：为什么线速率不能预测应用性能？](../../series/interconnect/COHERENCE/05-performance-reliability/cxl-latency-bandwidth-and-placement.md)
- [内存错误、复位与容量移除：数据何时仍然可用？](../../series/interconnect/COHERENCE/05-performance-reliability/memory-errors-and-lifecycle.md)
- [查阅与验证：把理解变成可检查的结论](../../series/interconnect/COHERENCE/06-reference/README.md)
- [设计与调试检查表：把现象转换为可验证的问题](../../series/interconnect/COHERENCE/06-reference/design-debug-checklist.md)
- [术语、版本与一手资料：怎样追溯本专题的结论？](../../series/interconnect/COHERENCE/06-reference/glossary-and-sources.md)
- [一致性模型怎样验证：从可检查状态到竞争反例](../../series/interconnect/COHERENCE/06-reference/modeling-and-validation.md)
- [一致性与内存互连：缓存副本如何协调，设备内存如何接入？](../../series/interconnect/COHERENCE/README.md)
- [CXL：从设备发现到内存访问](../../series/interconnect/COHERENCE/cxl-host-memory.md)
