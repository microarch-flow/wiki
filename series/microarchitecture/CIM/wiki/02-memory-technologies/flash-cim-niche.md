# Flash CIM：Mythic 的路线及其工程现实

上级：[02 Memory Technologies](./README.md)
相关：[ReRAM 作为计算元件](./reram-as-compute-element.md), [Mythic 公司卡片](../08-industry-and-products/company-cards/cim-companies-mythic.md), [Edge AI and CIM](../07-workloads/edge-ai-and-cim.md)

## 这页在回答什么问题

Flash CIM 为什么看起来适合极低功耗固定模型推理，却没有成为通用 CIM 主线？答案在于 Flash 的非易失和多状态存储能服务 analog weight storage，但工艺、写入、校准、精度和产品窗口把它压成一个 niche。

## Flash 为什么能做 CIM

Flash cell 用浮栅或电荷存储状态，阈值电压可以表达权重。读取时，输入激励与 cell 状态共同决定电流，多个 cell 的电流可以在列方向形成局部 analog accumulation。这与 ReRAM 的 conductance MVM 在系统直觉上相似：权重不是每次从 memory 读出来再送进 MAC，而是保存在 cell 的物理状态里。

Flash 的优势是非易失、适合固定权重、待机功耗低，并且在成熟节点上有工艺经验。Mythic 选择 Flash-based analog CIM，并不是偶然追求“旧工艺”，而是在用较成熟、analog 相对友好的工艺换取多状态权重存储和低功耗推理。

## 为什么它是 niche

Flash write/program 代价高于 SRAM 写入，适合离线编程的固定模型，不适合频繁更新权重。多状态阈值电压需要校准，温度、retention 和工艺分布会影响有效精度。再加上 ADC、输入编码、reference 和后级数字处理，Flash CIM 的系统优势高度依赖目标模型足够固定、功耗约束足够硬、客户愿意接受专用软件栈。

这使 Flash CIM 更适合 always-on sensor、edge inference、固定模型视觉或音频任务，而不是频繁迭代的大模型推理平台。

## 与 ReRAM-CIM 的差异

Flash 和 ReRAM 都能表达 analog weight，但风险分布不同。ReRAM 的叙事更强调新型高密度 crossbar 和 conductance MVM；Flash 的叙事更强调成熟非易失存储、固定权重和产品化尝试。Flash 的可编程窗口、写入和校准流程不同于 ReRAM，不能把两者简单并成 “NVM CIM”。

Digital Flash-CIM 不是主线。如果只把 Flash 当 binary memory 再接数字 logic，非易失优势还在，但 analog CIM 的密度和局部 MVM 优势会被削弱。Mixed-signal 是更现实的描述：cell 里保存 analog-ish 权重，外围负责转换、校准和数字后处理。

## Mythic 给出的教训

Mythic 的价值不只在技术路线本身，更在商业化教训。Flash analog CIM 可以讲出很强的低功耗 edge inference 故事，但产品必须同时解决模型转换、编译/runtime、精度承诺、校准、量产一致性和客户导入。如果客户场景不够刚需，或者软件和系统集成摩擦过大，漂亮的 array-native 叙事仍然难以转成稳定收入。

## 一句话理解

Flash CIM 是固定权重、低功耗 edge 推理的专用路线，不是通用 CIM 的默认答案；它用非易失和多状态存储换来了校准、写入和产品窗口限制。

## 研究启示

Flash CIM 的研究价值在于探索非易失 analog weight storage 的工程边界：阈值状态能保持多久、校准频率多高、模型精度如何随时间和温度衰减、固定模型场景是否足够大。产业实现已经证明这条路能做出产品尝试，也证明产品化难点不只在 cell，而在软件栈、客户场景和长期可靠性闭环。

