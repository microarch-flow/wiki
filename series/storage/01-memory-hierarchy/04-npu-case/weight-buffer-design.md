---
search:
  exclude: true
---

# NPU 权重缓冲区（原入口）

本页已并入[NPU 连算三个块，为什么外存只读 4 B 权重，阵列却要接收 12 B？](./npu-memory-hierarchy.md)。原文各小节可直接在新文中阅读。

<div markdown="1" data-storage-redirect="true">

- <span id="权重缓冲区从工作集与供数需求确定容量和组织"></span>[计算同时驻留的权重容量](./npu-memory-hierarchy.md#residency)
- <span id="weight-buffer-的容量与组织从-model-size-反推"></span>[从一块权重的驻留时间算空间](./npu-memory-hierarchy.md#residency)
- <span id="这页在回答什么问题"></span>[哪些权重必须同时放得下](./npu-memory-hierarchy.md#residency)
- <span id="权重工作集容量与复用"></span>[工作集、预取与容量](./npu-memory-hierarchy.md#residency)
- <span id="weight-buffer-的容量与组织"></span>[缓冲区怎样及时向阵列供数](./npu-memory-hierarchy.md#supply)
- <span id="局部与共享怎样选择"></span>[局部副本与共享缓冲区](./npu-memory-hierarchy.md#shared)
- <span id="一句话理解"></span>[分别核对容量与供数](./npu-memory-hierarchy.md#residency)
- <span id="建模启示"></span>[区分驻留与真实传输](./npu-memory-hierarchy.md#model)
- <span id="接下来怎么读"></span>[继续看激活供给与片上带宽](./npu-memory-hierarchy.md#next)

</div>
