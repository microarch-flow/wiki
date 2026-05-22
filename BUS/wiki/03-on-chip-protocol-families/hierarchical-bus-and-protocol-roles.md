# 分层总线与协议分工

上级：[03 片上总线协议族](./README.md)

相关：[AXI / AHB / APB 对照](./axi-ahb-apb-comparison.md)、[AHB-Lite 与 APB 深化](./ahb-lite-and-apb-deep-dive.md)、[互连组件与数据路径分解](../04-microarchitecture-integration/interconnect-components.md)、[Bridge、CDC 与 Width Adapter](../04-microarchitecture-integration/bridge-cdc-width-adaptation.md)

## 这页在回答什么问题

为什么 SoC 里的片上互连更像多层 bus fabric 加若干 bridge，而不是一条协议覆盖所有 master、slave 和访问类型。

## 分层是在隔离不同访问压力

单层互连的直觉很简单：所有 master 接到同一个 fabric，所有 slave 都挂在同一个地址空间里。但系统规模上来后，单层结构会把不同压力绑在一起：CPU/DMA 到 DDR 需要高吞吐和 outstanding，外设寄存器只需要清楚的 MMIO completion，boot/debug 需要早期可达，低速 peripheral 不能拖慢主干时序。

分层总线的目的不是让框图更整齐，而是把不同访问压力放在不同复杂度边界里。高性能主干承担 burst、outstanding、宽数据和多 master 争用；外设子树承担低速寄存器访问；bridge 在中间负责协议、时钟、位宽、错误和回压转换。

如果不分层，系统会在两个方向上浪费：让所有外设都直接接高性能 AXI，会把复杂握手和验证成本推到低速控制面；让主数据路径穿过低复杂度外设总线，会把吞吐和尾延迟问题推给软件和上游 master。

容易误解：分层只是物理连线优化。实际上，分层是在给不同路径分配不同事务能力和错误/回压边界。

## 高性能主干承担并发和长延迟

高性能主干连接 CPU cluster、DMA、accelerator、memory controller、high-performance SRAM 或 coherent/non-coherent fabric 边界。这里的主约束是吞吐、latency hiding、burst、outstanding、QoS 和返回路径能力。

AXI 或类似高并发协议适合放在这一层，是因为它能把读写、地址、数据和 response 分开推进。DDR 访问、DMA 数据搬运和 accelerator data mover 都可能有长服务时间；如果主干不能容纳多个 outstanding，请求会在长延迟中空等。

但高性能主干不该直接承担所有低速细节。把 UART、GPIO、timer 等外设直接挂在主干上，会增加 decode fanout、时序压力、低速 wait state 对主干的影响，以及外设端必须处理的协议状态。主干需要的是高吞吐路径的可组合性，不是把每个 control register 都暴露成高复杂度 endpoint。

## 外设层承担软件可见控制面

外设层连接 UART、SPI、I2C、GPIO、timer、watchdog、clock/reset controller、interrupt controller 配置寄存器等。这里的主约束是地址语义清楚、寄存器副作用可控、低功耗、低面积和容易验证。

APB 或类似低复杂度协议适合这一层，因为外设访问以单 beat control/status register 为主。软件关心的是写是否触发、读是否返回状态、错误是否可见、访问是否会卡住；它不需要每个外设都支持 burst、ID、多 outstanding 和独立返回路径。

外设层的低复杂度也保护了 bring-up。上电早期，clock、reset、strap、fuse、boot ROM、debug 和少量外设控制寄存器必须先可达；让这些路径依赖完整高性能 fabric 全部初始化，会增加 boot 风险。

## Bridge 是分层的语义转换点

Bridge 不只是 glue logic。它把上游协议的一笔 transaction 转换成下游协议的一笔或多笔 transaction，并决定 latency、ordering、error 和 backpressure 如何跨层传播。

一个 AXI-to-APB bridge 可能需要做这些事：

