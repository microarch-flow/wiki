# 非理想因素与误差来源

## 为什么这一页重要

很多 CIM 设计在原理层成立，但一旦进入真实器件、真实阵列和真实系统，误差就会迅速累积。尤其是 analog 和 mixed-signal 路线，非理想因素往往不是边缘问题，而是决定能否落地的中心问题。

## 常见来源

- thermal noise
- process variation
- IR drop
- device drift
- retention loss
- write noise
- quantization noise

## 按层级理解这些误差

### 器件级

- `device drift`
- `retention loss`
- `write noise`

这类误差直接关系到权重状态能否稳定保存，以及写入后是否能保持目标 conductance。

### 电路级

- `thermal noise`
- sense margin 不足
- ADC / DAC 自身误差

这类误差主要影响读出和转换链路。

### 阵列级

- `IR drop`
- 行列耦合
- 大阵列下的信号不均匀

这类误差会随着阵列规模扩大，往往决定“理论大阵列”能否真的工作。

### 系统级

- quantization noise
- 多 tile 归约误差
- 运行时校准不充分

这类问题最终决定模型精度是否可接受。

## 研究时要落地的问题

- 哪些误差是器件级
- 哪些误差是阵列级
- 哪些误差会最终放大到模型精度

## 一个实用的分析框架

研究一篇论文或一个产品时，可以顺着下面的问题链走：

1. 误差源来自器件、电路、阵列还是系统？
2. 它对读出值的影响是偏置、随机噪声还是动态漂移？
3. 误差是否会随着阵列尺寸、时间或温度放大？
4. 误差是离线可校准，还是运行时持续存在？
5. 最终会反映到 kernel 精度，还是模型级 accuracy？

## 典型应对方法

- 离线校准
- 在线补偿
- 差分编码
- 冗余存储
- 小阵列切分
- quantization-aware training
- variation-aware mapping

## 研究和记录时建议补的字段

- 误差类型
- 影响层级
- 是否可校准
- 校准频率
- 对模型精度的影响
- 是否有硅后数据支持

## 后续可补充内容

- 误差传播链
- 校准策略
- 仿真与硅后验证口径
