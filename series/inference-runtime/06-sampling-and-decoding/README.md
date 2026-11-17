# 采样与解码控制

上级：[推理运行时](../README.md)

本专题从 logits 走到提交的输出 token。先明确采样与停止，再说明候选验证和语法约束如何修改生成循环。

## 阅读顺序

1. [采样、停止与输出](sampling-and-stopping.md)
2. [推测解码](09-speculative-decoding.md)
3. [约束解码](13-constrained-decoding.md)

## 本专题的边界

逐位结果一致、分布一致、语法合法和任务质量接近是不同性质。每种机制只声明其真正能保证的部分。

前置阅读：[批处理与请求调度](../05-batching-and-scheduling/README.md)。继续阅读：[分布式执行与阶段分离](../07-distributed-execution/README.md)。
