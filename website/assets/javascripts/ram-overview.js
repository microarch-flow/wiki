(() => {
  const stages = [
    { node: "cpu", links: ["cpu-cache"], direction: "request", name: "处理器读取 A[0]", path: "处理器 → Cache", description: "处理器向 cache 提交已完成地址翻译的 4 B 读请求。" },
    { node: "cache", links: ["cache-controller"], direction: "request", name: "Cache 查找未命中", path: "Cache → 控制器", description: "cache 没有该数据，向下游请求包含 A[0] 的 64 B cache line。" },
    { node: "controller", links: ["controller-dram"], direction: "request", name: "控制器接收并调度", path: "控制器 → DRAM", description: "控制器根据地址映射、资源状态与时序条件安排 DRAM 访问。" },
    { node: "dram", links: ["controller-dram"], direction: "request", name: "DRAM 服务读取", path: "控制器 → DRAM", description: "DRAM 按目标 bank 的状态和协议条件服务请求。" },
    { node: "cache", links: ["controller-dram", "cache-controller"], direction: "return", name: "数据返回并回填", path: "DRAM → 控制器 → Cache", description: "完整的 64 B cache line 沿返回路径到达 cache。" },
    { node: "cpu", links: ["cpu-cache"], direction: "return", name: "处理器取得 A[0]", path: "Cache → 处理器", description: "cache 返回请求的 4 B 数据，处理器可将其提供给后续计算。" },
    { node: "cache", links: ["cpu-cache"], direction: "return", name: "再次读取时 cache 命中", path: "Cache → 处理器", description: "处理器读取 A[1]。它在同一条仍有效的 cache line 中，cache 直接返回数据。" },
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
      demo.querySelectorAll("[data-ram-link]").forEach((link) => link.classList.toggle("active", stage.links.includes(link.dataset.ramLink)));
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
