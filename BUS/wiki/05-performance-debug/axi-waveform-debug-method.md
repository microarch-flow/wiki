# AXI Waveform Debug 方法

上级：[05 性能与调试](./README.md)

相关：[AXI 五通道与 VALID/READY](../03-on-chip-protocol-families/axi-five-channels-handshake.md)、[Timeout、Fault 与 Hang 定位框架](./timeout-fault-hang-debug-framework.md)

## 这页在回答什么问题

当你已经打开 AXI 波形时，应该按什么顺序看，而不是在五条通道里盲目来回扫。

## 第一步：先决定当前是读问题还是写问题

- 写路径重点看 `AW / W / B`
- 读路径重点看 `AR / R`

不要一开始就把五条通道混着看。

## 第二步：找第一处不再 forward progress 的地方

常见判断方式：

- `VALID` 一直高但 `READY` 不来
- `READY` 一直高但上游没有再发
- 地址通道走了，但数据通道没跟上
- 数据到了，但 response 不回来

## 第三步：沿依赖链向前后各看一跳

例如如果看到：

- `RVALID` 没来，就回头看 slave 是否收到了 `AR`
- `BVALID` 没来，就看写数据是否真的被完整接收
- `AWREADY` 长期拉低，就看目标端口或内部 FIFO 是否堵住

## 第四步：把波形现象翻译成系统语言

波形不是结论，结论应该落成：

- 谁在反压谁
- 哪条通道先耗尽缓冲
- 是 master 自己没发，还是 slave 不肯收
- 是 fault，还是纯粹没前进

## 一句话理解

AXI 波形调试最有效的方法不是“多看”，而是按 `先分读写 -> 找第一处停滞 -> 沿依赖链展开` 的顺序系统地看。
