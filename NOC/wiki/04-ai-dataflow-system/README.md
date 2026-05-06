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
- [Physical Realization 与 Floorplan-Aware NoC](./physical-realization-floorplan-aware-noc.md)
- [GEMM Case Study](./workload-gemm-case-study.md)
- [Attention Prefill Case Study](./workload-attention-prefill-case-study.md)
- [Attention Decode Case Study](./workload-attention-decode-case-study.md)
- [MoE Case Study](./workload-moe-case-study.md)

## 一句话总纲

对 AI 芯片来说，NoC 不是独立层，而是数据流执行的一部分。只要把 NoC 脱离 `tile / SRAM / DMA / HBM / mapping` 来看，判断就很容易失真。
