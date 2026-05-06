# Fan-out 制造路线：Chip-first 与 Chip-last

上级：[[05 - Fan-out RDL]]

相关：[[10 - 共性工程问题]]

## 核心区别

判断标准只有一个：

- die 在 RDL 形成之前进场：chip-first
- die 在 RDL 形成之后进场：chip-last

## Chip-first

也可理解为 mold-first / RDL-last。

简化流程：

1. die placement
2. molding / embedding
3. grinding / planarization
4. RDL build-up
5. bump formation
6. singulation / 后续组装

特点：

- 工艺概念直接
- 成本通常较低
- 更适合 low I/O 或较低复杂度场景
- RDL 更容易受 die shift、die protrusion、warpage 影响

## Chip-last

也可理解为 RDL-first。

简化流程：

1. 在 carrier 上先做 fine-pitch RDL
2. 预留 die attach 区域
3. die-to-RDL 贴装/接合
4. molding
5. via / bump / debond
6. 后续组装

特点：

- 更适合 fine-pitch、高密度、多芯片 fan-out
- RDL 制作阶段更不受 die shift 干扰
- 对对位、接合、carrier 管理要求更高

## 如何选

- 成本敏感、I/O 较低：更偏 chip-first
- 高密度、多芯片、性能优先：更偏 chip-last

