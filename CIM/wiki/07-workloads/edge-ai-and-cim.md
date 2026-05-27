# Edge AI：能效需求驱动下 CIM 的现实定位

上级：[07 Workloads](./README.md)
相关：[CNN on CIM](./cnn-on-cim.md), [BUS: DMA CPU Peripheral Path](../../../BUS/wiki/04-microarchitecture-integration/dma-cpu-peripheral-memory-path.md), [FAB: Thermal Management](../../../FAB/wiki/06-cross-cutting-engineering/thermal-path-and-management.md)

## 这页在回答什么问题

为什么 CIM 更可能先在 edge AI 找到产品窗口？因为 edge 更看重 energy per inference、standby power、local response、BOM 和热约束，而不是数据中心级通用吞吐。

## Edge 的关键条件

edge workload 往往模型更小、任务更固定、功耗预算更硬、联网和外部 memory 更受限。只要模型能稳定运行，少搬数据就可能直接转成电池寿命、散热和成本收益。

但 edge 不等于低门槛。车载、工业、可穿戴、摄像头和手机 SoC 的可靠性、软件生态、OTA 更新和认证要求差异很大。CIM 需要匹配具体子场景，而不是笼统说“适合 edge”。

## 三条 Paradigm 的 Edge 落点

Analog ReRAM/Flash CIM 适合固定权重、低比特、低功耗、少更新的 edge inference。它的风险是校准、温度、retention、模型更新和客户软件栈。

Digital SRAM-CIM 更适合 SoC/MCU/NPU 内嵌，精度、测试、验证和 runtime 更稳。它牺牲一部分理想能效，换取产品集成路径。

Mixed-signal CIM 适合在能效和可控性之间折中：array 内保留局部物理并行，数字端处理 scale、校正和接口。edge 场景的固定模型和低功耗需求能放大它的价值。

## 子场景差异

可穿戴和 always-on sensor 关注 mW 级功耗、待机和唤醒延迟。边缘摄像头关注本地隐私、稳定推理和中等模型。手机更重视与现有 ISP/NPU/SoC 软件生态协同。车载 edge 还要跨温区、功能安全、长期供货和失效诊断。edge server 或 infra edge 的功耗边界更接近小型数据中心，DRAM/HBM/GDDR-PIM 或 NMC 才更可能作为 memory-side 对照。

这些场景共同要求：模型规模可控、权重更新频率低、外部 memory 访问少、fallback 少、热设计可闭合。FAB 的热路径和 BUS 的 DMA/外设路径会影响端侧真实功耗。

## PIM/NMC 对照

电池级 ultra-low-power edge 不适合把 DRAM/HBM/GDDR-PIM 当主路线，因为 HBM/GDDR 的封装、功耗和系统复杂度偏重。HBM base die、interposer、package-side logic、memory module 或 memory-adjacent accelerator 属于 NMC；若 compute 不在 cell/array/sense path 内，就不属于 CIM。DRAM/HBM/GDDR-PIM 更偏 edge server / infra edge 的高带宽 memory-side offload；edge CIM 更常是片上 SRAM/Flash/ReRAM macro 或固定 function block。

## 一句话理解

Edge AI 适合 CIM，不是因为它简单，而是因为固定低功耗任务更容易把局部少搬数据转成设备级收益。

## 建模启示

edge 建模要记录 workload phase、op mix、tensor shape、batch、reuse、precision sensitivity、fallback ratio、NoC traffic、host sync、latency target、power budget、duty cycle、energy per inference、standby power、wake-up latency、thermal envelope、model size、model update frequency、local memory fit、external DRAM dependency、external memory traffic、BOM/package proxy、certification 和 reliability target。可以折叠具体封装细节，但不能折叠功耗状态、唤醒路径、温度、OTA 更新频率和可靠性目标。
