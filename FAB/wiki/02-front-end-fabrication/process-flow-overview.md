# 前道工艺的整体节奏:FEOL/MOL/BEOL

上级:[前道工艺](./README.md)
相关:[前道与后道:产业分工和技术差异](../01-overview/front-end-vs-back-end.md), [光刻:把版图变成芯片的核心步骤](./photolithography-fundamentals.md), [BEOL 的金属互联:从 M0 到 redistribution](./interconnect-stack-beol.md)

## 这页在回答什么问题

前道制造为什么是一套反复“图形化、加工、平整化、连接”的节奏，而不是一次性把电路印出来。理解这个节奏，可以解释为什么设计规则、层数、良率和 PPA 会相互牵制。

## 整体流程图

一个简化的 front-end fabrication flow 可以写成：

```text
wafer preparation
  -> FEOL
       isolation / well / channel / gate / source-drain
  -> MOL
       contact / local interconnect
  -> BEOL
       repeated metal/via layers
  -> top metal / pad / passivation
  -> wafer sort preparation
```

每一层的基本节奏接近：

```text
deposit or grow material
  -> coat photoresist
  -> expose pattern by lithography
  -> develop resist
  -> etch / implant / plate / modify exposed area
  -> strip / clean
  -> CMP when planarity is needed
```

这不是为了制造“漂亮的层”，而是为了把版图里的几何图形转成可工作的材料结构。越先进的节点，图形越小、层数越多、overlay 越难、工艺窗口越窄，单个设计选择越容易在多个步骤里放大成 PPA 或良率问题。

## FEOL: 先让硅变成可控开关

FEOL 负责形成 transistor。它包括隔离结构、well、channel、gate stack、source/drain、应力工程等。架构师关心 FEOL，不是为了调 implant 条件，而是为了理解器件结构决定电压、频率、漏电、变异性和密度边界。

Planar 到 FinFET 再到 GAAFET 的演化，本质是为了在更短 channel 下保持更强 gate control。若 gate 控制不够，短沟道效应会让漏电和阈值控制恶化，节点继续缩小就不能稳定换来可用 PPA。

## MOL: 器件到金属栈的瓶颈区

MOL 把 transistor 连接到上方金属互联。它包括 contact、local interconnect 和早期金属层附近的连接结构。MOL 的物理尺度小、电流密度高、寄生效应敏感，所以它常常是先进节点里器件性能和布线能力之间的狭窄过渡区。

架构师在逻辑图上看到的是 gate 和 wire；物理上，中间必须经过 contact 和 local routing。若局部互联拥塞或 contact 电阻偏高，标准单元密度提高不一定完整转化为时序收益。

## BEOL: 让晶体管组成系统

BEOL 负责多层金属互联。底层金属细密，服务标准单元内部和局部连接；中间层服务模块级 routing；顶层金属更厚，服务长距离互联、时钟、供电和封装接口。BEOL 不是“连线而已”，它决定 NoC、BUS、SRAM 周边、clock tree、PDN 和 top-level floorplan 的物理代价。

和 BUS wiki 的 [互连组件与数据路径分解](../../BUS/wiki/04-microarchitecture-integration/interconnect-components.md) 对应，逻辑上的 decoder、arbiter、buffer 和 return path 最终都需要落到 BEOL 金属资源上。宽总线和复杂 NoC 如果忽略物理 routing，会在时序、功耗和拥塞上付出代价。

## PPA 影响表

| 工艺区段 | 主要物理变量 | PPA 影响 | 架构问题 |
| --- | --- | --- | --- |
| FEOL | 器件结构、Vt、漏电、变异性 | frequency、leakage、Vmin | 高性能库和低功耗库如何选 |
| MOL | contact 电阻、local routing 密度 | cell delay、局部 IR、面积 | 标准单元密度是否能转成性能 |
| BEOL lower metal | 细线 RC、拥塞、via 阻抗 | local timing、logic routing | 控制逻辑和 SRAM 周边是否拥塞 |
| BEOL upper metal | 长线 RC、EM、IR drop | NoC latency、clock、PDN | 宽 NoC/总线/供电网是否可实现 |
| top interface | pad/bump pitch、passivation | package attach、I/O floorplan | die 边界如何服务封装 |

## 常见误解

常见误解是“前道主要决定 transistor，互联问题留给后道”。实际 die 内互联由 BEOL 决定，且在先进节点中 wire delay、via、拥塞和 IR drop 经常比 transistor 本身更限制系统频率。

另一个误解是“标准单元密度提升等于芯片面积同比下降”。实际面积还受 SRAM、模拟、I/O、macro、routing channel、power grid、keep-out 和物理收敛影响。节点越先进，这些非理想项越需要在架构估算中显式保留。

## 一句话理解

前道工艺是一套反复图形化与材料加工的分层构造过程，FEOL 做开关，MOL 做接入，BEOL 把开关连成系统。

## 架构师启示

如果我在模型中把 NoC bisection bandwidth 翻倍，不能只乘一个 link 数量。BEOL 视角会问：这些 link 走哪几层金属，是否挤占 clock/PDN，长线 RC 和 repeater 代价是多少，跨 macro routing 是否破坏 floorplan。

因此，架构模型至少要把 compute/memory macro 的面积和片上互联的物理实现分开估算。否则模型可能认为 bandwidth 只是逻辑参数，真实物理设计却在 metal stack 上失败。
