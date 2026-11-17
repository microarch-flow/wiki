# 流水线的停顿与反压

上级：[流水线、时序与时钟域](./README.md)

流水线插入寄存器后，仍需要回答：下一段暂时不能接收结果时，当前数据放在哪里。**停顿期间必须保住有效数据和对应控制信息，恢复后每项工作只传递一次。**

## 先约定接口

本文使用同一时钟域中的 ready/valid 教学接口。发送端提供 data 和 valid；接收端提供 ready。上升沿同时看到 valid = 1、ready = 1 时，发生一次传递，记为 fire。

在这一接口约定下，发送端一旦置 valid，就保持 valid 及数据，直到传递发生。发送端不能仅因 ready 为低就丢弃当前项，也不能等 ready 为高才首次声明已有数据。这与 [Arm AXI 的 VALID/READY 规则](https://documentation-service.arm.com/static/68b03beb01ae952d9559f9eb)一致；本文只抽取单通道握手机制，不实现完整 AXI。

## 一个可停顿的单项寄存器

寄存器保存 payload 和 occupied。输出 valid 等于 occupied；若当前为空，或者当前项能在本拍被接收，就可接纳新项：

<div class="ram-calculation">
<p><strong>输入可接纳：</strong>in_ready = ¬occupied ∨ out_ready</p>
<p><strong>输入传递：</strong>in_fire = in_valid ∧ in_ready</p>
<p><strong>输出传递：</strong>out_fire = occupied ∧ out_ready</p>
</div>

在采样沿按以下顺序更新状态：

1. 若 in_fire 成立，存入新 payload，并令 occupied = 1。旧项若存在，必须同时 out_fire，才能安全替换。
2. 否则，若 out_fire 成立，令 occupied = 0。
3. 否则保持 payload 和 occupied。

因此寄存器可以同拍送走旧项、接收新项。若只在“寄存器为空”时接收，虽然也能保证正确，却可能每隔一拍才推进一项。

## 下游停两拍的轨迹

初始寄存器为空。表中状态是采样沿之前的状态，沿后动作发生于该沿。发送端持续提供 A、B、C，并在被接收后才换下一项。

| 边沿 | 沿前寄存器 | 输入 | out_ready | 输入传递 | 输出传递 | 沿后寄存器 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 空 | A | 1 | A | 无 | A |
| 1 | A | B | 0 | 无 | 无 | A |
| 2 | A | B | 0 | 无 | 无 | A |
| 3 | A | B | 1 | B | A | B |
| 4 | B | C | 1 | C | B | C |
| 5 | C | 无 | 1 | 无 | C | 空 |

边沿 1、2 不能把 B 覆盖到 A 上，也不能把 A 重复计为已输出。输出序列必须恰好是 A、B、C。指令流水线还要同时保存目标寄存器、异常、标签等 sideband；只保持数据、不保持标签，同样会写错对象。

## Bubble、stall 和 flush

**Bubble** 是没有有效工作的空槽。**Stall** 是当前工作不能推进，通常必须保持。**Flush** 是因分支恢复、取消等原因作废工作。三者对 valid 和资源释放的处理不同。

例如停顿时清零 valid 会丢数据；恢复分支时仅冻结错误路径而不清除，会让错误操作以后继续执行。取消还必须处理已发出的请求和迟到响应，不能只改本地有效位。

## 反压本身也有时序和容量成本

上述组合 in_ready 可以沿多级向上游传播。链太长会形成时序路径。若把反压寄存一拍，上游可能多发送一项；必须用额外缓冲容量或等价的信用机制接住这项数据。仅给 ready 加寄存器而不补容量，会在满载停止时溢出。

系统中还要避免组合环和协议等待环。跨时钟域不能直接使用这里的单沿推导，应采用经验证的 CDC 结构。更长距离的容量反馈见[NoC credit 流控](../../interconnect/NOC/02-router-microarchitecture/credit-based-flow-control.md)。

检查时可以保持三个不变量：已接收数 − 已发送数 = 当前占用数；占用不超过容量；无取消时输出顺序与输入顺序一致。只有满足正确性，才继续比较吞吐、时钟和缓冲面积。
