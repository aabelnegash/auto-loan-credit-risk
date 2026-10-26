(() => {
  const links = [...document.querySelectorAll('.contents a')];
  const sections = [...document.querySelectorAll('.content-section, .repository')];
  if (!('IntersectionObserver' in window)) return;
  const observer = new IntersectionObserver((entries) => {
    const visible = entries.filter(entry => entry.isIntersecting);
    if (!visible.length) return;
    const current = visible.sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0].target.id;
    links.forEach(link => {
      const active = link.getAttribute('href') === `#${current}`;
      link.classList.toggle('is-active', active);
      if (active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }, { rootMargin: '-10% 0px -65% 0px', threshold: 0 });
  sections.forEach(section => observer.observe(section));
})();
