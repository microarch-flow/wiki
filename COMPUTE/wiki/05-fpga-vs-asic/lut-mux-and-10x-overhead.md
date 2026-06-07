# FPGA vs ASIC:可配置性的 10× 代价,"muxes all the way down"

上级:[05 · FPGA vs ASIC](./README.md)
相关:[mux 与数据搬运成本](../02-datapath-foundations/mux-and-data-movement-cost.md)、[全局时钟同步](../04-clocking-and-pipeline/global-clock-synchronization.md)、[cache vs scratchpad](../06-memory-discipline/cache-vs-scratchpad.md)
主线:[计算 / 通信比](../01-overview/compute-communication-ratio.md)——本篇:可配置性是给分母交的税,固化(tape-out)省掉这 ~10× 的税。

---

## 这页在回答什么问题

同一个逻辑函数,在 FPGA 上实现比在 ASIC 上贵一个数量级。这 ~10× 从哪来?本篇回答:FPGA 的三大件(register / LUT / mux)如何用"可配置"换面积,LUT 为什么本质就是一个 mux("muxes all the way down"),以及什么时候这 10× 的税值得交。

---

## 1. 商业账先行:$10k vs $3000 万

先把决策的两端摆出来,后面的门级分析都是在解释这张表:

| | 第一颗成本 | 单位能效/成本 | 适用场景 |
|---|---|---|---|
| **FPGA** | ~$10k | 差一个数量级 | 确定性低延迟 + 高并行,但 workload 频繁改(如每月) |
| **ASIC** | ~$3000 万(一次 tape-out) | 好一个数量级 | workload 稳定、量大 |

FPGA 能表达的,ASIC 都能表达——ASIC 是 FPGA 的超集(去掉可配置性,直接固化)。**FPGA 存在的唯一理由是:想要确定性延迟 + 高并行,但又频繁改 workload,不愿每次都付 $3000 万的流片费。** 一旦 workload 稳定下来、量足够大,$3000 万摊到每颗芯片上变得便宜,ASIC 的 10× 能效/面积优势就压倒一切。

> 衔接 FAB:这个 $3000 万 tape-out 的量级,出处和构成(掩模、流片、良率爬坡)见 [`FAB/.../process-nodes-and-ppa-tradeoffs`](../../../FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md);FPGA 的"确定性低延迟"卖点和 [scratchpad 的确定性哲学](../06-memory-discipline/cache-vs-scratchpad.md) 同源。

---

## 2. FPGA 三大件,以及"muxes all the way down"

FPGA 用三种可配置积木拼出任意电路:

- **register**:存储(和 ASIC 一样)。
- **LUT(lookup table)**:可配置的门——用真值表实现任意逻辑函数。
- **大量 mux**:在"现场(field,指芯片部署到数据中心之后)"配置布线。每个单元前都挂一个 mux,从邻近电路里选输入。

**配置一块 FPGA = 配置所有这些 mux 的选择 + 所有 LUT 的真值表。** 没有改变任何物理连线,只是设定了海量 mux 选谁、海量 LUT 存什么真值表。Pope 的原话:**"muxes all the way down"**——往下看每一层都是 mux。

```
        电路 soup(一堆可用信号)
              │
          ┌───▼───┐  ← mux:从 soup 里选 4 个信号
          │ 前级mux│
          └───┬───┘
              ▼ 4 个选中的输入
          ┌───────┐
          │  LUT  │  ← 本身又是一个 16-entry 真值表的 mux
          └───┬───┘
              ▼
          ┌───────┐
          │ 后级mux│  ← mux:决定输出接到哪去
          └───────┘
```

