# DDR/IOMMU/Debug 集成清单

上级：[07 术语与检查清单](./README.md)

相关：[AXI 到 DDR Controller 的路径](../04-microarchitecture-integration/axi-to-ddr-controller-path.md)、[IOMMU、SMMU 与 DMA 寻址](../04-microarchitecture-integration/iommu-smmu-dma-addressing.md)、[Debug Path 与 System Access](../04-microarchitecture-integration/debug-path-system-access.md)

## 使用方式

DDR controller、IOMMU/SMMU、debug path 都不是挂在 BUS 旁边的附件。它们会改变事务延迟、错误归因、软件可见性和故障恢复能力。评审时要把三者放进端到端路径，而不是只检查接口连通。

## DDR / Memory Controller

| 检查项 | 要回答的问题 |
| --- | --- |
| address mapping | 地址如何映射到 channel/rank/bank/row/column，是否匹配主要访问模式 |
| request queue | read/write queue 深度、QoS、age limit、starvation bound 是否定义 |
| burst mapping | AXI burst 是否会跨 row/bank/page，是否被 controller 拆分 |
| read/write combine | write drain 是否会拉高关键 read tail latency |
| turnaround | read->write、write->read 切换成本是否进入性能预算 |
| return path | read data buffer、R channel、return arbiter 是否可能成为瓶颈 |
| write completion | B response 的完成点是 controller accept 还是更深层语义 |
| ECC/error | ECC、timeout、training/power 状态错误如何映射到上游 response |
| observability | row hit/miss、queue occupancy、turnaround、return wait 是否可观测 |

## IOMMU / SMMU

| 检查项 | 要回答的问题 |
| --- | --- |
| identity | stream ID、device ID、substream/context 是否和设备/队列匹配 |
| address space | descriptor、source、destination、completion 是否使用正确 IOVA/context |
| permission | read/write、secure、privileged、shareability/cache 属性是否匹配 |
| page walk | page table memory 是否可访问，walk latency 是否在预算内 |
| TLB lifecycle | mapping 更新后 invalidation、drain、completion wait 是否完整 |
| fault record | fault 是否记录 stream、IOVA、type、access、transaction stage |
| fault response | fault 后 DMA 是 error completion、retry、stop channel 还是 interrupt |
| resource release | fault 后 SMMU slot、DMA slot、queue entry 是否释放或冻结到可恢复状态 |
| observability | translation hit/miss、page walk、fault、outstanding age 是否可观测 |

## Debug Path

| 检查项 | 要回答的问题 |
| --- | --- |
| access scope | debug master 能访问哪些 memory/MMIO/debug register，哪些被禁止 |
| auth/security | debug unlock、lifecycle、secure/non-secure、firewall 是否覆盖 debug master |
| boot/reset | CPU 未启动、reset 中、boot 早期 debug path 是否可用 |
| low power | target power off、clock gated、isolation enabled 时访问如何响应 |
| side effect | debug read 是否会触发 MMIO read-clear/FIFO pop/status clear |
| priority/QoS | debug access 会不会干扰 realtime/CPU/DMA 正常流量 |
| failure return | debug 访问失败时是否有独立 error，而不是一起 hang |
| snapshot | 故障时是否能看到 FIFO、last transaction、fault record、timeout source |
| observability | debug link connected 与 system access path ready 是否分开记录 |

## 组合检查

| 组合场景 | 要检查 |
| --- | --- |
| DMA -> SMMU -> DDR | translation miss 是否与 data path 竞争 DDR，fault 是否能生成 completion |
| CPU debug 读 DDR | cache/coherence、权限、DDR power state、return path 是否一致 |
| DDR timeout + debug 取证 | debug 是否绕过故障路径读取 controller/fault 状态 |
| IOMMU fault + interrupt | fault record 是否先于 interrupt 对 CPU 可见 |
| low power wake | debug/BUS access 是否能唤醒目标，或返回可诊断错误 |

## 一句话理解

DDR 决定 memory path 的物理调度，IOMMU/SMMU 决定 DMA path 的身份与权限，debug path 决定系统失败后还能不能看见真相。

## 建模启示

这三类集成点要进入同一端到端模型。DDR 侧事件包括 `ddr_queue_enqueue`、`scheduler_pick`、`read_data_return`、`write_resp_release`；IOMMU 侧事件包括 `context_lookup`、`translation_miss`、`page_walk_done`、`iommu_fault_record`；debug 侧事件包括 `debug_auth_passed`、`debug_request_issue`、`target_domain_ready`、`debug_error_return`。

性能模型要把 DDR queue、SMMU translation queue、debug access latency 与主业务流量放在一起；功能模型要把 fault、timeout、power/reset、安全权限和 resource release 放在一起。否则系统会出现“性能慢看不出原因、fault 找不到来源、hang 后无法取证”的失败模式。
