# 失效模式：Bonding Defect

上级：[[48 - 失效模式层：先进封装常见失效总览]]

相关：[[19 - Hybrid Bonding vs Micro-bump]]、[[44 - 工艺深水区：Hybrid Bonding]]

## 这是什么

Bonding defect 指的是在 die-to-die、die-to-wafer、wafer-to-wafer 或其他高密度连接过程中，键合界面没有达到设计要求。

这类缺陷可能表现为：

- 对位偏差
- 局部未键合
- 界面污染
- 键合强度不足

## 为什么会发生

典型原因包括：

- 表面平坦度不够
- 界面洁净度不够
- 对位误差
- 薄 die handling 波动
- 工艺窗口太窄

## 为什么它在 advanced packaging 里特别关键

因为越高端的连接方式越依赖“界面质量”本身。

尤其在：

- hybrid bonding
- 超细 pitch
- 3DIC

这些场景里，bonding defect 往往不是局部瑕疵，而是决定：

- 良率
- 带宽
- 长期可靠性

## 它和测试的关系

bonding defect 之所以麻烦，是因为：

- 有时早期不一定完全显性
- stack 后更难直接探到内部界面

所以这类缺陷常常要求：

- 更强的前处理控制
- 更严格的中间测试
- 更完整的可靠性验证

## 你应该怎么用这个概念

以后看到：

- hybrid bonding
- sub-10 µm pitch
- 高价值 3D stack

就应该立刻问：

`这个平台的 bonding defect 最可能怎么出现，怎么被发现，怎么被拦住？`

