# 封装内的信号完整性

上级:[跨工艺共性问题](README.md)
相关:[PI、PDN、Decap:供电完整性](power-delivery-pi-pdn-decap.md), [2.5D 路线](../04-back-end-packaging/2.5d-routes/README.md), [HBM 如何把产业逼向 2.5D 和 3D](../04-back-end-packaging/hbm-as-case-study/why-hbm-forces-2.5d-3d.md)

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

## 一句话理解

封装内 SI 决定高速信号在 RDL、interposer、bump、TSV 和 substrate 中能否以足够低噪声、低损耗、低串扰稳定到达接收端。

## 架构师启示

架构师定义 D2D、HBM 和 SerDes 时，要同步定义链路距离、placement、带宽密度、功耗和可测试性。接口协议看似能跑，若封装 return path、串扰和 PDN 噪声无法闭合，最终产品仍会失败。
