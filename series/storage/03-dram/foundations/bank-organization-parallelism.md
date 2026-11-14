# DRAM bank：独立行状态与共享资源

上级：<span id="bank-为什么是-dram-并行性的最小单位"></span>[DRAM 单元与阵列](./README.md)

相关：[Row buffer 与行状态](./row-buffer-as-cache.md) · [控制器与性能](../../04-dram-controller/why-mc-is-the-real-bottleneck.md)

## 这页在回答什么问题

Bank 为什么有利于并行，又为什么增加 bank 不一定按比例增加带宽？在常见标准接口中，bank 是可见的行状态管理单位；这不意味着它是物理阵列中最小的并行单位。

## 独立 bank 状态与共享资源

不同 bank 可以分别维护行状态，并在时序允许时交错感测、恢复或列操作。但它们通常共享部分命令/地址和数据通路，还受到跨 bank 激活、bank group 和功耗约束。是否能同时进行某两个动作，必须查具体代际和器件。

假设某个 channel 的共享 DQ 执行四次同方向 BL8 传输，每次以 DDR 方式占用 4 CK；即使四次分别来自不同 bank，在没有空隙的理想情况下也要占用 **16 CK**。bank 并行可以隐藏部分阵列等待，却不会把同一组 DQ 变成四条总线。

芯片内部还可能有 subarray 等更细粒度组织。CMU 提出的 [SALP](https://users.ece.cmu.edu/~yoonguk/papers/kim-isca12.pdf) 探索了利用 subarray 并行的改动；它是研究方案，不能据此假设所有商用 DRAM 都公开相同能力。

## 一句话理解

Bank 提供可独立管理的行状态；实际并行度仍受器件和共享接口限制。

## 建模启示

将 bank 的状态与 channel 的命令、DQ 和跨 bank 约束分开建模。若目标设备提供其他粒度的并行机制，再依据其规格扩展。
