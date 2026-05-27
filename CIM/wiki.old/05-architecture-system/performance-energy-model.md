# 性能与能耗模型

## 为什么必须单独建模

很多 CIM 结果只停留在 `macro-level`，而真实系统收益要靠建模才能判断。否则很容易出现：

- 宏指标很漂亮
- 芯片指标一般
- 端到端收益并不明显

因此，在本 wiki 里，所有路线最终都应尽量落到统一的性能和能耗模型中。

## 建议统一模型

```text
E_total = E_compute + E_adc + E_dac + E_buffer + E_noc + E_dram + E_control
```

这个公式的目的不是追求绝对精确，而是强迫分析时把容易被忽略的成本显式写出来。

## 各项含义

- `E_compute`：阵列内或本地逻辑完成计算的能耗
- `E_adc`：模拟结果数字化的能耗
- `E_dac`：输入激励转换成本
- `E_buffer`：片上 buffer、scratchpad、寄存器搬运成本
- `E_noc`：tile 间、macro 间或 cluster 间通信成本
- `E_dram`：片外存储访问成本
- `E_control`：调度、控制、时钟和状态机开销

## 什么时候这个模型最有用

它尤其适合回答以下问题：

- 为什么某个 macro 很强，但 chip 收益不明显
- 为什么某条路线在 edge AI 有优势，但在大模型上不成立
- 为什么同样是 CIM，不同论文的能效几乎不可直接比较

## 推荐记录项

- 峰值吞吐
- 有效吞吐
- energy per op
- energy per byte moved
- utilization
- precision loss

## 建议增加的统一口径

- 指标层级：`macro / tile / chip / system`
- 精度条件：`INT4 / INT8 / mixed precision`
- 工作负载：`MVM / GEMM / CNN / Transformer`
- 是否包含外围：`ADC / NoC / DRAM / control`
- 是否来自 post-layout / silicon measurement

## 一个常用的分析套路

### 第一步：先判断瓶颈

区分当前 workload 主要是：

- `compute-bound`
- `memory-bound`
- `reduction-bound`
- `control-bound`

### 第二步：再看收益转移到哪里

很多设计减少了某一段成本，但会把压力转移到：

- ADC
- NoC
- DRAM
- 控制路径

### 第三步：最后看端到端利用率

理论峰值只有在高利用率下才有意义，因此要看：

- array utilization
- tile utilization
- host stall ratio
- data reuse efficiency

## roofline 风格的使用方式

可以把 CIM 系统也看成同时受两条上限约束：

- 计算峰值上限
- 数据搬运上限

如果一个 workload 长期卡在带宽线上，那么继续提升阵列峰值吞吐通常没有意义；这类问题更应考虑 PIM / near-memory 路线是否更合适。

## 后续可补充内容

- roofline-style 分析
- macro vs chip vs system 指标换算
- benchmark 口径说明
