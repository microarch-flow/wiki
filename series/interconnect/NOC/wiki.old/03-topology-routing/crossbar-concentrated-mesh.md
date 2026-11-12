# Crossbar 与 Concentrated Mesh

上级：[Topology 与 Routing](./README.md)

相关：[Hierarchical NoC 深化](./hierarchical-noc-deep-dive.md)、[Topology Family 深化](./topology-family-deep-dive.md)、[NoC 分类框架](../01-overview/taxonomy.md)

## 为什么要单独讨论 crossbar 和 concentrated mesh

几乎所有 AI 加速器都不是把每个 tile 直接接到一张大 mesh 上，而是把若干 tile 编成 cluster，cluster 内用 crossbar 或 local fabric，cluster 间再用 mesh / tree / ring 等全局 NoC 连通。

理解 crossbar 和 concentrated mesh，就是理解"cluster 内怎么连"和"全局 router 数量怎么减"这两个 AI 芯片互连设计的核心问题。

## Crossbar（交叉开关）

### 是什么

Crossbar 是一种全连接互连结构：任意一个输入端口都可以同时与任意一个输出端口通信（只要目标端口没被占用）。

```text
      Out0  Out1  Out2  Out3
       |     |     |     |
In0 --[x]---[x]---[x]---[x]--
In1 --[x]---[x]---[x]---[x]--
In2 --[x]---[x]---[x]---[x]--
In3 --[x]---[x]---[x]---[x]--
```

### 核心特点

- 单跳延迟：任意两个端口之间不需要中间转发
- 面积 O(N²)：crosspoint 数量随端口数平方增长
- 仲裁集中：需要一个中央 arbiter 决定每周期哪些输入-输出配对

### 适用规模

| 端口数 | 面积压力 | 典型用途 |
|---|---|---|
| 2-4 | 很小 | tile 内 PE 互连 |
| 4-8 | 可接受 | cluster 内 tile 互连 |
| 8-16 | 较大 | 小型 cluster 或 shared SRAM 互连 |
| >16 | 通常不可接受 | 需要切换到 NoC 或多级互连 |

### 仲裁策略

crossbar 的性能很大程度取决于仲裁策略：

- **round-robin**：公平但可能牺牲吞吐
- **priority-based**：可以给关键流量（如 control）更高优先级
- **age-based**：防止饥饿，按等待时间排序
- **iSLIP / wavefront**：更高效的迭代匹配算法，适合端口数较多的场景

### 为什么 AI 芯片 cluster 内几乎都用 crossbar

- cluster 内 tile 数量通常 2-8 个，crossbar 面积可控
- cluster 内通信频率高、延迟敏感（共享 SRAM、partial sum 交换）
- 单跳延迟对 pipeline 友好，编译器更容易调度
- 不需要 routing 算法，没有死锁问题

## Concentrated Mesh

### 是什么

普通 mesh 是每个 router 接一个 tile / endpoint。Concentrated mesh 是每个 router 接多个 tile / endpoint，也就是把多个 endpoint "集中"到一个 router 上。

普通 mesh：

```text
T---R---R---R---T
    |   |   |
T---R---R---R---T
    |   |   |
T---R---R---R---T
```

每个 R 接 1 个 T，9 个 tile 需要 9 个 router。

Concentrated mesh（concentration factor k=4）：

```text
T T       T T
 \|       |/
  R-------R
  |       |
  R-------R
 /|       |\
T T       T T
```

每个 R 接 4 个 T，16 个 tile 只需要 4 个 router。

### 核心参数：Concentration Factor (k)

k 是每个 router 服务的 endpoint 数量。

| k | router 数量（相对普通 mesh） | router radix | 效果 |
|---|---|---|---|
| 1 | 100% | 4+1=5（2D mesh） | 普通 mesh |
| 2 | 50% | 4+2=6 | router 减半 |
| 4 | 25% | 4+4=8 | router 降到 1/4 |
| 8 | 12.5% | 4+8=12 | router radix 开始很高 |

k 增大的好处：

