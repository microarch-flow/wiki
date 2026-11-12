"""Assign each existing article to one main series and topic."""

MICRO = "微架构"
STORAGE = "存储系统"
INTERCONNECT = "芯片与系统互连"

GROUPS = {
    MICRO: ("系列导读", "数值格式与算术数据通路", "时钟、流水线与吞吐", "计算阵列与数据流",
            "DMA 与异步数据搬运", "处理单元与芯片顶层组织", "存内计算 CIM", "制造与封测导读"),
    STORAGE: ("RAM 基础导读与自测", "SRAM 阵列、端口与宏接口", "DRAM 阵列、命令与接口族",
              "HBM 堆叠 DRAM 与宽接口", "HBF 高带宽闪存", "DRAM 控制器与请求调度", "存储层级、缓存与数据放置"),
    INTERCONNECT: ("片上事务与总线（BUS）", "片上网络（NoC）", "系统 I/O 互连（PCIe）",
                   "高速电链路（SerDes）", "共封装光学（CPO）"),
}

HBM = {
    "RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md",
    "RAM/wiki/08-packaging-integration/hbm-2.5d-3d-tsv.md",
    "RAM/wiki/08-packaging-integration/why-hbm-is-expensive.md",
    "RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu.md",
}


def owner(path):
    """Return the primary series and topic for a staged original-wiki path."""
    path = str(path)
    if path == "electrical-timing-foundations.md":
        return MICRO, "时钟、流水线与吞吐"
    if path in HBM:
        return STORAGE, "HBM 堆叠 DRAM 与宽接口"
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
            return STORAGE, "存储层级、缓存与数据放置"
        return MICRO, "系列导读"
    if path.startswith("RAM/"):
        for prefixes, group in (
            (("02-sram-foundations",), "SRAM 阵列、端口与宏接口"),
            (("04-dram-foundations", "05-dram-protocol-families"), "DRAM 阵列、命令与接口族"),
            (("06-memory-controller",), "DRAM 控制器与请求调度"),
            (("03-sram-applications", "07-system-architecture", "08-packaging-integration", "09-ai-chip-memory-architecture"), "存储层级、缓存与数据放置"),
        ):
            if any(path.startswith(f"RAM/wiki/{prefix}/") for prefix in prefixes):
                return STORAGE, group
        return STORAGE, "RAM 基础导读与自测"
    for prefix, series, group in (
        ("DMA/", MICRO, "DMA 与异步数据搬运"),
        ("CIM/", MICRO, "存内计算 CIM"),
        ("FAB/", MICRO, "制造与封测导读"),
        ("HBF/", STORAGE, "HBF 高带宽闪存"),
        ("BUS/", INTERCONNECT, "片上事务与总线（BUS）"),
        ("NOC/", INTERCONNECT, "片上网络（NoC）"),
        ("PCIE/", INTERCONNECT, "系统 I/O 互连（PCIe）"),
        ("SERDES/", INTERCONNECT, "高速电链路（SerDes）"),
        ("CPO/", INTERCONNECT, "共封装光学（CPO）"),
    ):
        if path.startswith(prefix):
            return series, group
    raise ValueError(f"No primary topic for {path}")


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
