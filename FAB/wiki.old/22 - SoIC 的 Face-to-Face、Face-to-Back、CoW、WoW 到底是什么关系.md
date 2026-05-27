# SoIC 的 Face-to-Face、Face-to-Back、CoW、WoW 到底是什么关系

上级：[[08 - 3D IC]]

相关：[[09 - W2W 与 D2W]]、[[19 - Hybrid Bonding vs Micro-bump]]、[[15 - CTE、热应力与 Warpage：从概念到 3DIC]]

## 先给结论

学习 SoIC 时最容易混的是把这四组概念揉成一团：

- Face-to-Face / Face-to-Back
- CoW / WoW

其实它们属于两个不同维度。

### Face-to-Face / Face-to-Back

回答的是：

`上下两层 die 的朝向关系是什么`

### CoW / WoW

回答的是：

`制造组织方式是什么`

所以：

- `Face-to-Face / Face-to-Back` 是结构拓扑问题
- `CoW / WoW` 是制造流程组织问题

## 1. 什么是 die 的“face”

在芯片语境里，face 可以先粗略理解成：

- 有主要器件层、金属互连层、主要连接界面的那一面

所以讨论 face-to-face / face-to-back，本质是在说：

- 两颗 die 的主要功能面是怎么相对摆放的

## 2. Face-to-Face 是什么

可以理解成：

- 两颗 die 的主要连接面彼此相对
- 高密度互连界面发生在两者相对的正面之间

它的直觉优势是：

- 互连最短
- 更容易获得高密度连接
- 更适合追求极限带宽和低功耗

但它的热、供电、后续引出路径会更复杂。

## 3. Face-to-Back 是什么

可以理解成：

- 一颗 die 的主要连接面朝向另一颗 die 的背面

这通常意味着：

- 有一层需要通过 TSV / backside routing 等方式把连接引出来
- 结构上更容易与外围封装体系结合

公开资料中，TSMC 对 SoIC CoW Face-to-Back 有明确量产表述。

## 4. CoW 是什么

CoW = chip-on-wafer。

它回答的是：

`上层对象是单颗 die/chiplet，还是整片 wafer`

CoW 的典型逻辑是：

1. 底层保持 wafer 形态
2. 上层先切成 die
3. 选 KGD
4. 再逐颗贴到底层 wafer 上

它更适合：

- 异构集成
- 不同尺寸 die
- 高价值逻辑 die

## 5. WoW 是什么

WoW = wafer-on-wafer。

它的典型逻辑是：

1. 上下都保持 wafer 形态
2. 整片对整片键合

它更适合：

- 同尺寸
- 规则阵列
- 高良率节点

## 6. 这两组关系怎样组合

最关键的一点是：

`Face-to-Face / Face-to-Back 和 CoW / WoW 可以交叉组合。`

也就是说：

- 你可以有 CoW Face-to-Back
- 也可以有 WoW 某种朝向关系

它们不是同义词，也不是互斥分类。

## 7. 为什么 TSMC 常强调 CoW Face-to-Back

从公开量产表述看，SoIC CoW Face-to-Back 更符合高价值异构逻辑芯粒的现实量产路线，因为它同时兼顾：

- KGD
- 异构灵活性
- 3D integration
- 后续再进 CoWoS / InFO 的系统路径

这说明台积电不是只追求“最纯理论结构”，而是在量产经济性和系统可扩展性之间做平衡。

## 8. 一个最实用的记忆方法

### 第一步

先问：上下两层怎么面对面？

- Face-to-Face
- Face-to-Back

### 第二步

再问：制造时是 die 贴 wafer，还是 wafer 贴 wafer？

- CoW
- WoW

只要你按这两个问题拆开，SoIC 的结构就不会再混。

