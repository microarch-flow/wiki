# Scratchpad 与 cache：SRAM 应用导读

<span id="scratchpad-和-cache-都是-sram差异在哪"></span>
<span id="这页在回答什么问题"></span>

上级：[SRAM 应用形态](./README.md)

本页原题为《Scratchpad 和 cache 都是 SRAM，差异在哪》。两种存储角色的数据放置、访问路径、写入和管理代价，已整理到[Cache 与 scratchpad](../../01-memory-hierarchy/02-access-paths/cache-vs-scratchpad.md)。

## SRAM 与两种系统角色 {#地址管理与数据放置方式}

Cache 的数据阵列和片上 scratchpad 都常用 SRAM。Cache 还要判断地址是否命中，并管理数据填充和替换；scratchpad 通常提供显式的本地地址，由使用方安排数据放置与生命周期。

相同的 SRAM 容量不代表两种资源的完整实现成本相同。比较时需要同时考虑 tag、控制、端口、bank、互连和具体工作条件。两种角色也不被限定为某一种物理实现。

## 一句话理解

SRAM 描述一种存储技术；cache 和 scratchpad 描述数据怎样在系统中被使用和管理。详细比较见 [Cache 与 scratchpad](../../01-memory-hierarchy/02-access-paths/cache-vs-scratchpad.md)。

## 建模启示

按研究问题区分 cache 的查找与替换、scratchpad 的放置与同步，以及两者共享的端口和 bank。需要比较访问时间时，应同时说明请求到达、接纳和完成的边界。

## 接下来怎么读？

- [Cache 与 scratchpad](../../01-memory-hierarchy/02-access-paths/cache-vs-scratchpad.md)：从同一份数据比较访问路径和管理责任。
- [Cache 的 tag 与 data](./cache-sram-tag-data-arrays.md)：看命中判断、阵列组织和时序路径。
- [NPU 的 SRAM buffer](./npu-weight-buffer-activation-buffer.md)：看局部数据的生命周期、端口和搬运。
