---
title: 芯片微架构笔记
hide:
  - toc
---

<div class="home-page">
  <section class="hero">
    <div class="hero-copy">
      <p class="eyebrow"><span></span> 芯片微架构笔记 / 系列首页</p>
      <h1>理解芯片，<br><em>从数据如何<br class="mobile-break">流动开始。</em></h1>
      <p class="hero-description">从电路与时序出发，理解数据如何存储、计算和移动，再把这些机制转化为可解释的模型。</p>
      <div class="hero-actions">
        <a class="hero-button primary" href="../articles/">阅读精选文章 <span aria-hidden="true">↗</span></a>
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
      <p>从计算与搬运出发，<br>也可以沿链接阅读存储、互连与制造系列。</p>
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
      <a class="topic-card" href="../SERDES/wiki/"><span class="topic-number">10 / SERIAL LINK</span><span class="topic-symbol">≋</span><h3>SerDes <small>高速串行链路</small></h3><p>从收发与训练，到设计验证、系统应用和建模。</p><span class="card-link">进入专题 ↗</span></a>
      <a class="topic-card" href="../HBF/wiki/"><span class="topic-number">11 / FLASH</span><span class="topic-symbol">▤</span><h3>HBF <small>高带宽闪存</small></h3><p>从 NAND 读取到近计算存储架构。</p><span class="card-link">进入专题 ↗</span></a>
    </div>
  </section>

  <section class="reading-section">
    <div class="section-heading"><div><span class="section-number">A GOOD PLACE TO START / 03</span><h2>推荐阅读</h2></div><p>选一条路径，<br>沿着问题继续深入。<br><a href="../articles/">查看全部精选文章 ↗</a></p></div>
    <div class="reading-grid">
      <a class="reading-card reading-image" href="../RAM/wiki/02-sram-foundations/6t-cell-bistable-storage/"><div class="reading-card-image"><img src="../RAM/wiki/img/6t-sram-cell.svg" alt="6T SRAM cell 晶体管连接图"></div><div><span>RAM · 基础</span><h3>6T SRAM cell：它如何保存、读取和写入 1 bit</h3><p>从存储单元理解保持、读和写。</p></div><b>↗</b></a>
      <a class="reading-card" href="../NOC/wiki/02-router-microarchitecture/credit-based-flow-control/"><div><span>NOC · 流控</span><h3>Credit 如何约束发送？</h3><p>从下游 buffer 空位理解局部流控。</p></div><b>↗</b></a>
      <a class="reading-card" href="../DMA/wiki/04-programming-model/tiling-double-buffering/"><div><span>DMA · 数据路径</span><h3>分块与双缓冲</h3><p>探索搬运与计算重叠的条件。</p></div><b>↗</b></a>
    </div>
  </section>
  <section class="reading-section" id="on-chip-data-supply">
    <div class="section-heading"><div><span class="section-number">DATA SUPPLY / 04</span><h2>片上存储与数据供给</h2></div><p>沿一块数据的路径，<br>从搬运读到存储端口和阵列供数。</p></div>
    <div class="reading-grid">
      <a class="reading-card" href="../DMA/wiki/04-programming-model/tiling-double-buffering/"><div><span>01 / DMA</span><h3>分块与双缓冲</h3><p>观察搬运与计算重叠需要满足的条件。</p></div><b>↗</b></a>
      <a class="reading-card" href="../RAM/wiki/02-sram-foundations/single-port-dual-port-multi-port/"><div><span>02 / SRAM</span><h3>单端口、双端口与多端口</h3><p>理解一次访问怎样使用存储端口。</p></div><b>↗</b></a>
      <a class="reading-card" href="../COMPUTE/wiki/03-systolic-array/weight-loading-and-trickle-feed/"><div><span>03 / ARRAY</span><h3>权重加载与阵列供数</h3><p>继续追踪操作数如何进入计算阵列。</p></div><b>↗</b></a>
    </div>
  </section>

  <section class="reading-section" id="architecture-modeling">
    <div class="section-heading"><div><span class="section-number">MODELING ROUTE / 05</span><h2>架构建模与性能分析</h2></div><p>先定义工作负载，<br>再建立模型并检查预测。</p></div>
    <div class="reading-grid">
      <a class="reading-card" href="../external/workload-wiki/06-chip-workload-analysis/workload-analysis-methodology/"><div><span>01 / WORKLOAD</span><h3>工作负载分析方法</h3><p>固定输入、阶段、数据量与依赖。</p></div><b>↗</b></a>
      <a class="reading-card" href="../RAM/wiki/06-memory-controller/mc-modeling-for-simulation/"><div><span>02 / MODEL</span><h3>DRAM 控制器建模</h3><p>把请求、状态与事件放入同一模型。</p></div><b>↗</b></a>
      <a class="reading-card" href="../NOC/wiki/08-simulator-construction/verification-and-calibration/"><div><span>03 / VALIDATE</span><h3>模型验证与校准</h3><p>区分手算检查、参数校准和独立负载验证。</p></div><b>↗</b></a>
    </div>
  </section>
  <div class="home-footer"><span>芯片微架构笔记</span><span>READ · THINK · MODEL</span></div>
</div>
