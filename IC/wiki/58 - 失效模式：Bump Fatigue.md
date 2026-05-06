# 失效模式：Bump Fatigue

上级：[[48 - 失效模式层：先进封装常见失效总览]]

相关：[[19 - Hybrid Bonding vs Micro-bump]]、[[28 - 先进封装测试：Wafer Sort、KGD、中测、Final Test]]

## 这是什么

Bump fatigue 指的是焊点或微凸点在反复热循环、机械应力或工作载荷下逐渐疲劳，最终导致连接失效。

常见对象包括：

- solder bump
- micro-bump
- Cu pillar 相关连接

## 为什么会发生

因为 bump 本身就在承受：

- 电连接
- 机械连接
- 热膨胀不匹配引起的反复应力

一旦经历很多轮：

- 制造热过程
- 温度循环
- 通电发热

疲劳就会积累。

## 哪些场景更怕它

- 大尺寸 package
- 热循环频繁产品
- CTE mismatch 明显的平台
- 需要长期高可靠性的高价值封装

## 为什么 advanced packaging 特别在意它

因为高级封装里：

- die 更贵
- stack 更复杂
- 局部连接更多
- 返工更难

所以一个 bump 失效的代价会比传统封装大得多。

## 它和 micro-bump / hybrid bonding 的关系

### 对 micro-bump

它是非常现实的一类可靠性挑战。  
这也是为什么 micro-bump 虽然成熟，但在极端条件下仍会被疲劳问题约束。

### 对 hybrid bonding

hybrid bonding 不是“没有可靠性问题”，只是问题机制不再完全等同于传统 bump fatigue。

## 你应该怎么用这个概念

当你分析：

- 高温
- 多次热循环
- 大尺寸封装
- 明显 CTE mismatch

时，就应该把 bump fatigue 放进风险列表。