- 接收 AXI `AW/W/B` 或 `AR/R` 语义，并转成 APB setup/access。
- 把 AXI burst 拆成多个 APB 单次访问，或拒绝不支持的访问形态。
- 把 `PREADY` wait state 转成上游 backpressure 或 response 延迟。
- 把 `PSLVERR`、decode miss、timeout 映射成上游 response。
- 在 clock 或 width 不一致时加入 FIFO、CDC 和 adapter 状态。

这些转换让分层可行，也带来风险。bridge 太浅，可能吸收不了 burst 和频率差；bridge 太深，会增加固定延迟和调试不可见性；错误映射不清楚，会让 master 看到一个 response，却不知道根因来自 decode、APB slave 还是 timeout wrapper。

容易误解：协议能转换就说明系统行为等价。实际上，bridge 会改变访问粒度、完成时机、错误类别、回压传播和可观测性。

## 分层会改变 ordering 和 completion

跨层访问的 completion 不等于下游单拍完成。上游 master 看到的是自己协议里的 response；下游 slave 看到的是 bridge 发出的访问。bridge 中间可能排队、拆分、合并、重试或合成错误。

例如，一个 AXI master 对 APB 外设发起写访问。上游可能先完成 AXI `AW` 和 `W` handshake，bridge 随后发起 APB setup/access，等 `PREADY` 后才生成 AXI `B` response。对 master 来说，真正释放 outstanding 的是 `B`；对 APB slave 来说，真正写入发生在 APB access phase。中间这段时间就是分层带来的 completion gap。

若 bridge 拆分 burst，这个 gap 会更明显。一笔上游 burst 可能对应多个下游寄存器访问；任何一个下游访问报错、timeout 或被 `PREADY=0` 拉住，都会影响上游 response 组织。模型如果只画一条“AXI 到 APB”的线，会看不到这些状态。

## 一个构造分层示例

| 层级 | 连接对象 | 协议倾向 | 主要状态 |
|---|---|---|---|
| 高性能主干 | CPU、DMA、accelerator、DDR controller | AXI / 高并发 fabric | outstanding、burst、QoS、return path |
| 局部子系统 | SRAM、ROM、简单 DMA、MCU peripheral cluster | AHB-Lite / 简化主干 | address/data phase、HREADY、HRESP |
| 外设寄存器层 | UART、GPIO、timer、watchdog | APB / register bus | setup/access、PREADY、PSLVERR |
| 桥接层 | AXI-to-APB、AHB-to-APB、CDC、width adapter | bridge logic | buffer、映射、拆分、错误转换 |

这张表不是固定模板。关键是每层只承担自己需要的事务能力：高性能层保留并发，外设层保留简单，bridge 明确转换边界。系统也可以有多个外设子树、多个 memory 子系统或 debug-only 低速路径。

## 一句话理解

分层总线的本质是把高吞吐数据路径、低复杂度控制路径和协议/时钟/位宽转换点分开管理，让每段路径只承担匹配自身压力的事务能力。

## 建模启示

建模分层 BUS 时，不要把整条 SoC 互连建成一个统一延迟。模型要按层记录入口、出口、协议、bridge、队列和 completion 边界。高性能主干要保留 outstanding、burst、返回路径和仲裁；外设层要保留寄存器访问、PREADY/PSLVERR 和副作用；bridge 要保留拆分、合并、CDC、width adaptation 和错误映射。

性能模型要特别关注跨层 backpressure。APB slave 的 `PREADY=0` 可以通过 bridge 变成 AHB `HREADY=0` 或 AXI response 延迟；返回路径堵塞也可能反压新的 request。只建上游主干吞吐，不建下游子树服务时间，会低估低速外设对 boot/debug/MMIO 路径的影响。

功能模型要检查跨层语义是否守恒：地址 decode 是否一致，非法访问如何返回，burst 拆分后的 response 如何合成，ordering 是否被 bridge 改变，width/narrow/WSTRB 语义是否被正确映射，timeout wrapper 是否释放上游 outstanding。

分层设计的建模问题可以写成一句话：这笔 transaction 穿过了哪些复杂度边界，每个边界改变了什么。只有把这些边界建出来，才能解释为什么同一个 master 访问 DDR、SRAM 和 UART 寄存器时，latency、error 和 backpressure 行为完全不同。
