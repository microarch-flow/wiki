# 公司全景对比矩阵：技术路线 × 产品阶段 × 应用定位

上级：[08 产业与产品](README.md)
相关：[公司卡片](company-cards/README.md), [产业全景](industry-landscape.md), [CIM/PIM/NMC 分类](../01-overview/cim-pim-nmc-taxonomy.md)

## 这页在回答什么问题

这页回答：如何用同一套产业口径比较 CIM/PIM/NMC 公司，而不是把不同层级的宣传指标横向相除。

| 公司/对象 | 角色 | Taxonomy | Memory technology | Compute paradigm | 产品层级 | 目标市场 | 软件栈成熟度 | 主要产业风险 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Mythic M1076/M2000 路线](company-cards/cim-companies-mythic.md) | AI chip startup | CIM | Flash/analog memory | analog + digital control | chip/IP/roadmap，含汽车联合开发 | edge、automotive、defense、future data center | 官方强调 compiler/SDK、ONNX/PyTorch/TensorFlow 支持 | analog 校准、汽车级验证、重启后路线兑现 |
| [Axelera Metis/Europa](company-cards/cim-companies-axelera.md) | AI accelerator startup | CIM | SRAM | digital CIM + RISC-V dataflow | chip、M.2、PCIe card、compute board | edge vision、industrial、retail、robotics、edge server | Voyager SDK、model zoo、可购买硬件 | 软件生态、模型覆盖、片上 SRAM 容量与产品代际 |
| [Samsung HBM-PIM](company-cards/pim-companies-samsung-hbm-pim.md) | memory vendor | PIM | HBM DRAM | bank-level digital/vector compute | HBM memory technology + accelerator test platform | HPC/AI memory-bound kernels | 需要 GPU/controller/runtime 支持 | 标准化、客户 qualification、HBM 产品线优先级 |
| [SK hynix GDDR6-AiM/AiMX](company-cards/pim-companies-sk-hynix-aim.md) | memory vendor | PIM | GDDR6 DRAM | memory-chip compute + card-level control | GDDR6-AiM sample、AiMX prototype card | LLM inference demo、AI/HPC | 需要 AiM control/runtime | 从 prototype/demo 到客户部署仍需证明 |
| [UPMEM DPU/DIMM](company-cards/nmc-companies-upmem.md) | near-data memory/system vendor | NMC 对照 | DDR4 DRAM module with DPU | programmable RISC near-data | DIMM/server platform/SDK | database、analytics、memory-bound kernels | C/Rust SDK、host+DPU 编程模型 | host/DPU 数据划分、同步、生态规模 |

比较时要先标注指标层级：

| 指标层级 | 可以比较什么 | 不能比较什么 |
| --- | --- | --- |
| macro-level | array 能效、ADC/DAC 开销、cell 非理想性 | 客户可部署性 |
| chip-level | peak TOPS、片上容量、I/O、功耗 | system-level TCO |
| card/module-level | host bandwidth、thermal、driver、form factor | cell-level energy/MAC |
| system-level | workload latency、energy/query、软件接入 | 单个 macro 的物理上限 |

CIM 公司适合看 energy/MAC、片上权重容量、量化精度、校准和模型覆盖；PIM 公司适合看 bandwidth、energy/byte、host offload、memory command 和 controller/runtime；NMC 公司适合看 host-DPU 数据划分、DMA、同步和系统吞吐。把这些指标混在一起排名，会得到错误结论。

## 一句话理解

公司矩阵的目的不是评冠军，而是先把产品层级和 taxonomy 对齐。

## 产业启示

CIM/PIM/NMC 的产业成熟度不能用一个 TOPS/W 数字概括。越接近客户部署，软件栈、接口、热、供应链和可维护性越重要；越接近 cell/array，制造、校准和误差容忍越重要。
