# 06 初始化与链路训练：链路怎样建立和维持？

上级：[SerDes Wiki](../README.md)

链路上电后，两端需要让时钟、接收器和协议状态进入可用条件。部分协议还让两端交换能力或调整均衡。运行期间，链路也可能需要恢复。具体状态和顺序取决于协议与器件。

## 阅读顺序

1. [初始化与校准：先让模块具备工作条件](./initialization-calibration.md)
2. [训练与自适应：谁观察，谁调整？](./training-and-adaptation.md)
3. [多 lane 为什么需要对齐？](./lane-alignment.md)
4. [重训练与运行观察：怎样定位变化？](./retraining-and-observation.md)
5. [PCIe 链路训练案例：从现象到证据](./pcie-training-case.md)

本章用抽象流程解释职责，再用有来源的器件和 PCIe 例子说明边界。它不是任何协议的完整状态机规范。
