---
title: "UR、CA 与 Timeout：有错误返回，还是没有等到返回？"
---

<div id="unsupported-requestcompleter-aborttimeout-怎么看" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# UR、CA 与 Timeout：有错误返回，还是没有等到返回？

上级：[性能与调试](README.md)

UR、CA 和 Timeout 描述不同观察结果。先识别原请求、Requester、目标及等待对象，再解释状态。一个错误码通常不足以确定根因。

## Unsupported Request 常提示什么

UR 表示请求在相关条件下不被支持。例如目标不支持请求类型，或地址未被合法资源接收。对需要 Completion 的请求，UR 可通过错误 Completion 返回；这说明收到了错误状态，不是成功读取了数据。

检查请求类型、地址、BAR 与桥窗口、Function 使能及目标能力。不能仅凭 UR 就判定是物理链路损坏。

## Completer Abort 常提示什么

CA 表示 Completer 无法完成该请求并报告中止。应查看目标内部错误、请求字段和设备运行状态。资源或配置问题可能参与其中，但 CA 不是“BAR 没分配”的固定同义词。

UR 与 CA 的具体 IP 交付方式可参考 [AMD 错误 Completion 说明](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Completions-with-Error-Status-UR-and-CA)，并结合目标协议版本和实现检查。

## 区分 PCIe Completion Timeout 和软件超时

以需要 Completion 的 Memory Read 为例：Requester 发出请求后，在适用时间窗口内未完成所需返回，可触发 Completion Timeout 处理。原因可能在请求路由、目标服务、返回路径或链路状态。首个 CplD 已到但剩余数据未完整返回，也不能把请求算成成功结束。支持的超时范围和适用请求规则须按目标控制器核查。

软件等待 CQE 超时是另一件事。即使 PCIe 读写均正常，设备执行未结束、CQE 发布失败或软件消费错误，都可能让命令超时。普通 posted Memory Write 则没有与该写对应的常规事务 Completion，不能套用“每次写都等 Cpl”的诊断模型。

<div id="调试时不要直接跳结论" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 用证据分支，不用错误名猜根因

| 观察 | 下一步 |
| --- | --- |
| 收到带 UR/CA 状态的 Completion | 解码请求和返回身份，检查地址、能力及目标错误 |
| 已发读请求，没有收齐返回 | 查 Requester 状态，沿请求与返回路径检查 |
| 事务都结束，命令没有 CQE | 查设备执行与完成发布 |
| CQE 已有效，应用仍超时 | 查同步、命令匹配、通知与软件消费 |

复位或重试前先保留在途请求、错误状态和队列证据。是否允许重试取决于操作副作用与设备恢复契约，不能对任意 MMIO 写或命令盲目重放。报告路径见 [Linux AER 指南](https://docs.kernel.org/PCI/pcieaer-howto.html)，记录格式见[故障复盘模板](../08-reference/pcie-debug-postmortem-template.md)。
