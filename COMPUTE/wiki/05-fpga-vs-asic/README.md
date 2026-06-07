# 05 · FPGA vs ASIC:可配置性的 10× 代价

[02–04 章](../02-datapath-foundations/) 搭出的门、阵列、流水,最终要落到硅上。一个根本选择:做成可重配的 FPGA,还是固化的 ASIC?本章用门级账回答这 ~10× 的差距从哪来。

## 篇目

1. **[FPGA vs ASIC:LUT、mux 与 10× 开销](./lut-mux-and-10x-overhead.md)**
   $10k vs $3000万 的商业账;FPGA 三大件与 "muxes all the way down";LUT 本质是 16-entry 真值表 mux;四路 AND 的 3 门 vs 32 门;10× 来自真值表的结构性冗余。

## 本章在主线上的位置

可配置性是[主线](../01-overview/compute-communication-ratio.md)里给**分母**交的税:为了"能变成任意电路",每个 LUT 都用穷举真值表(而非精简门)表达,外加海量配置 mux,使同一函数的开销膨胀 ~10×。tape-out 固化 = 一次性付 $3000万,把这份税永久省掉。这一章把 [datapath 的 mux 暗线](../02-datapath-foundations/mux-and-data-movement-cost.md)推到极致——FPGA 就是 mux 的海洋。

→ 算完的数据从哪来(确定性还是非确定性)?进入 [06 · 存储 discipline](../06-memory-discipline/)。
