# ReRAM / RRAM-CIM

## 路线定位

这是最典型的 crossbar 模拟存内矩阵乘路线，理论密度和能效都很吸引人，但工程风险也最高。

如果要找“最像教科书式存内计算”的路线，通常就是 ReRAM-CIM。因为它真的试图利用阵列物理规律，把乘法和求和直接压进存储路径里。

## 为什么这条路线这么吸引人

ReRAM 的一个核心优势是，权重可以映射为电导状态。当输入以电压形式施加到 crossbar 行上时，每个器件会根据其电导产生对应电流，各列电流再天然求和，从而接近完成矩阵向量乘：

```text
输入电压 V × 电导 G -> 电流 I
列电流累加 -> dot product / MVM
```

这使得 ReRAM-CIM 在概念上具备几个很强的卖点：

- 非易失
- 高密度
- 阵列并行度高
- 理论上非常适合 MVM

## 为什么它又这么难

吸引人的地方，恰好也是工程最难的地方。因为一旦计算依赖器件物理状态，就必须面对：

- 器件变异
- 写入误差
- conductance drift
- IR drop
- retention 和 endurance 限制
- 读出链路和 ADC 能耗

因此，ReRAM-CIM 往往不是“能不能做出一个可工作的 MVM”，而是“能不能在真实误差和真实系统约束下持续稳定工作”。

## 重点问题

- 权重如何映射为 conductance
- 输入如何编码为电压或脉冲
- 列电流如何转换为数字结果
- variation、IR drop、drift 如何影响精度
- 权重更新与校准成本有多高

## 常见分析维度

### 1. 阵列规模

crossbar 越大，理论并行性越强，但：

- IR drop 更严重
- 读出精度要求更高
- 校准难度更高

### 2. 权重表示

需要明确权重是如何编码到器件中的：

- 单器件单值
- 多器件拼接多比特
- 正负权重是否拆成差分对

### 3. 输入方式

输入通常需要转成：

- 模拟电压
- 脉冲宽度
- 位串行激励

这些选择会直接影响 `DAC` 成本、吞吐和精度。

### 4. 结果读出

阵列内求和只是第一步，真正的系统结果还依赖：

- 列电流采样
- ADC 量化
- 后级数字累加或校正

很多论文的理想能效，在系统里就是死在这一段。

## 典型优点

- 高密度，适合放更多权重
- 非易失，待机功耗低
- 对固定权重推理很有吸引力
- 理论能效和并行度上限很高

## 典型限制

- 模拟误差会直接影响模型精度
- ADC / DAC 成本可能非常重
- 写入和更新复杂，不一定适合频繁训练或动态更新
- 工艺、良率和大规模集成难度高

## 更适合哪些场景

| 场景 | 适配度 | 原因 |
| --- | --- | --- |
| Fixed-weight edge inference | 高 | 功耗敏感，模型相对稳定 |
| Sensor-side AI | 中高 | 极低功耗有吸引力 |
| Training | 低 | 写入精度和更新稳定性压力大 |
| Large general-purpose accelerator | 中 | 理论吸引力强，工程门槛高 |

## 研究和评估时要特别注意

### 是否把非理想因素算进去了

至少应检查：

- 器件级 variation
- IR drop
- retention drift
- ADC quantization
- temperature sensitivity

### 是否只给出宏级理想结果

如果论文主要展示的是阵列原理和局部结果，还需要继续追问：

- 系统怎么接
- 权重怎么编程
- 精度怎么保持
- 校准多久做一次

### 是否真的适配目标模型

很多设计在 `MVM` 上很漂亮，但要看它最终是否支撑：

- CNN
- Transformer FFN
- attention 子模块
- edge sensor model

## 关键指标

- conductance range
- retention / endurance
- ADC overhead
- inference accuracy loss
- calibration frequency

## 建议额外记录的指标

- crossbar size
- negative weight encoding method
- write / verify cost
- drift compensation strategy
- silicon measurement vs simulation

## 后续可补充内容

- crossbar MVM 推导
- 非理想建模方法
- 面向 edge AI 的适用性分析
