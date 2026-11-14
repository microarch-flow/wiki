# LPDDR：低功耗机制与系统集成

上级：<span id="lpddr为了功耗放弃了什么"></span>[DRAM 命令与接口](./README.md)

相关：[接口家族比较](./ddr-lpddr-gddr-hbm-tradeoff-map.md) · [移动封装](../../06-system-integration/packaging/pop-mcp-mobile-integration.md)

## 这页在回答什么问题

LPDDR 为了功耗采用哪些机制？哪些收益与代价取决于具体工作负载，而不能由名字直接断定？

## 移动系统的功耗与集成目标

LPDDR 面向低功耗系统，具体代际可提供不同的数据率、接口组织、低功耗状态和刷新控制。评估应分开活动传输、空闲和状态切换：降低待机能耗可能需要进入与退出时间，频繁唤醒会改变平均能耗与延迟。总功耗还包括 PHY、控制器及板级系统。

[Micron 低功耗内存资料](https://www.micron.com/content/dam/micron/global/public/products/product-flyer/flyer-lpdram-mobile-embedded.pdf)列出了部分产品的 partial-array self-refresh（PASR）与 deep power-down（DPD）等功能；但是否支持、配置方式和数据保留范围依具体器件和模式。进入会丢失内容的状态后，需要按器件与系统流程重新初始化或装载；不能把一种模式的保持行为泛化到所有 LPDDR。

LPDDR 常见于紧凑的板载或封装集成，也有可拆卸模块。例如 [Samsung LPCAMM2](https://semiconductor.samsung.com/dram/module/lpcamm2/) 使用 LPDDR5X 并采用可拆卸模块形式。因此不能把“LPDDR 一定焊死、无法升级”作为家族规则。

## 一句话理解

LPDDR 的低功耗目标通过器件、PHY 和系统状态共同实现，收益取决于实际运行与集成方式。

## 建模启示

记录各状态功率、进入退出时间、数据保持与请求比例；比较容量、有效带宽和总系统能耗时，使用同一负载与温度条件。
