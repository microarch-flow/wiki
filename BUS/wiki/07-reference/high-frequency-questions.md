# BUS 高频问题

上级：[07 术语与检查清单](./README.md)

相关：[术语表](./glossary.md)、[BUS 一页版总览](./bus-one-page.md)

说明：本 wiki 正文默认优先使用 `master / slave`，在更抽象的描述里会用 `initiator / target` 作为同义表述。

## 1. BUS 和 NoC 是不是一回事

不是。BUS 更强调共享事务互连，NoC 更强调大规模并发和拓扑化传输。

## 2. AXI 是不是一条“总线”

更准确地说，AXI 是一套事务协议，不是传统意义上一根共享总线。

## 3. AXI 比 AHB 新，是不是所有地方都应该用 AXI

不是。是否选 AXI，取决于复杂度预算、并发需求和验证成本。

## 4. APB 慢，是不是就不重要

不是。很多关键配置、状态和中断相关路径都在 APB 一类控制总线上。

## 5. address handshake 成功，是不是事务就完成了

不是。对 AXI 来说，请求被接收只代表事务开始，不代表数据和 response 已经闭环。

## 6. coherent 系统是不是就不需要 barrier

不是。一致性不等于所有访问顺序都天然满足软件预期。

## 7. DMA 完成了数据搬运，是不是软件一定已经看到完成

不是。还要看 writeback、cache 可见性和 interrupt / polling 链路。

## 8. IOMMU fault 是不是内存控制器问题

通常不是。它更常见于地址翻译、权限或映射生命周期问题。

## 9. 平均带宽够，是不是总线就没问题

不是。很多问题出在尾延迟、回压传播和局部热点。

## 10. 波形里 READY 拉低，是不是一定有 bug

不是。READY 拉低本身是正常流控现象，关键是它为什么拉低、是否长期不恢复。

## 11. CPU 读 MMIO 卡死，是不是一定是软件 bug

不是。很常见的根因是 bridge、外设时钟、返回路径或 error 机制不完整。

## 12. DDR 带宽高，是不是 AXI master 就一定体验好

不是。中间的 interconnect、return path、row locality 和 read/write turnaround 都会改变最终体验。

## 一句话理解

很多 BUS 误区都来自把 `协议、实现、内存、软件语义、调试现象` 混成一层看；把层次拆开后，大多数问题都会清楚很多。
