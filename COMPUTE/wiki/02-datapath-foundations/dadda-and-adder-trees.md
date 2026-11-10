# 压缩树与进位结构：从多行部分积到结果

上级：[02 · datapath 基础](./README.md)
相关：[MAC 与整数范围](./multiply-accumulate-from-gates.md)、[时钟路径与反馈](../04-clocking-and-pipeline/feedback-loop-clock-constraint.md)

## 输入和输出

整数乘法可产生多行按位权排列的部分积。压缩树将这些行逐层归约，输出两行等价的加数；末级 carry-propagate adder（CPA）再产生一个二进制结果。结果位宽和是否保留最高进位由接口和数值语义决定。

## Carry-save 为什么推迟跨列传播

full adder 可作为 3:2 compressor：同位权的三个 bit 变成当前列的 sum 和更高一列的 carry。下一层再处理 carry，当前层不需要等整个字宽的进位链完成。压缩层数、布线、最终 CPA 结构共同影响实现延迟；不能把压缩树深度与整个乘加路径延迟等同。

## Wallace 与 Dadda 的调度

Wallace 通常尽早压缩当前可用的部分积；Dadda 使用阶段目标高度安排压缩。两者都可实现两行输出，然后使用 CPA。Dadda 从目标高度 2 出发，递推 `d_next=floor(1.5*d)`，得到 2、3、4、6……。选小于初始最大列高的最大目标，再逆序执行。例如最大列高为 5，目标依次为 4、3、2。每阶段逐列计入本列输出以及低位列送来的进位，使下一阶段列高不超过目标。若目标为 4，本列有 5 个输入位且低位列送来 1 个进位，可用一个 full adder 压缩本列 3 位：本列留下 1 个 sum、2 个原位和 1 个送入进位，共 4 位；新 carry 送往更高列。不能忽略相邻列产生的进位。

具体 full adder、half adder 数量和层数取决于位宽、列高度、实现与优化约束。比较时应固定输入位宽、累加方式、时序目标和库，再评估面积、布线和延迟；没有适用于所有设计的固定胜者。

## 末级进位与时钟

ripple、carry-lookahead 和 prefix 等 CPA 结构具有不同的逻辑、布线及面积代价。若该路径是时钟域的有效 setup 路径之一，就要和同域其他前馈及反馈路径一起检查。hold 是独立的最短路径约束。反馈累加还须保持状态依赖与数值语义，详见[反馈环](../04-clocking-and-pipeline/feedback-loop-clock-constraint.md)。

## 建模启示

固定任务和跨边界字节时，换压缩树不会改变 `useful_MACs / boundary_bytes`。它可能改变面积、路径延迟、频率上限和能耗；需要分别配置并以目标实现校准。模拟器若不仿真单个压缩器，仍应记录 MAC 的数值语义、II、延迟和资源占用。
