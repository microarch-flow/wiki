# 从模块化到共享 BEV：驾驶系统改变了哪些接口

上级：[专题导读](README.md)

<span id="modular-to-bev-evolution" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么模块化会被取代直觉与类比" class="workload-legacy-anchor"></span>
<span id="从-bev-到-occupancy接口继续变宽" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


自动驾驶系统需要从观测得到可执行的车辆动作。模块化、共享 BEV 和端到端描述不同的组织维度，并不是一条旧方法必然被新方法取代的单线历史。

## 模块化把责任放在接口上

一种常见分解是感知、跟踪、预测、规划和控制。感知输出目标或道路结构；跟踪关联跨帧身份；预测估计其他参与者的未来；规划选择自车轨迹；控制把轨迹转换成执行命令。

明确接口便于单独测试和替换模块，但中间表示可能丢弃下游需要的信息。误差还可能被后续模块放大，因此模块指标与整车结果都要观察。

## 共享表示减少了什么

BEV 把多视角特征组织到统一平面坐标，多个任务可以共享这份表示。它可减少重复编码，也可让规划读取目标框之外的场景信息。

但共享 BEV 没有自动取消模块边界。系统仍可使用独立检测头、预测头和传统规划器；也可联合训练多个任务。共享特征、联合训练与直接输出控制量是三个不同选择。

## 端到端的范围要写全

“端到端”可以指从图像到检测集合，也可以指从传感器到轨迹或控制。必须指出输入、输出和联合优化的范围。UniAD 以规划为导向连接多个任务模块，仍保留结构化中间结果。

构造例：两个系统都输出未来 3 s 的轨迹。系统 A 先输出目标列表，再由优化器规划；系统 B 从共享特征直接预测轨迹。若 B 仍需车辆控制器执行，它就不是从像素直接输出电机命令。

## 比较收益需要相同条件

应固定传感器、训练数据、地图/导航信息、历史长度和评估协议。更好的开放环轨迹误差不自动证明更好的闭环行驶；新增监督也可能解释一部分收益。

本文提供接口地图。学习专家动作的目标见[行为克隆](behavior-cloning-e2e.md)，任务间耦合见[规划导向端到端](planning-oriented-e2e.md)，传感器到 BEV 的几何机制见 [BEV 感知](../02-vision-and-3d-perception/bev-perception.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [端到端驾驶早期案例 DAVE-2](https://arxiv.org/abs/1604.07316)
- [Lift-Splat-Shoot](https://arxiv.org/abs/2008.05711)
- [UniAD](https://arxiv.org/abs/2212.10156)