这正是 [datapath 那篇](../02-datapath-foundations/mux-and-data-movement-cost.md#4-mux-是全域反复出现的分母原语) 说的"mux 是全域分母原语"的极致体现:FPGA 把灵活性做到极致,代价就是把整片芯片做成了 mux 的海洋。

---

## 3. LUT 的本质就是一个 mux

把 LUT 拆开看:一个 4 输入 LUT 要实现"任意 4 输入 → 1 输出"的逻辑函数。做法:**存一张 16 行的真值表**(4 个输入有 2⁴ = 16 种组合,每种组合对应一个输出位),用 4 个输入位作为选择信号,从 16 行里 mux 出对应那一行的输出。

```
真值表(16 entry,配置时写入):
  输入 0000 → 输出 b0
  输入 0001 → 输出 b1
  ...                      ← 4 个输入位当 select,mux 选出 16 行里的 1 行
  输入 1111 → 输出 b15
```

所以一个 LUT = **一个 n=16、p=1 的 mux**(从 16 个真值表 entry 选 1)+ 一个把电路 soup 里的信号选 4 位喂进来的前级 mux。LUT 不是什么神秘器件,它就是"用真值表 + mux 实现任意小函数"。

> **真实硬件锚点**:LUT 典型 **4 输入**,是个 sweet spot。输入太少 → 需要更多 LUT 串联才能实现复杂函数(又是一个 compute/communication trade-off:串联的 LUT 之间要布线);输入太多 → 真值表 2ⁿ 指数膨胀(5 输入要 32 entry,6 输入 64 entry)。4 输入平衡了单 LUT 表达力和真值表大小。长距离连接由厂商(如 AMD)固定布线,只在局部邻域给你 mux 灵活性。

---

## 4. 10× 开销从哪来:真值表是冗余表达

拿一个具体函数对比:四路 AND `AND(AND(a,b), AND(c,d))`。

```
ASIC 直接实现:           3 个 AND 门
                         (两个 2 输入 AND + 一个 2 输入 AND)

FPGA(LUT)实现:         一个 16-entry 真值表的 mux ≈ 32 个门
                         (16 个 AND 做掩码 + ~16 个 OR 收拢)
```

**因为** 真值表是"穷举每一种输入组合"的冗余表达——它为了能表达**任意** 4 输入函数,存了全部 16 种情况;而直接写门是对**这一个**函数的简洁表达,只用了它真正需要的 3 个门。**所以** 可配置性的代价就是这 ~10× 的门数膨胀(3 → 32),以及对应的 polysilicon 和布线面积。

这就是"FPGA 比 ASIC 贵一个数量级"的微观出处:**你为"能变成任意电路"这个能力,在每一个 LUT 上都付了穷举真值表的冗余;ASIC 一旦 tape-out,就把这份冗余全部省掉,只留下真正需要的门。**

> ⚠️ 常见误解:以为 FPGA 慢/贵是因为"时钟跑不快"或"工艺差"。根本原因是**结构性冗余**:可配置性要求每个逻辑单元都用真值表(穷举)而非定制门(精简)表达,外加海量配置 mux。同样工艺下,这份冗余就是那 10×。

---

## 5. 本篇在主线上的位置

FPGA vs ASIC 是[计算 / 通信比](../01-overview/compute-communication-ratio.md)在"可配置性"维度上的一次清算:**可配置性是给分母交的税**——LUT 的真值表冗余 + 海量配置 mux,让同一个函数的"通信/开销"部分膨胀 ~10×。tape-out 固化就是一次性付 $3000 万,把这份税永久省掉,换来 10× 的面积/能效。选 FPGA 还是 ASIC,本质是"愿不愿意为频繁改 workload 持续交这 10× 的可配置税"。

---

## 建模启示

- **可配置性开销应建模为一个乘性面积/能效系数 `~10×`,作用在分母上。** 同一个逻辑块,FPGA 实现 vs ASIC 实现,`useful_compute` 不变,但 `area` 和 `energy` 乘以可配置系数。这让 archax 能在同一框架里比较 FPGA 原型和 ASIC 目标。
- **必须显式建模的状态变量**:`impl_target ∈ {FPGA, ASIC}`、`lut_inputs`(典型 4)、`config_mux_overhead`。FPGA 下逻辑面积 ≈ ASIC 面积 × 10。
- **可折叠**:LUT 内部真值表 mux、配置 mux 的具体结构 → 折叠成那个 ~10× 系数。布线细节交给厂商固定布线模型。
- **关心决策(FPGA vs ASIC)时必须保留**:`workload_change_frequency` 和 `volume`——它们和 $10k/$3000万 一起决定哪个更划算。频繁改 + 低量 → FPGA;稳定 + 高量 → ASIC。
- **事件/数据结构草图**:`LogicBlock{gates_asic, impl_target} → area = gates_asic · (impl_target == FPGA ? 10 : 1)`。决策层:`total_cost = NRE(impl) + volume · per_unit_cost(impl)`,NRE_FPGA ≈ $10k、NRE_ASIC ≈ $30M,交点处的 volume 即 ASIC 划算的门槛。
