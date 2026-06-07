# 02 · Datapath 基础:从逻辑门到数据搬运成本

本章自底向上搭出 AI 算力的最小单元,并暴露它真正的成本结构。读完你会明白:**算术单元很便宜、且能靠降精度二次变便宜;真正贵的是把数据搬到它面前(mux 选数)。** 这正是下一章 systolic array 要解决的问题。

## 篇目

1. **[从逻辑门搭出一个 MAC](./multiply-accumulate-from-gates.md)**
   为什么乘加是矩阵乘长出来的天然原语;精度非对称(乘低/累加高)的两个独立理由;`full adder 数 = p×q` 的代数闭合。

2. **[压缩树与进位结构:Wallace、Dadda、最终加法器](./dadda-and-adder-trees.md)** `[补全]`
   carry-save 为何避开进位链;Wallace vs Dadda 的面积取舍;final CPA 的进位结构(ripple/CLA/prefix)如何决定关键路径。

3. **[面积随位宽二次缩放](./quadratic-bitwidth-scaling.md)**
   面积 ∝ 位宽²;Nvidia 从线性标称改口 B300 的 FP4 3×;为什么 AI 降位宽而不用 Strassen 这类减乘法数的算法。

4. **[AI 的数字格式:INT8/FP8/FP4/bf16/MX 与 fungibility](./number-formats-for-ai.md)** `[补全]`
   离散格式的电路差异;bf16 的"保范围砍精度"哲学;MX 共享 exponent 如何改写搬运账;fungibility 为何让"FP4=2×FP8"不是精确比例。

5. **[mux 与数据搬运成本](./mux-and-data-movement-cost.md)**
   datapath 的真问题:24p 搬运 vs 4p 计算;为什么加大 RF 会被反噬;mux 是全域反复出现的分母原语。

## 本章在主线上的位置

- §1、§3、§4 处理**分子**:MAC 是分子的原子,二次律和数字格式让分子的单位成本变小。
- §2、§5 处理**分母**:压缩树是加法这件"通信"的优化;mux 是 datapath 上分母的第一次正式登场,给出 1:6 的劣势比值。

→ 比值劣势怎么翻转?进入 [03 · systolic array](../03-systolic-array/)。
