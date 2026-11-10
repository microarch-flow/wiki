# GPU 与 TPU 的顶层组织：局部资源和跨单元通信

上级：[07 · 芯片顶层组织](./README.md)
相关：[阵列 sizing](../03-systolic-array/array-sizing-tradeoff.md)、[NoC 与存储系统](../../../NOC/wiki/05-system-integration/noc-meets-memory-system.md)

## 芯片资源如何连接

计算阵列、向量处理、局部存储和网络可以按不同粒度分组。每种组织都要回答输入如何到达、结果在哪里归约、资源被谁共享，以及不同负载下阵列能否保持工作。GPU 和 TPU 各有多代实现，不能用一个固定图概括所有产品。

## 两个具体组织

[NVIDIA A100](https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/nvidia-ampere-architecture-whitepaper.pdf) 的 SM 调度 32 线程 warp，包含通用计算路径、寄存器、shared memory 和 Tensor Core。矩阵指令由 warp 协作提供操作数；其他受支持操作仍由相应的通用路径执行。SM 间的数据交换还涉及存储层次和互连。

[Google 第一代 TPU](https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu) 的 MXU 为 256×256 的 8-bit systolic 矩阵单元，配合 accumulator、unified buffer 和 activation 单元执行推理。阵列中权重和数据按指定数据流移动，结果经累加与后续激活处理。它的矩阵单元和 A100 Tensor Core 都承担矩阵运算，但控制、局部存储及数据流不同，不能把完整 SM 等同于 TPU 或把 GPU 定义为 TPU 的平铺。后续代际不可直接沿用上述规模。

## 2. 粗粒度 vs 细粒度：一张对比表

| 问题 | 较大共享阵列的可能代价 | 较小局部阵列的可能代价 |
|---|---|---|
| 面积 | 若外围固定，可摊销部分外围 | 更多外围复制 |
| 利用率 | 小工作块可能空置更多 PE | 小块较易匹配，但大工作需跨单元拆分 |
| 供数与归约 | 共享边界可能发生争用 | 跨单元搬运和归约可能增加 |

这些是候选机制，不是 TPU/GPU 通用的面积比例或带宽参数。以 byte/s、事务量、拓扑和访问轨迹判断某条链路是否为瓶颈。

## 3. MatX 的方向：splittable systolic array

可切分阵列允许一种硬件组织以多个粒度承载工作。比较时应记录可支持的模式、额外互连、分区约束、切换代价和利用率。访谈中的架构方向不能代替目标芯片的实测配置或性能。

## 建模启示

记录资源节点、位置、数据移动边界、各方向带宽、仲裁和每阶段有效计算。按同一工作量分别统计 RF、阵列和芯片外存流量，再评估延迟、吞吐、面积与能耗。阵列尺寸变化可能同时改变这些量，不能从单一门数代理推导其他指标。
