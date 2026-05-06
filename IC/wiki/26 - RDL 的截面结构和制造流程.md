# RDL 的截面结构和制造流程

上级：[[05 - Fan-out RDL]]

相关：[[05A - Fan-out 制造路线：Chip-first 与 Chip-last]]、[[20 - 大陆先进封装：材料、基板、设备分别卡在哪]]

## 先给结论

RDL = `Redistribution Layer`，重布线层。

它的本质不是“多做几根线”，而是：

`把原来 die 上的 I/O 重新映射到新的位置，并在封装级承担 die-to-die、die-to-substrate 或 die-to-ball 的互连。`

## 1. RDL 的截面结构怎么理解

可以把一个简化的 RDL 截面理解成下面几层反复堆叠：

- polymer dielectric
- Cu trace
- via
- 再叠一层 polymer
- 再叠一层 Cu

所以 RDL 不是单层铜，而是：

`聚合物介质 + 铜走线 + 通孔结构` 的多层 build-up 体系。

## 2. 为什么叫 redistribution

因为 die 上原始 pad 的位置，通常并不适合直接作为：

- 外部焊球位置
- 多 die 互连位置
- package-level routing 接口

RDL 的作用就是把这些 pad 重新排布到系统更需要的位置。

## 3. RDL 在先进封装里承担什么角色

### 3.1 die I/O 扇出

把连接引到 die 面积之外。

### 3.2 die-to-die 互连

在 fan-out / RDL interposer 平台上，多颗 die 可以通过 RDL 直接连接。

### 3.3 power / signal 路由

高端平台里，RDL 不只是信号线，也承担重要的供电路径。

## 4. 一个简化的制造主线

不同平台细节差很多，但可以先记住一个通用骨架。

### Step 1：准备承载平台

这个平台可能是：

- die + mold 的重构表面
- carrier
- interposer 相关表面

### Step 2：形成介质层

先形成 polymer dielectric。

### Step 3：开 via

在需要垂直接触的位置形成开口。

### Step 4：形成 Cu routing

做种子层、图形化、电镀等，形成铜走线。

### Step 5：重复 build-up

如果需要更多层，就反复堆叠：

- dielectric
- via
- Cu routing

### Step 6：形成最终连接界面

例如：

- bump pad
- solder 连接位
- 与下一层封装结构连接的接口

## 5. RDL 为什么难

### 5.1 线宽线距越来越细

越高端的 RDL，越接近“准硅级”布线能力，对工艺窗口要求越高。

### 5.2 polymer 体系不像硅那样稳定

材料尺寸稳定性、平整度、热膨胀表现都更复杂。

### 5.3 多层 build-up 会带来应力

层数越多，warpage、RDL cracking、via reliability 都更难控。

### 5.4 它同时承受电和机械任务

RDL 不只是要“导通”，还要兼顾：

- 高频性能
- 供电
- 热机械可靠性

## 6. 一个更实用的理解

RDL 可以看成：

`封装级金属互连网络`

它在先进封装里扮演的角色，有点像“把一部分片上布线能力外移到封装层”。

## 7. 常见误区

### 误区 1：RDL 就是几根铜线

不对。它是多层介质与金属 build-up 平台。

### 误区 2：RDL 只和 fan-out 有关

不对。RDL 也会出现在 interposer、bridge、CoWoS-R、CoWoS-L 等平台里。

### 误区 3：RDL 只是信号连接

不对。高端系统里，RDL 同时承担 signal 和 power 路径。

