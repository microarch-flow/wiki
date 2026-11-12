# 封装内的信号完整性

上级:[跨工艺共性问题](README.md)
相关:[PI、PDN、Decap:供电完整性](power-delivery-pi-pdn-decap.md), [2.5D 路线](../04-back-end-packaging/2.5d-routes/README.md), [HBM 如何把产业逼向 2.5D 和 3D](../04-back-end-packaging/hbm-as-case-study/why-hbm-forces-2.5d-3d.md), [SerDes：电信号与通道](../../../series/interconnect/SERDES/wiki/02-signal-channel/README.md)

## 这页在回答什么问题

封装内信号完整性关注什么，为什么高密度 D2D、HBM、SerDes 和 RDL/interposer routing 会让 return path、阻抗、串扰和损耗成为架构约束。

## SI 关注的不是“线连上”

Signal Integrity 关注信号在目标频率、目标电压和目标误码率下能否稳定传输。封装互连越长、越密、越高速，寄生电阻、电容、电感、阻抗不连续、串扰和回流路径问题越重要。

```text
driver -> package interconnect -> receiver
          R / L / C / return path / crosstalk
```

一条线在 DC 上导通，不代表高速下可用。

## 封装内 SI 的关键变量

| 变量 | 影响 |
| --- | --- |
| Interconnect length | 延迟、损耗、功耗 |
| Line/space | 串扰、routing density、阻抗控制 |
| Return path | 回流不连续会导致噪声和辐射 |
| Bump/TSV/via | 寄生和阻抗不连续 |
| Die-to-die placement | 链路长度和拓扑 |
| Power/ground quality | jitter、噪声耦合、误码 |

2.5D 的价值之一就是缩短 logic-to-HBM 或 chiplet-to-chiplet 距离，但这不自动解决所有 SI 问题。高密度 routing 反而会放大串扰和回流路径要求。

## 反射手算：终端阻抗为什么影响电压

假设均匀无损传输线特性阻抗 `Z0 = 50 Ω`，末端为纯电阻 `RL`，入射阶跃幅度 `Vi = 0.2 V`。终端电压反射系数 `ΓL = (RL − Z0)/(RL + Z0)`。这是首个波到达负载时的局部计算；尚未包括源端二次反射、频率相关损耗或串扰。

- `RL = 50 Ω` 时 `ΓL = 0`，负载首次阶跃为 `0.2 V`。
- `RL = 100 Ω` 时 `ΓL = 1/3`，首次负载阶跃为 `Vi(1+ΓL) ≈ 0.267 V`，比匹配时高约 `67 mV`。
- `RL` 开路时 `ΓL = 1`，首次负载阶跃为 `0.4 V`；是否会越限取决于器件规格与后续波形。

如果 `RL = 100 Ω ± 10 Ω` 而 `Z0` 固定，`ΓL` 约在 `0.286–0.375`，首次电压约 `0.257–0.275 V`。阻抗误差因此会传播到门限裕量，但无法仅由它推出 BER；还需要眼图、噪声、码型、均衡和接收判决条件。

## HBM 与 D2D 的差异

HBM 接口强调近距、超宽、并行和较低每 bit 能耗。它依赖 interposer/RDL 提供大量短距连接。D2D chiplet 链路可能更关注延迟、带宽密度、功耗和可扩展拓扑。SerDes 则更关注高速通道损耗、均衡、阻抗和封装到板级路径。

| 链路 | 主要 SI 关注点 |
| --- | --- |
| HBM interface | 宽接口、短距、串扰、PI/SI 耦合 |
| Chiplet D2D | 延迟、带宽密度、bump pitch、回流路径 |
| SerDes | 通道损耗、反射、均衡、封装/板级连续性 |

## SI 与 PI 的耦合

高速信号需要稳定参考平面和回流路径。电源/地噪声会变成 jitter 和误码，信号切换也会反过来制造电源噪声。封装内 SI 和 PI 不是两张独立图，而是同一组金属、介质、bump、TSV 和 substrate 的不同表现。

## 测试与诊断

SI 问题在 final test 中可能表现为接口误码、频率上不去、温度升高后不稳定、某些 traffic pattern 下失败。诊断时需要结合 pattern、温度、电压、链路训练、错误计数和物理路径。

如果在规定发送、接收和均衡条件下观察到误码，下一步取决于具体 HBM、D2D 或 SerDes 协议与实现：例如已有纠错可修正部分错误，已定义的重传或训练策略才可产生重传或重训。不同协议不一定都提供这些机制。没有阈值、动作和时间参数时，只报告眼图或误码余量，不能自动加入固定罚时或降速。

## 一句话理解

封装内 SI 决定高速信号在 RDL、interposer、bump、TSV 和 substrate 中能否以足够低噪声、低损耗、低串扰稳定到达接收端。

## 架构师启示

架构师定义 D2D、HBM 和 SerDes 时，要同步定义链路距离、placement、带宽密度、功耗和可测试性。接口协议看似能跑，若封装 return path、串扰和 PDN 噪声无法闭合，最终产品仍会失败。
