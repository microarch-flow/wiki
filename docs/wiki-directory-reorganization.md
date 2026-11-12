# 七系列源码目录调整

## 范围和基线

本次按七个系列整理主仓源码目录。网站的既有发布路径、历史资料和 Git 提交历史保持可用。旧来源仓、第三方原始资料及用户未跟踪文件不在本次移动范围内。

调整前主仓提交为 `e78679753a0d454f541c2307309881e5569a41e4`。该提交的独立干净检出通过严格构建与 17 项网站测试；构建产物包含 887 个页面、17,423 条正文站内引用和 20 个媒体文件，正文站内链接检查没有发现失效。

## 源码目标位置

| 原位置 | 新位置 | 网站暂存路径 |
| --- | --- | --- |
| `BUS/`、`NOC/`、`PCIE/`、`SERDES/`、`CPO/` | `series/interconnect/` 下同名目录 | 原同名路径 |
| `RAM/`、`HBF/` | `series/storage/` 下同名目录 | 原同名路径 |
| `COMPUTE/`、`DMA/`、`CIM/` | `series/microarchitecture/` 下同名目录 | 原同名路径 |
| `electrical-timing-foundations.md` 和 `img/electrical-timing-rc.svg` | `series/microarchitecture/foundations/` 下对应文件 | 原根文章和 `img/` 路径 |
| `FAB/` | `series/chip-development/FAB/` | 原 `FAB/` 路径 |
| 原 `series/chip-development/` 内容 | `series/chip-development/process/` | 原 `series/chip-development/` 路径 |

`series/workload/`、`series/inference-runtime/` 和 `series/chip-architectures/` 保持原源码路径。物理目录按专题整体归档；原有文章的主导航和文件级归属例外不变。

`CIM/`、`FAB/`、`NOC/` 中的 `wiki.old/` 和各目录维护说明随专题保留，不因移动而进入站点。七系列调整时，`reviews/` 的源码目录与公开位置均保留。根目录 `docs/`、`website/`、`.github/`、MkDocs 配置和本地忽略状态不作为正文目录移动。

GitHub Pages 的既有网址通过暂存路径映射保留。GitHub 上指向 `main` 分支旧源码路径的链接不会因 Git 重命名自动跳转；固定提交的历史链接仍可访问。

## 分批结果与验证

路径映射层先在旧目录布局下构建，并与基线对照。随后分别提交互连 `0c34957`、存储 `0b11796`、微架构 `0f40c54` 和芯片开发 `b3172fa` 四批移动。每批均完成严格构建、18 项网站测试及基线对照。

独立检出对照确认：四批完成后的 887 个页面、正文文字、已有锚点、17,423 条正文站内引用、20 个媒体文件、每页搜索记录和当前导航位置与基线一致。对 8,231 处原有源码相对引用，目标、查询参数和片段语义均保留；芯片开发新增的源码入口另有两条有效链接。

目录调整验收时，原有 184 个 `wiki.old/` 跟踪文件经逐个比较，迁移前后字节相同。原有提交没有被改写；BUS、NoC、CIM 和 FAB 等抽样文件的 `git log --follow` 可追溯到移动前。

源码检查发现一处基线已有的历史失效链接：`series/microarchitecture/CIM/wiki.old/SUMMARY.md` 指向 `../chat.md`。后续检查了本地副本、主仓 Git 历史及来源仓库的可见分支、标签和提交，没有找到该文件。另发现同主题候选对话，但无法确认它与缺失文件一致。归档索引已保留原路径并改为非链接标注；没有补造对话。归档原链接仍可在[来源仓固定提交](https://github.com/microarch-flow/CIM/blob/c532d9fd9b049ccdb3b7c646f3a4d9d44019c839/wiki/SUMMARY.md)中查看。

## 评审记录归档

七系列调整后，跨专题评审材料由根目录 `reviews/` 整体移至 `docs/reviews/`。基线报告、第二轮逐篇评审和第三轮盲测的题面、结果及参考模型继续保留。源码中的链接和盲测运行命令使用新路径。

网站暂存仍将这些文件发布到 `reviews/`，以保留原有网页地址。归档时评审页面仍可在导航和搜索中找到；后续按读者界面要求隐藏了这两个入口，原网址仍可访问。Git 既有提交不作改写；查看旧提交时应使用该提交中的原始路径。

原样移动提交 `e8ccd72` 用于保留逐文件历史。该中间状态尚未更新源码链接和网站构建配置，不能单独构建；检出时应同时包含后续的链接与构建修复提交。
