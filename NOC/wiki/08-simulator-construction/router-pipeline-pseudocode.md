# Router Pipeline Pseudocode

上级：[08 Simulator Construction](./README.md)

相关：[Router Pipeline Stages](../02-router-microarchitecture/router-pipeline-stages.md)、[Core Data Structures](./core-data-structures.md)

## 这页在回答什么问题

这页回答：一个最小但正确的 router tick 应该怎样组织，哪些阶段顺序不能乱，哪些资源释放时机必须明确。

## 核心原则

router tick 最容易出错的地方不是算法，而是时序：

- 什么时候读旧状态
- 什么时候更新 route / VC / switch 结果
- credit 何时返回
- tail 何时释放资源

这几件事只要顺序模糊，结果就会飘。

## 推荐的单 router 逻辑顺序

一个稳定的顺序通常是：

1. 接收 arriving flit 和 returning credit
2. 更新 local ejection 可用状态
3. 对 header 做 route compute
4. 对需要分配路径的 header 做 VC allocation
5. 对可前进 flit 发起 switch request
6. 运行 switch allocator
7. 执行 flit move
8. 释放 buffer slot，生成 credit
9. 对 tail 释放 packet path / VC state

## 为什么这个顺序重要

例如：

- 如果在 flit 真正离开前就返回 credit，会高估吞吐
- 如果 tail 太早释放 path，后包会错误抢跑
- 如果 ejection 状态不先更新，目的端阻塞会判断错误

所以阶段顺序不是实现风格问题，而是模型语义问题。

## 最小伪代码

```text
tick_router(router):
  accept_arriving_flits(router)
  accept_returning_credits(router)
  update_local_ejection_state(router)

  for each input_vc:
    if head_flit is HEADER and route not ready:
      compute_route(head_flit)

  for each input_vc:
    if head_flit is HEADER and needs output_vc:
      request_vc_allocation(input_vc)

  run_vc_allocator(router)

  for each input_vc:
    if head_flit can advance:
      request_switch(input_vc, output_port)

  run_switch_allocator(router)

  for each granted input_vc:
    move_flit(router, input_vc)
    if one input buffer slot released:
      schedule_credit_return()
    if flit is TAIL:
      release_path_state()
```

## ejection 不是特殊小事

目的端路径里最容易被简化错的是：

- 到目的 router
- 但 ejection queue 满

这时正确行为不是“算完成”，而是：

- 记录 `EJECTION_BLOCKED`
- 保持 flit 在本地待发 / 待收状态
- 继续阻挡 credit 回传链

这是很多系统级 backpressure 的起点。

## injection 也应有对称规则

source 端不能因为 packet 产生了就立刻进网。至少要满足：

- 本地 input VC 或注入口可用
- route / class 前置条件满足
- 下游等效接收条件能被表达

否则应记为 `INJECTION_BLOCKED` 或 `ROUTE_BLOCKED`。

## 双缓冲值得优先考虑

如果实现阶段担心同周期读写污染，推荐用：

- `current_state`
- `next_state`

哪怕会多一些代码，也能显著减少隐式抢跑和 debug 难度。

## 一句话理解

router pipeline 在代码里的关键不是把 RC/VA/SA/LT 名字写全，而是把资源分配、移动、credit 返回和 tail 释放的时序关系写对。

## 建模启示

实现阶段建议先为这些最小场景写手算对照：

- 3-hop 单 packet
- 两包抢同一输出
- buffer 满后的 backpressure
- tail 释放后下一包接续前进
- destination ejection blocked

如果这些最小场景还不稳定，就不要急着上复杂 workload。
