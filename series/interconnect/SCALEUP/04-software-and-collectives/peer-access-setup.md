# CUDA 与 HIP 对端访问：先查询能力，再建立有效路径

上级：[软件与集体通信](README.md)

对端访问 API 把硬件能力与软件地址空间连接起来。正确流程需要分别处理能力查询、访问启用、数据依赖和资源撤销。仅查看拓扑图不能代替 API 返回值。

## 建立 A 访问 B 的方向

下面是概念伪代码，不是可直接编译的 CUDA／HIP 程序。真实程序还要检查每一步错误，并按所用内存分配接口管理权限。

```text
选择发起设备 A
查询 A 是否能够访问 B
若支持：启用 A 到 B 的对端访问
若不支持：明确选择受支持的中转方案，或报告不支持
在 B 上生产数据，并建立生产完成到 A 访问之间的依赖
在 A 上使用 B 的有效缓冲，等待规定的完成事件
所有使用者完成后，撤销访问并释放资源
```

CUDA 常用 `cudaDeviceCanAccessPeer` 与 `cudaDeviceEnablePeerAccess`；HIP 提供对应的 `hipDeviceCanAccessPeer` 与 `hipDeviceEnablePeerAccess`。启用方向是当前设备访问对端，不应据此假设 B→A 已同时启用。[CUDA 对端接口](https://docs.nvidia.com/cuda/cuda-driver-api/cuda_driver_api/group__CUDA__PEER__ACCESS.html)、[HIP 对端接口](https://rocm.docs.amd.com/projects/HIP/en/latest/doxygen/html/group___peer_to_peer.html)

## 访问成功以后，仍需验证什么

| 验证项 | 为什么需要 |
| --- | --- |
| 普通访问与原子能力 | 能读写不代表支持所需的跨设备原子操作 |
| 分配类型及进程边界 | 单进程对端启用不能代替跨进程句柄导入 |
| 生产者与消费者依赖 | 地址有效不代表数据已经生产完成 |
| 实际传输路径 | 拓扑、平台策略或库选择可能影响路径 |
| 销毁顺序 | 释放资源前必须停止并完成在途使用 |

虚拟内存管理 API、托管内存和进程间共享可能有各自规则。本文流程解释职责，使用时应查目标 CUDA／HIP 版本及分配方式。

## 内核访问与搬运引擎不是同一实验

GPU 内核直接读取对端缓冲，会消耗执行和访存资源。显式异步复制可能使用不同的搬运路径。两者即使访问相同字节，也可能有不同并发、请求粒度和计时边界。

测试时先选择一种路径，验证结果，再扫描消息大小和并发。若不支持直接访问，主机缓冲中转需要两段明确的搬运和同步，不是交换机自动补出的透明路径。相关平台限制见[PCIe P2P](../../PCIE/07-advanced-topics/p2p-switch-topology-constraints.md)。
