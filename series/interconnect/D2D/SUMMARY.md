# 封装内芯粒互连：知识地图

上级：[封装内芯粒互连](./README.md)

从芯粒和封装连接读起。基础部分的寄存器读用同一幅图讲通用路径和 UCIe 1.1 承载 PCIe 的过程，后面的接口和案例可按需要选读。

## 01 芯粒与连接基础 {#foundations}

- [芯粒是什么](./01-foundations/what-is-a-chiplet.md)
- [芯粒怎样在封装内连接](./01-foundations/in-package-connections.md)
- [跨芯粒寄存器读](./ucie-pcie-read.md)

## 02 接口与案例 {#interfaces}

- [UCIe 1.1 链路启动与训练](./02-interfaces/ucie-1-1-link-bring-up.md)
- [UCIe-3D 垂直连接](./02-interfaces/ucie-3d.md)
- [UCIe.mem 存储访问](./02-interfaces/ucie-memory.md)
- [BoW PHY 2.0](./bow-phy.md)
- [BoW PHY 2.0 坏线重映射](./02-interfaces/bow-phy-redundancy.md)
- [BoW 存储接口](./02-interfaces/bow-memory.md)
- [BoW.Flexi 读取案例](./bow-flexi.md)
- [AIB 2.0](./02-interfaces/aib-2.md)
- [OIF 112G XSR+](./02-interfaces/oif-cei-112g-xsr-plus.md)
- [AMBA CHI C2C](./02-interfaces/chi-c2c.md)

## 03 系统集成与验证 {#system-integration}

- [芯粒互操作与启动](./03-system-design/interoperability-and-bring-up.md)
- [跨芯粒流控与前进条件](./03-system-design/flow-control-and-forward-progress.md)
- [跨芯粒链路错误检测与重放](./03-system-design/link-reliability.md)
- [跨芯粒读取的有效性能](./03-system-design/effective-bandwidth-and-latency.md)
- [多芯粒拓扑与数据放置](./03-system-design/multi-chiplet-topology.md)
- [链路测试与故障定位](./03-system-design/link-testing-and-diagnosis.md)
- [UCIe 2.0 测试访问与管理](./03-system-design/ucie-dfx-test-access.md)

## 04 产品与系统案例 {#product-cases}

- [Stratix 10 TX 产品案例](./04-product-cases/stratix-10-tx.md)
- [AMD EPYC 9004 产品案例](./04-product-cases/amd-epyc-9004-gmi.md)
- [AMD MI300A 产品案例](./04-product-cases/amd-mi300a.md)
