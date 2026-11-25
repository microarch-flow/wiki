---
search:
  exclude: true
---

# CUDA 与 HIP 对端访问（原章节入口）

原来的 CUDA／HIP 软件流程现已并入《GPU A 能访问 GPU B 的地址，什么时候才能读？》。选中原来读到的小节，可以接着看同一块缓冲区从授权到复用的过程。

<div markdown="1" data-article-redirect="true">

- <span id="cuda-与-hip-对端访问先查询能力再建立有效路径"></span>[从 B 的缓冲区和 A 的读请求开始](../01-access-semantics/address-mapping-and-permissions.md)
- <span id="建立-a-访问-b-的方向"></span>[在 A 上查询能力并启用对端访问](../01-access-semantics/address-mapping-and-permissions.md#peer-access)
- <span id="访问成功以后仍需验证什么"></span>[已经能够寻址以后，A 何时可以读](../01-access-semantics/address-mapping-and-permissions.md#ready)
- <span id="内核访问与搬运引擎不是同一实验"></span>[比较内核直接读取与显式复制](../01-access-semantics/address-mapping-and-permissions.md#copy)

</div>
