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

`CIM/`、`FAB/`、`NOC/` 中的 `wiki.old/` 和各目录维护说明随专题保留，不因移动而进入站点。`reviews/` 保留原公开位置。根目录 `docs/`、`website/`、`.github/`、MkDocs 配置和本地忽略状态不作为正文目录移动。

GitHub Pages 的既有网址通过暂存路径映射保留。GitHub 上指向 `main` 分支旧源码路径的链接不会因 Git 重命名自动跳转；固定提交的历史链接仍可访问。
