# DMA Completion 丢失案例卡

上级：[06 典型系统与案例](./README.md)

相关：[DMA Descriptor Fetch、Data Move 与 Writeback](../04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md)、[Doorbell、Completion 与 Interrupt Flow](../04-microarchitecture-integration/doorbell-completion-interrupt-flow.md)

## 现象

DMA 看起来已经把数据搬完，但软件迟迟收不到 completion，或者偶发收不到 completion。

## 典型根因方向

- completion writeback 还没真正可见
- interrupt 到了，但状态记录还没稳定
- CPU 读到的还是旧缓存副本
- writeback 与普通 data write 共路，尾部被堵
- 软件过早复用了 queue/completion buffer

## 排查顺序

1. 分清数据搬运完成，还是“软件可见完成”
2. 看 writeback 路径是否真的发出并返回
3. 看 interrupt 和 completion record 的先后关系
4. 先分清 DMA 路径是 coherent 还是 non-coherent，再看 CPU 侧是否做了正确 invalidate / barrier 或其他 cache maintenance

## 一个关键判断

completion 丢失很多时候不是 DMA 数据面失败，而是“完成通知链路”失败。

## 一句话理解

DMA completion 是 `writeback + 可见性 + 通知` 的联合结果，少了任何一环，软件都会觉得“任务没完成”。
