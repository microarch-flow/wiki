# 计算、数据移动与硬件成本：先确定指标边界

上级：[COMPUTE 域总览](./README.md)
相关：[算力单元的问题](./problem-statement.md)、[学习路线](./taxonomy-and-roadmap.md)

计算、数据移动、面积和能耗彼此相关，但它们不是同一个无量纲比值。比较前必须固定工作量、时间窗口、资源边界和单位。不同边界的统计值也不能直接相加：同一字节可能依次经过 RF、阵列和片外接口。

## 计算与搬运：算术强度

对指定边界和指定工作量：

```text
arithmetic_intensity = useful_MACs / bytes_crossing_boundary  [MAC/byte]
```

包括哪些数据必须写清楚：权重、激活、输出、配置、重试、metadata、填充和写回。`MAC` 是一次乘加；若用 FLOP，须声明一次 MAC 算几次 FLOP。只有同一口径才可比较数值。

手算假设：一个 `y=3` 行、`x=2` 列的阵列完成一个矩阵向量乘。每个权重和输入均为 1 B，每个输出为 4 B。6 个权重已驻留，3 个输入和 2 个输出跨越阵列边界，则得到 `6 MAC / (3+8) B = 6/11 MAC/B`。若首次还要从同一边界加载 6 B 权重，则是 `6/17 MAC/B`。这只是两个明确时间窗口下的计数；不是对所有阵列的通用性能结论。其他负载、重复使用次数、padding 和部分和路径都会改变结果。

## 面积、带宽、吞吐与能耗

| 指标 | 计算方式或单位 | 能回答的问题 |
|---|---|---|
| 面积估算 | mm²；或注明假设的门数代理 | 结构和实现成本 |
| 算术强度 | MAC/byte，指定边界 | 跨该边界的数据复用 |
| 带宽 | byte/s，指定链路与方向 | 数据能否及时供应 |
| 吞吐密度 | MAC/s/mm² | 单位面积完成多少有用工作 |
| 任务能量 | `E_task`，J/task | 指定任务和能耗边界内的总能量 |
| 每有效 MAC 的平均能量 | `E_task / N_useful_MAC`，J/MAC | 同一任务窗口与能耗边界；仅当 `N_useful_MAC > 0` 时定义 |

某一个指标上升不能证明其他指标也上升。高 MAC/byte 也不能单独证明高吞吐：供数、依赖、利用率、频率和资源竞争仍可能限制性能。

[datapath 的 `24p`、`4p` 例子](../02-datapath-foundations/mux-and-data-movement-cost.md)只是两个简化结构的门数代理；它不是 MAC/byte，也不能推出商业芯片的面积份额。[systolic array 的工作量示例](../03-systolic-array/why-systolic-array.md)使用具单位的跨边界字节，不能与门数代理比值相除。

## 各层应记录什么

- **datapath**：操作数位宽、选择网络、寄存器端口及其面积/时序估算。
- **array**：数据流、PE 使用率、阵列边界流量和权重驻留。
- **RF 与片上网络**：分别统计 RF 端口、链路容量与跨各自边界的 bytes。
- **片外存储**：统计 HBM/DRAM 边界的数据及有效带宽；不要把它与片上流量混成一个分母。
- **clock 与实现**：每域频率、II、功耗、面积和约束。

这些维度共同影响设计，不是一个跨层不变量。Pope 的 [Strassen 分析](https://reiner.org/strassen)提供一种特定假设下的算法与精度权衡；不能据此断言算法优化在所有 AI 工作负载均无价值。

## 建模启示

记录 `Compute{operation, useful_macs, precision, time}` 与 `Move{src, dst, bytes, time, kind}`。每项结果附带边界、统计窗口和是否包含初始化。针对某边界分别求 MAC/byte；跨多个边界的流量要保留来源，不能把同一次移动重复累计为芯片外存流量。面积、时间和能耗则用各自模型求值。对 archax 的字段映射是[建模建议](../08-modeling-for-archax/modeling-insights.md)，不是已验证的实现事实。
