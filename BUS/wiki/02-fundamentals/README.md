# 02 基础对象与事务语义

这一部分关注 BUS 到底在传什么、如何传、为什么会堵。

## 本章入口

1. [BUS vs NoC vs Point-to-Point](./bus-vs-noc-vs-point-to-point.md)
2. [地址、数据、响应与事务语义](./transaction-address-data-response.md)
3. [仲裁、顺序性与 Backpressure](./arbitration-ordering-backpressure.md)
4. [位宽、时钟、Burst 与延迟](./width-clock-burst-latency.md)

## 一句话总纲

BUS 的复杂度不在“连线数量”，而在 `共享访问、顺序约束、流控回压、时序粒度` 这些事务层规则。
