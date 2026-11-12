/* Render only marked expressions. KaTeX and fonts are served from this site. */
document.addEventListener("DOMContentLoaded", () => {
  const displays = [];
  const normalize = (tex) => tex.replace(/_\\max\b/g, "_{\\max}")
    .replace(/\^\\\*/g, "^{*}").replace(/½/g, "\\tfrac{1}{2}");
  document.querySelectorAll(".arithmatex").forEach((element, index) => {
    const source = element.textContent.trim();
    const displayMode = source.startsWith("\\[") && source.endsWith("\\]");
    const inline = source.startsWith("\\(") && source.endsWith("\\)");
    if (!displayMode && !inline) return;
    try {
      // Normalize legacy spellings without changing the Markdown source.
      const tex = normalize(source.slice(2, -2));
      katex.render(tex, element, { displayMode, throwOnError: true, strict: "ignore" });
    } catch (error) {
      // Keep the original TeX readable if a draft contains unsupported syntax.
      element.textContent = source;
      console.warn("Unable to render an inference formula:", error.message);
    }
    if (displayMode) {
      const hint = document.createElement("span");
      hint.id = `inference-math-scroll-hint-${index}`;
      hint.className = "inference-math-scroll-hint";
      hint.textContent = "公式可左右滚动";
      hint.hidden = true;
      element.after(hint);
      displays.push({ element, hint });
    }
  });

  // The TOC keeps a readable text fallback when scripts are unavailable.
  document.querySelectorAll(".inference-toc-math").forEach((element) => {
    const fallback = element.textContent;
    try {
      katex.render(normalize(element.dataset.tex), element, { displayMode: false, throwOnError: true, strict: "ignore" });
    } catch (error) {
      element.textContent = fallback;
      console.warn("Unable to render an inference TOC formula:", error.message);
    }
  });

  const updateScrolling = () => {
    displays.forEach(({ element, hint }) => {
      const scrollable = element.scrollWidth > element.clientWidth + 1;
      element.classList.toggle("is-scrollable", scrollable);
      hint.hidden = !scrollable;
      if (scrollable) {
        element.tabIndex = 0;
        element.setAttribute("role", "region");
        element.setAttribute("aria-label", "公式");
        element.setAttribute("aria-describedby", hint.id);
      } else {
        element.removeAttribute("tabindex");
        element.removeAttribute("role");
        element.removeAttribute("aria-label");
        element.removeAttribute("aria-describedby");
      }
    });
  };
  updateScrolling();
  window.addEventListener("resize", updateScrolling);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(updateScrolling);
});
