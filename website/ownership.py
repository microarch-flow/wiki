"""Assign each existing article to one main series and topic."""

from storage_navigation import RESOURCE_PAGE_SECTION, STORAGE_RESOURCES, SYSTEM_SELECTION

MICRO = "微架构"
STORAGE = "存储系统"
INTERCONNECT = "芯片与系统互连"
DEVELOPMENT = "芯片开发与实现"

GROUPS = {
    MICRO: ("系列导读", "数值格式与算术数据通路", "时钟、流水线与吞吐", "计算阵列与数据流",
            "DMA 与异步数据搬运", "处理单元与芯片顶层组织", "存内计算 CIM", "制造与封测导读"),
    STORAGE: ("存储层级与数据路径", "SRAM 器件与应用", "DRAM 器件与接口", "DRAM 控制器与请求调度",
              "HBF 高带宽闪存", "存储系统集成与选型"),
    INTERCONNECT: ("片上事务与总线（BUS）", "片上网络（NoC）", "系统 I/O 互连（PCIe）",
                   "高速电链路（SerDes）", "共封装光学（CPO）"),
    DEVELOPMENT: ("工程流程与制造导读", "产品定义、成本与实现策略", "RTL 设计与集成", "功能验证、覆盖与阶段签核",
                  "物理设计与签核", "流片与晶圆制造", "封装与多芯粒集成", "可测性设计、晶圆筛测与终测",
                  "硅后启动、测量与修订", "可靠性、良率与量产生命周期", "软件背景创始人导读"),
}

HBM_READING_ENTRY = "RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md"
HBM_SYSTEM_SELECTION = "RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu.md"


def owner(path):
    """Return the primary series and topic for a staged original-wiki path."""
    path = str(path)
    if path == "electrical-timing-foundations.md":
        return MICRO, "时钟、流水线与吞吐"
    if path in RESOURCE_PAGE_SECTION or path.startswith("RAM/wiki/10-reference/"):
        return STORAGE, STORAGE_RESOURCES
    if path == SYSTEM_SELECTION:
        return STORAGE, "存储系统集成与选型"
    if path == HBM_SYSTEM_SELECTION:
        return STORAGE, "存储系统集成与选型"
    if path.startswith("COMPUTE/"):
        for prefix, group in (
            ("02-datapath-foundations", "数值格式与算术数据通路"),
            ("03-systolic-array", "计算阵列与数据流"),
            ("04-clocking-and-pipeline", "时钟、流水线与吞吐"),
            ("05-fpga-vs-asic", "处理单元与芯片顶层组织"),
            ("07-chip-organization", "处理单元与芯片顶层组织"),
            ("08-modeling-for-archax", "处理单元与芯片顶层组织"),
        ):
            if path.startswith(f"COMPUTE/wiki/{prefix}/"):
                return MICRO, group
        if path.startswith("COMPUTE/wiki/06-memory-discipline/"):
            return STORAGE, "存储层级与数据路径"
        return MICRO, "系列导读"
    if path.startswith("RAM/"):
        for prefixes, group in (
            (("02-sram-foundations", "03-sram-applications"), "SRAM 器件与应用"),
            (("04-dram-foundations", "05-dram-protocol-families"), "DRAM 器件与接口"),
            (("06-memory-controller",), "DRAM 控制器与请求调度"),
            (("07-system-architecture", "09-ai-chip-memory-architecture"), "存储层级与数据路径"),
            (("08-packaging-integration",), "存储系统集成与选型"),
        ):
            if any(path.startswith(f"RAM/wiki/{prefix}/") for prefix in prefixes):
                return STORAGE, group
        return STORAGE, "存储层级与数据路径"
    for prefix, series, group in (
        ("DMA/", MICRO, "DMA 与异步数据搬运"),
        ("CIM/", MICRO, "存内计算 CIM"),
        ("HBF/", STORAGE, "HBF 高带宽闪存"),
        ("BUS/", INTERCONNECT, "片上事务与总线（BUS）"),
        ("NOC/", INTERCONNECT, "片上网络（NoC）"),
        ("PCIE/", INTERCONNECT, "系统 I/O 互连（PCIe）"),
        ("SERDES/", INTERCONNECT, "高速电链路（SerDes）"),
        ("CPO/", INTERCONNECT, "共封装光学（CPO）"),
    ):
        if path.startswith(prefix):
            return series, group
    if path.startswith("FAB/"):
        if path in {"FAB/wiki/03-wafer-test-and-cp/yield-and-defect-density.md", "FAB/wiki/06-cross-cutting-engineering/yield-economics-across-stages.md"}:
            return DEVELOPMENT, "可靠性、良率与量产生命周期"
        if path == "FAB/wiki/05-final-test-and-reliability/final-test-methodology.md":
            return DEVELOPMENT, "可测性设计、晶圆筛测与终测"
        if path == "FAB/wiki/06-cross-cutting-engineering/from-architecture-to-process-selection.md" or path.startswith("FAB/wiki/07-industry-map/"):
            return DEVELOPMENT, "产品定义、成本与实现策略"
        for prefix, group in (
            ("FAB/wiki/02-front-end-fabrication/", "流片与晶圆制造"),
            ("FAB/wiki/03-wafer-test-and-cp/", "可测性设计、晶圆筛测与终测"),
            ("FAB/wiki/04-back-end-packaging/", "封装与多芯粒集成"),
            ("FAB/wiki/05-final-test-and-reliability/", "可靠性、良率与量产生命周期"),
            ("FAB/wiki/06-cross-cutting-engineering/", "封装与多芯粒集成"),
        ):
            if path.startswith(prefix):
                return DEVELOPMENT, group
        return DEVELOPMENT, "工程流程与制造导读"
    raise ValueError(f"No primary topic for {path}")


