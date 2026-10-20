// Enhance the inherited theme TOC without copying its layout or includes.
document.querySelectorAll('.wide .sidebar__right .toc').forEach((toc) => {
  if (toc.closest('details')) return;
  const details = document.createElement('details');
  details.className = 'museum-toc';
  const summary = document.createElement('summary');
  summary.textContent = 'On this page — show sections';
  details.append(summary);
  toc.before(details);
  details.append(toc);
  details.addEventListener('toggle', () => {
    summary.textContent = details.open ? 'On this page — hide sections' : 'On this page — show sections';
  });
});

// Keyboard users can scroll code and wide tables without scrolling the whole page.
document.querySelectorAll('.page__content pre, .page__content table').forEach((element) => {
  element.tabIndex = 0;
  if (element.tagName === 'PRE') element.setAttribute('aria-label', 'Code example; scroll horizontally for long lines');
});
document.querySelectorAll('.greedy-nav a').forEach((link) => {
  if (new URL(link.href).pathname === window.location.pathname) link.setAttribute('aria-current', 'page');
});

document.querySelectorAll('video').forEach(video => { video.tabIndex = 0; });
