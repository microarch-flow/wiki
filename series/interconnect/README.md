# 芯片与系统互连

主机向加速卡请求一个数，卡边已经收到请求，还要等谁取回数据？从[第一次跨桥读取](PCIE/06-workloads-case-studies/pcie-vs-axi-noc-boundary.md)跟这笔请求走一个来回。已经熟悉单机数据路径的读者，可以直接算[四张 GPU 的一次 AllReduce](SCALEUP/04-software-and-collectives/four-gpu-allreduce-egress.md)，看两台服务器之间哪个出口最忙。

1. [片上事务与总线（BUS）](BUS/README.md)：事务、握手、仲裁与桥接。
2. [片上网络（NoC）](NOC/README.md)：路由、缓冲、流控与拓扑。
3. [封装内芯粒互连](D2D/README.md)：跨 die 的接口、链路和协议承载。
4. [系统 I/O 互连（PCIe）](PCIE/README.md)：设备枚举、地址与事务。
5. [一致性与内存互连](COHERENCE/README.md)：缓存副本、一致性协议与设备内存访问。
6. [加速器互连](SCALEUP/README.md)：加速器间的访问语义、交换结构、软件通信与任务性能。
7. [系统网络](NETWORK/README.md)：端点、Ethernet/IP、RDMA、RoCE、InfiniBand 与网络性能。
8. [高速电链路（SerDes）](SERDES/README.md)：发送、接收、训练与验证。
9. [共封装光学（CPO）](CPO/README.md)：光引擎、封装和系统集成。

源码目录与网站发布路径分别配置。现有文章保留历史公开路径。

## 专题目录约定

- 每个专题使用根目录的 `README.md` 作为正文入口；文章、章节和图片放在该专题内。
- `SUMMARY.md` 只在需要单独维护文章索引时使用，不要求每个专题都创建。
- 专题根目录中的 `AGENTS.md` 是适用于该专题的协作说明，不是正文。
- 历史维护资料单独归档，不作为现行正文维护。

已归档的互连历史资料见 [历史资料索引](../../docs/archive/interconnect/README.md)。
