/* Render only marked expressions. KaTeX and fonts are served from this site. */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".arithmatex").forEach((element) => {
    const source = element.textContent.trim();
    const displayMode = source.startsWith("\\[") && source.endsWith("\\]");
    const inline = source.startsWith("\\(") && source.endsWith("\\)");
    if (!displayMode && !inline) return;
    try {
      // Normalize legacy spellings without changing the Markdown source.
      const tex = source.slice(2, -2).replace(/_\\max\b/g, "_{\\max}")
        .replace(/\^\\\*/g, "^{*}").replace(/½/g, "\\tfrac{1}{2}");
      katex.render(tex, element, { displayMode, throwOnError: true, strict: "ignore" });
    } catch (error) {
      // Keep the original TeX readable if a draft contains unsupported syntax.
      element.textContent = source;
      console.warn("Unable to render an inference formula:", error.message);
    }
  });
});
