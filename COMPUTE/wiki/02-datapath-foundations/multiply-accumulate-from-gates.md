# 从逻辑门搭出一个 MAC:为什么乘加是 AI 芯片的天然原语

上级:[02 · datapath 基础](./README.md)
相关:[压缩树:Wallace 与 Dadda](./dadda-and-adder-trees.md)、[面积随位宽二次缩放](./quadratic-bitwidth-scaling.md)、[mux 与数据搬运成本](./mux-and-data-movement-cost.md)
主线:[计算 / 通信比](../01-overview/compute-communication-ratio.md)——本篇是"分子"(有用计算)的最小构造单元。

---

## 这页在回答什么问题

为什么 AI 芯片的基本算术单元偏偏是 **multiply-accumulate(乘加,MAC)**,而不是单独的乘法器或加法器?这不是工程惯例,而是矩阵乘自己长出来的结论。本篇从一个逻辑门开始手工搭出一个 MAC,顺带回答两个常被混淆的问题:乘法和累加为什么用**不同**精度,以及一个 MAC 到底要花多少门。

---

## 1. MAC 是矩阵乘的最内层循环

矩阵乘的本质是三重循环:

```
for i:
  for k:
    for j:
      out[i,k] += in[i,j] * w[j,k]   # 每一步:乘了再累加 = 一次 MAC
```

**因为** 每一个最内层迭代恰好是"乘一次、累加进结果",**所以** MAC 不是被人为选出来的原语——它是矩阵乘的最内层循环体本身。AI 负载的算术几乎全是矩阵乘(全连接、卷积、attention 的 QK/AV),所以把 MAC 固化进硬件,就是把分子的单位运算固化进硬件。

> 这也是为什么后面 systolic array 的思路是"把这个三重循环再往上提两层固化"——见 [why-systolic-array](../03-systolic-array/why-systolic-array.md)。MAC 是上提的起点。

---

## 2. 精度非对称:乘法用低精度,累加用高精度

一个常被当成"经验法则"记住、实则有硬物理依据的设计:**乘法用低位宽(如 4-bit×4-bit),累加用高位宽(如 8-bit 甚至更高)。** 两个**独立**的理由:

1. **误差沿求和链累积**。累加沿 j 维重复 j 次,每次都引入一次舍入误差,误差会沿这条求和链累积;而乘法链上每个输出只经过**一次**乘法,几乎不累积误差。所以累加路径对精度更敏感。
2. **数值范围**。j 个乘积相加,结果的动态范围比单个乘积大得多,需要更多位来容纳。

> ⚠️ 常见误解:以为"累加要高精度"只因为结果数值更大。数值范围只是理由之一,**更本质的是误差沿求和链累积**——即使数值不溢出,低精度累加也会因反复舍入而劣化结果。这两个理由独立成立,缺一不可。

**所以** "4-bit × 4-bit 乘 + 8-bit 累加"是有物理依据的非对称设计,不是随手定的位宽。这个非对称还会在 [number-formats-for-ai](./number-formats-for-ai.md) 里以"FP8 累加用更高精度的 partial sum"的形式再次出现。

---

## 3. 手工推导:一个 4×4 MAC 要花多少门

把 `1001 × ????` 用长乘法摊开,顺手把 8-bit accumulator 一起加进来:

```
        1 0 0 1            ← 被乘数(p=4 位)
      × ? ? ? ?            ← 乘数(q=4 位,逐位)
      ---------
        1 0 0 1            ← 部分积 0(乘数第 0 位 = 1)
      0 0 0 0              ← 部分积 1(乘数第 1 位 = 0)
    1 0 0 1                ← 部分积 2
  0 0 0 0                  ← 部分积 3
+ a a a a a a a a          ← accumulator 一并加入(8 bit)
  -----------------
        (一个 8-bit 五路求和)
```

只需**两类门**:

### 3.1 AND 门生成部分积

每个部分积比特 = (被乘数某位) AND (乘数某位)。p 位 × q 位的乘法需要 **p×q 个 AND 门**(本例 4×4 = 16 个)。这是整个乘法器里唯一"做乘法"的部分,而且便宜。

### 3.2 Full adder(3→2 compressor)做求和

