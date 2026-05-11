# AXI Response 与错误路径

上级：[03 片上总线协议族](./README.md)

相关：[地址、数据、响应与事务语义](../02-fundamentals/transaction-address-data-response.md)、[争用、QoS 与可观测性](../05-performance-debug/contention-qos-observability.md)

## 这页在回答什么问题

当 AXI 事务失败、decode 不到目标、或者 slave 自己报错时，系统应该怎么理解和调试 response path。

## Response 在回答什么

response 的核心职责是告诉 master：

- 这笔事务有没有成功
- 错误属于哪一类
- 读写流程是否已经完整结束

但不要把这句话读得太满：  
`BRESP / RRESP` 通常只能告诉你成功/失败类别，例如 `DECERR`、`SLVERR`，不等于它能直接把精确根因完整讲出来。真正的根因往往还要结合 interconnect、slave 状态寄存器或 debug 日志继续追。

所以 response 不是“可有可无的附加信息”，而是事务闭环的一部分。

## 常见错误来源

### Decode error

地址没有命中有效目标，或者命中了当前不可访问区域。

### Slave error

目标设备收到了请求，但内部无法正确完成，例如：

- 非法寄存器访问
- 状态机不允许当前写入
- ECC / protection / timeout 等内部异常

### Timeout / fabricated error

有些 interconnect 或 bridge 会在下游长期无响应时主动合成错误返回，避免 master 永久挂死。

## 为什么错误路径很重要

如果错误路径设计不清楚，就会出现：

- master 永远等不到 completion
- 软件只能看到“卡住”，看不到原因
- bridge 吞掉错误，导致定位极难

## 调试时最该看什么

- 错误类别是 `DECERR`、`SLVERR` 还是 fabric 合成 timeout
- 问题是 decode 前产生、slave 内部产生，还是中间路径超时后被包装成错误
- response 是否被阻塞在返回路径
- timeout 是真实外设慢，还是互连自己堵住
- 软件能否区分“访问错地址”和“设备自己报错”

## 一句话理解

AXI 的错误路径不是异常分支，而是系统能否可诊断、可恢复的重要基础设施。
