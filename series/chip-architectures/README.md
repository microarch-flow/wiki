# 芯片架构实例

本系列按具体产品和代际阅读芯片的计算、存储、互连及软件映射。它包含从原仓迁入的架构笔记，并非统一条件下的性能实测。原稿中的推断、商业判断与性能比较仍需结合各自出处和测量条件评估。

- [AWS Inferentia2 / NeuronCore-v2](AWS-NeuronCore/README.md)：器件与片上引擎。横向报告中的 Trainium2 使用 NeuronCore-v3，不能混用其规格。
- [Cerebras WSE / CS 系统](Cerebras/README.md)：WSE 是晶圆级芯片，CS 是系统。文章分别标注 WSE-2、CS-2 与 WSE-3、CS-3 资料。
- [Graphcore IPU](Graphcore_IPU/README.md)：以 Colossus Mk2 GC200 的 tile、同步和交换为主要例子。
- [Meta MTIA](Meta_MTIA/README.md)：区分第一代 MTIA 1 和第二代 MTIA 2i 的芯片及实验。
- [SambaNova RDU](SambaNova/README.md)：以 SN40L 为主，区分单 RDU 参数和系统级资源；部分历史示例来自 SN10。
- [云端芯片架构横向对比报告](云端推理芯片架构横向对比报告.md)：原报告的比较范围、编写日期和资料口径随文保留。

不同产品的峰值吞吐、片上带宽与片外带宽采用不同口径。比较前应核对产品代际、精度、工作负载、系统边界及测量方法。Groq 和 Maia 100 暂无经整理的独立主文；报告中保留它们的资料入口。

原稿中引用的 30 张图片未确认转载许可。本站用文字说明和原发布资料链接替代；逐图记录见[图片来源与公开边界](https://github.com/microarch-flow/wiki/blob/main/docs/migration/chip-image-provenance.md)。
