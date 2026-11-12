# Power Area Modeling

上级：[07 Evaluation Methodology](./README.md)

相关：[Router Power Area Tradeoff](../02-router-microarchitecture/router-power-area-tradeoff.md)、[Chiplet And Die To Die Interconnect](../06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md)

## 这页在回答什么问题

这页回答：为什么 NoC 评估不能只谈 latency / throughput，也必须把面积和功耗作为一等约束一起带上。

## 性能最优不等于可实现

在架构探索里，很多看起来很美的方案最后会输在：

- buffer 太深
- VC 太多
- crossbar radix 太高
- 物理线太长

也就是说，面积和功耗不是最后再补的一列，而是决定某些方向是否值得继续探索的硬边界。

## NoC 的面积和功耗大头通常在哪里

最典型的构成是：

- buffer / SRAM
- crossbar
- allocator / control
- link / repeater / PHY
- NI

其中最常见的大头通常是：

- buffer 面积和动态能耗
- 高 radix crossbar 的面积与能耗
- 长链路或跨 die 互连的线能耗

这和性能参数是强耦合的。

## 常见的一阶 trade-off

### 加深 buffer

收益：

- 吸收 credit round-trip
- 缓解部分流控停顿

代价：

- 固定宽度和实现组织时逻辑 bit 数线性上升；宏面积还受外围和端口影响
- 动态与 leakage 需按访问次数和工艺模型估计

### 增加 VC

收益：

- 减少 HOL blocking
- 更好做 class 隔离

代价：

- 每 VC 深度、宽度固定时 buffer bit 数随 VC 数增加；总 bit 数固定时增加 VC 会使每 VC 变浅，不必增加总容量
- allocator 复杂度上升

### 提高 radix

收益：

- hop 数减少
- 某些 topology 更扁平

代价：

- crossbar 面积与功耗增速很快
- 时序与布线难度上升

### 加宽 link

收益：

- 单跳带宽线性提升

代价：

- 线资源、驱动与能耗上升
- 局部 endpoint 不一定真能吃满

## 为什么这一页要和 workload 一起看

面积功耗不是抽象常数，它们的价值要看 workload。

例如：

- 如果某个 workload 根本不需要更多 VC，那增加 VC 只是在烧面积和功耗
- 如果某个热点只出现在少量 dynamic case，做全网高 radix 可能不划算

所以 power/area 评估必须和 workload 结果一起读，而不是单独做排行榜。

## 什么时候需要粗模型就够

在 architecture exploration 早期，粗粒度相对模型通常就足够有用，例如：

- buffer cost roughly linear
- crossbar cost grows faster with radix
- long link / cross-die cost noticeably higher

你不一定一开始就需要工艺级绝对数字，但至少要能比较相对代价。

## 一句话理解

NoC 的性能改进只有在面积、功耗和实现复杂度成本可接受时才有意义；否则只是“仿真里更快”。

## 建模启示

同样 bit 数的不同 SRAM 宏组织、端口和外围电路面积也可能不同。动态能量可按 `E_dynamic=Σ(操作次数_i × 单次能量_i)` 估算，包括 buffer 读写、crossbar、link 与仲裁；`P_average=(E_dynamic+E_leakage)/measurement_time`，其中 leakage 能量随状态与时间变化。单次能量、泄漏及面积需要工艺、电压、频率、宏库和活动率校准；没有这些数据只能给明确假设下的相对 proxy。

第一版 power/area 模型至少要有相对成本项：

- buffer cost
- VC cost
- radix cost
- link length cost
- extra-network cost

然后把这些和性能结果并排呈现成简单 Pareto 视图：

- performance gain
- area delta
- power delta
- complexity / verification delta

这样 architecture exploration 才能真正做取舍，而不是只追一个方向上的最优。
