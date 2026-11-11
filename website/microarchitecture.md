---
title: 芯片微架构笔记
hide:
  - navigation
  - toc
---

<div class="home-page">
  <section class="hero">
    <div class="hero-copy">
      <p class="eyebrow"><span></span> MICROARCHITECTURE NOTES</p>
      <h1>理解芯片，<br><em>从数据如何<br class="mobile-break">流动开始。</em></h1>
      <p class="hero-description">从电路与时序出发，理解数据如何存储、计算和移动，再把这些机制转化为可解释的模型。</p>
      <div class="hero-actions">
        <a class="hero-button primary" href="../articles/">阅读精选文章 <span aria-hidden="true">↗</span></a>
        <a class="hero-button secondary" href="../visuals/">探索互动图解 <span aria-hidden="true">→</span></a>
      </div>
      <div class="hero-footnote"><span>01 / 03</span> 电路 <i></i> 架构 <i></i> 建模</div>
    </div>
    <div class="hero-art">
      <img src="../assets/images/chip-map.svg" alt="芯片内部计算、存储、互连与外部存储关系的概念示意图">
      <div class="hero-art-caption"><span>FIG. 01</span> 芯片中的数据路径 · 概念示意</div>
    </div>
  </section>

  <section class="intro-band">
    <div><span class="section-number">THE NOTEBOOK / 01</span><h2>从一个问题出发</h2></div>
    <p>先弄清输入、资源和约束，再观察数据的路径与完成条件。这里的例子用于帮助理解机制；具体器件的时序与性能仍需要查阅规格并校准。</p>
  </section>

  <section class="explore-section" id="topics">
    <div class="section-heading">
      <div><span class="section-number">EXPLORE THE TOPICS / 02</span><h2>选择一个专题</h2></div>
      <p>九个相互连接的视角，<br>从基础概念到系统问题。</p>
    </div>
    <div class="topic-grid">
      <a class="topic-card" href="../RAM/wiki/"><span class="topic-number">01 / STORAGE</span><span class="topic-symbol">▦</span><h3>RAM <small>存储系统</small></h3><p>从 SRAM、DRAM 单元到存储层级和控制器。</p><span class="card-link">进入专题 ↗</span></a>
      <a class="topic-card" href="../COMPUTE/wiki/"><span class="topic-number">02 / COMPUTE</span><span class="topic-symbol">✳</span><h3>COMPUTE <small>计算</small></h3><p>数据通路、流水线和算力资源如何形成吞吐。</p><span class="card-link">进入专题 ↗</span></a>
      <a class="topic-card" href="../BUS/wiki/"><span class="topic-number">03 / INTERCONNECT</span><span class="topic-symbol">⇄</span><h3>BUS <small>片上总线</small></h3><p>理解事务、握手、仲裁和共享资源。</p><span class="card-link">进入专题 ↗</span></a>
      <a class="topic-card" href="../NOC/wiki/"><span class="topic-number">04 / NETWORK</span><span class="topic-symbol">⌗</span><h3>NoC <small>片上网络</small></h3><p>从 router、流控到拓扑与仿真。</p><span class="card-link">进入专题 ↗</span></a>
      <a class="topic-card" href="../DMA/wiki/"><span class="topic-number">05 / MOVEMENT</span><span class="topic-symbol">↗</span><h3>DMA <small>数据搬运</small></h3><p>描述符、并发与数据搬运的完成边界。</p><span class="card-link">进入专题 ↗</span></a>
      <a class="topic-card" href="../PCIE/wiki/"><span class="topic-number">06 / HOST LINK</span><span class="topic-symbol">⇌</span><h3>PCIe <small>主机互连</small></h3><p>主机与设备之间的链路和事务。</p><span class="card-link">进入专题 ↗</span></a>
      <a class="topic-card" href="../CIM/wiki/"><span class="topic-number">07 / IN-MEMORY</span><span class="topic-symbol">⊞</span><h3>CIM <small>存内计算</small></h3><p>存储阵列、外围电路和计算的边界。</p><span class="card-link">进入专题 ↗</span></a>
      <a class="topic-card" href="../CPO/wiki/"><span class="topic-number">08 / OPTICAL</span><span class="topic-symbol">✺</span><h3>CPO <small>光互连</small></h3><p>光引擎、链路预算与系统集成。</p><span class="card-link">进入专题 ↗</span></a>
      <a class="topic-card" href="../FAB/wiki/"><span class="topic-number">09 / PHYSICAL</span><span class="topic-symbol">◫</span><h3>FAB <small>制造与封装</small></h3><p>工艺、封装、测试与工程约束。</p><span class="card-link">进入专题 ↗</span></a>
    </div>
  </section>

  <section class="feature-section">
    <div class="feature-copy"><span class="section-number">LEARN BY SEEING / 03</span><h2>让过程<br>动起来。</h2><p>一步一步观察 DRAM 命令顺序，或查看一个简化的双缓冲时间线。每个图解都标出假设和适用边界。</p><a href="../visuals/">打开互动图解 <span aria-hidden="true">↗</span></a></div>
    <div class="feature-graphic" aria-hidden="true"><div class="feature-line"><span>ACT</span><b></b><span>RD</span><b></b><span>PRE</span></div><div class="feature-bars"><i></i><i></i><i></i><i></i><i></i></div><small>COMMAND SEQUENCE / SCHEMATIC</small></div>
  </section>

  <section class="reading-section">
    <div class="section-heading"><div><span class="section-number">A GOOD PLACE TO START / 04</span><h2>推荐阅读</h2></div><p>选一条路径，<br>沿着问题继续深入。<br><a href="../articles/">查看全部精选文章 ↗</a></p></div>
    <div class="reading-grid">
      <a class="reading-card reading-image" href="../RAM/wiki/02-sram-foundations/6t-cell-bistable-storage/"><div class="reading-card-image"><img src="../RAM/wiki/img/6t-sram-cell.svg" alt="6T SRAM cell 晶体管连接图"></div><div><span>RAM · 基础</span><h3>6T SRAM cell：它如何保存、读取和写入 1 bit</h3><p>从存储单元理解保持、读和写。</p></div><b>↗</b></a>
      <a class="reading-card" href="../NOC/wiki/02-router-microarchitecture/credit-based-flow-control/"><div><span>NOC · 流控</span><h3>Credit 如何约束发送？</h3><p>从下游 buffer 空位理解局部流控。</p></div><b>↗</b></a>
      <a class="reading-card" href="../DMA/wiki/04-programming-model/tiling-double-buffering/"><div><span>DMA · 数据路径</span><h3>分块与双缓冲</h3><p>探索搬运与计算重叠的条件。</p></div><b>↗</b></a>
    </div>
  </section>
  <div class="home-footer"><span>芯片微架构笔记</span><span>READ · THINK · MODEL</span></div>
</div>
