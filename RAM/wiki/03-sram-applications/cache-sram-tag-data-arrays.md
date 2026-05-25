# Cache 里的 SRAM：tag 阵列与 data 阵列的差异

上级：[SRAM 应用形态](./README.md)
相关：[Register file 为什么是一种特殊 SRAM](./register-file-as-sram.md), [Cache 和 DRAM 如何协同，miss 之后发生了什么](../07-system-architecture/cache-dram-coordination.md)

## 这页在回答什么问题

cache 为什么不能被理解成“一个普通 SRAM 宏，只是里面装了缓存数据”。更准确地说，cache 是怎样把 SRAM 阵列、tag 比较、命中判断和替换控制绑成一个整体的，以及为什么 tag array 和 data array 虽然都用 SRAM 实现，却承担了完全不同的时序角色。

## 正文

把 cache 粗略描述为”用 SRAM 做出来的高速缓存”当然没错，但这句话最大的问题是把 cache 的关键复杂性抹掉了——就像说”图书馆就是一屋子书”，忽略了分类目录、借阅系统和管理员。真正让 cache 成为 cache 的，不是它用了 SRAM，而是它把一块 SRAM 变成了一个由硬件管理的、带命中不确定性和替换语义的数据层。register file、scratchpad 和 cache 都可能用 SRAM 实现，但只有 cache 会主动替软件猜：当前访问的地址有没有已经被我留在本地，如果有，它在哪一行、哪一路、是否有效、是否脏、是否需要回写。这个”猜”的过程，决定了 cache 绝不是一块单纯的数据阵列。

这也是为什么 cache 往往天然分成 `tag array` 和 `data array`。data array 负责存放真正的数据块，通常按 cache line 组织，因此容量占大头。tag array 则存放每条 line 对应的地址标签、valid/dirty 等元数据，并参与比较判断。两者虽然都常常由 SRAM cell 组成，但它们服务的时序任务不同：data array 关注的是在命中后尽快把整块或部分字返回；tag array 关注的是在访问的很早阶段尽快判定“这是不是我要的那条 line”。常见误解是认为 tag 只是 data 的附属注释——就像以为图书馆的索引卡片只是"装饰"。实际上，很多 cache 的关键频率路径首先卡在 tag 查找和命中判决（你找到索引卡片的速度），而不只是卡在数据本身的读取（从书架上取书的速度）。

先看为什么 tag 路径往往比直觉中更敏感。一次 cache 访问要先根据 index 找到一个 set，对应地读出该 set 中所有候选 way 的 tag，再把访问地址中的 tag 字段和这些候选标签比较，最后决定是否命中以及命中哪一路。只有这个判决结束后，系统才能确定 data array 里哪一路的数据是有效目标，或者是否需要走 miss 路径。换句话说，tag 路径不只是“读一点小 metadata”，而是要在极短时间里完成 `读 tag -> 比较 -> 选择` 这整串控制判断。尤其在高关联度 cache 中，way 越多，比较器越多，判决和多路选择就越重。

data array 的压力则不同。它通常承载更大的位宽和更高的总容量，因此更受 bitline 长度、bank 切分、line 宽度和读出能耗影响。tag array 容量小得多，但每次访问几乎必然要读，而且要尽早得出结果；data array 容量大、读宽高，但命中时才真正有价值。因此两者的最优组织未必一致。很多 cache 设计会让 tag array 更小、更快、可能甚至复制或分片得更激进，而 data array 则更多围绕 line 宽度、bank 并行和访问能耗去组织。你如果只把 cache 看成“一块 SRAM”，就会错过这组内部分化。

这里还会自然引出一个和 register file 很不一样的点：cache 不会轻易为“任意并发访问”直接付真多端口代价。因为 cache 访问虽然频繁，但它的管理语义允许设计者引入更多结构化优化。例如，I-cache 和 D-cache 分离，本身就是在系统层拆并发；多 bank 可以让不同 index 落到不同数据块；way prediction 可以提前猜一路，降低全并行读取压力；tag array 可以复制而 data array 维持较少端口；非阻塞 cache 可以把 miss 管理和 hit 返回解耦。换句话说，cache 的性能提升常常来自组织和流水，而不是像 register file 那样直接把同拍多读多写都硬吃进单体阵列。

