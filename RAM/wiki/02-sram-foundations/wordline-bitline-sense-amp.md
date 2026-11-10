# 字线、位线与读出放大器：SRAM 的阵列路径

上级：[SRAM 基础](./README.md)
相关：[一次访问的电气阶段与接口时序](./read-write-cycle-timing.md)、[DRAM 行列译码与感测](../04-dram-foundations/row-column-decode-sense-amplify.md)

## 阵列中的职责

字线 `WL` 控制一行 cell 的访问晶体管；位线 `BL/BLB` 在列方向连接 cell 和外围；sense amp 判断读出信号，写驱动器建立写入信号。地址译码、列选择和输出电路把这些组件连接到宏接口。字线负载、位线电容、外围电路及布局都会影响时序和能耗。

## 读：位线电荷与差分

以一种常见的 6T 差分读为例。先将 `BL/BLB` 预充至接近相同的高电平。若选中 cell 为 `Q=1, QB=0`，打开 `WL` 后，`QB` 所连接的位线通过访问晶体管和下拉晶体管放电；另一侧保持较高电平。差分达到电路要求后，sense amp 判决并输出数字结果。选中 cell 的低节点也受到预充位线扰动，因此必须满足读稳定性。

具体预充电平、感测方式和时机由宏实现决定。并非所有 SRAM 都使用同一种差分读。长位线通常带来更大电容，并改变差分建立时间和充放电能耗；局部划分可缩短路径，但会增加外围和译码成本。

SRAM 的读感测一般不承担 DRAM 那种对电容 cell 的破坏性读恢复。DRAM 的 sense amp 与打开行的恢复有不同职责，详见[DRAM 感测](../04-dram-foundations/row-column-decode-sense-amplify.md)。

## 写：位线驱动 cell

写驱动在 `BL/BLB` 建立目标差分，`WL` 导通后，访问路径推动内部 `Q/QB` 跨过翻转点。必须满足宏规定的驱动强度和字线脉宽，才能在关闭 `WL` 后保持新状态。读和写共用部分阵列，但成功条件不同。

## 建模启示

字线译码、位线发展、感测和恢复是电气阶段，不自动对应独立的整数周期。它们可能并行或与相邻访问重叠。以目标宏的 PVT、输入采样、输出负载和 timing library 定义接口可见时间及下一次接纳间隔；不要把每项延迟分别向上取整后相加。

```text
SramArrayTimingModel {
  rows_per_bank, cols_per_bank, pvt_and_interface
  read_visible_time, read_accept_interval
  write_visible_time, write_accept_interval
}
```

模拟器可记录 `accept`、数据可见、端口冲突和下一次接纳。没有电路仿真或实测数据时，这些事件不能证明位线电压或 cell 噪声裕量。
