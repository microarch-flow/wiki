# Axelera：SRAM-CIM 商业化的代表

上级：[公司卡片](README.md)
相关：[SRAM-CIM 基础](../../02-memory-technologies/sram-cim-foundation.md), [Digital CIM](../../03-compute-paradigms/digital-cim-fundamentals.md), [软件栈](../../06-software-stack/README.md)

## 这页在回答什么问题

这页回答：Axelera 为什么是 SRAM-based digital CIM 的产业代表，以及它和 analog CIM startup 的产品化压力有什么不同。

| 字段 | 内容 |
| --- | --- |
| 公司/对象 | Axelera AI，Metis AIPU、Metis M.2/PCIe/Compute Board、Europa AIPU |
| 本 wiki 分类 | CIM |
| 技术路线 | SRAM-based Digital In-Memory Computing (D-IMC) + RISC-V controlled dataflow |
| compute paradigm | digital CIM |
| 产品层级 | chip、M.2 card、PCIe card、compute board、partner systems；Europa 是 2025 发布的新一代 AIPU |
| 目标市场 | edge computer vision、industrial、retail、security、robotics、edge server |

Axelera 符合 CIM 的原因是：官方技术页把 D-IMC 描述为基于 SRAM 并结合 digital computations，使 memory cell 有效成为 compute element。它不是“SRAM buffer + 外围 MAC”这种常规 NPU 结构，而是把计算功能压进 SRAM array 近侧路径；但它走的是 digital CIM，不依赖 analog 电流精确累加。来源：[Axelera technology page](https://axelera.ai/technology)。

Metis 的产品口径更接近当前可部署硬件。官方 Metis AIPU 页面给出最高 214 TOPS INT8、15 TOPS/W、典型功耗 10 W，并强调 Voyager SDK 用于构建高性能 AI 应用。截至 2026-05-27 访问，Axelera store 页面展示 M.2、PCIe 和 Metis Compute Board 等形态，价格、发货和开发者入口都有公开页面；这说明官方提供了购买/评估入口，不等同于判断其规模化出货。来源：[Metis AIPU page](https://axelera.ai/ai-accelerators/aipu/metis), [Axelera store](https://store.axelera.ai/)。

Axelera 的产业路线选择很明确：用 SRAM digital CIM 换取标准 CMOS、factory agnostic、数字验证和软件可控性。官方技术页强调其 SRAM-based D-IMC 使用标准 CMOS 工艺，材料和制造流程容易由 foundry 获得。这一点和 [RAM wiki 的 SRAM array/bitcell](../../../../RAM/wiki/02-sram-foundations/README.md)、[FAB wiki 的工艺/DFT/良率](../../../../FAB/wiki/README.md) 直接相关：digital CIM 仍有 array compute mode 的验证问题，但比新型 analog memory 更容易进入现有制造生态。

2025 年 10 月，Axelera 发布 Europa AIPU，宣称 8 个第二代 AI cores、每个 core 使用 D-IMC，并配合 RISC-V vector cores、128 MB on-chip L2 SRAM 和 LPDDR5 interface，目标从 edge 扩到更高性能的 multi-modal/edge server 场景。来源：[Europa announcement](https://axelera.ai/news/axelera-announces-europa-aipu-setting-new-industry-benchmark-for-ai-accelerator-performance-power-efficiency-and-affordability)。

产业判断：Axelera 的强项不是单纯讲 macro 能效，而是把 SRAM-CIM 做成 card、board、SDK、model zoo、partner systems 和 web store。它的风险也因此从“电路能不能 work”转向“软件生态能否覆盖足够多模型、客户是否愿意在非 CUDA 平台上部署、[片上 SRAM](../../../../RAM/wiki/03-sram-applications/README.md) 容量与外部 DRAM 带宽如何支撑 transformer/SLM 工作负载”。

主要风险：

| 风险 | 为什么重要 |
| --- | --- |
| 模型覆盖 | Edge 客户需要 YOLO、ResNet、segmentation、SLM 等真实模型稳定跑通 |
| 软件生态 | Voyager SDK 必须降低从 ONNX/PyTorch 到硬件部署的摩擦 |
| 容量边界 | SRAM-CIM 面积大，片上容量会限制大模型映射方式 |
| 产品代际 | Metis 面向 edge vision，Europa 扩展到更高性能场景，两代软件/硬件兼容性影响客户投入 |
| 竞争口径 | GPU/NPU 竞品以成熟生态取胜，Axelera 需要用 FPS/W、FPS/$ 和部署便利性证明价值 |

## 一句话理解

Axelera 代表 SRAM digital CIM 的商业化路线：不追求 analog 极限，而是用标准 CMOS、可购买板卡和 SDK 去降低客户导入成本。

## 产业启示

SRAM-CIM 更可能先以 edge AI accelerator 的形态进入市场，因为它能复用数字芯片制造、PCIe/M.2 form factor 和软件工具链。它的商业化瓶颈不是“能否制造出 array”，而是能否让客户在真实模型、真实摄像头/工业场景和真实部署流程中获得稳定收益。
