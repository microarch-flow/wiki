# CPU 读 MMIO 卡死案例卡

上级：[06 典型系统与案例](./README.md)

相关：[MMIO、Cache 与 Interrupt 视角](../04-microarchitecture-integration/mmio-cache-interrupt-view.md)、[Timeout、Fault 与 Hang 定位框架](../05-performance-debug/timeout-fault-hang-debug-framework.md)

## 现象

CPU 读取某个外设寄存器后，软件线程或整个系统卡住，迟迟不返回。

## 典型根因方向

- 地址 decode 没命中有效 slave，且没有正确 error return
- 外设时钟没开，slave 永远不给 response
- bridge / APB 子系统卡住，返回路径断掉
- 访问了当前状态下不允许读的寄存器窗口

## 排查顺序

1. 先确认这是 `fault` 还是 `hang`
2. 看 `AR` 是否真的发到目标端口
3. 看目标端口是否给过 accept
4. 看 `R` response 是没回来，还是回来后被挡在中间

## 这类问题为什么常见

因为 MMIO 路径看起来简单，但它高度依赖：

- 时钟/复位状态
- bridge 正常工作
- 明确的 error/timeout 机制

## 一句话理解

CPU 读 MMIO 卡死，最常见的不是“CPU 坏了”，而是某个低速控制路径没有把读事务闭环完成。
