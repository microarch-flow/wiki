(() => {
  const sidebar = document.querySelector('.md-sidebar--primary');
  if (!sidebar) return;

  // Keep the full name available when a navigation label is visually shortened.
  sidebar.querySelectorAll('.md-nav__link > .md-ellipsis').forEach((text) => {
    const label = text.textContent.replace(/\s+/g, ' ').trim();
    if (label && !text.parentElement.hasAttribute('title')) text.parentElement.setAttribute('title', label);
  });

  sidebar.querySelectorAll('li.md-nav__item--nested').forEach((item) => {
    const toggle = item.querySelector(':scope > input.md-nav__toggle');
    const panel = item.querySelector(':scope > nav.md-nav');
    const heading = item.querySelector(':scope > .md-nav__link');
    if (!toggle || !panel || !heading) return;
    // The theme renders section headers as non-interactive labels.
    if (item.classList.contains('md-nav__item--section') && !heading.classList.contains('md-nav__container')) return;

    const link = heading.querySelector(':scope > a.md-nav__link');
    const control = heading.matches('label') ? heading : heading.querySelector(':scope > label.md-nav__link');
    const text = heading.querySelector('.md-ellipsis');
    const list = panel.querySelector(':scope > ul.md-nav__list');
    // Material opens the current index as a drawer even when it has no child
    // pages. Keep the active topic link visible in its parent instead.
    if (link?.getAttribute('aria-current') === 'page' && list && !list.children.length) {
      toggle.checked = false;
      panel.setAttribute('aria-expanded', 'false');
      return;
    }
    if (!control || control.htmlFor !== toggle.id || !text) return;

    const name = text.textContent.replace(/\s+/g, ' ').trim();
    panel.id ||= `${toggle.id}-content`;
    control.setAttribute('role', 'button');
    control.setAttribute('aria-controls', panel.id);
    control.setAttribute('aria-label', `${name}目录`);
    const current = link && link.getAttribute('aria-current') === 'page' ? link : null;
    if (current) current.setAttribute('aria-controls', panel.id);

    const sync = () => {
      const expanded = String(toggle.checked);
      control.setAttribute('aria-expanded', expanded);
      if (current) current.setAttribute('aria-expanded', expanded);
    };
    toggle.addEventListener('change', sync);
    sync();

    // Other titles still navigate to their own pages. A click on the current
    // index title instead operates its existing disclosure control.
    if (current) current.addEventListener('click', (event) => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      control.click();
    });
  });
})();
