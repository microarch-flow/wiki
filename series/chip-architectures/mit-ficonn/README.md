# MIT FICONN 怎样用光场完成三层推理？

MIT FICONN 是一颗硅光子研究芯片。论文用六路光场执行三层神经网络，在三级矩阵乘之间插入两级非线性激活。本文跟踪一次前向计算，再用作者公开数据复算六类元音的测试准确率。 [Nature Photonics 正式论文，图 1–4](https://www.nature.com/articles/s41566-024-01567-z)

## 层间怎样传递激活

发射器把一个输入向量的六个分量分别编码到六路光场的幅度和相位中。相干矩阵乘法单元（CMXU）使用马赫–曾德尔干涉仪网格，让不同路径的光场叠加。网格的移相器设置决定六路输入怎样线性组合成六路输出。 [正式论文，图 1–2](https://www.nature.com/articles/s41566-024-01567-z)

<figure class="chip-lifecycle-flow" aria-label="发射器编码六路光场。信号经过三次矩阵乘和两次非线性激活，最后到达相干接收器。">
  <div class="chip-flow-step"><strong>发射器</strong><small>把六个输入分量编码到光场</small></div>
  <div class="chip-flow-arrow" aria-hidden="true">↓</div>
  <div class="chip-flow-step"><strong>三层光子计算</strong><small>矩阵乘 → 激活 → 矩阵乘 → 激活 → 矩阵乘</small></div>
  <div class="chip-flow-arrow" aria-hidden="true">↓</div>
  <div class="chip-flow-step"><strong>相干接收器</strong><small>读出最后一层输出</small></div>
  <figcaption>图中只画出前向计算的信号路径。</figcaption>
</figure>

前两级矩阵乘之后，每路光都经过一个非线性光学函数单元（NOFU）。该单元分出一部分光送入光电二极管，产生的光电流驱动微环谐振器。输入光强改变时，谐振器对主路光场的响应也随之改变，形成非线性激活。主路光场直接进入下一级，层间省去数字化和重新编码。第三层的光场由片上相干接收器读出，测试板再把输出信号数字化。 [正式论文，图 1、图 3](https://www.nature.com/articles/s41566-024-01567-z) · [补充材料，第 II、IX 节](https://static-content.springer.com/esm/art%3A10.1038%2Fs41566-024-01567-z/MediaObjects/41566_2024_1567_MOESM1_ESM.pdf#page=4)

## 怎样复算六类元音的测试准确率

训练时，作者对当前参数沿同一个随机方向施加正、负两组扰动。芯片分别执行前向计算，控制端根据两次分类损失的差值更新参数。作者还用未扰动的参数记录当轮训练准确率。这里的原位训练指前向计算经过实际芯片，损失计算和参数写回由控制端完成。 [正式论文，图 4](https://www.nature.com/articles/s41566-024-01567-z) · [补充材料，第 VI 节](https://static-content.springer.com/esm/art%3A10.1038%2Fs41566-024-01567-z/MediaObjects/41566_2024_1567_MOESM1_ESM.pdf#page=8)

复算使用作者发布的 `Fig4.h5`，沿用图 4 的选轮规则。对每个样本，取六路输出中数值最大的一路作为预测类别。先用 `train_data` 和 `Vowel data/train_y` 比较 5,000 轮训练准确率。第 **3,894** 轮最高，540 份训练样本中有 523 份分类正确。 [Figshare 数据条目 v1](https://api.figshare.com/v2/articles/27174468/versions/1) · [图 4 数据（145 MB）](https://ndownloader.figshare.com/files/49621572) · [作者绘图脚本](https://ndownloader.figshare.com/files/49760358)

固定第 3,894 轮，再从 `test_data/test after epoch 3894` 读取芯片输出，与 `Vowel data/test_y` 比较。294 份测试样本中有 **272** 份分类正确。测试准确率为 **272 ÷ 294 ≈ 92.5%**，与正式论文一致。这个数字来自作者保留的实机输出及标签。 [正式论文，图 4](https://www.nature.com/articles/s41566-024-01567-z)

## 410 ps 从哪里算到哪里

计时从芯片光输入到片上相干接收器。芯片输入处将光分到两臂。信号臂经过三层网络，本振臂沿较短的波导直接到达接收器。作者向芯片送入两个间隔可调的光脉冲。如果先发脉冲经信号臂、后发脉冲经本振臂同时到达，接收器就能观察到两者的干涉。 [补充材料，第 VII 节、图 S10](https://static-content.springer.com/esm/art%3A10.1038%2Fs41566-024-01567-z/MediaObjects/41566_2024_1567_MOESM1_ESM.pdf#page=13)

干涉可见度在脉冲间隔为 **280 ps** 时达到峰值，这是实验测得的两臂时差。作者按约 1 cm 的本振波导和群折射率约 3.8，估算本振臂传播时延约 **130 ps**。两者相加，得到信号臂从芯片光输入到片上接收器约 **410 ps**。脉冲间隔的实验分辨率为 40 ps。 [补充材料，第 VII 节、图 S10](https://static-content.springer.com/esm/art%3A10.1038%2Fs41566-024-01567-z/MediaObjects/41566_2024_1567_MOESM1_ESM.pdf#page=13)

元音分类演示还使用了板级输入编程、输出数字化和分类处理。这些步骤的耗时在上述光路边界之外。输入向量能多快连续送入芯片，还取决于发射、非线性单元和读出链路的带宽。 [补充材料，第 VII、IX 节](https://static-content.springer.com/esm/art%3A10.1038%2Fs41566-024-01567-z/MediaObjects/41566_2024_1567_MOESM1_ESM.pdf#page=15)

若要比较光器件在系统中的职责，可以对照 CPO 的收发路径。那里追踪数据如何跨越链路。若要看模拟计算的层间交接，可以对照 HERMES 的片上数字归并和测试板转运。 [CPO 系统栈与接口位置](../../interconnect/CPO/03-architecture-platform/system-stack.md) · [IBM HERMES](../ibm-hermes/README.md)