- 全局 router 数量减少
- 全局 hop 数减少（网络直径更小）
- 全局布线复杂度降低

k 增大的代价：

- router radix 增高 → 仲裁更复杂、面积更大
- cluster 内 endpoint 到 router 需要局部互连（通常是 crossbar）
- 同一 router 下的 endpoint 共享出口带宽 → 可能成为瓶颈

### 与 crossbar 的关系

concentrated mesh 的每个 router 下面，endpoint 到 router 的局部互连通常就是一个 crossbar 或 mux。所以：

> **concentrated mesh ≈ cluster-local crossbar + global mesh 的形式化表达**

两者描述的是同一种设计模式，只是视角不同：

- concentrated mesh 从网络拓扑的角度看：router 的 concentration factor
- cluster-local crossbar + global mesh 从系统组织的角度看：两级互连

## 三者关系梳理

```text
                    全局视角
                   ┌─────────────────────────────────┐
                   │                                 │
                   │  hierarchical mesh               │
                   │  = 两级 mesh                     │
                   │  cluster 内是小 mesh              │
                   │  cluster 间是大 mesh              │
                   │                                 │
                   ├─────────────────────────────────┤
                   │                                 │
                   │  concentrated mesh               │
                   │  = mesh + 每个 router 接多个 tile │
                   │  cluster 内共享 router            │
                   │  cluster 间走 mesh               │
                   │                                 │
                   ├─────────────────────────────────┤
                   │                                 │
                   │  cluster-local crossbar          │
                   │    + global mesh                 │
                   │  = concentrated mesh 的常见实现   │
                   │  cluster 内 crossbar             │
                   │  cluster 间 mesh                 │
                   │                                 │
                   └─────────────────────────────────┘
```

关键区别：

- **hierarchical mesh**：cluster 内部仍然是 mesh（有多个 router），cluster 间也是 mesh
- **concentrated mesh**：cluster 内部共享一个 router（router radix 更高），cluster 间是 mesh
- **cluster-local crossbar + global mesh**：cluster 内部用 crossbar 连到一个 gateway router，gateway router 之间走 mesh

在实践中，concentrated mesh 和 cluster-local crossbar + global mesh 几乎等价。hierarchical mesh 则更适合 cluster 内 tile 数量较多（>8）、需要内部路由的场景。

## 对建模的影响

### 普通 mesh 建模

```text
tile -> router -> router -> ... -> router -> tile
```

每一跳都是 router-to-router，模型相对简单。

### Concentrated mesh / cluster-local crossbar 建模

```text
tile -> local crossbar -> gateway router -> mesh router -> ... -> gateway router -> local crossbar -> tile
```

需要额外建模：

- **local crossbar 延迟和仲裁**：cluster 内多个 tile 竞争出口
- **gateway router 注入/弹出带宽**：k 个 tile 共享 gateway 的 local port 带宽
- **cluster 内 vs cluster 间流量比**：locality 越好，全局网络压力越小

### 架构探索时的关键问题

- cluster 多大合适？（k 取多少？）
- cluster 内流量占比多少？（locality 好不好？）
- cluster 内 crossbar 仲裁是否会成为瓶颈？
- gateway router 的注入带宽是否够用？

## AI 芯片中的典型应用

| 设计选择 | 适用场景 |
|---|---|
| 4 tile + crossbar → 1 gateway router | 中等规模 NPU，cluster 内共享 SRAM |
| 8 tile + crossbar → 1 gateway router | 大规模 tile array，强调局部数据复用 |
| 2×2 mesh cluster → hierarchical mesh | cluster 内 tile 数多，需要内部路由 |
| 单级 flat mesh | 小规模原型、tile 数 <16 |

## 本页结论

crossbar 和 concentrated mesh 不是"高级拓扑"，而是 AI 加速器 NoC 设计中最基础的构建模块。理解它们，就是理解从 flat mesh 到 cluster 化设计的关键一步。建模时不要跳过 cluster 内互连的开销——它看起来是"局部小事"，但当 cluster 内流量占比很高时，它直接决定系统吞吐。
