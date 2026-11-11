(() => {
  const stages = [
    { node: "cpu", direction: "request", name: "处理器发出读取", path: "处理器 → Cache", description: "处理器向 cache 提交已经完成地址翻译的读请求。" },
    { node: "cache", direction: "request", name: "Cache 查找未命中", path: "Cache → 控制器", description: "本例中的 cache 没有所需数据，因此向下游发起读取。" },
    { node: "controller", direction: "request", name: "控制器接收并调度", path: "控制器 → DRAM", description: "控制器接收请求，按地址映射和可用资源安排访问；具体等待由模型或器件条件决定。" },
    { node: "dram", direction: "request", name: "DRAM 服务读取", path: "控制器 → DRAM", description: "DRAM 在目标 bank 的状态和协议时序允许时服务请求。命令次序不是固定不变的。" },
    { node: "cache", direction: "return", name: "数据返回并回填", path: "DRAM → 控制器 → Cache", description: "数据沿返回路径到达 cache。本例假设完整块回填后再向处理器响应。" },
    { node: "cpu", direction: "return", name: "处理器取得数据", path: "Cache → 处理器", description: "请求的数据对处理器可见。此事件不自动等于指令退休。" },
  ];

  document.querySelectorAll("[data-ram-overview]").forEach((demo) => {
    const buttons = Object.fromEntries([...demo.querySelectorAll("[data-ram-action]")].map((button) => [button.dataset.ramAction, button]));
    let index = 0;
    let timer = null;

    function stop() {
      if (timer !== null) window.clearInterval(timer);
      timer = null;
      buttons.play.textContent = "自动播放";
    }

    function render() {
      const stage = stages[index];
      demo.dataset.index = String(index);
      demo.dataset.direction = stage.direction;
      for (const key of ["name", "path", "description"]) {
        demo.querySelector(`[data-ram-field="${key}"]`).textContent = stage[key];
      }
      demo.querySelector('[data-ram-field="counter"]').textContent = `${String(index + 1).padStart(2, "0")} / ${String(stages.length).padStart(2, "0")}`;
      demo.querySelectorAll("[data-ram-node]").forEach((node) => node.classList.toggle("active", node.dataset.ramNode === stage.node));
      buttons.prev.disabled = index === 0;
      buttons.next.disabled = index === stages.length - 1;
      buttons.play.disabled = false;
      buttons.reset.disabled = false;
    }

    buttons.prev.addEventListener("click", () => { stop(); index = Math.max(0, index - 1); render(); });
    buttons.next.addEventListener("click", () => { stop(); index = Math.min(stages.length - 1, index + 1); render(); });
    buttons.reset.addEventListener("click", () => { stop(); index = 0; render(); });
    buttons.play.addEventListener("click", () => {
      if (timer !== null) { stop(); return; }
      if (index === stages.length - 1) index = 0;
      render();
      buttons.play.textContent = "暂停";
      timer = window.setInterval(() => {
        index += 1;
        render();
        if (index === stages.length - 1) stop();
      }, 2400);
    });
    render();
  });
})();
