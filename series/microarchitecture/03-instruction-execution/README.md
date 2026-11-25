# 指令执行与处理器控制

在[三级流水线](../02-pipeline/pipeline-register-insertion.md)里，后一项运算有时要等前一项交出结果。如果再来一条独立指令，谁决定它能否先执行？先跟踪三条指令怎样使用数据和端口，再看从取指到提交的完整过程。

## 阅读顺序

1. [第三条指令能先执行吗](./dependencies-bypass-issue.md)　对照三种发射日程，找出哪条指令在等数据、哪条在等端口。
2. [从取指到提交](./instruction-lifecycle.md)：指令职责、精确异常与软件可见状态。

这两篇建立执行主线。分支预测器、重命名、ROB 和 load/store queue 的完整实现还需继续专题展开。并行线程与通道组织见[并行执行](../04-parallel-execution/README.md)。
