# NoC Wiki Summary

这页只保留章节和文件级入口，用于骨架确认。

## 01 Overview

- [README](./01-overview/README.md)
- [problem-statement](./01-overview/problem-statement.md)
- [bus-vs-noc-vs-crossbar](./01-overview/bus-vs-noc-vs-crossbar.md)
- [learning-roadmap](./01-overview/learning-roadmap.md)
- [taxonomy](./01-overview/taxonomy.md)

## 02 Router Microarchitecture

- [README](./02-router-microarchitecture/README.md)
- [packet-flit-phit-hierarchy](./02-router-microarchitecture/packet-flit-phit-hierarchy.md)
- [router-pipeline-stages](./02-router-microarchitecture/router-pipeline-stages.md)
- [input-buffer-organization](./02-router-microarchitecture/input-buffer-organization.md)
- [virtual-channel-fundamentals](./02-router-microarchitecture/virtual-channel-fundamentals.md)
- [allocator-design-vc-switch](./02-router-microarchitecture/allocator-design-vc-switch.md)
- [credit-based-flow-control](./02-router-microarchitecture/credit-based-flow-control.md)
- [wormhole-vs-vct-vs-store-forward](./02-router-microarchitecture/wormhole-vs-vct-vs-store-forward.md)
- [router-power-area-tradeoff](./02-router-microarchitecture/router-power-area-tradeoff.md)

## 03 Topology

- [README](./03-topology/README.md)
- [topology-design-metrics](./03-topology/topology-design-metrics.md)
- [mesh-and-torus](./03-topology/mesh-and-torus.md)
- [ring-and-hierarchical-ring](./03-topology/ring-and-hierarchical-ring.md)
- [tree-and-fat-tree](./03-topology/tree-and-fat-tree.md)
- [crossbar-and-concentrated-mesh](./03-topology/crossbar-and-concentrated-mesh.md)
- [flattened-butterfly-dragonfly](./03-topology/flattened-butterfly-dragonfly.md)
- [topology-physical-realization](./03-topology/topology-physical-realization.md)
- [topology-selection-framework](./03-topology/topology-selection-framework.md)

## 04 Routing And Flow Control

- [README](./04-routing-and-flow-control/README.md)
- [routing-algorithm-classes](./04-routing-and-flow-control/routing-algorithm-classes.md)
- [dimension-order-routing](./04-routing-and-flow-control/dimension-order-routing.md)
- [deadlock-avoidance-turn-model](./04-routing-and-flow-control/deadlock-avoidance-turn-model.md)
- [adaptive-routing-tradeoffs](./04-routing-and-flow-control/adaptive-routing-tradeoffs.md)
- [source-routing-for-deterministic-systems](./04-routing-and-flow-control/source-routing-for-deterministic-systems.md)
- [arbitration-policies](./04-routing-and-flow-control/arbitration-policies.md)
- [qos-and-priority-classes](./04-routing-and-flow-control/qos-and-priority-classes.md)
- [deadlock-livelock-starvation](./04-routing-and-flow-control/deadlock-livelock-starvation.md)

## 05 System Integration

- [README](./05-system-integration/README.md)
- [ni-network-interface-design](./05-system-integration/ni-network-interface-design.md)
- [address-map-and-routing-table](./05-system-integration/address-map-and-routing-table.md)
- [dma-engine-noc-interaction](./05-system-integration/dma-engine-noc-interaction.md)
- [traffic-patterns-and-characterization](./05-system-integration/traffic-patterns-and-characterization.md)
- [multiple-physical-networks](./05-system-integration/multiple-physical-networks.md)
- [noc-meets-memory-system](./05-system-integration/noc-meets-memory-system.md)
- [noc-vs-bus-revisited](./05-system-integration/noc-vs-bus-revisited.md)

## 06 AI NoC Specifics

- [README](./06-ai-noc-specifics/README.md)
- [why-ai-noc-is-different](./06-ai-noc-specifics/why-ai-noc-is-different.md)
- [broadcast-multicast-tree](./06-ai-noc-specifics/broadcast-multicast-tree.md)
- [reduction-and-collective-networks](./06-ai-noc-specifics/reduction-and-collective-networks.md)
- [deterministic-noc-and-static-scheduling](./06-ai-noc-specifics/deterministic-noc-and-static-scheduling.md)
- [tile-architecture-and-noc](./06-ai-noc-specifics/tile-architecture-and-noc.md)
- [memory-centric-noc](./06-ai-noc-specifics/memory-centric-noc.md)
- [chiplet-and-die-to-die-interconnect](./06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md)
- [compiler-noc-co-design](./06-ai-noc-specifics/compiler-noc-co-design.md)
- [workload-gemm-on-noc](./06-ai-noc-specifics/workload-gemm-on-noc.md)
- [workload-attention-prefill](./06-ai-noc-specifics/workload-attention-prefill.md)
- [workload-attention-decode-kv-cache](./06-ai-noc-specifics/workload-attention-decode-kv-cache.md)
- [workload-moe-routing](./06-ai-noc-specifics/workload-moe-routing.md)

## 07 Evaluation Methodology

- [README](./07-evaluation-methodology/README.md)
- [metrics-latency-throughput-saturation](./07-evaluation-methodology/metrics-latency-throughput-saturation.md)
- [from-workload-to-traffic-trace](./07-evaluation-methodology/from-workload-to-traffic-trace.md)
- [modeling-layers-analytical-event-cycle](./07-evaluation-methodology/modeling-layers-analytical-event-cycle.md)
- [power-area-modeling](./07-evaluation-methodology/power-area-modeling.md)
- [stall-taxonomy-and-attribution](./07-evaluation-methodology/stall-taxonomy-and-attribution.md)
- [architecture-exploration-loop](./07-evaluation-methodology/architecture-exploration-loop.md)
- [case-card-template](./07-evaluation-methodology/case-card-template.md)

## 08 Simulator Construction

- [README](./08-simulator-construction/README.md)
- [simulator-design-spec](./08-simulator-construction/simulator-design-spec.md)
- [core-data-structures](./08-simulator-construction/core-data-structures.md)
- [event-driven-vs-cycle-accurate](./08-simulator-construction/event-driven-vs-cycle-accurate.md)
- [router-pipeline-pseudocode](./08-simulator-construction/router-pipeline-pseudocode.md)
- [traffic-injection-and-tracing](./08-simulator-construction/traffic-injection-and-tracing.md)
- [verification-and-calibration](./08-simulator-construction/verification-and-calibration.md)
- [implementation-roadmap](./08-simulator-construction/implementation-roadmap.md)

## 09 Reference

- [README](./09-reference/README.md)
- [glossary](./09-reference/glossary.md)
- [checklists](./09-reference/checklists.md)
- [high-frequency-questions](./09-reference/high-frequency-questions.md)
- [noc-design-decision-tree](./09-reference/noc-design-decision-tree.md)
