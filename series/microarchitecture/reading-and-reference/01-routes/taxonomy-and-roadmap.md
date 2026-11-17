# 从门电路到系统：阅读路线与专题边界

<span class="micro-legacy-anchor" id="学习路线与域边界原语-阵列-流水-布局"></span>
<span class="micro-legacy-anchor" id="这页在回答什么问题"></span>
<span class="micro-legacy-anchor" id="2-章节地图"></span>
<span class="micro-legacy-anchor" id="3-域边界compute-不重写什么"></span>
<span class="micro-legacy-anchor" id="4-怎么读三种进入路径"></span>
<span class="micro-legacy-anchor" id="5-本篇在主线上的位置"></span>
<span class="micro-legacy-anchor" id="建模启示"></span>


上级：[从门电路到 AI 计算单元](./README.md)


<span class="micro-legacy-anchor" id="1-为什么自底向上"></span>

## 为什么自底向上

这条路线每次引入一个约束：MAC 如何产生结果；选择网络如何取得操作数；阵列如何复用数据；流水线如何推进；存储和互连如何供数。完整步骤见[路线导读](./README.md#主线与章节地图)，此处不再复制章节表。

固定工作量和边界流量时，改变流水深度不会自动改变 MAC/B，却可能改变频率、延迟、面积与能量。

## 专题边界

| 主归属 | 负责的内容 | 相邻接口 |
| --- | --- | --- |
| 运算与并行执行 | 运算格式、数据路径、PE 映射与数据流 | 操作数请求、结果、各边界字节 |
| 指令与任务控制 | 发射、提交、跨引擎依赖和资源释放 | 就绪、完成、取消、错误 |
| DMA | 描述符、事务展开、搬运与完成接口 | 存储端口、互连服务、消费者可见性 |
| 存储系统 | cache、SRAM、DRAM、控制器 | 请求、响应、bank/端口争用 |
| 互连 | 事务、路由、仲裁和流控 | 到达、接纳、反压与完成 |
| 存内与近存计算 | 计算位置、阵列参与方式和宏到系统成本 | 数据编码、转换、同步和回传 |
| 芯片开发与实现 | 工艺、物理设计、验证和签核 | 面积、时序、功耗及证据 |

模型可以折叠内部细节，但要验证折叠后仍保留所研究的瓶颈。例如用固定延迟替代拥塞网络，只适用于该近似已被验证的流量范围。

## 按问题选入口

研究指令何时执行，从[依赖与发射](../../03-instruction-execution/dependencies-bypass-issue.md)开始。研究连续供数，从[跨引擎协作](../../06-task-control/dma-compute-writeback.md)开始。研究仿真器，从[指标定义](../02-analysis/compute-communication-ratio.md)与[建模建议](../03-modeling/modeling-insights.md)开始。

CPU、GPU、NPU 的路线由[系列首页](../../README.md)统一维护；本页保留原有公开入口，职责是解释跨专题边界。
