# 算法工作负载分析导读

上级：[算法与模型](../README.md)

<span id="chip-workload-analysis" class="workload-legacy-anchor"></span>
<span id="这章在回答什么问题" class="workload-legacy-anchor"></span>
<span id="本章方法" class="workload-legacy-anchor"></span>
<span id="页面列表" class="workload-legacy-anchor"></span>
<span id="workload-对硬件-wiki-的连接" class="workload-legacy-anchor"></span>
<span id="archax-建模入口" class="workload-legacy-anchor"></span>

<!-- nav-title: 算法工作负载分析 -->


把确定的模型配置转成工作量、流量、容量和依赖，再用测量检验瓶颈。下面按方法、算子案例、系统路径和部署约束阅读；不要求机制文章重复同一模板。

## 阅读顺序

1. [工作负载分析方法](workload-analysis-methodology.md)
2. [记录字段](workload-characterization-axes.md)
3. [CNN 工作负载](cnn-workload.md)
4. [Transformer 工作负载](transformer-workload.md)
5. [SSM 工作负载](ssm-workload.md)
6. [MoE 工作负载](moe-workload.md)
7. [BEV 工作负载](bev-workload.md)
8. [Occupancy 工作负载](occupancy-workload.md)
9. [驾驶 E2E 工作负载](e2e-workload.md)
10. [VLA 工作负载](vla-workload.md)
11. [世界模型工作负载](world-model-workload.md)
12. [端侧推理约束](edge-inference-chip-requirements.md)
13. [云端推理与仿真](cloud-inference-and-simulation-chip.md)
14. [世界模型端云协作](edge-cloud-collaborative-world-model.md)
15. [架构实验设计](ad-robotics-chip-architecture-summary.md)
16. [工作负载比较索引](workload-comparison-table.md)

## 原入口

这些页面保留旧引用，完整内容已合并到对应主文。

1. [从算法到工作负载原入口](workload-lens.md)

## 阅读边界

本文系列提出工作负载与实验需求；具体硬件机制和工具实现状态由[微架构](../../microarchitecture/README.md)、[存储](../../storage/README.md)、[互连](../../interconnect/README.md)及相应工具文档负责。
