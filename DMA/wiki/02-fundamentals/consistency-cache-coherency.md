# 缓存一致性、IOMMU 与地址空间

上级：[02 基础对象与传输语义](./README.md)

相关：[Non-Coherent vs Coherent DMA](./noncoherent-vs-coherent-dma.md)、[同步、一致性与常见错误](../04-programming-model/synchronization-errors.md)、[PCIE：IOMMU、地址翻译与设备隔离](../../../PCIE/wiki/03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)

## 这页在回答什么问题

为什么很多 DMA 问题表面上像“搬运错了”，根因却是 cache 可见性、地址翻译或权限配置错误；以及为什么 DMA 从来不能简单理解成“拿着物理地址直接搬”。

## Non-coherent DMA 的难点不是 API，而是所有权切换

non-coherent DMA 最根本的问题不是“到底该调哪个 flush/invalidate API”，而是 CPU 和 DMA 看到的数据副本可能不同。CPU cache 里可能还有旧版本，DMA 则直接访问外部 memory；或者反过来，DMA 已经写回 memory，但 CPU 仍在读 cache 里的旧副本。

所以更稳的理解方式不是死记某个平台的 recipe，而是先追踪 buffer ownership。`DMA_TO_DEVICE` 的关键是 CPU 在交出 buffer 前，先让自己的修改对 DMA 可见；`DMA_FROM_DEVICE` 的关键是 CPU 在重新接管 buffer 前，别再读到旧 cache 副本。API 只是具体实现，真正需要被管理的是所有权边界和可见性边界。

## Coherent DMA 为什么仍然会出错

coherent DMA 经常被误讲成“什么都自动对了”。这是危险的。coherent 只说明 CPU 和 DMA 在某个一致性域里共享更统一的数据视图，不说明下面几件事自动成立：

- descriptor 写入与 doorbell 的先后关系正确
- completion 对软件的可见性延迟可以忽略
- 地址翻译与权限检查没有成本
- 一致性流量不会制造额外拥塞

换句话说，coherent 减轻的是“副本不一致”这类劳动，不是把时序、同步和系统性能问题全部抹平。后面 `04-programming-model/synchronization-errors.md` 会反复看到这一点。

## IOMMU / SMMU 改变的是设备的地址世界

DMA 文档里最容易混淆的一个点，是 CPU 进程看到的地址、内核看到的物理页、设备真正发起访问时看到的 IOVA，并不一定是同一个东西。IOMMU / SMMU 的作用，就是在设备侧建立自己的地址视图与保护边界。

它至少在做四件事：

- IOVA 到物理地址的翻译
- 限定设备可访问的地址范围
- 支持 scatter-gather 映射和用户态 buffer 直通
- 在权限错误或缺页时报告 fault

把它理解成园区门禁和路线许可表比较合适。设备不是看到整个城市的真实地图，而是拿着一张只允许自己进入若干区域的通行图。这个类比的边界是：IOMMU 不负责真正搬货，它只决定“这辆车能不能走这条路，以及看到的路标如何翻译成真实地理位置”。

## 地址空间一旦分层，completion 语义也会变化

只要系统里出现 IOMMU、用户态直通设备、多 VM 共用设备或 SR-IOV 一类能力，DMA 就不再是裸物理地址搬运。descriptor 中保存的可能是 IOVA，completion 中记录的 token 也可能要回到某个虚拟函数、某个进程上下文或某个 runtime 队列。

这意味着错误处理不能只看“地址对不对”，还要看“这个地址对谁可见、在什么上下文下可用、谁负责回收映射”。很多 bring-up 问题其实不是数据坏了，而是 mapping 生命周期和 DMA 生命周期错位了。

## 常见误解

常见误解：`只要 coherent 就不用管同步`。实际上 barrier、doorbell 顺序、completion 可见性和 buffer 生命周期仍然需要明确管理。

常见误解：`IOMMU 只是安全附加项`。实际上它会直接影响地址组织、scatter-gather、fault 行为和 steady-state latency。

常见误解：`DMA 看到的地址就是 CPU 打印出来的地址`。实际上用户虚拟地址、内核地址、物理地址、IOVA 往往属于不同视图。

## 一句话理解

DMA 看到的不只是地址和数据，它还必须服从 cache 可见性、地址翻译、权限隔离和 buffer ownership 这些系统语义。

## 建模启示

如果模型里完全没有 `address_domain` 和 `visibility_domain`，那它只能解释理想 memcpy，解释不了真正的 DMA。event-driven 仿真中，至少应显式建模 `map_ready`、`cache_visible`、`dma_access_ok`、`fault_raised` 这几类状态或事件。

一个够用的状态结构可以写成：

```text
BufferState {
  cpu_visible
  dma_visible
  mapped_iova
  owner: cpu | dma | shared
}
```

只关心吞吐时，可以把 translation latency 折叠成固定或分布式开销；只要关心功能正确性、fault 或用户态直通，`owner`、`mapped_iova` 和 `fault_raised` 就必须保留。
