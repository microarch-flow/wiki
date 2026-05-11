# Master/Slave/Bridge 设计清单

上级：[07 术语与检查清单](./README.md)

相关：[BUS 设计检查清单](./bus-design-checklist.md)、[Bridge、CDC 与 Width Adapter](../04-microarchitecture-integration/bridge-cdc-width-adaptation.md)

## Master 侧

- outstanding 深度是否和下游能力匹配
- ID 分配是否清楚，是否可能引入不必要保序
- burst 生成是否考虑边界拆分
- response 长时间不返回时是否有 timeout / recovery 策略
- 是否能区分 descriptor、data、writeback 等不同流量

## Slave 侧

- 地址窗口和寄存器语义是否清楚
- accept request 后是否一定能最终返回 response
- 是否支持 narrow transfer / byte strobe
- error return 和 busy / stall 的边界是否明确定义
- 低功耗、复位、时钟关闭状态下访问行为是否有定义

## Bridge 侧

- 协议转换后顺序语义是否仍成立
- CDC 缓冲深度是否足够
- 宽窄转换是否正确处理 byte lane 和对齐
- timeout / error 是否会被 bridge 吞掉
- bridge 满载时会把 backpressure 传到哪里

## 一句话理解

master、slave、bridge 最容易各自“局部正确但系统拼不起来”，所以评审时必须分角色逐项过一遍。
