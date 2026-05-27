# 研究视角与产业视角的差异

上级：[09 研究前沿](README.md)
相关：[08 产业与产品](../08-industry-and-products/README.md), [指标术语表](metrics-glossary.md), [CIM/PIM/NMC 分类](../01-overview/cim-pim-nmc-taxonomy.md)

## 这页在回答什么问题

这页回答：为什么很多 CIM/PIM/NMC 论文非常有价值，却不能直接推出“这条路线已经可以商业化”。

研究论文的目标是隔离一个难点并证明新的解决方式。产业产品的目标是把所有难点同时闭环。CIM 论文可以只证明一个 macro 的 ADC 能效、一个 ReRAM compensation scheme、一个 HBM-PIM kernel mapping；产品必须同时处理制造测试、良率、软件栈、客户模型、接口、热和维护。

最常见的误读来自层级混淆：

| 论文层级 | 研究价值 | 不能直接推出 |
| --- | --- | --- |
| device/cell | 新存储机制、conductance 控制、retention/endurance | 可运行完整神经网络 |
| macro | array、SA/ADC、local accumulation、bitline compute 可行 | chip/system 端到端收益 |
| test chip | 工艺和电路实测可信度提高 | 客户可部署产品 |
| architecture simulator | dataflow、tiling、mapping 策略有效 | 真实 PVT/DFT/driver 成熟 |
| system prototype | 某类 workload 可跑通 | 广泛模型和长期维护可行 |

08 和 09 的分工也不同。08 问“这个对象怎么交付给客户”；09 问“这个对象推进了哪一个研究问题”。Samsung HBM-PIM 在 08 里要看 memory vendor、HBM 产品线、controller/runtime 和客户验证；在 09 里要看 bank-level compute 对 memory-bound kernel 的建模方式、offload granularity、host stall 与 system-level energy。

研究视角还必须承认 benchmark selection 的影响。CIM 论文更容易在 weight-stationary、低精度、阵列满载、数据复用高的 workload 上表现好；PIM 论文更容易在 bandwidth-bound kernel 上表现好。若论文没有说明 workload、precision、是否包含外围、是否包含 data movement，指标就不能跨论文比较。

## 一句话理解

研究论文证明“一个难点有解法”，产业产品证明“所有难点能一起交付”。

## 研究启示

读 CIM/PIM/NMC 论文时，第一步不是抄指标，而是标注层级、taxonomy、memory technology、compute paradigm、workload 和包含的开销。只有这样，论文结果才能被用于研究判断，而不是误导成产业成熟度判断。
