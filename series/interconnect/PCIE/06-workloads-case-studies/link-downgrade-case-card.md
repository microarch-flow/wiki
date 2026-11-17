---
title: "链路降速或降宽：先核对能力、配置与实际状态"
---

<div id="链路降速案例卡" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# 链路降速或降宽：先核对能力、配置与实际状态

上级：[工作负载与案例](README.md)

链路实际速率或宽度低于预期，会降低传输容量。但应用变慢不等于链路降档；两端标称能力也不保证沿途每段链路都达到同一状态。

<div id="典型现象" class="pcie-legacy-anchor"></div>

## 先明确“预期”来自哪里

记录两端能力、目标速率设置、主板实际布线、lane 分配，以及 Switch、转接板、线缆和 retimer 等路径。外形为 x16 的插槽可能只提供较少 lane；平台分叉配置也会改变分配。

<div id="最常见误判" class="pcie-legacy-anchor"></div>

## 一个构造例子

假设端点标称 Gen4 x8，但与上游端口的实际链路状态是 Gen3 x4。仅扣编码后的单向容量分别约为 15.75 GB/s 与 3.94 GB/s，后者是前者的四分之一。此计算只比较上界，不意味着应用吞吐一定下降四倍。

若应用原先由设备计算限制在 1 GB/s，降档后仍可能维持原吞吐。因此应同时记录链路状态和业务服务量。

## 最短排查链

1. 检查目标链路两端及每个共享上游链路的实际 speed/width。
2. 比较能力、配置目标与实际结果，排除正常的较低速率或较少 lane 配置。
3. 记录重训练、每 lane 状态、错误与重放增量，以及负载和环境。
4. 在其他条件可比时比较插槽或路径；只有应用吞吐变化，没有链路证据时，不直接判定训练故障。

<div id="最值得抄走的判断" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 分开系统判断与电气诊断

本页负责确认容量是否下降及其性能影响。LTSSM、均衡和通道质量的深入诊断转到 [SerDes 的 PCIe 训练案例](../../SERDES/06-link-operation/pcie-training-case.md)。实际训练过程与测试范围参见 [PCI-SIG PCIe 5.0 测试问答](https://pcisig.com/blog/pcie%C2%AE-50-protocol-and-electrical-compliance-testing-deep-dive-webinar-qa)。

链路已达到预期状态但吞吐仍低时，继续看[性能参数](../05-performance-debug/bandwidth-latency-credit-mps-mrrs.md)与[瓶颈拆解](../05-performance-debug/host-device-bottleneck-breakdown.md)。
