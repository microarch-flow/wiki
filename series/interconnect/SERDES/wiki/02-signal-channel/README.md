# 02 电信号与通道：信号为什么会变化？

上级：[SerDes Wiki](../README.md)

数据在导线上表现为随时间变化的电压和电流。通道不是一根没有代价的理想线。它会改变波形，并与终端、封装和邻近信号共同影响接收条件。

## 阅读顺序

1. [电压、电流和有限的翻转时间](./voltage-current-and-switching.md)
2. [差分信号、共模与回流](./differential-and-return.md)
3. [时序偏差、抖动和采样窗口](./timing-skew-and-jitter.md)
4. [特性阻抗、终端与反射](./impedance-and-reflection.md)
5. [怎样读损耗、dB 和 S 参数？](./loss-db-and-s-parameters.md)
6. [ISI、噪声与眼图怎样影响判决？](./isi-noise-and-eye.md)

完成后进入[发送端](../03-transmitter/README.md)，看发送侧怎样产生波形并补偿部分通道影响。
