# Row buffer：DRAM 内部的小 cache

上级：[DRAM 基础](./README.md)
相关：[行列解码与读出放大：为什么 DRAM 必须先开行](./row-column-decode-sense-amplify.md), [Cache 里的 SRAM：tag 阵列与 data 阵列的差异](../03-sram-applications/cache-sram-tag-data-arrays.md)

## 这页在回答什么问题

为什么很多人会把 row buffer 类比成 DRAM 内部的小 cache，以及这个类比到底在哪些地方成立、在哪些地方会误导。更关键的是，row buffer 为什么会把一个本来“很慢的大内存”，变成一个对访问模式高度敏感的层次化对象。

## 正文

只要你理解了上一页“为什么 DRAM 必须先开行”，row buffer 的概念就已经呼之欲出了。某一行被激活时，这一整行 cell 的状态会被感测到 sense amp 一侧，并在那里暂时维持成一个可读、可写、可继续列访问的工作副本。对于后续针对同一行的访问来说，系统不需要再重新经历那笔昂贵的行打开成本，而只需要在已打开行中做列选择。因此，从性能现象上看，row buffer 的确很像一个只容纳当前打开行的小缓存：命中了它，延迟显著低；没命中，就要付出大得多的前置成本。

这个类比为什么有用，首先在于它抓住了一个真实结构相似性：两者都在用更靠近访问路径的较快状态，去屏蔽更慢、更原始的底层存储访问。对 cache 来说，被屏蔽的是下一级 SRAM 或 DRAM；对 row buffer 来说，被屏蔽的是重新对原始 DRAM cell 执行整行感测和恢复。于是 row hit 与 cache hit 一样，都会让后续访问看上去突然便宜很多。也正因为这种命中现象真实存在，row locality 才会成为理解 DRAM 性能的核心词。

但 row buffer 绝不是一个真正意义上的通用 cache。第一，它的内容不是通过 tag 和替换策略“主动挑出来”的，而是某次 ACT 之后被动形成的整行工作副本。第二，它的粒度固定而且很粗，一次就是整行，而不是按 cache line 精细管理。第三，它不是一个独立于底层阵列的附加存储层，而是 sense amp 在执行感测与恢复后顺手承担的暂存角色。第四，是否“命中”它，取决于目标地址是不是当前 bank 中已经打开的那一行，而不是由硬件替换算法根据局部性智能保留了哪几块数据。常见误解就是把 row buffer 想成 DRAM 内部真正的 L0 cache；这个说法会把它和 cache 的管理语义混为一谈。

更准确的说法是：row buffer 更像是 DRAM 阵列访问副作用形成的工作集窗口。你之所以能命中它，不是因为系统事先聪明地把这行留在了更快层，而是因为上一笔访问刚好已经把这整行激活出来，而且 controller 还没有把它关掉或切换到别的行。这也是为什么 row buffer 的命中如此依赖访问顺序。若一串请求在同一 bank 上持续复用同一行，它们会显得像在“高速缓存”里连续命中；若请求在同一 bank 上来回切换不同行，则每次都要付出 precharge + activate 的开销，看上去会非常痛苦。

因此，row buffer 真正重要的地方，不是它像不像 cache，而是它把 DRAM 的访问成本做成了强烈的二态分布。对同一 bank 中同一行的后续列访问，代价可能接近“只付列访问成本”；一旦换到别的行，代价就跳到“先关当前行，再开新行，再列访问”。这种大幅跳变是 DRAM 与 SRAM 最根本的访问模式差异之一。SRAM 的本地访问成本通常相对稳定，而 DRAM 的访问成本会因为 row buffer 是否命中而出现明显分层。后面 page policy 和 address mapping 的很多优化，实际上都在努力提升 row buffer 的有效利用率。

row buffer 为什么对系统性能如此关键，还因为它把工作负载的空间局部性重新映射成了“行局部性”。软件层面看到的是地址流，controller 看到的是这些地址经映射后落在哪个 channel、bank、row、column。只有当相邻或相关访问在同一 bank 中恰好落到同一 row 时，row buffer 命中才会发生。也就是说，row locality 不是程序地址顺序本身的属性，而是“程序地址模式 + 地址映射方式 + DRAM 组织”三者共同作用的结果。常见误解是认为只要程序有顺序访问就一定 row hit 多；实际上，如果地址映射把相邻地址优先打散到多个 bank，行局部性和 bank 并行性之间就会出现 trade-off。

