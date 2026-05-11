# 架构探索方法

上级：[建模与评估](./README.md)

相关：[Topology 与物理布局](../03-topology-routing/topology-layout.md)、[流量模式](../04-ai-dataflow-system/traffic-patterns.md)

## 读这页前先统一几个词

- `parameter sweep`：系统性扫描一组参数，观察趋势而不是只看单点结果
- `baseline`：用来对照的新旧方案中的基准方案
- `sensitivity`：结果对某个参数变化是否敏感
- `root cause`：表面现象背后的真正原因
- `tradeoff`：一个方向变好时，另一个方向通常会付出的代价

## 你现在能开始做什么

基于现有知识，已经可以开始第一阶段探索：

评估 `flat mesh（扁平网格）vs cluster-hierarchical NoC（分簇层次化片上网络）` 在 `GEMM（通用矩阵乘法）/ attention-like traffic（注意力类流量）` 下的：

- link utilization（链路利用率）
- stall breakdown（停顿分类统计）
- average / tail latency（平均/尾部延迟）
- tile utilization（计算单元利用率）

## 推荐的参数扫描顺序

### 第一组：网络结构

- 拓扑
- cluster 大小
- HBM（高带宽内存）/ DMA（直接内存访问）端口位置

### 第二组：router / link

- link width（链路宽度）
- buffer depth（缓冲深度）
- flit size（流控单元大小）
- packet size（数据包大小）
- VC（虚通道）数量

### 第三组：系统交互

- source injection rate（源端注入速率）
- destination FIFO（目的端先入先出队列）深度
- DMA burst size（DMA 突发传输大小）
- tile 消费速率

### 第四组：workload / mapping

- placement（放置策略）
- tensor（张量）切分方式
- 是否 tile-to-tile forwarding
- 是否回写全局存储

## 一个有效的分析套路

1. 先找最先饱和的 link / port
2. 再区分是 credit stall（信用停顿）还是 switch stall（交叉开关停顿）
3. 再判断根因在 NoC、NI（网络接口）、DMA 还是 memory endpoint（存储端点）
4. 最后再改参数，而不是先盲目加宽链路

## 你现在还不该追求什么

- 直接得出“最终芯片最优 NoC”
- 只凭单一 synthetic traffic（合成流量）下结论
- 忽略软件映射和端点行为
- 把第一版 simulator 当成 RTL 替代品

## 一阶洞察与严肃结论的边界

第一版模型可以支持：

- 相对比较
- 热点定位
- 参数敏感性分析
- 明显错误架构的快速排除

但还不够支持：

- 精确 tape-out（流片）级时序结论
- 极细粒度 QoS（服务质量）保证
- 复杂协议 correctness 证明

## 本页结论

对你当前阶段最重要的，不是把所有 NoC 细节一次做完，而是先建立一套能把 workload（工作负载）、mapping（映射）和 NoC 性能连起来的探索框架。
