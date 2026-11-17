# 机器人与自动驾驶：相同决策闭环，不同动作接口

上级：[专题导读](README.md)

<span id="robotics-vs-autonomous-driving" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么能放一起比直觉与类比" class="workload-legacy-anchor"></span>
<span id="共性可共享的那一半" class="workload-legacy-anchor"></span>
<span id="差异决定芯片需求分叉的那一半" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


两类系统都依据不完整观测选择动作，再接受环境反馈。共同的抽象有助于复用方法；具体的观测、动力学和执行约束决定方法能否迁移。

## 先比较接口，而不是模型名称

| 接口 | 自动驾驶常见形式 | 机器人操作常见形式 |
| --- | --- | --- |
| 观测 | 多相机、LiDAR、雷达、自车状态、地图 | 外部或腕部相机、关节、末端、力觉 |
| 决策输出 | 路径、带时间轨迹、速度或控制量 | 末端位姿增量、关节目标、夹爪或力目标 |
| 环境交互 | 车辆、行人及道路约束 | 接触、抓取、工具和物体约束 |
| 反馈链 | 感知—预测—规划—车辆控制 | 感知—策略—运动/阻抗控制—执行器 |

这些是典型配置，不覆盖所有车辆和机器人。移动机器人也会做导航，车辆系统也可能直接输出控制量。

## 动作语义决定迁移难度

同样一个 7 维向量，可以表示末端平移、旋转与夹爪，也可以表示七个关节角。维数相同不代表动作兼容。单位、坐标系、绝对量/增量、控制周期及执行器约束都应写入接口。

构造例：策略输出“向前 1 cm”，如果训练坐标是末端局部坐标，部署却按世界坐标执行，模型输出的数值即使完全正确，动作方向仍可能错误。这个问题无法通过扩大网络直接解决。

## 共用训练方法，分别验证闭环

行为克隆、强化学习、模型预测控制和生成式策略都可用于两类系统。采用哪种训练目标，与最终输出轨迹还是控制量是不同维度，见[模仿学习与强化学习](imitation-and-reinforcement-learning.md)。

离线动作误差小，不保证长时间执行成功。机器人接触误差可逐步积累；驾驶中的其他参与者会对自车行为作出反应。闭环测试应覆盖恢复能力、观察延迟和分布变化。

<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 工作负载如何比较

不要直接比较“机器人 50 Hz”和“车辆 10 Hz”。先问它们指传感器更新、策略重推理、动作样本还是底层控制。一个策略可以每 500 ms 生成动作块，再以 50 Hz 执行其中 25 个动作。

比较表应记录观测尺寸、历史、动作长度、调用次数和截止时间。公共分析方法见[工作负载分析](../06-chip-workload-analysis/workload-analysis-methodology.md)，具体系统见[驾驶规划](../03-autonomous-driving-algorithms/planning-oriented-e2e.md)和 [VLA 基础](../04-robotics-and-vla/vla-fundamentals.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [π0 原论文 v1：动作块与执行频率](https://arxiv.org/html/2410.24164v1)
- [UniAD](https://arxiv.org/abs/2212.10156)
