# 企业地图：Intel Foundry

上级：[[46 - 企业地图：先进封装关键玩家总览]]

相关：[[19 - Hybrid Bonding vs Micro-bump]]、[[24 - 台积电、Intel、大陆平台在 AI 封装上的真实差距]]

## 公司定位

Intel Foundry 在先进封装里的特点是：

- 平台能力强
- 3D / bridge 路线鲜明
- packaging 与 test 一起作为系统级 foundry 能力的一部分

它的逻辑更像：

`IDM / foundry + bridge + 3D stack + advanced test`

## 当前公开平台

根据 Intel Foundry Packaging 官方资料，其关键平台包括：

- `EMIB 2.5D`
- `EMIB 3.5D`
- `Foveros-S 2.5D`
- `Foveros-R 2.5D`
- `Foveros Direct 3D`

其中最值得你抓住的两条主线是：

- `EMIB`：bridge 路线
- `Foveros / Foveros Direct`：3D 路线

## 它的优势在哪

### 1. Bridge 和 3D 的路线非常鲜明

如果 TSMC 的核心印象是 `CoWoS + SoIC`，  
那 Intel 的核心印象就是：

- `EMIB`
- `Foveros`

这让它在：

- 3.5D
- bridge
- active base die + 3D stack

这些方向上有很强辨识度。

### 2. Foveros Direct 把 hybrid bonding 公开推得很明确

Intel 官方资料明确把 `Foveros Direct 3D` 与：

- `Cu-to-Cu hybrid bonding interface`
- `ultra-high bandwidth`
- `low power interconnect`

绑定在一起。

所以 Intel 是理解 3DIC 与 hybrid bonding 的关键平台案例之一。

### 3. test 也是其 platform 叙事的一部分

Intel Foundry Packaging 页面把 packaging 与 test 放在一起讲，这说明它不是把测试当成最后附属动作，而是 platform value 的一部分。

## 它和 TSMC 的差异

更准确的说法不是“Intel 不强”，而是：

- Intel 很强，尤其在 bridge / 3D 路线
- 但在对外 foundry + packaging 客户广度、以及 logic + HBM 主战场规模上，公开印象仍和 TSMC 不同

## 当前阅读建议

配套阅读：

1. [[19 - Hybrid Bonding vs Micro-bump]]
2. [[35 - 课程主线二：3DIC、Hybrid Bonding、CTE 与测试]]
3. [[24 - 台积电、Intel、大陆平台在 AI 封装上的真实差距]]

## 参考资料

- Intel Foundry Packaging: https://www.intel.com/content/www/us/en/foundry/packaging.html
- Intel Fact Sheet: https://www.intel.com/content/www/us/en/foundry/library/fact-sheet.html

