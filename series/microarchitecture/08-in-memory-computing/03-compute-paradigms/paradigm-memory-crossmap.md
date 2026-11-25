# 存储介质与求值方式的交叉检查

<span class="micro-legacy-anchor" id="三种-paradigm-三种-memory哪些组合是主流哪些罕见为什么"></span>
<span class="micro-legacy-anchor" id="这页在回答什么问题"></span>

上级：[阵列求值与信号转换](./README.md) · [存储介质与计算路径](../02-memory-technologies/README.md)

看到一张标着「MRAM 计算阵列」的图，先遮住标题。只送入两个位，问图中的第一份结果是什么。是一个存储位的读数，是两位共同决定的 OR，还是能表示多项贡献的模拟量？知道存储单元用磁态保存数据，还答不了这个问题。

<span class="micro-legacy-anchor" id="crossmap"></span>
<span class="micro-legacy-anchor" id="交叉检查表"></span>
<span class="micro-legacy-anchor" id="三个主流组合"></span>
<span class="micro-legacy-anchor" id="罕见组合为什么罕见"></span>

## 从哪一步查起？ {#read-cross-check}

- **查一种介质能怎样算。** 在双行 MRAM 的教学例里，同样的 6 µA 能随比较参考的改变分别判出 OR 的 1 或 AND 的 0。另一种实测 MRAM 阵列用电阻求和。沿这两个例子对照，再去查 SRAM、ReRAM、Flash、PCM 各自的编码、读出和外围。[路线速查中的介质与求值方式交叉检查](../02-memory-technologies/memory-tech-comparison-matrix.md#medium-and-evaluation)
- **查一颗宏怎样交付数字。** 画出输入编码和权重所在的位置，沿阵列结果找第一次转换，再追数字累加和最终输出。模拟部分和与数字结果各在线路的哪一端，决定了面积、时间和能量要算到哪里。[从模拟量进入数字部分和](./mixed-signal-cim.md#signal-handoff)

<span class="micro-legacy-anchor" id="独立-cu-单列"></span>

若行缓冲仍然交出原样的权重，沿线找到它与输入第一次相乘的位置。独立计算单元要查指令、寄存器和数据接口；即使它和 DRAM bank 位于同一颗 die，也能把这段操作与阵列读出分别画清楚。[bank 旁的运算单元](../02-memory-technologies/memory-tech-comparison-matrix.md#independent-cu-path) · [计算位置与术语](../01-overview/cim-pim-nmc-taxonomy.md)

<span class="micro-legacy-anchor" id="怎样使用这张表"></span>
<span class="micro-legacy-anchor" id="一句话理解"></span>
<span class="micro-legacy-anchor" id="研究启示"></span>

若两条路径都能算出 23，再把它们放在相同任务、精度和输出位置下比较。转换、部分和归并和最后一次搬运是否计入，往往会改变答案。[沿同一点积比较两种实现](./analog-vs-digital-tradeoff-map.md#same-dot-product) · [检查权重复用与整次任务能量](../02-memory-technologies/memory-tech-comparison-matrix.md#比较前统一什么)
