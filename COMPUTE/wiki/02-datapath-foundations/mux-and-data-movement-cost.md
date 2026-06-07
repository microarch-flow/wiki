# mux 与数据搬运成本:datapath 的真问题

上级:[02 · datapath 基础](./README.md)
相关:[从门搭 MAC](./multiply-accumulate-from-gates.md)、[算力单元要解决什么问题](../01-overview/problem-statement.md)、[为什么要 systolic array](../03-systolic-array/why-systolic-array.md)
主线:[计算 / 通信比](../01-overview/compute-communication-ratio.md)——本篇让"分母"第一次正式登场,并暴露裸 datapath 上比值的劣势。

---

## 这页在回答什么问题

[从门搭 MAC](./multiply-accumulate-from-gates.md) 证明了 MAC 本身很便宜(p×q 门)。那为什么一个真实的 CUDA core / CPU 标量单元这么大?答案:**把 MAC 塞进一个带 register file 的可编程单元后,绝大部分面积花在"选数"——也就是 mux 上。** 本篇把这笔账算清,它是整个 systolic array 章的直接动机。

---

## 1. "选第 3 号寄存器"是一个组合电路,不是免费操作

结构:一个 register file(比如 8 entry)+ 一个 MAC,从 RF 读 3 个输入、写回 1 个结果。

```c
out = a[i] * b[j] + c[k];   // 软件视角:三次取数看似免费
```

软件里"取第 i 号寄存器"是零成本的索引。硬件里它是一个 **mux(多路选择器)**:从 n 个寄存器里电路化地选出一个。mux 的内部:

```
n 个输入 ─┬─ AND(掩码:要的那行 AND 1,其余 AND 0)
          │
          └─ OR(把 n 行收拢成 1 行)
```

**一个 n 输入、p 位的 mux 成本**:n×p 个 AND + (n−1)×p 个 OR ≈ **n×p 个门量级**。它本身就是一个相当复杂的电路——选择的"自由度"(从 8 个里任选)直接变成 n 这个因子。

> ⚠️ 常见误解:把"选一个寄存器"当成零成本操作。它是一个 n×p 量级的组合电路,是全栈数据搬运成本的第一层。软件的免费索引,硬件要用一整块 mux 来兑现。

---

## 2. 算总账:搬运 24p 门 vs 计算 4p 门

MAC 有 3 个输入(被乘数、乘数、累加数)→ 3 个 mux。取 n=8 entry、p 位宽、q=4:

```
数据搬运(3 个 mux):  3 × n × p = 3 × 8 × p = 24p 个门
真正计算(乘加器):    p × q     =     4 × p =  4p 个门
                     ──────────────────────────────────
比例:                搬运 : 计算 = 24 : 4 = 6 : 1
```

> **七八成的面积花在了软件完全不可见的数据搬运上,真正做乘加的逻辑只占零头。**

这不是设计失误,是**通用可编程性的结构性代价**:要支持"从任意寄存器选数",就得为每个输入付一个 n×p 的 mux。

---

## 3. 为什么"无脑加大 register file"会被反噬

直觉:RF 越大越灵活(能缓存更多操作数,少访问慢存储)。但看 mux 成本:

```
mux 成本 ∝ n  (RF entry 数)
而且:这个成本在每次访问都付 —— 不是一次性的
```

**因为** RF 越大,选数 mux 越贵(线性 ∝ n),且每次读写都付这个成本;**所以** "加大 register file 换灵活性"会被数据搬运成本反噬——多出来的灵活性,代价是每次访问都更贵的 mux,以及吃掉本可给算术单元的面积。

这正是 **Volta 之前 GPU(以及 CPU)CUDA core 的状态**:一个 MAC 被一圈昂贵的 mux 和 RF 包着,比值卡在 1:6 的劣势。它也是 **Tensor Core / systolic array 出现的直接动机**——见 [why-systolic-array](../03-systolic-array/why-systolic-array.md)。

> RF 大小不是越大越好,也不是越小越好,而是一个**面积预算下的优化**:给数据搬运设一个预算(如"RF 占 10%、阵列占 90%"),反推 RF 大小。这个 sizing 决策在 [array-sizing-tradeoff](../03-systolic-array/array-sizing-tradeoff.md) 展开。

---

## 4. mux 是全域反复出现的分母原语

值得记住:**mux 不只在这里出现,它是整个 COMPUTE 域分母的通用积木**:

- 这里:从 RF 选操作数(n×p)。
- [FPGA](../05-fpga-vs-asic/lut-mux-and-10x-overhead.md):LUT 本质是一个 16-entry 真值表的 mux;FPGA 的可配置布线全是 mux——"muxes all the way down"。
- [cache](../06-memory-discipline/cache-vs-scratchpad.md):way 选择、line 选择也是 mux。

所以"选数的代价"是一条贯穿全域的暗线:任何"运行时可选"的灵活性,都要用 mux 兑现,而 mux 就是分母。

---

## 5. 本篇在主线上的位置

这一篇让[计算 / 通信比](../01-overview/compute-communication-ratio.md)的**分母第一次正式登场**,并给出一个刺眼的结论:在裸 datapath 上,比值是 1:6 的劣势——搬运(mux 选数)碾压计算。这是问题,不是解。**怎么把这个劣势翻转?把循环上提一层,让一份搬运喂更多计算——这就是 [systolic array](../03-systolic-array/why-systolic-array.md) 的全部动机。** 本章到此把问题彻底摆清,下一章给解。

---

## 建模启示

- **必须显式建模的状态变量**:RF entry 数 `n`、位宽 `p`、每条指令的输入操作数个数(MAC 是 3)、每次访问跨 RF 边界的字节数。mux 面积 ∝ n×p,是一个可参数化的 sizing 旋钮。
- **核心派生量**:`data_movement_gates / compute_gates`——在裸 datapath 上 ≈ 6。这个比值就是计算 / 通信比的倒数在该层级的取值,是"该不该走 systolic"的判据:比值长期 < 某阈值,就该上提循环。
- **可折叠**:mux 内部 AND/OR 结构 → 折叠成 `n×p` 面积数。RF 的具体 bank 组织对算术单元建模可折叠(交给 RAM 域的 [register-file-as-sram](../../../RAM/wiki/03-sram-applications/register-file-as-sram.md))。
- **关心面积/能效账时必须保留**:每次算术伴随的访问次数与字节数——这是分母,且每次访问都付,比一次性成本更重要。
- **事件/数据结构草图**:`RegAccess{port, entry, bytes}` 与 `MAC{}` 的配对频率,直接给出该单元在某 workload 上的计算 / 通信比。`bytes_moved` 在此累加,作为可审计物理量。
