# IBM HERMES 怎样在片上归并卷积部分和？

IBM HERMES 是一颗 64 核混合信号存内计算研究芯片。相变存储器（PCM）阵列完成矩阵向量乘，本地数字单元汇总多核的部分结果。论文的 ResNet-9 演示还使用了测试板 FPGA，将激活从当前网络层送往下一层。本文分别跟踪同一层的归并和层间的转运。 [IBM 原始论文](https://arxiv.org/html/2212.02872v1)

## 模拟计算怎样交给数字单元

每个 HERMES 核有一个 256 × 256 的阵列。权重以 PCM 器件的电导编码，输入值用脉冲宽度表示。阵列在列上累加响应，由模数转换器（ADC）产生数字结果。本地数字处理单元（LDPU）处理缩放等数字运算，并利用芯片内部链路传送或归并结果。 [原论文的芯片架构与模拟计算核](https://arxiv.org/html/2212.02872v1) · [IBM 芯片说明](https://research.ibm.com/blog/analog-ai-chip-inference)

## 一层卷积怎样分给八个核

论文方法节给出 ResNet-9 深层卷积的一个实际映射。把一个卷积窗口展开后，输入向量有 2,016 项，权重矩阵为 2,016 × 224，产生 224 项输出。芯片将输入维分成八段，每段 252 项。相应的八个权重子矩阵均为 252 × 224，在各核阵列中补零到 256 × 256。 [原论文方法节的权重映射](https://arxiv.org/html/2212.02872v1)

1. **各核计算部分和。** 每个核负责 252 项有效输入，形成对同一组 224 项输出的贡献。补零部分在理想矩阵运算中贡献为零。
2. **片上归并。** 八组贡献经过模数转换，由片上链路与 LDPU 沿输入分段相加。每个输出位置收到八段各自的贡献，合成一组 224 项的层内结果。
3. **完成本层。** 接收汇总结果的 LDPU 做批归一化和 ReLU，生成本层激活。本次映射的维度可由 8 × 252 = 2,016 核对。 [原论文第 V 节、图 3 与方法节](https://arxiv.org/html/2212.02872v1)

## 下一层怎样取到激活

在这个演示中，同一层的部分结果沿芯片内部链路归并。完成一层之后，激活经过测试板上的 FPGA，再送入芯片供下一层使用。ResNet-9 的最大池化由软件执行。论文的单层分析和整网演示因此有各自的观察边界。 [原论文第 V 节的实验边界](https://arxiv.org/html/2212.02872v1)

<figure class="chip-lifecycle-flow" aria-label="各片上 PCM 核计算部分和。ADC 转为数字结果后，片上链路和 LDPU 归并。板上 FPGA 把本层激活送给下一层。">
  <div class="chip-flow-step"><strong>片上 · 八个 PCM 核</strong><small>阵列计算与模数转换</small></div>
  <div class="chip-flow-arrow" aria-hidden="true">↓ 八组数字部分和</div>
  <div class="chip-flow-step"><strong>片上 · 本地数字处理单元</strong><small>归并、批归一化和 ReLU</small></div>
  <div class="chip-flow-arrow" aria-hidden="true">↓ 本层激活</div>
  <div class="chip-flow-step"><strong>片外 · 测试板 FPGA</strong><small>转运激活，送回芯片供下一层使用</small></div>
  <figcaption>论文中 ResNet-9 的层内归并与层间转运示意。</figcaption>
</figure>

作者报告 ResNet-9 在 CIFAR-10 上采用双器件编程（TDP）时的准确率为 **92.81%**，软件基准为 **93.67%**，相差 **0.86 个百分点**。这个结果对应论文的硬件感知训练、权重编程方案和测试分工。 [原论文图 3 与方法节](https://arxiv.org/html/2212.02872v1)

存储材料与模数转换误差的背景可从已有专题接着读。 [PCM 和 MRAM 作为 CIM 介质](../../microarchitecture/08-in-memory-computing/02-memory-technologies/pcm-mram-for-cim.md) · [模拟存内计算](../../microarchitecture/08-in-memory-computing/03-compute-paradigms/analog-cim-deep-dive.md)
