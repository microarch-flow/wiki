# 实验结果沉淀模板与状态页

上级：[建模与评估](./README.md)

相关：[实验模板与结果模板](./experiment-result-templates.md)、[Simulator 最小实现路线](./simulator-implementation-roadmap.md)

## 为什么这页现在就值得建

即使你还没开始跑 simulator（模拟器），也最好先把结果沉淀结构建好。  
否则后面一旦开始扫参数，记录很容易迅速失控。

## 建议的目录结构

后续可以按下面方式组织：

- `results-log/`
- `parameter-sweeps/`
- `workload-studies/`
- `interim-conclusions/`

## 状态页模板

```md
# NoC Experiment Status

## Current Simulator Status
- implemented
- partially implemented
- not implemented

## Current Verified Experiments

## Current Open Questions

## Most Recent Findings

## Next 3 Experiments
```

## 单次实验日志模板

```md
# Experiment Log: <date / name>

## Goal

## Configuration

## What Changed Since Last Run

## Raw Results

## Interpreted Results

## Confidence Level

## Next Action
```

## 参数扫描汇总模板

```md
# Sweep: <name>

## Sweep Dimensions

## Key Observations

## Best Point So Far

## Suspicious Results

## Follow-up Runs
```

## 阶段性结论页应该怎么写

不要直接写“某拓扑最好”。  
更稳的写法是：

- 在什么 workload 下
- 在什么模型假设下
- 哪些指标上更优
- 哪些风险还没覆盖

## 一个很重要的字段：Confidence

建议每条结论都标：

- low
- medium
- high

因为早期很多结论只是：

- first-order insight

而不是强验证结论。

## 你后面最应该沉淀的 4 类结果

- hotspot（热点）定位结果
- stall breakdown（停顿分类统计）对比
- topology（拓扑）/ hierarchy（层次化）比较
- QoS（服务质量）/ response isolation（响应隔离）结果

## 本页结论

实验结果沉淀页的价值，在于让 simulator 一旦开始产出结果，你就能立刻把“现象、解释、可信度、下一步动作”组织成长期可复用的研究资产。
