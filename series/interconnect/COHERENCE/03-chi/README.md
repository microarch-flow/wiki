# CHI：从节点职责到事务完成

<!-- nav-title: 03 CHI -->

本章用 CHI 说明真实接口怎样表达一致性事务。输入是节点发出的请求与响应；输出是数据、权限变化和事务完成。网络负责承载这些消息，节点仍须履行状态与资源义务。

事务基线固定为 Arm IHI 0050E.b。先辨认 RN、HN、SN 和通道，再跟踪内存或缓存供数，最后区分链路信用、协议信用及完成确认。

本章不展开 CHI C2C 容器、UCIe 适配或厂商 mesh 的物理实现。它们分别属于封装内芯粒互连和 NoC。理解本章不要求已经掌握 CXL；两者是建立在基础概念上的不同分支。

## 阅读顺序

1. [节点与通道](chi-nodes-and-channels.md)
2. [读取与写权限](chi-read-and-ownership.md)
3. [流控、重试与完成](chi-flow-control-retry-completion.md)

返回[专题导读](../README.md)，选择 CHI、CXL 或其他章节的阅读路线。
