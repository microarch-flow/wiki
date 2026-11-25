"""Stable published pages and source-aligned groups for storage navigation."""

# Keep these legacy URLs tied to their source section when validating publication.
MEMORY_LEGACY_PAGE_SECTION = {
    "RAM/wiki/09-ai-chip-memory-architecture/data-movement-first-principle.md": "04-npu-case",
    "RAM/wiki/09-ai-chip-memory-architecture/weight-buffer-design.md": "04-npu-case",
}

INTEGRATION_LEGACY_PAGE_SECTION = {
    "RAM/wiki/08-packaging-integration/hbm-2.5d-3d-tsv.md": "packaging",
    "RAM/wiki/08-packaging-integration/why-hbm-is-expensive.md": "packaging",
}

# Published URLs that lead into sections of merged storage articles.
STORAGE_LEGACY_PAGES = {
    *MEMORY_LEGACY_PAGE_SECTION,
    *INTEGRATION_LEGACY_PAGE_SECTION,
    "RAM/wiki/02-sram-foundations/sram-macro-interface-and-semantics.md",
    "RAM/wiki/04-dram-foundations/row-column-decode-sense-amplify.md",
    "RAM/wiki/04-dram-foundations/row-buffer-as-cache.md",
    "RAM/wiki/05-dram-protocol-families/timing-parameters-trcd-trp-tras.md",
    "RAM/wiki/06-memory-controller/page-policy-open-close-adaptive.md",
}

MEMORY_TOPIC = "存储层级与数据路径"
STORAGE_RESOURCES = "查阅与练习"
RESOURCE_HOME = "RAM/wiki/reading-and-reference/README.md"
MEMORY_HOME = "RAM/wiki/01-overview/README.md"
SYSTEM_SELECTION = "RAM/wiki/07-system-architecture/why-systems-choose-different-memory.md"
INTEGRATION_TOPIC = "存储系统集成与选型"
INTEGRATION_HOME = "RAM/wiki/system-integration/README.md"
INTEGRATION_PACKAGING = (
    ("封装与集成", "RAM/wiki/08-packaging-integration/README.md"),
    ("DIMM 与 SODIMM", "RAM/wiki/08-packaging-integration/dimm-sodimm-traditional-forms.md"),
    ("PoP 与 MCP", "RAM/wiki/08-packaging-integration/pop-mcp-mobile-integration.md"),
)
INTEGRATION_AFTER = (
    ("NPU 的 HBM 与 LPDDR 选型", "RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu.md"),
    ("CXL 与近存计算", "RAM/wiki/08-packaging-integration/future-packaging-cxl-near-memory.md"),
)
INTEGRATION_PAGE_SECTION = {
    **INTEGRATION_LEGACY_PAGE_SECTION,
    INTEGRATION_HOME: "",
    SYSTEM_SELECTION: "",
    **{page: "packaging" for _, page in INTEGRATION_PACKAGING},
    **{page: "" for _, page in INTEGRATION_AFTER},
}

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
        ("Cache 怎样判断命中", "RAM/wiki/07-system-architecture/cache-hit-lookup.md"),
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
        ("权重驻留与阵列供数", "RAM/wiki/09-ai-chip-memory-architecture/npu-memory-hierarchy.md"),
        ("激活缓冲与双缓冲", "RAM/wiki/09-ai-chip-memory-architecture/activation-buffer-and-double-buffering.md"),
        ("片上带宽预算", "RAM/wiki/09-ai-chip-memory-architecture/on-chip-bandwidth-budget.md"),
    )),
)

RESOURCE_SECTIONS = (
    ("阅读路线与自测", "01-reading", (
        ("阅读路线与自测", "RAM/wiki/README.md"),
        ("按目标选择学习路径", "RAM/wiki/01-overview/learning-roadmap.md"),
        ("自测问题", "RAM/self-test-questions.md"),
        ("Cache 与 scratchpad 原入口", "COMPUTE/wiki/06-memory-discipline/README.md"),
    )),
    ("参考资料与工具", "02-reference", (
        ("参考资料与工具", "RAM/wiki/10-reference/README.md"),
        ("术语表", "RAM/wiki/10-reference/glossary.md"),
        ("高频问答", "RAM/wiki/10-reference/high-frequency-questions.md"),
        ("跨层分析要点", "RAM/wiki/10-reference/first-principles.md"),
        ("DRAM 时序速查", "RAM/wiki/10-reference/timing-parameter-cheatsheet.md"),
        ("SRAM 选型清单", "RAM/wiki/10-reference/sram-design-checklist.md"),
        ("DRAM 性能排查清单", "RAM/wiki/10-reference/dram-debug-checklist.md"),
        ("存储系统建模模板", "RAM/wiki/10-reference/memory-modeling-template.md"),
    )),
)

MEMORY_PAGE_SECTION = {
    **{page: directory for _, directory, pages in MEMORY_SECTIONS for _, page in pages},
    **MEMORY_LEGACY_PAGE_SECTION,
}
RESOURCE_PAGE_SECTION = {page: directory for _, directory, pages in RESOURCE_SECTIONS for _, page in pages}
