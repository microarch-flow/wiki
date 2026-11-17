# 服务生命周期与副本管理

上级：[推理运行时](../README.md)

本专题处理一次执行循环之外的服务行为：请求进入哪个副本，如何扩缩容，以及取消或失败后如何收尾。

## 阅读顺序

1. [路由与扩缩容](routing-and-scaling.md)
2. [取消、故障与资源回收](request-resource-lifecycle.md)

## 本专题的边界

路由、引擎调度和资源回收属于不同控制层。模型身份、在途工作和已提交输出将它们连接起来。

前置阅读：[分布式执行与阶段分离](../07-distributed-execution/README.md)。继续阅读：[测量、建模与框架案例](../09-measurement-and-cases/README.md)。
