# 架构探索方法

上级：[建模与评估](./README.md)

相关：[Topology 与物理布局](../03-topology-routing/topology-layout.md)、[流量模式](../04-ai-dataflow-system/traffic-patterns.md)

## 你现在能开始做什么

基于现有知识，已经可以开始第一阶段探索：

评估 `flat mesh vs cluster-hierarchical NoC` 在 `GEMM / attention-like traffic` 下的：

- link utilization
- stall breakdown
- average / tail latency
- tile utilization

## 推荐的参数扫描顺序

### 第一组：网络结构

- 拓扑
- cluster 大小
- HBM / DMA 端口位置

### 第二组：router / link

- link width
- buffer depth
- flit size
- packet size
- VC 数量

### 第三组：系统交互

- source injection rate
- destination FIFO 深度
- DMA burst size
- tile 消费速率

### 第四组：workload / mapping

- placement
- tensor 切分方式
- 是否 tile-to-tile forwarding
- 是否回写全局存储

## 一个有效的分析套路

1. 先找最先饱和的 link / port
2. 再区分是 credit stall 还是 switch stall
3. 再判断根因在 NoC、NI、DMA 还是 memory endpoint
4. 最后再改参数，而不是先盲目加宽链路

## 你现在还不该追求什么

- 直接得出“最终芯片最优 NoC”
- 只凭单一 synthetic traffic 下结论
- 忽略软件映射和端点行为
- 把第一版 simulator 当成 RTL 替代品

## 一阶洞察与严肃结论的边界

第一版模型可以支持：

- 相对比较
- 热点定位
- 参数敏感性分析
- 明显错误架构的快速排除

但还不够支持：

- 精确 tape-out 级时序结论
- 极细粒度 QoS 保证
- 复杂协议 correctness 证明

## 本页结论

对你当前阶段最重要的，不是把所有 NoC 细节一次做完，而是先建立一套能把 workload、mapping 和 NoC 性能连起来的探索框架。
