# 队列、Doorbell 与 Completion

上级：[04 软件栈与编程模型](./README.md)

相关：[软件栈与编程模型](./software-stack.md)、[同步、一致性与常见错误](./synchronization-errors.md)

## 这页在回答什么问题

为什么现代 DMA 的软件接口通常都围绕 queue、doorbell 和 completion 组织，以及这些对象如何决定正确性和吞吐。

## Queue 在解决什么

queue 让软件可以批量提交任务，而不是一条一条同步等完成。  
它直接影响：

- 提交开销
- 并发度
- backpressure 暴露方式

## Doorbell 在解决什么

doorbell 是“硬件有新任务可取”的通知机制。  
它的关键不是名字，而是：

- 写 doorbell 前数据是否已可见
- doorbell 触发是否会过频
- 多队列时是否需要分离 doorbell

## Completion 在解决什么

completion 负责把“硬件完成”传回软件世界。  
常见方式：

- interrupt
- polling
- completion record
- event queue

## 最容易出的错

- queue entry 写了一半就敲 doorbell
- completion record 被过早复用
- interrupt 太频繁导致 CPU 侧成为瓶颈
- polling 太激进导致系统抖动

## 一句话理解

queue、doorbell 和 completion 共同定义了 DMA 的软件时序边界，没有这三者的清晰契约，就很难得到既正确又高吞吐的系统。
