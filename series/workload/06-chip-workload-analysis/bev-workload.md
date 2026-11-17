# BEV 工作负载：视角变换、采样与历史特征

上级：[专题导读](README.md)

<span id="bev-workload" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="view-transform-为什么是-bev-的真正瓶颈" class="workload-legacy-anchor"></span>
<span id="共享-bev-特征收益与陷阱并存" class="workload-legacy-anchor"></span>
<span id="可建模参数" class="workload-legacy-anchor"></span>
<span id="硬件连接" class="workload-legacy-anchor"></span>
<span id="archax-建模" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


BEV 输出尺寸相同的两个系统，可能有完全不同的中间执行图。先分相机编码、视角变换、历史融合和任务头，再分析每一段的形状与流量。

## LSS 的逻辑中间量

设相机数为 $N_c$，图像特征为 $H_f\times W_f\times C$，深度分箱数为 $D$。朴素提升会构造约 $N_cH_fW_fDC$ 个特征元素，再按几何索引汇聚到 BEV。

构造 $N_c=6,H_f=32,W_f=64,D=80,C=64$，FP16 视锥特征约 120 MiB。这是物化完整中间张量时的容量，不是所有 LSS 实现不可避免的下界。

BEVPoolv2 重组乘积与归约，避免显式构造大型视锥特征。比较时应注明使用的是朴素路径还是优化实现，不能沿用旧中间量预测新内核。

## 查询式路径的另一组变量

BEVFormer 的空间采样取决于 BEV query 数、参考高度、可见相机、特征层和采样点。其成本不是完整图像 token 与所有 BEV query 的稠密两两 attention。

几何索引可能预计算，也可能因标定、增强或动态输入而更新。gather/scatter 的逻辑不规则性需要结合布局和合并访问观察，不能直接断言每次都造成 DRAM 行失配。

## 输出与历史状态

$200\times200$ 网格是 40,000 个单元。每格 128 通道、FP16 为 9.77 MiB。若保留 4 份同形历史特征，仅历史为 39.06 MiB；当前特征、对齐工作区和其他状态另计。

按自车运动重采样历史会引入读写和插值。历史越长，信息与资源成本都可能增加，但时序误差和动态目标失配也可能增加。

## 适合验证的假设

分别改变相机数、输入分辨率、深度分箱、BEV 分辨率和历史长度。若仅改变 BEV 分辨率，不能假定所有相机骨干成本也同比变化。

记录索引生成、采样、归约和任务头的时延；检查是否出现主机与加速器往返。机制与坐标条件见 [BEV 感知](../02-vision-and-3d-perception/bev-perception.md)，传输路径背景见[互连系列](../../interconnect/README.md)。

<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [LSS](https://arxiv.org/abs/2008.05711)
- [BEVFormer](https://arxiv.org/abs/2203.17270)
- [BEVPoolv2](https://arxiv.org/abs/2211.17111)
