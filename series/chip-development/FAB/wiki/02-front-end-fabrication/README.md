# 晶圆制造

<span class="micro-legacy-anchor" id="前道工艺"></span>

上级：[FAB 制造与封测](../README.md)

<span class="micro-legacy-anchor" id="一句话理解"></span><span class="micro-legacy-anchor" id="架构师启示"></span>

## 这页在回答什么问题

晶圆制造怎样形成晶体管、接触结构和金属互连？架构与物理实现怎样使用相关约束？

## 前道的主线

先准备晶圆，再按目标工艺反复做薄膜、光刻、刻蚀、材料处理和平坦化。通常将形成晶体管的部分称为 FEOL，将连接器件到金属堆栈的接触结构归入 MOL，将晶圆内的金属互连归入 BEOL。具体边界与层名随工艺而异。封装后道在另一层次完成裸片、载体和板侧连接。 [ASML 芯片制造](https://www.asml.com/en/technology/all-about-microchips/how-microchips-are-made) · [前道与后道](../01-overview/front-end-vs-back-end.md)

<span class="micro-legacy-anchor" id="本章怎么读"></span><span class="micro-legacy-anchor" id="本章正文"></span>

## 阅读顺序

1. [晶圆与硅基底](wafer-the-substrate.md)
2. [FEOL、MOL 与 BEOL](process-flow-overview.md)
3. [光刻的图形转移](photolithography-fundamentals.md)
4. [EUV 与多重图形化](euv-and-multi-patterning.md)
5. [沉积、刻蚀与 CMP](etching-deposition-cmp.md)
6. [掺杂与离子注入](doping-and-ion-implantation.md)
7. [平面晶体管、FinFET 与 GAAFET](transistor-evolution-planar-finfet-gaa.md)
8. [片内 BEOL 互连](interconnect-stack-beol.md)
9. [工艺规则与 PDK](design-rule-and-pdk.md)
10. [工艺节点与 PPA](process-nodes-and-ppa-tradeoffs.md)

## 前道对架构的主要约束

器件结构和电压影响单元表征。存储宏、布局与布线受具体库、层和规则约束。PPA 比较需要注明工艺、标准单元、SRAM、负载、工作点和实现阶段。节点和项目决策见[工艺节点选择](../../../process/01_product_definition_and_architecture/05_process_node_selection.md)。
