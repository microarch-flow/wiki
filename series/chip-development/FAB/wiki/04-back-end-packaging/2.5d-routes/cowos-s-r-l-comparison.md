# CoWoS-S、R、L 的互连平台有何不同

<span class="micro-legacy-anchor" id="cowos-srl-的真正差别"></span>

上级：[2.5D 路线](README.md)
相关：[硅中介层](si-interposer-fundamentals.md) · [局部硅桥](embedded-bridge-emib-and-cowos-l.md) · [RDL 结构](../key-components/rdl-redistribution-layer.md)

<span class="micro-legacy-anchor" id="不要理解成线性替代"></span>

## 这页在回答什么问题

CoWoS 是 TSMC 的封装家族。三种变体的关键区别是哪些结构承担全局布线，哪些结构承担局部连接。 [TSMC CoWoS 官方平台](https://3dfabric.tsmc.com/schinese/dedicatedFoundry/technology/cowos.htm)

## 根本区别

| 变体 | 全局互连平台 | 选型时检查 |
| --- | --- | --- |
| CoWoS-S | 硅中介层 | 可用布线、平台尺寸、垂直互连、供电与制造限制 |
| CoWoS-R | RDL 中介层 | RDL 层、材料、信号路径、封装尺寸与测试 |
| CoWoS-L | RDL 中介层结合局部硅互连 | 局部硅互连的位置和密度、与全局 RDL 的配合及装配 |

## CoWoS-S

芯粒和 HBM 堆栈位于硅中介层上。硅中介层上的结构提供细密互连，并经垂直连接与基板交接。面积、走线资源、热机械和供电条件要按实际配置评估。

## CoWoS-R

铜线和聚合物介质构成 RDL 中介层。连线、电源和机械条件来自该 RDL 工艺与封装组合。系统应核对在目标尺寸、堆栈数量和布线密度下是否可行。

## CoWoS-L

全局平台使用 RDL，并嵌入局部高密度硅互连（LSI）。互连图要分别标出 LSI 上的局部连接和 RDL 上的全局连接。实际走线、电源、去耦和结构取决于所采用的变体。

## 对照表

以上表格按公开结构比较。若要得出容量、成本或良率结论，固定产品的芯粒面积、数目、接口、供电、热边界、规模与时期，再比较可实现方案。官方平台资料提供候选结构。客户的实际报价、良率与出货需要单独证据。 [TSMC 2024 年报平台说明](https://investor.tsmc.com/static/annualReports/2024/english/ebook/files/basic-html/page100.html)

<span class="micro-legacy-anchor" id="架构师启示"></span>

## 一句话理解

S 采用硅中介层，R 采用 RDL 中介层，L 将 RDL 平台和局部硅互连结合。架构选型沿着实际连线、热和供电路径检查。
