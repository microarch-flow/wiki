# DMA 与异步数据搬运

<span class="micro-legacy-anchor" id="dma-wiki"></span>
<span class="micro-legacy-anchor" id="这套-wiki-的边界"></span>
<span class="micro-legacy-anchor" id="维护原则"></span>


把一块数据从内存搬进阵列输入槽，软件交给 DMA 一项任务。顺着这块数据，可以看到引擎怎样算地址、限制同时在途的数据量，最后通知下一位使用者。


<span class="micro-legacy-anchor" id="dashboard"></span>
<span class="micro-legacy-anchor" id="快速开始"></span>
<span class="micro-legacy-anchor" id="路线-1第一次学-dma"></span>
<span class="micro-legacy-anchor" id="路线-2想把-dma-engine-学透"></span>
<span class="micro-legacy-anchor" id="路线-3想从软件和系统角度建立判断"></span>

## 从哪里开始

如果你从[两个分块的搬入、计算与写回](../06-task-control/dma-compute-writeback.md)读到这里，先把视线停在图里的「搬入」方框。里面的引擎要等到哪一步，才敢告诉阵列整块可读？

### 沿一项 DMA 搬运读四篇 {#dma-first-reads}

1. [一条 DMA 描述符，为什么会变成多笔读写请求？](./02-fundamentals/address-descriptor-burst.md)　跟一笔跨越 4 KiB 边界的 32 B 复制，数出读请求、写请求和数据拍。
2. [矩阵每行隔着一段空隙，DMA 怎样只搬有效数据？](./03-dma-microarchitecture/multidimensional-stride-dma.md)　把同样的搬运换成三行，跟踪哪几个字节要复制，哪几个填充字节要原样保留。
3. [后发的 DMA 请求先回来，数据怎样放回正确的位置？](./03-dma-microarchitecture/scheduling-outstanding.md)　让后一行先返回，看引擎把数据放进哪个槽，以及下一个请求何时能发出。
4. [DMA 已经取走描述符，软件现在能复用缓冲区吗？](./04-programming-model/queues-doorbells-completions.md)　把四槽提交队列填满再回卷，分别找出描述符槽和数据缓冲能交还给软件的时刻。

想先弄清设备地址、缓存一致性，可以按[基础学习顺序](./01-overview/learning-roadmap.md)补前置。要选择 IP、分析端口压力或定位超时，可以从[按目标导航](./01-overview/goal-oriented-navigation.md)跳到对应的案例与查阅资料。全部文章按章节列在[知识地图](./SUMMARY.md)。


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

DMA 专题负责一项搬运如何提交、推进、通知和回收。[第一块还在算，第二块能开始搬吗？](../06-task-control/dma-compute-writeback.md)负责多个引擎之间的依赖与 buffer 所有权。存储器件与互连协议分别由存储、互连系列展开；此处保留影响搬运的接口条件。
