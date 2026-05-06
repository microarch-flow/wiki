# NI / DMA / 存储接口

上级：[AI Dataflow 系统视角](./README.md)

相关：[Credit / Backpressure](../02-router-microarchitecture/credit-backpressure.md)

## 为什么这一层必须单独拿出来

很多人把 NoC 建成“router + link”就停了，但真正决定系统堵不堵的，常常是端点。

尤其在 AI accelerator 里，下面这些对象都不是被动终点：

- Network Interface
- DMA engine
- tile local SRAM interface
- HBM / memory controller port
- destination stream FIFO

## NI 的职责

Network Interface 通常负责：

- tile / DMA 事务与 packet 格式之间的转换
- source injection
- destination ejection
- 本地流量分类
- 与 tile FIFO / SRAM / DMA 描述符接口对接

所以 NI 不是薄壳，而是 NoC 与系统语义的翻译层。

## DMA 的职责

DMA 一般负责：

- 把大块数据在 HBM、SRAM、tile 之间搬运
- 生成 read request / write packet
- 接收 response 并组织回写
- 与编译器或 runtime 计划配合

架构探索里，DMA 的 burst 行为经常决定：

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

只要目的端消费速度下降，NoC backpressure 就会被拉起来。

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
