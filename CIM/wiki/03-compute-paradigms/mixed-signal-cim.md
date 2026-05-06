# Mixed-Signal CIM

## 定位

Mixed-signal CIM 是更常见的折中路线，阵列内做部分模拟计算，外围负责数字控制、转换和归约。

如果说 Digital CIM 更稳，Analog CIM 更激进，那么 Mixed-signal CIM 往往是最接近“现实工程平衡点”的那一类设计。

## 为什么这条路线常见

因为很多团队最终都会发现：

- 纯数字路线收益不够大
- 纯模拟路线工程风险太高

于是最自然的落点就是：

- 阵列内保留最有价值的模拟并行计算
- 把精度敏感、控制复杂、归约复杂的部分交给数字外围

## 常见边界划分

### 阵列内

通常负责：

- 局部乘法
- 局部求和
- 电流 / 电荷域并行

### 阵列外

通常负责：

- ADC / DAC
- 数字校正
- 多周期累加
- 控制与调度
- tile 间归约

## 关键问题

- 模拟部分和数字部分的边界在哪里
- 哪些开销必须算进 system-level 指标
- mixed-signal verification 如何做

## 研究和评估时该怎么读

### 先问边界划分是否合理

一个 mixed-signal 设计是否成立，关键就在于：

- 哪些部分放在阵列里
- 哪些部分必须拿出来
- 这种边界是否真正降低了总成本

### 再问是否把折中代价算清楚了

折中不等于免费。常见代价包括：

- 设计复杂度升高
- 验证复杂度升高
- 指标口径更容易被美化

### 最后问 system-level 是否仍然成立

很多 mixed-signal 设计在 macro 层看很均衡，但系统层仍可能被：

- ADC
- NoC
- buffer
- control

这些部分吞掉收益。

## 更适合的场景

- 想保留部分模拟收益，又需要可控精度的系统
- edge inference
- 研究向片上 CIM 宏和实验芯片

## 与案例库的关系

- [TSMC 16nm CIM Macro](../09-research/case-studies/tsmc-16nm-cim-macro.md) 和 [东京大学 ReRAM-CiM](../09-research/case-studies/u-tokyo-reram-cim.md) 都可以拿来从 mixed-signal 视角重新判断其真实边界

## 后续可补充内容

- 典型 block diagram
- 误差预算拆分
- 为什么产业界更偏向折中方案
