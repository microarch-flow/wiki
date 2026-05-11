# NI / DMA / 存储接口

上级：[AI Dataflow 系统视角](./README.md)

相关：[Credit / Backpressure](../02-router-microarchitecture/credit-backpressure.md)

## 读这页前先统一几个词

- `NI`：Network Interface，端点和 NoC 之间的协议转换层
- `injection`：把 packet 从端点送进 NoC
- `ejection`：把 packet 从 NoC 弹出到目的端点
- `reassembly`：把收到的一串 flit 重组成完整 packet 或完整数据块
- `outstanding request`：已经发出但还没收到响应的请求；数量过大时会放大 response 回流压力

## 为什么这一层必须单独拿出来

很多人把 NoC 建成“router + link”就停了，但真正决定系统堵不堵的，常常是端点。

尤其在 AI accelerator 里，下面这些对象都不是被动终点：

- Network Interface（网络接口）
- DMA engine（直接内存访问引擎）
- tile（计算单元）local SRAM（片上静态存储）interface
- HBM（高带宽存储器）/ memory controller port
- destination stream FIFO

## NI 的职责

Network Interface 是 tile 世界（语义层）和 NoC 世界（传输层）之间的翻译层：

```
tile 侧（语义层）            NI                     NoC 侧（传输层）

"读地址 0x1000"  ───────→  打包成 read request     ──→ header + body flit
                           packet：填入源地址、          注入到 router
                           目的地址、消息类型、
                           长度等字段

                           ←── 收到 response             ←── flit 到达
"收到 64B 数据"  ←───────  packet，解包还原为            header + body + tail
                           tile 可消费的数据块            flit 重组为完整 packet
```

具体职责：

- **发送侧打包**：将 tile 的读写请求 / DMA 事务打包成 packet（添加 header、切分为 flit），注入 NoC
- **接收侧解包**：将到达的 flit 重组为完整 packet，还原为 tile 可消费的数据
- **协议转换**：tile 侧可能是 AXI / TileLink 等总线协议，NI 转换为 NoC 的 flit 格式
- **缓冲**：injection FIFO 和 ejection FIFO，吸收 tile 和 NoC 之间的速率差异
- 本地流量分类
- 与 tile FIFO / SRAM / DMA descriptor（描述符）接口对接

### Packet 间的依赖关系不由 NoC 管

NoC 只负责把每个 packet 从源送到目的地，不理解 packet 之间的语义依赖。依赖和顺序由上层保证：

| 层 | 职责 |
|---|---|
| 编译器 / runtime | 规划发送顺序和时序，确保依赖正确 |
| NI / DMA 控制器 | 按编译器指定的顺序发起传输，用 barrier / descriptor 做同步 |
| NoC | 只管转发，不重排、不理解依赖 |
| 目的端 NI | 按到达顺序交付，或结合 tag / sequence id 做重组与重排 |

很多常见 wormhole（虫孔转发）+ per-VC FIFO（每 VC 先进先出）实现里，**同一源、同一目的、同一路径、同一 VC 上的 packet 通常可维持发送顺序**。  
但这不是无条件保证：如果存在多路径、自适应路由、多队列注入，或端点侧显式重排，就不应默认全局 FIFO，而应依赖 tag / sequence id / scoreboard 做重组。

### 片上 NoC 不丢数据

这是和片外网络（以太网、互联网）最本质的区别。以太网交换机 buffer 满了会主动丢包（drop），所以需要 TCP 做重传。片上 NoC 不存在这种场景：

- **credit 机制**保证发送方不会发超过下游 buffer 容量的 flit → 不会因溢出丢包
- 信号在芯片内部走短距离金属线，物理上极可靠
- wormhole 下 flit 一旦进入 router buffer 就被安全存储

所以 NI 的协议层主要处理的是**打包 / 解包 / 重组 / 顺序**，不需要像 TCP 那样做丢失检测和重传。数据完整性在 NoC 层面通过 credit 就已经保证了。

高可靠性场景（如车规级芯片）可能在 link 上加 ECC（纠错码）或 parity（奇偶校验）来应对极罕见的软错误（如宇宙射线位翻转），但消费电子级设计通常不加。

## DMA 的职责

DMA 一般负责：

- 把大块数据在 HBM、SRAM、tile 之间搬运
- 生成 read request / write packet
- 接收 response 并组织回写
- 与编译器或 runtime 计划配合

架构探索里，DMA 的 burst（突发传输）行为经常决定：

- packet 粒度
- memory traffic 峰值
- 是否压住 control 小消息

## 存储接口为什么会反向决定 NoC 行为

NoC 看上去在“搬数据”，但最终数据必须被端点消费。

所以必须显式考虑：

- tile local SRAM bank 冲突
- HBM controller port 带宽
- response reordering 能力
- destination ejection FIFO 深度

只要目的端消费速度下降，NoC backpressure（反压）就会被拉起来。

## 第一版模型里最低限度需要的端点建模

- source injection FIFO
- destination ejection FIFO
- DMA request / response 队列
- tile 消费速率
- memory port 带宽限制

## 一个很实用的工程判断

NoC 的瓶颈不一定在 NoC 内部。  
很多“link 利用率不高但系统还是慢”的情况，本质是：

- destination 消费不动
- response 回不来
- SRAM/HBM 接口节奏不匹配

## 本页结论

如果不把 NI、DMA 和存储接口纳入模型，你得到的 NoC 结论往往只是“网络空转视角”的结论，而不是系统视角的结论。
