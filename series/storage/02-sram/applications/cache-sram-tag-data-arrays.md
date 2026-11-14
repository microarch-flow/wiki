# Cache 的 tag 与 data 阵列：查找路径与实现取舍

上级：[SRAM 应用形态](./README.md)

相关：<span id="cache-里的-sramtag-阵列与-data-阵列的差异"></span>[寄存器堆](./register-file-as-sram.md) · [Cache miss 的处理](../../01-memory-hierarchy/02-access-paths/cache-dram-coordination.md)

## 这页在回答什么问题

Cache 里的 SRAM：tag 阵列与 data 阵列的差异是什么？本页解释一笔访问如何用地址查找、比较和选择数据，以及不同访问顺序对命中时间和活动范围的影响。

## 数据阵列与标记阵列的职责

Data 阵列保存缓存行的数据。Tag 阵列保存用于区分地址的标记；有效位以及脏位、一致性和替换状态等元数据也参与控制，但不必与 tag 放在同一个物理阵列。Tag 和 data 可以使用 SRAM，具体实现由 cache 设计决定。

访问时，索引选择候选 set，候选 tag 与请求地址比较；有效匹配决定命中及相应的 way。Data 可以与查找并行读取，也可以等命中判定后读取。未命中的后续请求、填充和可能的回写见 [Cache miss 的处理](../../01-memory-hierarchy/02-access-paths/cache-dram-coordination.md)。

### 一个地址与容量例子

假设地址为 **32 bit 物理地址**，cache 使用物理索引和物理 tag，有 64 个 set、2 个 way，每行 64 B。忽略虚拟地址、额外寻址或压缩：

| 项目 | 推导 | 结果 |
| --- | --- | --- |
| 行内偏移 | log₂(64 B) | 6 bit |
| set 索引 | log₂(64) | 6 bit |
| 每行 tag | 32 − 6 − 6 | 20 bit |
| 数据容量 | 64 set × 2 way × 64 B | 8 KiB |
| tag 位数 | 64 × 2 × 20 | 2,560 bit，即 320 B |
| 有效位 | 每行 1 bit，共 128 行 | 128 bit，即 16 B |

这里的 tag 容量不含有效位、脏位、替换状态、ECC、阵列外围或副本；有效位也未计入数据容量。该结果不适用于所有索引方案或地址宽度。IBM 的[片上 tag SRAM 论文](https://research.ibm.com/publications/15-kb-15-ns-access-on-chip-tag-sram)给出了一个实际的组相联 cache tag 电路实例。

### 串行和并行的命中路径

设 tag 读取、比较、data 读取和输出选择的延迟分别为 T<sub>tag</sub>、T<sub>cmp</sub>、T<sub>data</sub> 和 T<sub>mux</sub>。以下只比较同一请求的组合路径，假设路径起点和终点对齐，选择后无其他关键延迟：

<div class="ram-calculation">
  <span>先查 tag，再读取命中 way：T = T<sub>tag</sub> + T<sub>cmp</sub> + T<sub>data</sub> + T<sub>mux</sub></span>
  <span>tag 与候选 data 同时启动：T = max(T<sub>tag</sub> + T<sub>cmp</sub>, T<sub>data</sub>) + T<sub>mux</sub></span>
</div>

并行访问可能缩短组合路径，但可能同时激活没有命中的 data way。串行访问可以等判定后再读数据，却增加路径依赖。Way prediction 可能减少活动范围，也需要处理预测错误。实际设计可能分流水或使用不同的选择电路；上述公式不能替代时序分析，也不能仅凭访问顺序推断实际功耗。

在容量、地址映射、替换和请求序列均不变，且没有预测副作用的假设下，只改变 tag/data 的访问顺序不必改变 miss 数。

## 一句话理解

Tag 和控制逻辑判断数据能否作为命中结果；data 阵列提供对应内容。两条路径的组织共同影响命中时序与访问活动。

## 建模启示

若只关心固定命中延迟，可以使用已校准的接口参数。若比较阵列组织或能耗，需要分别表达 tag 查找、比较、data 读取、way 选择和流水边界；研究 miss 时还应加入填充、替换与共享资源。记录被激活的 way 和实际读宽，避免把逻辑命中数直接当成物理阵列访问量。
