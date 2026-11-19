document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".fab-diagram-scroll, .fab-diagram-aligned pre > code").forEach((panel, index) => {
    const hint = document.createElement("p");
    hint.className = "fab-diagram-hint";
    hint.id = `fab-diagram-hint-${index}`;
    hint.textContent = "横向滚动查看完整图解";
    hint.hidden = true;
    const block = panel.closest(".fab-diagram-aligned") || panel;
    block.before(hint);
    const graph = panel.querySelector(".fab-diagram-inner");
    let centered = false;

    const update = () => {
      const overflow = panel.scrollWidth > panel.clientWidth + 1;
      hint.hidden = !overflow;
      if (overflow) {
        if (!centered && panel.hasAttribute("data-top-down") && graph.querySelector("div.mermaid")) {
          panel.scrollLeft = (panel.scrollWidth - panel.clientWidth) / 2;
          centered = true;
        }
        panel.tabIndex = 0;
        panel.setAttribute("role", "region");
        panel.setAttribute("aria-label", "图解");
        panel.setAttribute("aria-describedby", hint.id);
      } else {
        panel.removeAttribute("tabindex");
        panel.removeAttribute("role");
        panel.removeAttribute("aria-label");
        panel.removeAttribute("aria-describedby");
      }
    };

    const observer = new ResizeObserver(update);
    observer.observe(panel);
    if (graph) observer.observe(graph);
    update();
  });
});
