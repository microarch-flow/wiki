# 从 SRAM 到 HBM 的系统分层

上级：[04 系统架构视角](./README.md)

相关：[SRAM vs DRAM 对照](../02-memory-cells-arrays/sram-vs-dram.md)、[DRAM 家族对照：DDR / LPDDR / GDDR / HBM](../03-ddr-protocol-families/ddr-lpddr-gddr-hbm-comparison.md)

## 为什么系统一定是分层的

没有任何一种内存能同时做到：

- 像 SRAM 那样低延迟
- 像 DRAM 那样大容量
- 像 HBM 那样高带宽
- 还像通用 DDR 那样低成本

所以现代系统几乎都采用分层：

- 用少量快速存储服务热点数据
- 用大量便宜存储承载大数据集

## 一个典型层级

### 片上最近处

- register file
- L1 / L2 cache
- on-chip SRAM scratchpad

这里更看重：

- 单次访问延迟
- 带宽确定性
- 与计算阵列的距离

### 片外主存层

- DDR / LPDDR

这里更看重：

- 容量
- 成本
- 标准化部署

### 高端加速器带宽层

- GDDR
- HBM

这里更看重：

- 总带宽
- 每比特能耗
- 与计算 die 的集成密度

## CPU、手机、GPU、AI 芯片为什么选型不同

### CPU 服务器

通常更重视：

- 大容量
- 容量成本
- 多路扩展

所以 DDR 是主线。

### 手机和移动设备

更重视：

- 续航
- 封装尺寸
- 功耗

所以更偏 LPDDR。

### 独立 GPU

更重视：

- 板级高带宽
- 图形和并行吞吐

所以长期偏 GDDR，高端再走 HBM。

### AI / HPC 加速器

更重视：

- 带宽密度
- 每比特能耗
- 封装级就近供数

所以 HBM 越来越成为主线。

## 一句话理解

系统里的 RAM 不是单选题，而是 `SRAM 负责近和快，DDR 负责大和通用，GDDR/HBM 负责高带宽` 的分层协作。
