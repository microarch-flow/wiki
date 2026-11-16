# Turn Model 与逃逸资源：怎样限制路由依赖？

上级：[04 路由、仲裁与服务保证](./README.md)

相关：[维序路由](./dimension-order-routing.md)、[死锁、活锁与饥饿](./deadlock-livelock-starvation.md)、[虚通道基础](../02-router-microarchitecture/virtual-channel-fundamentals.md)

<span id="deadlock-avoidance-turn-model"></span><span id="这页在回答什么问题"></span>Turn Model 通过限制可用转向，改变通道之间可能出现的依赖。另一类设计保留满足特定安全条件的逃逸资源。两种方法都需要说明网络、允许路径和资源契约。

## 转向怎样影响依赖

<span id="背景"></span><span id="为什么转弯是关键"></span>在二维 Mesh 中，一个包从某方向进入路由器，再沿另一个方向离开，会形成相应的通道获取关系。若可用转向组合允许资源依赖闭合成环，就需要进一步分析。限制转向可以去掉部分依赖，同时保留一些路径选择。

<span id="常见例子"></span>以下限定有限、无故障、非环绕二维 Mesh；包只走最短路径，不做 U-turn。方向表示**包的行进方向**：X 增大为 East，Y 增大为 North。表中的禁止转向只适用于这组约定。

| 模型 | 路径规则 | 禁止的直角转向 |
| --- | --- | --- |
| West-First | 需要向西时，先走完向西的位移 | N→W、S→W |
| North-Last | 需要向北时，向北位移放在最后 | N→E、N→W |
| Negative-First | 先走完负方向 W、S，再走正方向 E、N | N→W、E→S |

<span id="west-first"></span>例如从 (1,0) 到 (0,1)，West-First 允许 W→N，不允许 N→W。<span id="north-last"></span>从 (0,0) 到 (1,1)，North-Last 允许 E→N，不允许 N→E。<span id="negative-first"></span>从 (0,1) 到 (1,0)，Negative-First 允许 S→E，不允许 E→S。

这些规则在指定模型中限制了通道依赖；实际实现还必须检查可达性、VC 映射和路由规则是否与证明一致。[Glass 与 Ni，The Turn Model for Adaptive Routing](https://researchportal.hkust.edu.hk/en/publications/the-turn-model-for-adaptive-routing-2/)

## 路径选择和安全范围

<span id="它和-dor-的关系"></span><span id="它的收益边界"></span>在上述普通 Mesh 中，XY 为一个源目的对选定一条最短路径；某些 Turn Model 则保留多条合法最短路径。并不是每个源目的对都有多个选择，也不是任意被禁止的转向组合都能保持连通和无死锁。

<span id="它不能自动解决什么"></span>转向规则只处理它所证明的路由资源依赖。请求与响应的协议依赖、端点缓冲、饥饿和有限完成时间需要另行分析。原始 Turn Model 也研究了其他网络与路径范围；上表不能直接套到 Torus、故障 Mesh 或任意非最短规则。

## 逃逸 VC 是什么

<span id="和-escape-vc-的配合"></span>一种教学构造给自适应包保留一个 escape VC 类别，让它遵守已证明无环且可到达目的地的规则；其他 VC 可以使用更灵活的候选。还需保证包在所需状态下能够申请合适的逃逸资源，并检查自适应与逃逸资源之间的依赖。

例如，可以设计只允许从自适应类别进入 escape 类别、进入后继续按安全规则前进的转换，并证明该设计覆盖所有允许路径。这只是可选构造，不是所有正确算法都必须采用的唯一转换规则。不同 VC 仍可共享物理链路，是否得到服务需要相应仲裁；最终到达还依赖公平服务、端点可接收及活锁控制。

<span id="为什么很多-ai-npu-不把它当默认主线"></span><span id="一个工程判断标准"></span>不能只凭“增加一个 escape VC”证明安全，也不应一概要求所有 Turn Model 都配置 escape VC。设计者应先列出允许的路由和资源转换，再针对选定模型完成证明。[Duato，A New Theory of Deadlock-Free Adaptive Routing](https://web.csl.cornell.edu/courses/ece5750/duato.tpds93.pdf)讨论了允许完整通道依赖图有环的自适应路由条件。

<span id="建模启示"></span>模型应记录方向约定、合法转向、候选 VC 和类别转换。无环检查可用于所选模型的充分性分析；若使用其他逃逸证明，需检查该证明要求的完整条件。

<span id="一句话理解"></span>先定义允许的资源获取关系，再证明路由安全；仅有策略名称或 VC 数量不构成证明。