def development_owner(path):
    """Return the primary topic for a path relative to silicon-atlas."""
    path = str(path)
    if path in {"00_overview/03_cost_structure.md", "00_overview/04_startup_vs_bigcompany.md", "03_backend_physical_design/09_backend_outsourcing.md"}:
        return "产品定义、成本与实现策略"
    if path in {"02_frontend_design_and_verification/03_verification_methodology.md", "02_frontend_design_and_verification/08_signoff_criteria.md"}:
        return "功能验证、覆盖与阶段签核"
    if path == "02_frontend_design_and_verification/05_dft_introduction.md":
        return "可测性设计、晶圆筛测与终测"
    if path.startswith("04_tapeout_and_post_silicon/"):
        filename = path.rsplit("/", 1)[-1]
        if filename.startswith(("01_", "02_")):
            return "流片与晶圆制造"
        if filename.startswith("03_"):
            return "封装与多芯粒集成"
        if filename.startswith("07_"):
            return "可靠性、良率与量产生命周期"
        if filename.startswith(("04_", "05_", "06_", "08_")):
            return "硅后启动、测量与修订"
        return "工程流程与制造导读"
    for prefix, group in (
        ("01_product_definition_and_architecture/", "产品定义、成本与实现策略"),
        ("02_frontend_design_and_verification/", "RTL 设计与集成"),
        ("03_backend_physical_design/", "物理设计与签核"),
        ("05_production_and_lifecycle/", "可靠性、良率与量产生命周期"),
        ("06_cross_cutting_topics/", "产品定义、成本与实现策略"),
        ("07_for_software_background_founders/", "软件背景创始人导读"),
    ):
        if path.startswith(prefix):
            return group
    return "工程流程与制造导读"


INFERENCE_GROUPS = ("推理执行阶段与服务指标", "推理算子、内核与量化执行", "KV 缓存管理与前缀复用",
                    "请求调度与动态批处理", "解码策略与输出约束", "分布式并行与分离式推理",
                    "系列案例与估算", "术语与约定")


def inference_owner(path):
    """Assign the numbered inference drafts to their primary topics."""
    path = str(path)
    number = path.split("/", 1)[-1].split("-", 1)[0] if path.startswith("topics/") else ""
    for numbers, group in (
        ({"01", "02", "03", "15"}, "推理执行阶段与服务指标"),
        ({"05", "10"}, "推理算子、内核与量化执行"),
        ({"06", "07"}, "KV 缓存管理与前缀复用"),
        ({"04", "08"}, "请求调度与动态批处理"),
        ({"09", "13"}, "解码策略与输出约束"),
        ({"11", "12"}, "分布式并行与分离式推理"),
        ({"14"}, "系列案例与估算"),
    ):
        if number in numbers:
            return group
    return "术语与约定"


WORKLOAD_GROUPS = ("系列导读与参考", "骨干网络与序列建模", "表示学习与训练目标", "自回归与扩散生成",
                   "视觉感知与三维场景表示", "自动驾驶感知、预测与规划", "机器人策略与视觉语言动作模型",
                   "世界模型与环境预测", "算法工作负载分析")


def workload_owner(path):
    """Return the primary topic for a path relative to the workload root."""
    path = str(path)
    if path in {"00-overview/workload-lens.md", "07-reference/workload-comparison-table.md"} or path.startswith("06-chip-workload-analysis/"):
        return "算法工作负载分析"
    if path in {"01-foundation-model-components/contrastive-learning.md", "01-foundation-model-components/jepa-and-self-supervised.md"}:
        return "表示学习与训练目标"
    if path == "01-foundation-model-components/diffusion-models.md":
        return "自回归与扩散生成"
    for prefix, group in (
        ("01-foundation-model-components/", "骨干网络与序列建模"),
        ("02-vision-and-3d-perception/", "视觉感知与三维场景表示"),
        ("03-autonomous-driving-algorithms/", "自动驾驶感知、预测与规划"),
        ("04-robotics-and-vla/", "机器人策略与视觉语言动作模型"),
        ("05-world-model-and-generative/", "世界模型与环境预测"),
    ):
        if path.startswith(prefix) and path != "01-foundation-model-components/README.md":
            return group
    return "系列导读与参考"
