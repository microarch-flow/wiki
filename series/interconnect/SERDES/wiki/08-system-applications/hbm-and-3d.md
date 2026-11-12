# HBM 与 3D 堆叠：数据经过哪些连接？

上级：[系统应用](./README.md)

HBM 是堆叠式 DRAM 与宽接口的系统。分析它时，应区分 **HBM 堆栈内部**的连接，以及 **主机与 HBM 堆栈之间**的接口。两者相互配合，但不是同一段通道。

## 沿数据路径看边界

一次主机读取可以抽象为：主机侧 HBM 控制器 / PHY → 封装内通道 → HBM 堆栈接口 → 堆栈内的逻辑与 DRAM 阵列 → 数据按相反方向返回。堆栈可能包含多个 DRAM die 和基底逻辑；TSV、微凸点等可参与垂直连接。具体结构取决于代际与产品。[Micron：HBM 基础](https://www.micron.com/products/memory/hbm)

主机与堆栈间的接口提供多条并行数据连接及相关命令、时钟等信号。它使用的是指定 HBM 标准的接口和时序；不能把它直接等同于前文的单 lane 嵌入时钟 SerDes。反过来，宽接口内部也可能采用串并转换、训练或其他实现手段，不能说它完全没有这些功能。

## 一个带宽手算

[AMD Versal HBM 接口文档](https://docs.amd.com/r/en-US/am011-versal-acap-trm/HBM-Interface)给出其指定器件中每堆栈 16 组、每组 `64` 条双向数据信号的实例，共 `1024` 条。假设这个教学例子里全部数据线都在同一方向持续以 `2 Gb/s` 传输，则仅按数据位计算的峰值为：

`1024 × 2 Gb/s ÷ 8 = 256 GB/s`。

`2 Gb/s` 是本例自设条件，不是对该器件全部工作模式的声明；`GB` 按十进制计算。命令、读写切换、刷新、bank 冲突与控制器调度都可能使实际有效带宽更低。不能把单方向峰值同时计作读和写各自达到峰值。

TSV 的数量、微凸点或混合键合方式，也不能单独推出协议、带宽或良率。堆栈结构可继续读 [HBM 封装架构](../../../../../FAB/wiki/04-back-end-packaging/hbm-as-case-study/ai-gpu-hbm-package-architecture.md)和 [HBM 存储协议](../../../../../RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md)。

## 接下来怎么读

读[CPO：电链路怎样接入光链路？](./cpo-electrical-optical.md)，看另一种封装级路径。
