# OSAT 版图:ASE/Amkor/JCET/通富/华天

上级:[产业地图](README.md)
相关:[全球产业链全景图](industry-chain-overview.md), [大陆先进封装瓶颈](mainland-china-bottlenecks.md), [终测与可靠性](../05-final-test-and-reliability/README.md)

## 这页在回答什么问题

OSAT 在先进封装中承担什么角色，ASE、Amkor、JCET、通富、华天这类厂商如何从传统封测扩展到 Fan-out、2.5D、bridge、3D 和测试可靠性。

## OSAT 的角色变化

传统 OSAT 主要承担 assembly 与 final test。先进封装把 OSAT 的角色推向更复杂的系统集成：高密度 RDL、Fan-out、2.5D/3D、bridge、HBM 相关组装、热机械控制、中间测试和可靠性验证。

```text
traditional assembly/test
  -> high-density package platform
  -> chiplet / HBM / AI-HPC system integration
```

OSAT 的价值不只在产能，也在工艺窗口、材料协同、测试能力和多客户服务经验。

## 国际 OSAT

| 公司 | 公开对象与证据 | 能支持的结论 |
| --- | --- | --- |
| ASE | [2022-06-01 VIPack 公告](https://ase.aseglobal.com/press-room/vipack/) | 厂商当日列出 FOCoS、FOCoS-Bridge、FOPoP、FOSiP、TSV 2.5D/3D 和 CPO 等平台组成；不证明某客户良率 |
| Amkor | [2022-09-22 S-SWIFT 资料](https://amkor.com/blog/heterogeneous-ic-packaging-optimizing-performance-and-cost/) | 当时描述 substrate 上的高密度 fan-out 工艺及资格验证阶段；后续量产状态另查 |

## 大陆 OSAT

| 公司 | 公开对象与证据 | 待核验 |
| --- | --- | --- |
| JCET 长电科技 | [2024 年报](https://www.jcetglobal.com/uploads/%26e9%2695%26bf%26e7%2694%26b5%26e7%26a7%2691%26e6%268a%26802024%26e5%26b9%26b4%26e5%26b9%26b4%26e6%268a%26a5.pdf)披露 XDFOI 系列进入量产及应用领域 | 具体客户、产品、批量和合格率未在本表确立 |
| 通富微电 | 待核实具体产品与原厂披露 | 指定工艺、资格阶段、交付与良率 |
| 华天科技 | 待核实具体产品与原厂披露 | 指定工艺、资格阶段、交付与良率 |

平台声明、研发、样片、资格和持续出货分别是不同证据层级。比较必须使用同一产品类别、时间与良率分母。

## OSAT 与 foundry packaging 的差异

Foundry packaging 更容易和先进逻辑节点、PDK、DFT、chip-package co-design 直接耦合。OSAT 的优势是服务多来源 die、多客户、多封装形态，但它需要和客户、foundry、memory、基板和材料设备共同建立接口。

## 一句话理解

OSAT 正从封装测试服务商变成先进封装系统集成平台，但高端 AI/HPC 能力取决于 RDL/bridge/2.5D/3D 工艺、测试可靠性和客户导入深度。

## 架构师启示

架构师选择 OSAT 路线时，要确认的不只是封装形式可做，还要确认材料窗口、substrate 配套、KGD 交接、中间测试、热机械仿真和 failure analysis 是否能支撑目标产品。
