# 术语、版本与一手资料：怎样追溯本专题的结论？

同一中文词可能对应不同英文概念，同一协议名称也可能跨多个版本。查资料时，应把术语、版本和被验证的结论一起记录。

## 核心术语

| 本专题用语 | 英文 | 判断依据 |
| --- | --- | --- |
| 缓存一致性 | Cache coherence | 副本、权限及同一位置的数据历史 |
| 内存一致性模型 | Memory consistency model | 程序允许的内存观察结果 |
| 一致性域 | Coherence domain | 哪些参与者和访问受同一保证覆盖 |
| 归属节点 | Home node | 对该地址协调事务，不等于数据必经点 |
| 所有者 | Owner | 具体协议定义的数据或权限责任 |
| 共享者 | Sharer | 持有共享副本的参与者 |
| 探查 | Snoop | 请求缓存报告或改变副本状态 |
| 瞬态状态 | Transient state | 事务尚有未完成义务的状态 |
| 主机管理的设备内存 | HDM | 主机可按配置访问的设备内存 |
| 主机／设备物理地址 | HPA / DPA | 主机侧路由地址／设备内部地址 |
| 内存区域 | CXL region | Linux 中绑定地址范围与交织目标的对象 |

Owner 不统一译成“写入者”，因为脏共享等协议中 owner 未必有独占写权限。Coherence 与 consistency 首次出现时保留英文，后文分别用“缓存一致性”和“内存一致性模型”。

## 本专题采用的资料基线

| 内容 | 主要资料 | 使用方式 |
| --- | --- | --- |
| 权限约束与模型边界 | [Primer 第二版，2020](https://pages.cs.wisc.edu/~markhill/papers/primer2020_2nd_edition.pdf) | 基础概念；本文另行定义教学模型 |
| MSI 控制器 | [gem5 Ruby MSI 教程](https://www.gem5.org/documentation/learning_gem5/part3/cache-intro/) | 阅读状态、事件和队列，不宣称本文等于该代码 |
| CHI 事务 | [Arm IHI 0050E.b](https://documentation-service.arm.com/static/6295e03db334256d9ea8ae86) | 固定版本核对事务、完成、重试与信用 |
| CHI 仿真实现 | [gem5 CHI](https://www.gem5.org/documentation/general_docs/ruby/CHI/) | 同时阅读其规范差异和未实现功能 |
| CXL 基本事务与 BI | [CXL 3.0 规范](https://computeexpresslink.org/wp-content/uploads/2024/02/CXL-3.0-Specification.pdf) | 特别区分设备类型、内存模式和事务方向 |
| CXL 版本演进 | [官方规范入口](https://computeexpresslink.org/cxl-specification/) | 查询目标版本，不以最新版本替代已安装能力 |
| Linux CXL 对象 | [Linux 6.16 驱动文档](https://docs.kernel.org/6.16/driver-api/cxl/linux/cxl-driver.html) | 固定内核文档基线；不等于已在硬件上运行 |
| CXL 管理工具 | [NDCTL/CXL 工具手册](https://docs.pmem.io/ndctl-user-guide/cxl-man-pages/cxl-list-1) | 实验时另记工具版本与命令输出 |

资料核查日期：2026-11-17。CHI E.b 和 Linux 6.16 是本专题的教学基线，不声称它们是最新版本。CXL 章节显式区分 2.0、3.x、4.0；最新规范能力与实际系统支持范围必须分别检查。

## 哪些内容是构造示例

A、B、H 的 MSI 流程、目录位图容量、二路地址交织、64 B 伪共享和并发带宽算例均由文章明确给出假设。它们用于解释因果关系，不是某个产品的实测或完整实现。

本专题没有宣称完成 CHI 合规验证、CXL 硬件实验或缓存协议形式化证明。需要把文章用于 RTL、模拟器或驱动实现时，继续核对所选版本的字段、异常路径、资源依赖和平台限制。

资料冲突时，先比较版本、设备类型、内存模式和访问方向；再区分规范允许、实现选择、软件支持和实验结果。不要把这四类证据合成一句“支持 CXL”。