这又带出 row hit、row miss 和 row conflict 这组后续会反复出现的概念。若目标 bank 当前打开的正是目标 row，就是 `row hit`，只需列访问。若目标 bank 当前没有打开任何 row，就是 `row miss`，需要 activate 后再访问。若目标 bank 当前打开的是别的 row，就是 `row conflict`，往往需要先 precharge，再 activate，再访问。把 row buffer 看懂之后，这三者就不再只是控制器里的状态标签，而是三种完全不同成本路径的简写。

为什么这个类比又不能无限延伸到“DRAM = cache 行命中机器”，还因为 row buffer 完全不具备 cache 的一些关键自由度。cache 可以容纳多条 line、可多级层次化、可由替换策略主动保留热点；row buffer 通常每个 bank 只对应一条当前打开行的工作状态，而且它的存在与否直接受预充、刷新、冲突和 page policy 影响。它不像 cache 那样是一个独立的资源池，更像 DRAM 打开行状态的延伸。也正因为这么脆弱，controller 才必须决定“保持行打开多久”“什么时候主动关行”“冲突来时是否牺牲当前局部性”。

与 SRAM cache 再做一次对比，也能帮助收紧边界。cache 的本体常由 SRAM 阵列、tag compare 和替换控制构成，它服务的是“下一级更慢存储”的平均访问优化；row buffer 则直接从 DRAM sense amp 阵列长出来，它服务的是“当前 bank 已打开行”的短期重用。cache miss 会把请求送往下一级层次；row buffer miss 则往往意味着同一层 DRAM 内部需要重新执行昂贵的行切换。两者都能用“命中/未命中”来描述，但它们命中的来源、替换机制和代价传播路径都不一样。

所以，把 row buffer 类比成小 cache 是有价值的，但前提是你明确知道类比的边界。它有用，是因为它帮你迅速抓住“同一行连续访问会便宜很多”这个非平凡事实；它危险，是因为它容易让人误以为 DRAM 内部还有一个像 cache 一样独立管理的小层级。更稳妥的表述应该是：row buffer 是 DRAM 通过整行感测后临时形成的工作副本，而 row locality 是决定 DRAM 访问性能的第一层局部性。

## 一句话理解

Row buffer 像 cache 的地方在于命中后能显著降低后续访问成本；不像 cache 的地方在于它不是被替换策略主动管理的小存储层，而是 DRAM 打开一整行后自然形成的临时工作副本。

## 建模启示

在模型里，row buffer 最关键的不是被单独建成多大容量，而是要被建成 `per-bank open-row state`。也就是说，它更像 bank 状态机的一部分，而不是一个独立缓存模块。只要这层状态存在，`row hit / miss / conflict` 三种代价路径就能自然表达出来。

一个够用的状态草图可以是：

```text
RowBufferState {
  open_row[bank]: row_id | INVALID
  valid[bank]: bool
}
```

对应访问分类可以直接写成：

```text
if valid[bank] and open_row[bank] == target_row:
    access_type = ROW_HIT
elif not valid[bank]:
    access_type = ROW_MISS
else:
    access_type = ROW_CONFLICT
```

如果只关心非常粗粒度的系统吞吐，可以把 row buffer 效果折进一个经验性 row-hit-rate 参数；但只要你要分析 page policy、地址映射或 workload 对 DRAM 的适配程度，就最好显式保留 `open_row` 状态。因为很多看似“同样带宽需求”的工作负载，实际表现差异就是来自 row-hit-rate 的巨大不同。

一个更完整但仍然简洁的数据结构可以是：

```text
DramBankModel {
  open_row: row_id | INVALID
  row_buffer_valid: bool
  last_access_cycle: cycle
  auto_precharge_enabled: bool
}
```

这里的关键不是把 row buffer 复杂化，而是避免把它误建成真正的 set-associative cache。它首先是 bank 内部打开行状态，其次才表现出类似“命中缓存”的性能现象。
