---
title: "一次跨桥读取：PCIe、AXI 与 NoC 分别负责什么？"
---

<div id="pcie-vs-axi-noc边界与分工" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# 一次跨桥读取：PCIe、AXI 与 NoC 分别负责什么？

上级：[工作负载与案例](README.md)

PCIe、AXI 和 NoC 可以串联服务同一次访问，但它们不是同一层面的替代方案。以下是一个具有 PCIe-to-AXI 桥和片内 NoC 的教学设备；其他设备未必采用这些内部接口。

## 先约定请求与目标

主机读取某个 BAR 窗口中的数据，该窗口映射到设备内部 SRAM。BAR 与桥窗口已配置，访问合法。桥接模块负责把 PCIe 请求转换为片内请求，并把片内结果转换回 PCIe Completion。

<div id="axi-更常解决什么" class="pcie-legacy-anchor"></div>
<div id="noc-更常解决什么" class="pcie-legacy-anchor"></div>
<div id="pcie-更常解决什么" class="pcie-legacy-anchor"></div>

## 沿一次读取划分职责

| 阶段 | 模块输入 | 模块职责与输出 |
| --- | --- | --- |
| 主机到设备 | PCIe Memory Read | PCIe 接口接收请求，保留请求身份与返回所需状态 |
| 事务转换 | BAR 地址及请求长度 | 桥译码目标，生成适用的 AXI 读请求 |
| 片内传输 | AXI 地址/控制与网络映射 | NoC 在节点间传送请求，处理路由、仲裁和拥塞 |
| 目标服务 | SRAM 访问 | 数据通过片内返回路径和 AXI R 接口回到桥 |
| 设备到主机 | 数据或错误结果 | 桥按适用规则生成 CplD 或错误 Completion |

PCIe Tag 与 AXI ID 不是同一个命名空间。桥可能拆分、合并或缓冲内部事务，必须维护足以恢复原请求的映射；不能未经说明就假定字段数值直接透传。

<div id="对体系结构最关键的判断" class="pcie-legacy-anchor"></div>

## 两个观察边界

主机看到的是 PCIe 请求发出到所需 Completion 收齐的时间。片内可以分别测量 AXI 地址握手到最终 R 数据返回的时间。NoC 竞争会延长片内段，PCIe 返回链路拥塞会延长后续段。

若片内返回稳定而主机读时延变大，应查桥缓冲、Completion 调度及返回路径；若两者都增加，还须检查片内竞争和目标服务。单一端到端计数不足以定位。

<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 写响应不能直接替换

普通 PCIe Memory Write 没有逐笔事务 Completion；AXI 写接口有 B 响应。桥必须按自身契约吸收、报告或传播错误，不能凭空给普通 PCIe 写创造一个成功 Cpl。AXI B 也不自动证明数据已对最终 CPU 缓存可见。

AXI 机制归 [BUS](../../BUS/README.md)，片内网络归 [NoC](../../NOC/README.md)，本页只保留桥边界及观察方法。一个厂商实现如何把 PCIe 状态映射到 AXI 错误，可参见 [AMD PCIe Subsystem](https://docs.amd.com/r/en-US/am026-versal-ai-edge-prime-gen2-trm/PCIe-Subsystem)；其中的具体返回策略不是所有桥的统一保证。
