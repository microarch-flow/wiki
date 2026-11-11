# 术语、资料与自测

上级：[HBF Wiki](./README.md)

本页帮助读者检查术语和证据边界。技术规范、厂商目标和教学假设应分别引用。资料核查日期为 2026-11-11。

## 术语

| 术语 | 本专题中的含义 |
| --- | --- |
| HBF | High Bandwidth Flash；一种近计算、高带宽 NAND 存储技术及相关规范名称 |
| host / xPU | 发起和管理 HBF 访问的计算系统；具体架构由产品决定 |
| core die | 保存 NAND 阵列及相关电路的 die |
| base die | 处理 host 接口、内部调度、ECC 和管理等功能的 die |
| channel | 接口或内部通路的划分；使用时必须说明是哪一层 |
| bank / plane | NAND 内部组织与资源名称；具体映射和独立性取决于实现 |
| WL / BL | wordline / bitline；分别参与选择、控制与感测路径 |
| page / block | 读取或编程相关的数据单位 / 常见的 NAND 擦除单位 |
| FTL | Flash Translation Layer；常用于管理逻辑地址与 NAND 物理位置 |
| ECC | Error Correction Code；用于检测和纠正一定范围内的数据错误 |
| P/E | program/erase，即编程/擦除；循环次数与磨损有关 |
| GB / GiB | 10⁹ B / 2³⁰ B；两者数值不能直接互换 |

## 一手资料

1. [OCP，HBF High-Level Base Die Specification v0.7.0，2026-08-03](https://www.opencompute.org/documents/ocp-hbf-architecture-specification-v0-7-0-final-pdf/)：接口、映射、软件、可靠性、封装和应用示例。使用时注明章节；这是规范版本，不是具体器件的实测报告。
2. [Sandisk，HBF Fact Sheet，2025-07](https://documents.sandisk.com/content/dam/asset-library/en_us/assets/public/sandisk/collateral/company/Sandisk-HBF-Fact-Sheet.pdf)：首代目标、单位定义与后续路线图。内部模拟的系统性能结论也应按其模型条件解释。
3. [SK hynix，首份 HBF 规范公告，2026-08-04](https://news.skhynix.com/en/hbf-at-fms-2026/)：规范发布背景和厂商对应用场景的描述。
4. [Sandisk，财年 2027 第一季度材料，第 5 页](https://investor.sandisk.com/static-files/4ca97b6e-7da4-4d52-b4ac-0e80f462716f)：首颗 die tape-out 和样品路线图状态。
5. [Western Digital，Flash 101 and Flash Management](https://documents.sandisk.com/content/dam/asset-library/en_us/assets/public/western-digital/collateral/white-paper/white-paper-sandisk-flash101-management.pdf)：NAND、保持、干扰和管理机制的通用背景；不能把其中旧器件数值当作 HBF 产品规格。
6. [KIOXIA，NAND 耐久性技术说明，2024](https://americas.kioxia.com/content/dam/kioxia/en-us/business/memory/mlc-nand/asset/KIOXIA_TBW_WAF_NAND_Endurance_Technical_Brief.pdf)：P/E 磨损和电荷存储结构的背景。

## 还需要验证什么

- 具体产品的 cell 编码、内部并行结构、地址映射、容量保留与访问粒度。
- 不同负载、温度和占空比下的读取延迟、有效带宽、尾延迟及错误率。
- 产品的 idle/读/写/维护功耗、热限制、P/E 寿命和数据保持条件。
- 样品交付、产品验证、良率、量产规模与成本；路线图不能代替这些证据。
- host 软件、固件和应用的恢复责任，以及数据在断电和重启后的系统级保证。

## 自测

1. 为什么 3D NAND 的 WL 层数与 HBF 的 die stack 高度是两个不同概念？
2. 在 4 KiB 读取案例中，host 事务粒度、NAND page 和 block 擦除粒度分别指什么？
3. 全局地址到 channel 的分配，与 channel 局部地址到内部 bank/die 的映射，分别由谁处理？
4. 四个不同 block 为什么不一定能同时读取？应检查哪些共享资源？
5. 为什么高聚合带宽不能直接推出单次访问的低延迟？
6. 何时可以用 M × S / T 估算阵列服务上界？若资源可以流水，T 应表示什么？
7. NAND 的数据刷新和 DRAM refresh 为什么不能当作同一种操作？
8. 如果读取报告不可纠正错误，系统在什么条件下可以恢复数据？
9. 规范带宽等级、厂商产品目标和实测带宽有什么区别？512 GB 与 512 GiB 为什么也要区分？
10. 将高频写入的 KV cache 放入 NAND 区域前，需要验证哪些写入和寿命条件？

答案可以从[阅读顺序](./README.md)中的相应章节推导。若结论需要具体产品数字，先补充产品规格和测量条件。
