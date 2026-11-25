# 芯片与系统互连

一次通信可能同时涉及事务语义、网络转发和物理链路。本系列从片上延伸到封装、设备与系统网络，分别解释各个边界上的问题。

## 一次访问会经过哪些边界

主机要从加速卡的片上内存（SRAM）读回数值 42。假设卡内的桥把 PCIe 请求转换为 AXI 读，再经片上网络送往 SRAM。卡边已经收到请求，这时 42 到了哪里？从系列第一课[《一次跨桥读取：设备已经收到请求，主机为什么还在等？》](PCIE/wiki/06-workloads-case-studies/pcie-vs-axi-noc-boundary.md)跟着这笔读走一个来回。

想把桥交出地址的那一刻放大到逐拍看，接着读[《地址已经收下，数据为什么还没回来？》](BUS/wiki/02-fundamentals/transaction-address-data-response.md)。要沿着这笔读追进卡内，看地址如何到达 SRAM、42 如何回到桥，读[《一次读取怎样变成 NoC 里的请求包和返回包？》](NOC/wiki/05-system-integration/ni-network-interface-design.md)。再加一个同时读 SRAM 的端点，试试[两笔读能同时通过吗？](NOC/wiki/01-overview/bus-vs-noc-vs-crossbar.md)

如果目标在另一颗芯粒上，可以转到[封装内芯粒互连](D2D/wiki/README.md)。如果两台服务器上的四张 GPU 都在等同一次求和，可以沿着每一块数据逐方向数，看改变通信顺序后，哪个网卡出口要多送一份。[四张 GPU 做一次 AllReduce，哪个出口最忙？](SCALEUP/wiki/04-software-and-collectives/four-gpu-allreduce-egress.md)

## 从问题选择专题

1. [片上事务与总线（BUS）](BUS/wiki/README.md)　[地址已经收下，数据为什么还没回来？](BUS/wiki/02-fundamentals/transaction-address-data-response.md)
2. [片上网络（NoC）](NOC/wiki/README.md)　[一次读取怎样变成 NoC 里的请求包和返回包？](NOC/wiki/05-system-integration/ni-network-interface-design.md)
3. [封装内芯粒互连](D2D/wiki/README.md)　[一次跨芯粒的寄存器读，什么时候才算完成？](D2D/wiki/ucie-pcie-read.md)
4. [系统 I/O 互连（PCIe）](PCIE/wiki/README.md)　[主机第一次读卡上的寄存器，地址是怎么来的？](PCIE/wiki/03-configuration-enumeration-addressing/config-space-bar-capability.md)
5. [一致性与内存互连](COHERENCE/wiki/README.md)　[内存里还是 0，为什么 B 能读到 A 写的 1？](COHERENCE/wiki/01-foundations/coherence-invariants.md)
6. [加速器互连](SCALEUP/wiki/README.md)　[GPU A 能访问 GPU B 的地址，什么时候才能读？](SCALEUP/wiki/01-access-semantics/address-mapping-and-permissions.md)
7. [系统网络](NETWORK/wiki/README.md)　[同样发 4 KiB，TCP 和 RDMA 什么时候能复用缓冲区？](NETWORK/wiki/01-foundations/host-nic-data-path.md)
8. [高速电链路（SerDes）](SERDES/wiki/README.md)　[一个 32 位字怎样穿过 SerDes，又怎样拼回来？](SERDES/wiki/01-overview/link-end-to-end.md)
9. [共封装光学（CPO）](CPO/wiki/README.md)　[一个比特怎样从电路进入光纤，再回到电路？](CPO/wiki/04-optical-engine/optical-link-basics.md)

前七项按通信场景和系统问题组织，后两项关注链路实现与集成。这个顺序供入门参考，不表示它们互斥，也不规定一种固定协议栈。

## 相关系列

- [半导体与电路基础](foundations/README.md)　接收端选定采样时刻后，输入还需要稳定多久？从锁存器看边沿附近的时间窗口。[时钟边沿附近发生了什么](foundations/latch-and-divider/README.md#timing)
- [计算微架构的 DMA 专题](DMA/wiki/README.md)　一条搬运命令会展开成多笔读写。当多个引擎共用缓冲，任务还要等数据就绪才能消费。[DMA 描述符与总线请求](DMA/wiki/02-fundamentals/address-descriptor-burst.md) · [搬入、计算与写回的依赖](microarchitecture/06-task-control/dma-compute-writeback.md)
- [存储系统](storage.md)　核心读一个地址时，缓存怎样把整行取回来？先知道副本怎么产生，再看两个核心怎样协调写权限。[缓存行的首次填充](RAM/wiki/07-system-architecture/cache-hit-lookup.md#first-fill)
- [推理运行时](series/inference-runtime/README.md)　模型切到多张卡上以后，哪些并行方式会引入通信？[集群并行与通信边界](series/inference-runtime/topics/11-cluster-parallelism.md)
