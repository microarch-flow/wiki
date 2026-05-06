# Samsung HBM / HBM-PIM

## 基本信息

- 公司：Samsung Electronics / Samsung Semiconductor
- 对象：`HBM-PIM`
- 路线归类：`DRAM / HBM-PIM`
- 公司角色：`memory vendor`

## 时间点

- `2021-02-17`：Samsung 公布 HBM-PIM，称其为业界首个将 AI processing power 集成到 HBM 中的产品
- `2026-02-12`：Samsung 官方新闻稿宣布 HBM4 已开始量产并向客户出货

## 官方口径里最值得记的内容

从 `2021-02-17` 的官方新闻看，Samsung 对 HBM-PIM 的核心表述是：

- HBM 内集成 `PIM` 架构
- 面向 `HPC`、training、inference 等 AI workload
- 相比传统 HBM2 系统，性能可提升到两倍以上，系统能耗可降低 70% 以上

这说明 Samsung 对这条路线的定义，从一开始就偏向：

- system-level 提效
- memory-side processing
- 高带宽内存体系内的 offload

而不是阵列级 analog CIM。

## 怎么看这条路线

### 它的核心价值

- 站在内存厂商视角，直接在 memory subsystem 里增强处理能力
- 抓住 AI / HPC 中最痛的数据搬运问题
- 更接近“带处理能力的高带宽内存”而非独立 AI 芯片

### 它的核心边界

- 不应拿来和 `ReRAM-CIM` 的阵列级指标直接比较
- 其收益依赖 workload 是否真的 memory-bound
- 评价它时必须看 host、GPU、controller 和 runtime 的协同

## 在产业图谱中的位置

如果要画一张路线图，Samsung 更适合放在：

- `memory vendor 主导路线`
- `HBM / DRAM-PIM`
- `data center / HPC / AI infra`

而不是：

- edge analog CIM
- 纯片上 SRAM-CIM

## 我的判断

Samsung HBM-PIM 的意义不在于证明“所有 CIM 都会走向 HBM”，而在于它很早就把一个关键问题钉死了：

> 对大模型和大工作集来说，减少 processor 与 memory 之间的数据移动，本身就是一条独立且合理的技术路线。

## 官方来源

- Samsung 新闻稿，`2021-02-17`：<https://semiconductor.samsung.com/news-events/news/samsung-develops-industrys-first-high-bandwidth-memory-with-ai-processing-power/>
- Samsung 技术博客：<https://semiconductor.samsung.com/news-events/tech-blog/hbm-pim-cutting-edge-memory-technology-to-accelerate-next-generation-ai/>
- Samsung HBM 产品页：<https://semiconductor.samsung.com/dram/hbm/>
- Samsung HBM4 量产新闻，`2026-02-12`：<https://news.samsung.com/global/samsung-ships-industry-first-commercial-hbm4-with-ultimate-performance-for-ai-computing>
