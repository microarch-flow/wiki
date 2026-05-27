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

| 公司 | 公开平台/方向 | 产业位置 |
| --- | --- | --- |
| ASE | VIPack、FOCoS、FOCoS-Bridge、2.5D/3D、CPO | 高端 OSAT 平台型玩家 |
| Amkor | SWIFT、S-SWIFT、S-Connect、advanced SiP | Fan-out、bridge-like、高密度多芯片封装 |

ASE 的 VIPack 把 FOCoS、FOCoS-Bridge、FOPoP、FOSiP、2.5D/3D 和 CPO 放入一个先进封装平台叙事中。Amkor 的 S-SWIFT 强调 fan-out on substrate、RDL 缩短 D2D 连接、高 I/O 密度和 interposer-less 方向。

## 大陆 OSAT

| 公司 | 公开方向 | 判断重点 |
| --- | --- | --- |
| JCET | XDFOI、Fan-out、高密度异构集成、部分 2.5D/3D 表达 | 平台表达完整度、客户导入、量产深度 |
| 通富微电 | 高性能处理器封装、Chiplet、2.5D/3D 布局 | 高端客户经验、AI/HPC 相关承接能力 |
| 华天科技 | WLP、Fan-out、2.5D/3DIC 平台建设 | 先进封装平台上移和量产窗口 |

大陆 OSAT 的关键问题不是“有没有先进封装项目”，而是是否能在 AI/HPC 高价值场景中形成稳定良率、完整材料设备配套、客户导入和中间测试闭环。

## OSAT 与 foundry packaging 的差异

Foundry packaging 更容易和先进逻辑节点、PDK、DFT、chip-package co-design 直接耦合。OSAT 的优势是服务多来源 die、多客户、多封装形态，但它需要和客户、foundry、memory、基板和材料设备共同建立接口。

## 一句话理解

OSAT 正从封装测试服务商变成先进封装系统集成平台，但高端 AI/HPC 能力取决于 RDL/bridge/2.5D/3D 工艺、测试可靠性和客户导入深度。

## 架构师启示

架构师选择 OSAT 路线时，要确认的不只是封装形式可做，还要确认材料窗口、substrate 配套、KGD 交接、中间测试、热机械仿真和 failure analysis 是否能支撑目标产品。