求和的主体是 **full adder**。关键认识:它**不是**软件里那种 32-bit 加法器。一个 full adder 把同一比特位上的 **3 个 1-bit 数**压成 **2 bit 输出**(sum + carry)——本质是"数一列里有几个 1,用二进制表达"。

```
   a  b  cin            3 个 1-bit 输入
    \ | /
   [full adder]
    /     \
  sum     carry         2 bit 输出 = (a+b+cin) 的二进制
```

沿每一列反复用 full adder,每次吃掉 3 个数、吐出 2 个数(其中 carry 进位到高一列),直到每列只剩 1 个数。这套"逐层压缩部分积"的组织方式就是 [Wallace / Dadda 压缩树](./dadda-and-adder-trees.md),本篇先把它当黑盒,下一篇展开 Wallace vs Dadda 的差别。

---

## 4. 一个漂亮的代数闭合:full adder 数 = p×q

数一下用了几个 full adder。**每用一次 full adder 净消掉 1 个比特**(3 进 2 出),所以:

```
full adder 数 = 起始比特数 − 输出比特数
            = (p×q + (p+q)) − (p+q)
            = p×q
```

部分积 p×q 个比特,加上 accumulator 的 p+q 个比特;最后输出 p+q 个比特。一减,**accumulator 项完全抵消**,full adder 数恰好 = p×q。

这正是选 **MAC(而非纯乘法)** 作为原语的第二个理由:把 accumulator 一起算进去,得到这么干净的 p×q 代数——加法器规模由乘法规模决定,累加几乎"免费搭车"。

> ⚠️ 严谨边界:`full adder 数 = p×q` 是**首阶估计**,不是精确恒等式。压缩过程中产生的进位会反馈进各列的高度,实际 full adder 数受列高度分布与压缩调度(Wallace 还是 Dadda)影响,会在 p×q 附近小幅波动。这个优雅结论用来建立直觉极好,但精确计数要看具体压缩树——见 [dadda-and-adder-trees](./dadda-and-adder-trees.md)。

---

## 5. 这一节的收束:乘法器面积 ∝ p×q

把 §3、§4 合起来:AND 门 p×q 个、full adder ~p×q 个,所以**乘法器面积正比于 p×q**。当 p、q 同步缩放(位宽减半),面积 ∝ 位宽²,降到 1/4 而非 1/2。这条二次律是低精度算术对 AI 如此有效的根本原因,单独成篇展开:[quadratic-bitwidth-scaling](./quadratic-bitwidth-scaling.md)。

---

## 6. 本篇在主线上的位置

MAC 是[计算 / 通信比](../01-overview/compute-communication-ratio.md)的**分子的原子**——一次有用计算的最小硬件构造。它本身很便宜(p×q 量级门)。主线的张力还没出现:要等到把 MAC 塞进一个带 register file 的单元、付出 mux 选数的代价时,分母才登场(见 [mux-and-data-movement-cost](./mux-and-data-movement-cost.md))。本篇确立的是:**分子便宜,且可以靠降位宽二次变便宜。**

---

## 建模启示

- **可折叠到一个面积权重**:对性能/面积建模,一个 MAC 单元可折叠成两个数——`area ∝ p×q`(门当量)和 `precision`(位宽)。门级的 AND/full-adder 结构不必逐个仿真。
- **必须显式建模的状态变量**:乘法位宽 `p`、`q` 与累加位宽 `acc_bits`(三者独立)。把累加位宽折叠进乘法位宽会丢掉精度非对称这一真实约束——它影响数值正确性,也影响累加器的面积与反馈环关键路径(见 [feedback-loop-clock-constraint](../04-clocking-and-pipeline/feedback-loop-clock-constraint.md))。
- **关心吞吐/面积时可折叠**:压缩树的具体拓扑、进位结构 → 折叠成面积常数。
- **关心频率上限时必须保留**:累加路径的精度决定了累加器的关键路径长度,这是频率的硬约束之一,不能折叠。
- **事件/数据结构草图**:`MAC{p, q, acc_bits}` → 派生 `area = k·p·q`、`theoretical_macs += 1`。`theoretical_macs` 正是计算 / 通信比的分子,应作为可审计物理量累加。
