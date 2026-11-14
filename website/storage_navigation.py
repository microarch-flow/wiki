"""Stable published pages and source-aligned groups for storage navigation."""

MEMORY_TOPIC = "存储层级与数据路径"
STORAGE_RESOURCES = "查阅与练习"
MEMORY_HOME = "RAM/wiki/01-overview/README.md"
SYSTEM_SELECTION = "RAM/wiki/07-system-architecture/why-systems-choose-different-memory.md"

# Entries use the preserved staging paths. prepare.py validates that every
# page's current source directory matches its section before it is published.
MEMORY_SECTIONS = (
    ("系统基础", "01-system-basics", (
        ("系统视角", "RAM/wiki/07-system-architecture/README.md"),
        ("存储系统为何难设计", "RAM/wiki/01-overview/problem-statement.md"),
        ("RAM 分类与命名", "RAM/wiki/01-overview/taxonomy.md"),
        ("存储层次与系统角色", "RAM/wiki/07-system-architecture/memory-hierarchy-as-system.md"),
        ("速度·容量·成本·功耗", "RAM/wiki/01-overview/memory-hierarchy-tension.md"),
        ("局部性与数据搬运", "RAM/wiki/01-overview/locality-working-set-data-movement.md"),
        ("SRAM 与 DRAM 的分化", "RAM/wiki/01-overview/sram-dram-divergence.md"),
    )),
    ("访问路径与数据管理", "02-access-paths", (
        ("Cache miss 的处理", "RAM/wiki/07-system-architecture/cache-dram-coordination.md"),
        ("Cache 与 scratchpad", "COMPUTE/wiki/06-memory-discipline/cache-vs-scratchpad.md"),
        ("SRAM bank 与 DRAM 行状态", "RAM/wiki/07-system-architecture/sram-vs-dram-access-pattern.md"),
        ("多通道与 NUMA", "RAM/wiki/07-system-architecture/numa-multi-channel-multi-socket.md"),
    )),
    ("性能分析与瓶颈", "03-performance", (
        ("带宽与延迟", "RAM/wiki/07-system-architecture/bandwidth-vs-latency-fundamental.md"),
        ("峰值与有效带宽", "RAM/wiki/07-system-architecture/effective-bandwidth-vs-peak.md"),
        ("存储瓶颈与计算瓶颈", "RAM/wiki/09-ai-chip-memory-architecture/memory-bound-vs-compute-bound.md"),
    )),
    ("NPU 数据路径与存储组织", "04-npu-case", (
        ("NPU 数据路径与存储组织", "RAM/wiki/09-ai-chip-memory-architecture/README.md"),
        ("NPU 存储层次", "RAM/wiki/09-ai-chip-memory-architecture/npu-memory-hierarchy.md"),
        ("数据搬运与复用", "RAM/wiki/09-ai-chip-memory-architecture/data-movement-first-principle.md"),
        ("权重缓冲区", "RAM/wiki/09-ai-chip-memory-architecture/weight-buffer-design.md"),
        ("激活缓冲与双缓冲", "RAM/wiki/09-ai-chip-memory-architecture/activation-buffer-and-double-buffering.md"),
        ("片上带宽预算", "RAM/wiki/09-ai-chip-memory-architecture/on-chip-bandwidth-budget.md"),
    )),
)

RESOURCE_SECTIONS = (
    ("阅读路线与自测", "01-reading", (
        ("RAM 阅读路线", "RAM/wiki/README.md"),
        ("学习路径与章节依赖", "RAM/wiki/01-overview/learning-roadmap.md"),
        ("自测问题", "RAM/self-test-questions.md"),
        ("Cache 与 scratchpad 原入口", "COMPUTE/wiki/06-memory-discipline/README.md"),
    )),
    ("参考资料", "02-reference", (
        ("参考资料", "RAM/wiki/10-reference/README.md"),
        ("存储设计第一性原理", "RAM/wiki/10-reference/first-principles.md"),
        ("术语表", "RAM/wiki/10-reference/glossary.md"),
        ("高频问答", "RAM/wiki/10-reference/high-frequency-questions.md"),
        ("DRAM 时序速查", "RAM/wiki/10-reference/timing-parameter-cheatsheet.md"),
        ("SRAM 选型清单", "RAM/wiki/10-reference/sram-design-checklist.md"),
        ("DRAM 调试清单", "RAM/wiki/10-reference/dram-debug-checklist.md"),
        ("存储系统建模模板", "RAM/wiki/10-reference/memory-modeling-template.md"),
    )),
)

MEMORY_PAGE_SECTION = {page: directory for _, directory, pages in MEMORY_SECTIONS for _, page in pages}
RESOURCE_PAGE_SECTION = {page: directory for _, directory, pages in RESOURCE_SECTIONS for _, page in pages}
