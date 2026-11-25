(() => {
  const examples = {
    read: [
      { name: "初始：保持", wl: "0", bl: "未指定", blb: "未指定", q: "1", qb: "0", phase: "idle", description: "WL 为低，假设 Q = 1、QB = 0。两条位线的电平暂不指定。", path: "访问管关闭。" },
      { name: "预充与均衡", wl: "0", bl: "≈ VDD", blb: "≈ VDD", q: "1", qb: "0", phase: "precharge", description: "外围电路将 BL、BLB 预充并均衡到接近 VDD。完成后释放预充，再进入示例中的读访问。", path: "WL 保持低电平，访问管关闭。" },
      { name: "选通与差分建立", wl: "1", bl: "较高", blb: "开始下降", q: "1", qb: "0 附近", phase: "read", description: "WL 打开 N3、N4。BLB 通过低节点一侧开始放电，QB 受到扰动而略微升高；成功的读操作不应翻转 cell。", path: "主要放电路径：BLB → N4 → QB → N2 → VSS。" },
      { name: "感测差分", wl: "1", bl: "较高", blb: "较低", q: "1", qb: "0 附近", phase: "read", description: "当位线差分和使能时机满足感测要求，sense amp 判定本例中 Q 的值为 1。", path: "QB 仍受读扰动；差分足够与 cell 稳定是两个不同条件。" },
      { name: "关闭字线", wl: "0", bl: "较高", blb: "较低", q: "1", qb: "0", phase: "idle", description: "读出后关闭 WL。cell 保持原状态；外围在适当时机为下一次访问准备位线。", path: "访问管关闭；位线何时恢复由宏电路决定。" },
    ],
    write: [
      { name: "初始：保持", wl: "0", bl: "未指定", blb: "未指定", q: "1", qb: "0", phase: "idle", description: "WL 为低。假设初始 Q = 1、QB = 0，目标是将 Q 写成 0。", path: "访问管关闭。" },
      { name: "准备写数据", wl: "0", bl: "0", blb: "1", q: "1", qb: "0", phase: "drive", description: "写驱动建立目标差分：BL = 0、BLB = 1。此时 WL 尚未打开，cell 仍保持旧值。", path: "外部写驱动控制位线；本例建立写数据时已关闭读预充路径。" },
      { name: "字线打开，拉低 Q", wl: "1", bl: "0", blb: "1", q: "下降中", qb: "偏低", phase: "write", description: "N3、N4 导通。BL 经 N3 拉低 Q，原先导通的 P1 仍在向上拉 Q。", path: "主要写入作用路径：Q → N3 → 低电平 BL。" },
      { name: "交叉耦合反馈推动翻转", wl: "1", bl: "0", blb: "1", q: "趋向 0", qb: "上升中", phase: "feedback", description: "Q 降低使 P2 逐渐导通、N2 减弱。P2 为 QB 充电。QB 上升又使 N1 增强、P1 减弱，帮助 Q 继续下降。", path: "上拉路径：VDD → P2 → QB。翻转成功后，P2 把 QB 拉向完整高电平。" },
      { name: "关闭字线，保持新值", wl: "0", bl: "0", blb: "1", q: "0", qb: "1", phase: "idle", description: "示例假设翻转已完成。关闭 WL 后，cell 在持续供电和满足保持条件时保存 Q = 0、QB = 1。", path: "访问管关闭；写驱动可按宏控制时序释放。" },
    ],
  };

  document.querySelectorAll("[data-sram-demo]").forEach((demo) => {
    const states = examples[demo.dataset.sramDemo];
    if (!states) return;
    const buttons = Object.fromEntries([...demo.querySelectorAll("[data-sram-action]")].map((button) => [button.dataset.sramAction, button]));
    let index = 0;
    let timer = null;

    function stop() {
      if (timer !== null) window.clearInterval(timer);
      timer = null;
      buttons.play.textContent = "自动播放";
    }

    function render() {
      const state = states[index];
      demo.dataset.phase = state.phase;
      demo.dataset.index = String(index);
      demo.dataset.wl = state.wl;
      for (const [field, value] of Object.entries(state)) {
        demo.querySelectorAll(`[data-sram-field="${field}"]`).forEach((element) => { element.textContent = value; });
      }
      demo.querySelector('[data-sram-field="counter"]').textContent = `${String(index + 1).padStart(2, "0")} / ${String(states.length).padStart(2, "0")}`;
      buttons.prev.disabled = index === 0;
      buttons.next.disabled = index === states.length - 1;
      buttons.play.disabled = false;
      buttons.reset.disabled = false;
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
      }, 2400);
    });
    render();
  });
})();
