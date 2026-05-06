# HBM Stack 是怎么制造出来的

上级：[[17 - 为什么 HBM 逼着产业走向 2.5D 和 3D]]

相关：[[04 - Si Interposer]]、[[08 - 3D IC]]、[[09 - W2W 与 D2W]]

## 先给结论

HBM 不是“把几颗 DRAM 摞起来”这么简单，它本质上是：

- 多层 memory die 的 3D 堆叠
- 通过 TSV 建立垂直互连
- 通过 base die 或底层逻辑层与外部系统连接
- 最终再作为一个完整 memory stack 参与 2.5D / 3D 系统封装

也就是说，HBM 在进入 CoWoS 之前，自己已经先完成了一次高难度 3D 集成。

## 1. HBM stack 里有哪些对象

一个简化后的 HBM stack 可以理解成：

- 多层 DRAM memory dies
- TSV 垂直通道
- micro-bump / 混合堆叠连接
- base die 或底部控制/接口层
- 保护、支撑和热机械相关材料

所以在 CoWoS 里看到的 “一个 HBM” ，其实已经不是单层 die，而是一个先封好的高复杂器件。

## 2. 为什么 HBM 要做成 stack

因为它要同时满足：

- 更高容量密度
- 更高总带宽
- 更短互连
- 更低 power-per-bit

如果继续用平面式 memory 布局，这几个目标会彼此打架。堆叠能把容量和 I/O 密度一起拉高。

## 3. 一个简化的制造主线

### Step 1：DRAM wafer 制造

先完成 memory die 的前道制造。

### Step 2：TSV 相关结构形成

HBM 需要 memory die 具备垂直互连能力，所以会形成 TSV 相关结构。

### Step 3：wafer thinning

为了后续堆叠，memory die 通常要做薄化。

### Step 4：切割成 die

从 wafer 切出可用于堆叠的 memory dies。

### Step 5：die stacking

把多层 memory die 逐层堆起来，形成 memory stack。

### Step 6：形成对外连接界面

让整个 HBM stack 能以一个器件身份，继续参与逻辑系统封装。

### Step 7：测试与筛选

因为 HBM stack 本身价值很高，所以测试和已知良品筛选非常关键。

## 4. 为什么 HBM 制造难度高

### 4.1 它同时是 memory 制造问题和先进封装问题

HBM 不只是 DRAM 工艺难，还多了一层：

- 薄 die handling
- 多层堆叠
- TSV 良率
- 热机械可靠性

### 4.2 层数增加会把热和应力一起放大

层数越高：

- 热越难出去
- 对位越难
- 应力更复杂
- 良率耦合更强

### 4.3 它后面还要继续参与更大系统封装

HBM stack 不是终点，它还要再和 logic die 在 interposer/RDL 平台上集成，因此它的对外接口、尺寸、热和可靠性都必须满足下一层系统的要求。

## 5. 为什么这会直接影响先进封装

因为系统厂拿到的不是“很多 DRAM die”，而是“几个 HBM stack + 一个 logic die/多个 chiplets”。

这就把先进封装问题改写成了：

- 怎么把多个高价值 HBM stack 放到 logic 边上
- 怎么做足够高密度的 routing
- 怎么解决 PI / thermal / warpage

这正是 CoWoS、SoIC 这些平台会变得关键的原因。

## 6. 最重要的心智模型

学习 AI/HPC 封装时，要分清两层：

### 第一层

HBM 自己内部已经是 3D stack。

### 第二层

HBM stack 再和 logic / chiplet 做 2.5D 或更高层级系统集成。

所以你看到的高端封装，常常本身就是：

`memory 的 3D + logic 与 memory 的 2.5D/3D`

