# BUS 协议阅读模板

上级：[07 术语与检查清单](./README.md)

## 推荐结构

```md
# 协议名称

## 它在解决什么问题

一句话说明协议定位。

## 事务模型

- request / response 如何组织：
- 是否分离读写通道：
- 是否支持多个 outstanding：
- 顺序模型：

## 关键机制

- arbitration / backpressure：
- burst / alignment / boundary：
- error / timeout：
- narrow transfer / byte strobe：

## 系统集成关系

- 适合接什么 master / slave：
- 常见 bridge 对象：
- 和 DMA / DDR / MMIO 的关系：

## 最容易踩的坑

- 

## 最适合的场景

- 
```

## 一句话理解

协议阅读模板的重点不是抄字段名，而是把 `定位、事务模型、关键机制、系统关系` 一次记清楚。
