# 驾驶行为克隆：模仿轨迹为何不等于闭环成功

上级：[专题导读](README.md)

<span id="behavior-cloning-e2e" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效又为什么会崩直觉与类比" class="workload-legacy-anchor"></span>
<span id="基本形式与输出接口" class="workload-legacy-anchor"></span>
<span id="与-planning-oriented-e2e-的差别" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


行为克隆（BC）用示范数据监督策略输出。对驾驶任务，输出可以是控制量、航点或带时间的轨迹。BC 是训练目标，不是与“规划”互斥的系统结构。

## 训练样本中包含什么

输入通常包含传感器观测、历史状态和导航条件，目标来自专家动作或轨迹。构造训练对时必须保持时间和坐标一致，并说明目标是否使用了未来真值。

简化回归目标为：

$$
\mathcal L_{\rm BC}=\mathbb E_{(o,c,a^*)\sim D}
\|\pi_\theta(o,c)-a^*\|^2
$$

$c$ 可以是导航指令。实际轨迹模型可能采用多模态分布、分类或其他损失；平方误差只是一个例子。

## 平均轨迹为什么可能不可用

在路口，向左绕过障碍和向右绕过障碍都可能合理。若监督存在多种选择，单一均方误差回归可能预测两条路线的平均，恰好指向障碍。输出多模态候选或条件化决策可以缓解，但仍需选择与约束机制。

导航条件也不能省略。同一视觉场景在“左转”和“直行”任务下对应不同动作；不给条件却要求唯一正确输出，问题本身就不充分。

## 分布偏移来自执行反馈

训练数据主要覆盖专家到过的状态。部署中的小误差会改变位置、视角和其他车辆反应，使策略进入训练分布外的状态。离线回放固定了环境轨迹，不能完整暴露这种累积。

DAgger 展示了通过策略访问状态并追加专家标注来处理这类问题的思路。驾驶场景中的数据收集仍需明确测试范围与监督方式，不能把算法框架直接当作道路安全方案。

<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 评价和工作负载

离线可检查航点误差、速度与转向分布；闭环应检查任务完成、碰撞、越界、舒适性及恢复行为。低误差可能来自路线或历史运动的强先验，需用输入消融确认模型实际使用了哪些信息。

运行时可是一遍前向，也可以生成多候选再筛选。训练采用 BC 并不能决定推理调用数。共享方法见[模仿学习与强化学习](../decision-and-policy/imitation-and-reinforcement-learning.md)，系统成本见 [E2E 工作负载](../06-chip-workload-analysis/e2e-workload.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [DAgger](https://arxiv.org/abs/1011.0686)
- [DAVE-2](https://arxiv.org/abs/1604.07316)
- [UniAD](https://arxiv.org/abs/2212.10156)
