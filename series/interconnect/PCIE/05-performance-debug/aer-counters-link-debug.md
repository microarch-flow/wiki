---
title: "AER 与链路计数器：错误在哪里被观察到？"
---

<div id="aer计数器与链路调试路径" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# AER 与链路计数器：错误在哪里被观察到？

上级：[性能与调试](README.md)

AER（Advanced Error Reporting）扩展 PCIe 的错误记录和报告能力。报错端口是观察点，不必然是故障源。要定位问题，应同时记录事务、链路状态、设备状态及平台日志。

## AER 在做什么

错误分为 Correctable 与 Uncorrectable；后者再按严重性分 Non-Fatal 与 Fatal。分类不是固定的恢复脚本。某些错误由硬件机制纠正，其他错误可能需要驱动恢复、复位或隔离。

操作系统是否收到报告还受硬件能力、使能、掩码、固件控制和平台处理影响。Linux 的 AER 使用与恢复流程见[官方指南](https://docs.kernel.org/PCI/pcieaer-howto.html)。

## 常见观测点

<div class="bus-read-trace" markdown="1">

| 观察点 | 记录内容 | 注意事项 |
| --- | --- | --- |
| 目标 Function 及每跳端口 | BDF、LnkCap/LnkSta、速率和宽度 | 端点能力不能替代沿途实际状态 |
| AER 状态与日志 | 错误类型、源身份、可用头部日志、时间 | 掩码和日志限速会影响可见数量 |
| 设备或控制器计数器 | replay、信用等待、吞吐、请求状态 | 定义、清零方式和方向依实现 |
| 驱动与平台 | 命令超时、IOMMU fault、恢复动作 | 对齐时间线，保留恢复前证据 |

</div>

<div id="调试时先分三层" class="pcie-legacy-anchor"></div>

## 调试时先分观察层次

链路未建立或协商宽度异常，先查复位、配置和训练路径；重放增加，查传输可靠性及对应链路；UR、CA 或 Completion Timeout，则结合原始请求和路由检查事务路径。AER 可能记录不同层次的错误，不能把“AER 报错”直接归为某一层。

例如同一窗口吞吐下降、重放计数增加，但没有新的 AER 日志。它支持“发生了控制器定义的重放事件”，不支持“没有错误”或“打开 AER 导致重放”。反过来，多条 AER 日志也不能直接换算为同样数量的重发包。

<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 从只读记录开始

假设要检查一块挂在 PCIe Switch 下的加速卡。下面的地址、能力和状态都是**教学构造**，输出按 pciutils 的格式删节。先在 Linux 上读拓扑，再读同一条链路两端的配置空间。这两步都只读。不同 pciutils 版本的标签可能有差异，权限也会影响能看到哪些字段。[lspci 手册](https://man7.org/linux/man-pages/man8/lspci.8.html)

```text
$ lspci -t
-[0000:00]---01.0-[01-03]----00.0-[02-03]----01.0-[03]----00.0
```

从左往右读，`[0000:00]` 是域 0000 的根总线 00。方括号前的 `01.0` 是这条总线上的设备号和功能号，合起来就是根端口 `0000:00:01.0`。它后面的 `[01-03]` 表示桥后可达的总线号范围，紧接着的 `00.0` 位于这段范围的首条总线 01。照此再读两次，就能找到末跳的两端。

<div class="bus-read-trace" markdown="1">

| 树中的位置 | 完整地址 | 在本例中的角色 |
| --- | --- | --- |
| 根总线上的 `01.0` | `0000:00:01.0` | 根端口，接到 Switch |
| `[01-03]` 后的 `00.0` | `0000:01:00.0` | Switch 上行端口，面向根端口 |
| `[02-03]` 后的 `01.0` | `0000:02:01.0` | Switch 下行端口，直接接卡 |
| `[03]` 后的 `00.0` | `0000:03:00.0` | 卡上的端点 Function |

</div>

树给出了父子关系，速率和宽度要从端口的配置空间读取。为了解卡所在的这一跳，用 `-s` 分别选中最后两个地址，用 `-vv` 查看详细字段。以下仅保留与本例有关的行，省略号表示删节。

```text
$ lspci -D -s 0000:02:01.0 -vv
        Capabilities: [40] Express (v2) Downstream Port (Slot-), ...
                LnkCap: Port #1, Speed 16GT/s, Width x8, ...
                LnkSta: Speed 8GT/s, Width x4

$ lspci -D -s 0000:03:00.0 -vv
        Region 0: Memory at 80000000 (32-bit, non-prefetchable) [size=64K]
        Capabilities: [80] Express (v2) Endpoint, ...
                LnkCap: Port #0, Speed 16GT/s, Width x8, ...
                LnkSta: Speed 8GT/s (downgraded), Width x4 (downgraded)
```

- `Downstream Port` 和 `Endpoint` 确认了两份记录各来自哪一端。`Express (v2)` 中的版本号属于这组能力寄存器，链路代际要从速率字段读。
- `LnkCap` 表示本端支持的最高速率和最大宽度。两端各报 16 GT/s、x8，即每条 lane 最高每秒 160 亿次传输，最多 8 条 lane。
- `LnkSta` 表示读取时已协商的状态。两端都显示 8 GT/s、x4，因此卡到 Switch 的这一跳此时以 Gen3 x4 工作。pciutils 可能只在端点旁标出 `(downgraded)`，两行中的数值仍然一致。[pciutils 链路字段解码](https://github.com/pciutils/pciutils/blob/master/ls-caps.c)
- `Region 0` 是卡的 BAR0。本例假设 CPU 侧资源地址与 PCI 总线地址数值相同，窗口从 `0x80000000` 起共 64 KiB，使用 32 位内存 BAR，标记为不可预取。这个窗口告诉驱动去哪里访问寄存器，窗口大小与链路宽度分别描述两件事。

这张快照只能确定末跳当时的状态。要判断是否曾以 Gen4 x8 运行、是否影响业务，还需要平台配置、历史状态和同一负载下的对照，见[链路降速案例的带宽计算与对照](../06-workloads-case-studies/link-downgrade-case-card.md#一个构造例子)。写配置、清状态或触发重训练之前，应先保存这份快照和对应时间的日志。事务错误的判别见 [UR、CA 与 Timeout](common-failures-ur-ca-timeout.md)。
