# 04 AI Dataflow 系统视角

本章把 NoC 放回 AI accelerator 系统里，而不是单独讨论网络。

## 本章入口

- [AI Dataflow NoC vs CPU Coherent NoC](./ai-vs-cpu-noc.md)
- [NI / DMA / 存储接口](./ni-dma-memory-interface.md)
- [流量模式](./traffic-patterns.md)
- [Collective Communication](./collective-communication.md)
- [Memory-Centric NoC](./memory-centric-noc.md)
- [KV Cache / Decode Memory Path 深化](./kv-cache-decode-memory-path.md)
- [SRAM Bank Conflict / Local Memory System](./sram-bank-conflict-local-memory-system.md)
- [DMA Engine / Request-Response Scheduling](./dma-engine-request-response-scheduling.md)
- [CPU/Cache Coherent NoC 对照专题](./cpu-cache-coherent-noc-reference.md)
- [Collective Implementation 深化](./collective-implementation-deep-dive.md)
- [多网络组织（Multi-Network NoC）](./multi-network-organization.md)
- [Broadcast / Multicast / Reduction 网络](./broadcast-multicast-reduction-network.md)
- [Physical Realization 与 Floorplan-Aware NoC](./physical-realization-floorplan-aware-noc.md)
- [Tile 微架构与 NoC 接口](./tile-architecture-noc-interface.md)
- [地址空间与路由映射](./address-map-routing.md)
- [Chiplet 与 Die-to-Die 互连](./chiplet-die-to-die-interconnect.md)
- [GEMM Case Study](./workload-gemm-case-study.md)
- [Attention Prefill Case Study](./workload-attention-prefill-case-study.md)
- [Attention Decode Case Study](./workload-attention-decode-case-study.md)
- [MoE Case Study](./workload-moe-case-study.md)

## 读本章前先统一 7 个词

- `dataflow`：数据由谁产生、在哪里暂存、何时搬运、被谁复用的执行组织方式
- `tile`：一个基础计算块，通常带本地算力和本地存储
- `DMA`：负责批量搬运数据的引擎，不直接做计算
- `mapping`：把逻辑计算任务映射到哪些 tile、SRAM 或 NoC 资源上
- `memory path`：一次访存从请求发出、仲裁、返回到被端点消费的完整依赖路径
- `placement`：数据、算子、memory port 在物理阵列里的放置位置
- `critical path`：会直接决定下一步能否继续执行的关键依赖路径

如果读到 `KV cache / response path / bank conflict / ejection` 这类词会停顿，建议同时开着 [术语表](../06-reference/glossary.md)。

## 一句话总纲

对 AI 芯片来说，NoC（片上网络）不是独立层，而是数据流执行的一部分。只要把 NoC 脱离 `tile（计算单元） / SRAM（片上静态存储） / DMA（直接内存访问引擎） / HBM（高带宽存储器） / mapping（映射策略）` 来看，判断就很容易失真。
