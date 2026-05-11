# 03 片上总线协议族

这一部分关注常见 on-chip bus family 的分工，而不是把所有协议细节逐信号重写。

## 本章入口

1. [AXI / AHB / APB 对照](./axi-ahb-apb-comparison.md)
2. [AXI Channel、ID 与 Outstanding](./axi-channel-id-outstanding.md)
3. [AXI 五通道与 VALID/READY](./axi-five-channels-handshake.md)
4. [AXI Burst、对齐与边界](./axi-burst-alignment-boundary.md)
5. [AXI Narrow Transfer 与 WSTRB](./axi-narrow-transfer-wstrb.md)
6. [AXI Response 与错误路径](./axi-response-error-path.md)
7. [AHB-Lite 与 APB 深化](./ahb-lite-and-apb-deep-dive.md)
8. [分层总线与协议分工](./hierarchical-bus-and-protocol-roles.md)
9. [Coherent Bus vs Non-Coherent Bus](./coherent-bus-vs-noncoherent-bus.md)
10. [TileLink 概览](./tilelink-overview.md)

## 一句话总纲

选 BUS 协议时，最重要的不是“谁更新”，而是 `事务能力、复杂度、软件需求、系统规模` 是否匹配。