这也是为什么 tag/data array 的关系不能只画成“左边存 tag，右边存 data”的静态图。两者之间还隔着命中判决、多路选择、替换状态、dirty 管理、fill/writeback 路径。比如一次 load hit，表面上只是取到数据；但内部实际上至少经历了 `set index -> tag compare -> hit way select -> data mux -> word select`。若 miss，还会进一步触发 miss status tracking、victim 选择、可能的 writeback，以及后续 refill。tag array 在这里的作用，不是提供辅助信息，而是决定你到底能否把 data array 当前读出的内容当成合法结果。

tag 和 data 的时序关系在不同 cache 里也会不同。最激进的 L1 设计常常追求一拍命中，因此会让 tag compare 和 data access 高度并行，再在周期后半段决定取哪一路的数据。这种设计追求延迟极低，但能耗较高，因为可能会同时激活多路 data array。另一类设计会先判 tag 再读 data，或者用 way prediction 缩小数据读取范围，以换取更低能耗或更容易提频。这里没有单一最优解，只有不同目标函数下的取舍。常见误解是把 cache hit latency 当成一个纯容量函数；实际上，关联度、tag/data 组织和能耗策略同样深度参与其中。

从 SRAM 角度看，cache 的特殊性还在于它把”不确定性”制度化了。register file 就像你自己的口袋——你确切知道里面有什么；scratchpad 像你的书桌——你亲手摆放了每一份文件；TCM 像固定工位上的文件架——位置永远不变。而 cache 更像一个智能助手替你管理的工作台：它会猜你接下来可能需要哪些文件，提前放好；猜对了你很高兴，猜错了你就得等它去档案室现找。SRAM 在这里承载的不只是存储，还承载了一个基于局部性的投机策略。这种策略的收益是平均延迟下降，代价是引入命中/未命中不确定性、替换副作用和更复杂的控制路径。

把 cache 放回应用谱系里看，它和 register file 的差别就更清楚了。两者都追求快，但 register file 优先保同拍并发和严格语义，因此愿意为多端口正面付费；cache 优先保平均访问延迟，因此更愿意为 tag 比较、关联度、替换和分层管理付费。它们底层都用 SRAM，甚至都可能受相似的位线与 bank 约束，但上层目标函数完全不同。也正因为如此，cache 的“难点”往往不是把某个 cell 读快一点，而是怎样在命中路径、能耗和 miss 代价之间找到系统最优点。

后面当我们进入 DRAM 和系统层时，这种差异会更重要。因为 cache 并不是 SRAM 话题的终点，而是连接片上快速存储和片外主存的第一道转换层。tag/data 组织方式决定命中路径速度，也决定 miss 发起频率和 refill 粒度；这些因素最终都会传导到 memory controller 和 DRAM 访问模式上。理解 cache 里的 SRAM，不是为了单独学一个结构，而是为了看清它如何把局部 SRAM 约束翻译成整机行为。

## 一句话理解

Cache 不是“一块存数据的 SRAM”，而是由 tag array、data array 和命中/替换控制共同组成的局部性管理器；tag 路径之所以关键，是因为它决定 data array 读出的内容能不能算结果。

## 建模启示

在架构模型里，cache 不应被压成一个统一的 `latency + hit_rate` 黑盒，至少应该把 `tag check` 和 `data access` 分成两个阶段，因为它们决定了是否能做 way prediction、tag/data 并行访问，以及 hit latency 与能耗的关系。只用一个单标量 latency，很难表达“同样命中率下，为什么两个 L1 cache 的频率和能耗表现差很多”。

一个够用的抽象草图可以是：

```text
CacheSramModel {
  sets: int
  ways: int
  line_bytes: int
  tag_read_cycles: int
  tag_compare_cycles: int
  data_read_cycles: int
  tag_data_parallel: bool
  way_prediction: bool
  bank_count: int
}
```

对应事件流可以写成：

```text
event TagLookup(cache_id, set_id, req_id)
event TagMatchResolve(cache_id, req_id, hit, hit_way)
event DataArrayRead(cache_id, bank_id, way_id, req_id)
event CacheHitReturn(cache_id, req_id)
event CacheMissAllocate(cache_id, req_id)
```

如果只关心粗粒度系统性能，`tag_read_cycles + tag_compare_cycles + data_read_cycles` 可以折叠成单个 hit latency；但如果你需要分析 L1 频率、能耗，或者研究 cache 组织选择对 miss 流量的影响，`tag_data_parallel` 和 `way_prediction` 这类字段就不应该省略。它们直接决定“为了一拍命中，你是否愿意每次多唤醒几路 data array”。
