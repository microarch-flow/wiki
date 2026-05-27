# 2.5D 路线

上级:[后道封装](../README.md)
相关:[封装分类](../packaging-taxonomy.md), [为什么先进封装变重要](../why-advanced-packaging-now.md), [HBM 作为案例](../hbm-as-case-study/README.md)

## 这页在回答什么问题

2.5D 封装到底解决什么问题，为什么它既不是传统多芯片封装，也不是把 die 直接堆起来的 3DIC。本页给出 2.5D 的核心定义、主要路线和后续阅读顺序。

## 2.5D 的核心定义

2.5D 的关键不是名字里的 “0.5”，而是对象关系：

```text
die / HBM stack
       |
high-density horizontal integration layer
       |
package substrate
```

多个 die 或 HBM stack 并排放置在一个高密度中间互连层上。这个中间层可以是 silicon interposer、RDL interposer，也可以是带局部 silicon bridge 的混合平台。它让横向 die-to-die 或 die-to-HBM 连接比传统 substrate 更短、更密、更可控。

2.5D 与 3D 的分界也在这里。2.5D 的主问题是横向高密度集成；3D 的主问题是垂直堆叠和垂直互连。HBM stack 自身是 3D memory，但 logic die 与 HBM stack 放在 interposer 上形成的系统属于典型 2.5D package。

## 三条主路线

| 路线 | 中间互连平台 | 主要价值 | 主要代价 |
| --- | --- | --- | --- |
| Si interposer | 整块硅中介层 | 极高 routing density、强 HBM 适配、PI/SI 能力强 | 成本、面积、warpage、热机械耦合压力高 |
| Fan-out / RDL | polymer dielectric + Cu RDL | 成本和尺寸弹性更好，I/O 重分配灵活 | 极限密度弱于硅平台，die shift 和 RDL stress 关键 |
| Embedded bridge | 局部硅桥 + 外围 substrate/RDL | 只在关键局部付出硅级互连成本 | 桥区到外围平台的过渡和对位复杂 |

这三条路线不是线性升级关系，而是三组目标函数。Si interposer 追求极限密度，RDL 追求系统折中，bridge 追求局部高密度与全局扩展性的组合。

## 本目录阅读顺序

```text
2.5d-routes
  -> si-interposer-fundamentals
  -> cowos-s-r-l-comparison
  -> cowos-s-complete-process
  -> fan-out-rdl-overview
  -> fan-out-chip-first-vs-chip-last
  -> embedded-bridge-emib-and-cowos-l
  -> 2.5d-routes-tradeoff-map
```

先看 Si interposer，是因为它最清楚地展示了 2.5D 为什么适合 logic + HBM。再看 CoWoS-S/R/L，可以把同一平台族拆成三种不同中间层。随后看 Fan-out/RDL 和 bridge，理解为什么产业不会把所有问题都交给整块硅中介层。最后用 trade-off map 把路线选择方法收束起来。

## 2.5D 的系统边界

2.5D 不是单独的封装工艺标签，而是一组系统边界条件：

| 边界条件 | 它影响什么 |
| --- | --- |
| HBM stack 数量 | package 尺寸、interposer/RDL 面积、热耦合 |
| D2D 接口宽度 | routing density、bump pitch、链路能耗 |
| KGD 策略 | 组合良率、返修价值、报废成本 |
| Substrate 能力 | 全局电源、板级连接、机械支撑 |
| 散热结构 | logic die 功耗、HBM 温度、TIM/lid 设计 |

2.5D 设计失败的根因很少只是某根线画不出来。更常见的失败方式是互连、供电、测试、热和机械目标无法同时闭合。

## 一句话理解

2.5D 用一个高密度中间互连层把并排的 logic、chiplet 和 HBM stack 组织成系统，核心价值是横向带宽和封装级协同。

## 架构师启示

选择 2.5D 时，架构师要先问系统真正需要哪一种密度：全局都需要硅级互连，还是只有局部 die-to-die 链路需要。这个问题会直接决定路线偏向 Si interposer、Fan-out/RDL，还是 embedded bridge。

一个具体判断：如果 compute die 与多颗 HBM stack 之间需要非常宽的低能耗接口，并且封装成本可以接受，Si interposer 会变得合理。若只是几个 chiplet 间有局部高带宽需求，bridge 可能比整块 interposer 更接近真实目标函数。
