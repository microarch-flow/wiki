# Sony IMX500 怎样把检测结果交给主机？

Raspberry Pi AI Camera 在 Sony IMX500 内执行模型推理。主机接收检测张量，筛选结果，再把框和标签叠加到预览图像上。本文跟踪 Raspberry Pi 官方 MobileNet SSD 示例。主机源码与模型配置均固定在 `rpicam-apps` 提交 `7b69b7c`。 [Sony 传感器架构](https://www.sony-semicon.com/en/technology/ivs/index.html) · [Raspberry Pi 官方相机示例文档](https://github.com/raspberrypi/documentation/blob/97485d9742bcd15765f208d8c01735d74d542650/documentation/asciidoc/accessories/camera/ai-camera.adoc) · [固定版本的模型配置](https://github.com/raspberrypi/rpicam-apps/blob/7b69b7cde5612677b0eb3ee29bf24ad165a599c1/assets/imx500_mobilenet_ssd.json)

## 图像和检测结果怎样分流

IMX500 把像素芯片和逻辑芯片堆叠在一起。像素芯片提供成像数据。逻辑侧的图像信号处理器（ISP）准备模型输入，专用 AI 处理单元在传感器内执行推理。官方示例选择输入为 320 × 320 的 MobileNet SSD 模型。相机向主机提供成像数据和模型输出，主机可以把检测结果叠加在预览上。 [Sony 智能视觉传感器说明](https://www.sony-semicon.com/en/technology/ivs/index.html) · [Raspberry Pi 的 IMX500 数据路径](https://github.com/raspberrypi/documentation/blob/97485d9742bcd15765f208d8c01735d74d542650/documentation/asciidoc/accessories/camera/ai-camera.adoc) · [模型配置](https://github.com/raspberrypi/rpicam-apps/blob/7b69b7cde5612677b0eb3ee29bf24ad165a599c1/assets/imx500_mobilenet_ssd.json#L1-L10)

主机的检测处理阶段从相机请求的元数据读取 `CnnOutputTensor` 和 `CnnOutputTensorInfo`。前者提供数据，后者说明各输出张量的形状等信息。处理阶段在两项都可用时解析新结果，并结合 `ScalerCrop` 把检测框从推理坐标变换到最终图像坐标。若这次请求缺少推理张量，当前示例可以沿用此前保存的可见检测结果。 [固定版本的元数据处理](https://github.com/raspberrypi/rpicam-apps/blob/7b69b7cde5612677b0eb3ee29bf24ad165a599c1/post_processing_stages/imx500/imx500_object_detection.cpp#L126-L177) · [坐标转换的调用](https://github.com/raspberrypi/rpicam-apps/blob/7b69b7cde5612677b0eb3ee29bf24ad165a599c1/post_processing_stages/imx500/imx500_object_detection.cpp#L256-L271)

## 一个包含两个候选槽的算例

该示例要求输出信息中有四个张量。设第一个张量能容纳 *N* 个候选框，每框四个坐标。主机将第一个张量的元素数除以 4 得到候选槽数。后面的数据按同样的槽数存放类别和置信度，另有一项记录实际检测数。 [输出张量校验](https://github.com/raspberrypi/rpicam-apps/blob/7b69b7cde5612677b0eb3ee29bf24ad165a599c1/post_processing_stages/imx500/imx500_object_detection.cpp#L229-L249)

| 输出内容 | 计数规则 | 2 个槽 |
| --- | --- | ---: |
| 框坐标 | 每槽 4 | 8 |
| 类别编号 | 每槽 1 | 2 |
| 置信度 | 每槽 1 | 2 |
| 实际检测数 | 每帧 1 | 1 |

按源码，主机收到的扁平数据应有 **6 × 2 + 1 = 13 个浮点元素**。这是主机侧的示例数组长度。实际型号与模型决定张量的容量，相机链路的流量还需计入图像和封装开销。

假设两个候选的类别编号都合法，置信度分别为 0.80 和 0.50，实际检测数为 2。官方配置将置信度门槛设为 0.60，最多检查 5 个候选。这样在单次解析阶段只有第一个候选通过筛选。后续的时序过滤和画框阶段再决定预览上显示哪些结果。 [阈值与时序过滤配置](https://github.com/raspberrypi/rpicam-apps/blob/7b69b7cde5612677b0eb3ee29bf24ad165a599c1/assets/imx500_mobilenet_ssd.json) · [解析和筛选源码](https://github.com/raspberrypi/rpicam-apps/blob/7b69b7cde5612677b0eb3ee29bf24ad165a599c1/post_processing_stages/imx500/imx500_object_detection.cpp#L233-L271)

若要继续比较端侧的算子放置，可以看 STM32N657 怎样在同一 MCU 内协调 NPU 与 CPU。 [STM32N657 Neural-ART](../stm32n657-neural-art/README.md)
