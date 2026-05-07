# 术语表

上级：[06 术语与速查](./README.md)

## SRAM

Static RAM。通常用 6T 单元实现，不需要刷新，常用于 cache 和片上局部存储。

## DRAM

Dynamic RAM。通常用 1T1C 单元实现，需要刷新，常用于大容量主存和高带宽外部内存。

## DDR

Double Data Rate。每个时钟周期在上升沿和下降沿各传一次数据。

## MT/s

Mega Transfers per second。表示每秒发生多少百万次传输，常用于表述 DDR 接口速率。

## ACT

Activate。打开某个 DRAM row，并将其内容感测到 row buffer。

## PRE

Precharge。关闭当前行并恢复位线状态，为下一次 activate 做准备。

## Row Buffer

行缓冲。可理解为 bank 当前已打开的一行的工作副本。

## Row Hit

请求命中当前已打开行，因此无需重新 activate，延迟较低。

## Channel

内存控制器与 DRAM 间的一条独立通道，是扩展带宽的重要资源。

## Rank

共享通道一部分资源的物理组织单位，常用于容量扩展。

## Bank

DRAM 内部的并行存储子阵列，是控制器调度和并行度管理的关键资源。

## LPDDR

Low Power DDR。面向低功耗系统的 DRAM 路线。

## GDDR

Graphics DDR。面向图形和独立 GPU 的高带宽板级 DRAM 路线。

## HBM

High Bandwidth Memory。通过 3D 堆叠和先进封装实现超宽近距互连的高带宽 DRAM 路线。

## TSV

Through-Silicon Via。穿硅通孔，用于 die 垂直互连，是 HBM 堆叠的重要基础结构。

## 2.5D

通常指多个 die 并排放在中介层上，通过高密度短距互连连接。

## 3D

通常指 die 在垂直方向直接堆叠形成更高集成密度的互连结构。
