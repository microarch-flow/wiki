# BUS 故障复盘模板

上级：[07 术语与检查清单](./README.md)

相关：[Timeout、Fault 与 Hang 定位框架](../05-performance-debug/timeout-fault-hang-debug-framework.md)、[Counters、Trace 与观测点设计](../05-performance-debug/counters-trace-observation-points.md)、[AXI Waveform Debug 方法](../05-performance-debug/axi-waveform-debug-method.md)

## 使用方式

复盘不是写”修了哪个 bug”的流水账，而是像**交通事故调查报告**一样把整个事件链还原：哪辆车（transaction）没到目的地，在哪个路口（Resource）被卡住，交警（timeout/error wrapper）是怎么处理的，驾驶员（软件）看到的和实际发生的是否一致。好的复盘能让下一个工程师不用重新翻监控录像就知道发生了什么。

## 推荐模板

```md
# 故障标题

## 现象

- 触发条件：
- 外部表现：
- 是否稳定复现：
- 首次发现阶段：仿真 / FPGA / bring-up / 压测 / 量产
- 软件看到的是：timeout / fault / hang / wrong data / missing completion

## 影响范围

- 影响模块：
- 影响 workload / 场景：
- 影响路径：control path / data path / completion path / debug path
- 是否阻塞 boot / debug / driver / DMA / interrupt：

## 事务路径

- master / initiator：
- target / slave：
- 中间路径：decoder / crossbar / bridge / CDC / width adapter / SMMU / DDR：
- request path：
- response path：
- completion / interrupt path：
- 是否涉及 MMIO side effect / cache / barrier：

## 初步分类

- timeout / fault / hang：
- read path / write path：
- request 未发出 / target 未接收 / response 未返回 / completion 未可见：
- 错误是原生错误还是中间层映射：

## Timeline

| 时间点 | 事件 | 证据 |
| --- | --- | --- |
| T0 |  |  |
| T1 |  |  |
| T2 |  |  |

## 证据

- 波形：
- counter / trace：
- 寄存器状态：
- fault / timeout record：
- 软件日志：
- transaction ledger：
- last forward progress：

## 根因

- 直接根因：
- 触发条件：
- 为什么已有设计没有闭环：
- 为什么测试或观测点没有提前发现：

## 修复

- RTL 改动：
- 配置改动：
- 驱动 / firmware 改动：
- 文档 / 约束改动：
- 是否影响软件 ABI 或寄存器语义：

## 验证

- 新增 directed test：
- 新增 stress / random：
- 新增 error injection：
- 新增 assertion / cover：
- 回归范围：

## 防复发

- 新增观测点：
- 新增 checklist 项：
- 新增 timeout / fault / resource release 检查：
- 需要更新的设计模板或 wiki：
```

## 填写规则

| 项目 | 要求 |
| --- | --- |
| 现象 | 用软件或系统可见行为描述，不直接写猜测根因 |
| 事务路径 | 至少写清 master、target、bridge/fabric、response path |
| 分类 | 先分 timeout/fault/hang，再分 read/write/control/data/completion |
| Timeline | 用事件排序，不用大段叙述 |
| 证据 | 每个结论要能对应波形、counter、trace、寄存器或日志 |
| 根因 | 区分直接根因、触发条件和设计缺口 |
| 修复 | 写清是否改变协议、软件模型、寄存器语义或错误路径 |
| 防复发 | 至少落到测试、观测点、checklist 或 assertion 之一 |

## 常见复盘缺口

| 缺口 | 后果 |
| --- | --- |
| 只写“DMA hang” | 无法区分 descriptor、data、writeback、interrupt 哪段失败 |
| 只贴波形不写 transaction ledger | 下一次很难快速找到未闭环事务 |
| 只写 RTL 修复，不写软件语义 | driver 或 firmware 可能继续触发边界条件 |
| 不记录 last forward progress | hang 类问题无法复盘 |
| 不写防复发项 | 同类 bug 会换一个路径再次出现 |

## 一句话理解

BUS 故障复盘要把 bug 从“现象描述”还原成一条没有正确闭环的 transaction path。

## 建模启示

复盘模板本身就是模型校验表。每次故障都应补齐 `request_accept`、`service_start`、`response_return`、`completion_visible`、`timeout_fire`、`fault_recorded`、`resource_release`、`last_forward_progress` 这些事件中的相关子集。

如果某个事件无法被证据支持，就说明当前设计缺少观测点；如果某个错误路径没有 resource release，就说明模型缺少闭环；如果软件现象无法映射回 transaction path，就说明文档和调试语言仍然混层。
