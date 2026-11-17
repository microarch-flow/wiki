# NCCL 与 RCCL：通信组、执行依赖和底层路径怎样连接

上级：[软件与集体通信](README.md)

NCCL 和 RCCL 向应用提供集体通信及点对点原语。它们负责把指定参与者的数据操作映射到受支持的设备与传输路径。应用仍需保证参与者、数据布局和调用依赖正确。

## 一次调用的输入与结果

以 AllReduce 为例，输入包括通信组、每个 rank 的输入缓冲、元素数量、数据类型、归约算子和执行流。输出是在各参与者的输出缓冲中取得约定归约结果。基础语义见[集体通信基础](../../NOC/06-ai-noc-specifics/collective-communication-basics.md)。

| 应用需要确定 | 库需要完成 |
| --- | --- |
| rank 与设备绑定、通信组 | 建立通信状态和可用路径 |
| 匹配的操作、数量、类型和顺序 | 选择受支持的算法、分块和传输 |
| 输入已经就绪 | 在流依赖满足后执行通信 |
| 输出后续如何使用 | 提供符合接口的执行及错误状态 |

参与者调用不匹配可能导致等待或错误。把一个 rank 放错设备也会改变拓扑；NCCL 明确不支持同一 communicator 中用同一 CUDA 设备充当多个 rank。[通信组创建规则](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html)

## API 返回不等于 GPU 已经完成

按 NCCL 的[流语义](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/streams.html)，通常调用在操作入队后返回，设备异步执行。后续消费者应使用同一流的顺序或明确的跨流事件依赖。主机只测 API 调用时间，通常测到的是提交开销，而不是完整通信时间。

非阻塞 communicator、分组调用和异步错误处理还具有专门规则，不能只用一个返回成功值覆盖所有情况。RCCL 的接口使用及版本支持应查其[官方文档](https://rocm.docs.amd.com/projects/rccl/en/latest/what-is-rccl.html)。

## 算法、传输与拓扑分开看

Ring、tree 等描述数据怎样分步交换；NVLink、xGMI、PCIe 或网络描述可用承载。两者之间由库选择和映射，不能把“运行 NCCL”当作“必然使用 NVLink”或“必然运行 ring”。

诊断先记录库版本、设备拓扑、通信组及配置，再查看库日志和性能测量。强制某种算法可以用于对照实验，但在一个消息大小上获胜，不说明它适合所有规模。具体映射见[集体通信到硬件](collective-mapping-and-offload.md)。
