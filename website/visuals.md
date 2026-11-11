---
title: 互动图解
hide:
  - toc
---

<div class="visual-page">
  <header class="visual-intro"><p class="eyebrow dark"><span></span> INTERACTIVE NOTES</p><h1>把过程拆开来看。</h1><p>使用“下一步”逐项观察状态变化。每张图都是特定假设下的示意，不是器件波形或性能测试。</p></header>

  <section class="demo-section" id="dram" data-demo="dram">
    <div class="demo-heading"><div><span class="section-number">DIAGRAM / 01</span><h2>DRAM：从打开行到预充</h2></div><span class="demo-tag">命令顺序示意</span></div>
    <p class="demo-lead">观察单个 bank 在一次读操作中的状态。按顺序执行 ACT、RD 和显式 PRE；按钮切换的是逻辑阶段，不代表相等的时间间隔。</p>
    <div class="diagram-panel dram-panel" data-step="0">
      <div class="dram-path"><div class="diagram-block controller"><small>CONTROLLER</small><strong>控制器</strong><span data-field="command">等待 ACT</span></div><div class="path-arrow" aria-hidden="true">→</div><div class="diagram-block bank"><small>DRAM BANK</small><strong>目标 bank</strong><div class="row-buffer"><span>ROW BUFFER</span><div class="buffer-cells" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></div><b data-field="buffer">无打开行</b></div></div><div class="path-arrow" aria-hidden="true">→</div><div class="diagram-block response"><small>DATA</small><strong>读数据</strong><span data-field="data">尚未返回</span></div></div>
      <div class="state-indicator"><span>当前阶段 <b data-field="index">01 / 05</b></span><strong data-field="name">已预充</strong></div>
      <p class="state-description" role="status" aria-live="polite" data-field="description">初始时没有打开的行。此示例从目标 bank 已预充且允许 ACT 的状态开始。</p>
      <div class="demo-controls"><button type="button" data-action="prev" disabled>上一步</button><button type="button" class="next-button" data-action="next" disabled>下一步 →</button><button type="button" data-action="play" disabled>自动播放</button><button type="button" data-action="reset" disabled>重置</button></div>
    </div>
    <div class="demo-note"><strong>前提与边界</strong><p>这里只展示单 bank 的一次读流程，忽略其他 bank、refresh、仲裁和总线冲突。RD 要满足所选器件及模式的 ACT→RD 等约束；显式 PRE 要同时满足 ACT、RD 等形成的相关下界。PRE 发出后还要等待 tRP 等约束，才能再次 ACT。时序值及额外条件以目标器件规格为准。</p><a href="../RAM/wiki/05-dram-protocol-families/commands-act-rd-wr-pre/">阅读 DRAM 命令与时序 →</a></div>
  </section>

  <section class="demo-section" id="double-buffer" data-demo="buffer">
    <div class="demo-heading"><div><span class="section-number">DIAGRAM / 02</span><h2>双缓冲：搬运与计算重叠</h2></div><span class="demo-tag">三周期理想示例</span></div>
    <p class="demo-lead">两个 tile 分别使用两个 buffer。观察 DMA 和计算资源何时工作，以及计算何时可以使用已搬运的数据。</p>
    <div class="diagram-panel buffer-panel" data-step="0">
      <div class="timeline" aria-label="双缓冲的三个周期时间线">
        <div class="time-label"></div><div class="time-head" data-cycle="0">周期 1</div><div class="time-head" data-cycle="1">周期 2</div><div class="time-head" data-cycle="2">周期 3</div>
        <div class="time-label"><small>TRANSFER</small><strong>DMA</strong></div><div class="time-cell dma" data-cycle="0"><b>填充 A</b><span>buffer 0</span></div><div class="time-cell dma" data-cycle="1"><b>填充 B</b><span>buffer 1</span></div><div class="time-cell idle" data-cycle="2">空闲</div>
        <div class="time-label"><small>COMPUTE</small><strong>计算</strong></div><div class="time-cell idle" data-cycle="0">等待 A</div><div class="time-cell compute" data-cycle="1"><b>处理 A</b><span>buffer 0</span></div><div class="time-cell compute" data-cycle="2"><b>处理 B</b><span>buffer 1</span></div>
      </div>
      <div class="state-indicator"><span>当前阶段 <b data-field="index">01 / 03</b></span><strong data-field="name">周期 1</strong></div>
      <p class="state-description" role="status" aria-live="polite" data-field="description">DMA 填充 buffer 0。计算等待 A 在本周期结束后可用。</p>
      <div class="demo-controls"><button type="button" data-action="prev" disabled>上一步</button><button type="button" class="next-button" data-action="next" disabled>下一步 →</button><button type="button" data-action="play" disabled>自动播放</button><button type="button" data-action="reset" disabled>重置</button></div>
    </div>
    <div class="demo-note"><strong>前提与边界</strong><p>假设 DMA 填充一个 tile 和计算一个 tile 各占一个完整周期；结果在周期结束后可供下一周期使用。两个 buffer 独立，DMA 与计算资源可并行，且访问端口和互连不会冲突。buffer 0 要等周期 2 的计算结束后才能复用。资源冲突、不同阶段耗时、写回和实际同步开销都可能改变时间线。</p><a href="../DMA/wiki/04-programming-model/tiling-double-buffering/">阅读 Tiling 与 Double Buffer →</a></div>
  </section>
</div>
