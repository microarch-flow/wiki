# DMA 与异步数据搬运

<span class="micro-legacy-anchor" id="dma-wiki"></span>
<span class="micro-legacy-anchor" id="这套-wiki-的边界"></span>
<span class="micro-legacy-anchor" id="维护原则"></span>


DMA 把搬运任务展开为地址、事务和完成事件。理解它需要同时检查数据路径、并发容量、可见性和资源回收。


<span class="micro-legacy-anchor" id="dashboard"></span>
<span class="micro-legacy-anchor" id="快速开始"></span>
<span class="micro-legacy-anchor" id="路线-1第一次学-dma"></span>
<span class="micro-legacy-anchor" id="路线-2想把-dma-engine-学透"></span>
<span class="micro-legacy-anchor" id="路线-3想从软件和系统角度建立判断"></span>

## 从哪里开始

第一次学习，按[基础学习顺序](./01-overview/learning-roadmap.md)建立前置知识。已有具体工程问题，使用[按目标导航](./01-overview/goal-oriented-navigation.md)。全部文章索引见[知识地图](./SUMMARY.md)。


<span class="micro-legacy-anchor" id="工作台"></span>
<span class="micro-legacy-anchor" id="学习"></span>
<span class="micro-legacy-anchor" id="分析"></span>
<span class="micro-legacy-anchor" id="查阅"></span>

## 阅读顺序

1. [概览与问题定义](./01-overview/README.md)
2. [基础对象与传输语义](./02-fundamentals/README.md)
3. [DMA 引擎微架构](./03-dma-microarchitecture/README.md)
4. [软件栈与编程模型](./04-programming-model/README.md)
5. [系统集成](./05-system-integration/README.md)
6. [性能建模与调优](./06-performance-modeling/README.md)
7. [工作负载与案例](./07-workloads-case-studies/README.md)
8. [DMA IP 与产业视角](./08-industry-ip/README.md)
9. [参考资料与研究模板](./09-reference-research/README.md)

## 与任务控制的边界

DMA 专题负责一项搬运如何提交、推进、通知和回收。[DMA、计算与写回如何协作](../06-task-control/dma-compute-writeback.md)负责多个引擎之间的依赖与 buffer 所有权。存储器件与互连协议分别由存储、互连系列展开；此处保留影响搬运的接口条件。
