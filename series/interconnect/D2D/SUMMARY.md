# 封装内芯粒互连：知识地图

上级：[封装内芯粒互连](./README.md)

先认识芯粒、封装连接和一次通信，再阅读具体接口案例。

## 01 芯粒与连接基础 {#foundations}

- [芯粒是什么](./01-foundations/what-is-a-chiplet.md)
- [芯粒怎样在封装内连接](./01-foundations/in-package-connections.md)
- [一次跨芯粒通信](./01-foundations/cross-die-communication.md)

## 02 接口与案例 {#interfaces}

- [UCIe 1.1 读取案例](./ucie-pcie-read.md)
- [BoW PHY 2.0](./bow-phy.md)
- [BoW PHY 2.0 坏线重映射](./02-interfaces/bow-phy-redundancy.md)
- [BoW.Flexi 读取案例](./bow-flexi.md)
- [AIB 2.0](./02-interfaces/aib-2.md)
- [OIF 112G XSR+](./02-interfaces/oif-cei-112g-xsr-plus.md)
- [AMBA CHI C2C](./02-interfaces/chi-c2c.md)

## 03 系统集成与验证 {#system-integration}

- [芯粒互操作与启动](./03-system-design/interoperability-and-bring-up.md)
- [跨芯粒流控与前进条件](./03-system-design/flow-control-and-forward-progress.md)
- [跨芯粒链路错误检测与重放](./03-system-design/link-reliability.md)
- [跨芯粒读取的有效性能](./03-system-design/effective-bandwidth-and-latency.md)
- [链路测试与故障定位](./03-system-design/link-testing-and-diagnosis.md)

## 04 产品与系统案例 {#product-cases}

- [Stratix 10 TX 产品案例](./04-product-cases/stratix-10-tx.md)
- [AMD EPYC 9004 产品案例](./04-product-cases/amd-epyc-9004-gmi.md)
- [AMD MI300A 产品案例](./04-product-cases/amd-mi300a.md)
