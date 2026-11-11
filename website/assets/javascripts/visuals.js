(() => {
  const examples = {
    dram: [
      { name: "已预充", command: "等待 ACT", buffer: "无打开行", data: "尚未返回", description: "初始时没有打开的行。此示例从目标 bank 已预充且允许 ACT 的状态开始。" },
      { name: "ACT 已发出", command: "ACT", buffer: "目标行激活中", data: "尚未返回", description: "控制器发出 ACT，目标行开始激活；后续 RD 还必须满足 ACT 到 RD 的时序等条件。" },
      { name: "RD 已发出", command: "RD", buffer: "目标行保持打开", data: "按读延迟返回", description: "满足相关条件后发出 RD。读数据按所选器件及模式的读延迟返回；图中不表示具体波形。" },
      { name: "PRE 已发出", command: "PRE", buffer: "关闭与预充中", data: "按读延迟返回", description: "只有 ACT、RD 等约束均允许时才能发出显式 PRE。发出 PRE 后，bank 尚需完成预充。" },
      { name: "预充完成", command: "等待下一次 ACT", buffer: "无打开行", data: "按读延迟返回", description: "满足 PRE 后的 tRP 等条件后，bank 可在其他约束也允许时接受新的 ACT。" },
    ],
    buffer: [
      { name: "周期 1", description: "DMA 填充 buffer 0。计算等待 A 在本周期结束后可用。" },
      { name: "周期 2", description: "DMA 填充 buffer 1，同时计算使用 buffer 0 中的 A。两个访问路径按假设互不冲突。" },
      { name: "周期 3", description: "B 已在上一周期结束后可用，计算使用 buffer 1 中的 B。DMA 在这个示例中空闲。" },
    ],
  };

  document.querySelectorAll("[data-demo]").forEach((demo) => {
    const states = examples[demo.dataset.demo];
    const panel = demo.querySelector(".diagram-panel");
    const buttons = Object.fromEntries([...demo.querySelectorAll("[data-action]")].map((button) => [button.dataset.action, button]));
    let index = 0;
    let timer = null;

    function stop() {
      if (timer !== null) window.clearInterval(timer);
      timer = null;
      buttons.play.textContent = "自动播放";
    }

    function render() {
      const state = states[index];
      panel.dataset.step = String(index);
      demo.querySelector('[data-field="index"]').textContent = `${String(index + 1).padStart(2, "0")} / ${String(states.length).padStart(2, "0")}`;
      for (const [field, value] of Object.entries(state)) {
        const element = demo.querySelector(`[data-field="${field}"]`);
        if (element) element.textContent = value;
      }
      buttons.prev.disabled = index === 0;
      buttons.next.disabled = index === states.length - 1;
      buttons.reset.disabled = false;
      buttons.play.disabled = false;
      demo.querySelectorAll("[data-cycle]").forEach((cell) => {
        cell.classList.toggle("current", Number(cell.dataset.cycle) === index);
      });
    }

    buttons.prev.addEventListener("click", () => { stop(); index = Math.max(0, index - 1); render(); });
    buttons.next.addEventListener("click", () => { stop(); index = Math.min(states.length - 1, index + 1); render(); });
    buttons.reset.addEventListener("click", () => { stop(); index = 0; render(); });
    buttons.play.addEventListener("click", () => {
      if (timer !== null) { stop(); return; }
      if (index === states.length - 1) index = 0;
      render();
      buttons.play.textContent = "暂停";
      timer = window.setInterval(() => {
        index += 1;
        render();
        if (index === states.length - 1) stop();
      }, 1800);
    });
    render();
  });
})();
