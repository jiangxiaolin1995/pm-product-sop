(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('document-data').textContent);
  const panels = { sop: document.getElementById('panel-sop'), template: document.getElementById('panel-template') };
  const positions = { sop: 0, template: 0 };
  let currentPanel = 'sop';
  let toastTimer;
  const mobile = matchMedia('(max-width: 900px)');

  function toast(text) {
    clearTimeout(toastTimer);
    const target = document.getElementById('toast');
    target.textContent = text;
    target.classList.add('is-visible');
    toastTimer = setTimeout(() => target.classList.remove('is-visible'), 3000);
  }

  function setMenu(open, restoreFocus = false) {
    document.body.classList.toggle('menu-open', open);
    document.getElementById('menu-toggle').setAttribute('aria-expanded', String(open));
    document.getElementById('nav-backdrop').hidden = !open;
    if (open) document.querySelector(`#${currentPanel}-toc a`)?.focus();
    else if (restoreFocus) document.getElementById('menu-toggle').focus();
  }

  function setPanel(name, restorePosition = true) {
    if (!panels[name]) return;
    if (name !== currentPanel) positions[currentPanel] = window.scrollY;
    currentPanel = name;
    for (const [key, panel] of Object.entries(panels)) {
      panel.hidden = key !== name;
      const tab = document.getElementById(`tab-${key}`);
      tab.setAttribute('aria-selected', String(key === name));
      tab.tabIndex = key === name ? 0 : -1;
      document.getElementById(`${key}-toc`).hidden = key !== name;
    }
    setMenu(false);
    if (restorePosition) window.scrollTo({ top: positions[name], behavior: 'instant' });
    observeHeadings();
  }

  function navigateHash() {
    const hash = decodeURIComponent(location.hash.slice(1));
    if (!hash) return;
    const name = hash.startsWith('template') ? 'template' : 'sop';
    setPanel(name, false);
    const target = hash === name ? panels[name] : document.getElementById(hash);
    if (target && panels[name].contains(target)) {
      requestAnimationFrame(() => target.scrollIntoView({ block: 'start', behavior: 'instant' }));
    }
  }

  const observer = new IntersectionObserver(entries => {
    const entry = entries.find(item => item.isIntersecting && !item.target.closest('[hidden]'));
    if (!entry) return;
    document.querySelectorAll('.toc-link[aria-current]').forEach(link => link.removeAttribute('aria-current'));
    const link = document.querySelector(`.toc-link[href="#${entry.target.id}"]`);
    if (link) link.setAttribute('aria-current', 'location');
  }, { rootMargin: '-85px 0px -66% 0px', threshold: 0 });

  function observeHeadings() {
    observer.disconnect();
    panels[currentPanel].querySelectorAll('.markdown-body h2, .markdown-body h3').forEach(node => observer.observe(node));
  }

  async function copyText(text, button) {
    const originalLabel = button.textContent;
    let copied = false;
    button.disabled = true;
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
        copied = true;
      }
    } catch (_) { /* A local file may not have Clipboard API access. */ }
    if (!copied) {
      const field = document.createElement('textarea');
      field.value = text;
      field.setAttribute('aria-label', '待复制内容');
      field.style.cssText = 'position:fixed;left:0;top:0;opacity:0;pointer-events:none;';
      document.body.appendChild(field);
      field.focus();
      field.select();
      try { copied = document.execCommand('copy'); } catch (_) { copied = false; }
      field.remove();
      button.focus({ preventScroll: true });
    }
    button.disabled = false;
    if (copied) {
      button.textContent = '已复制';
      toast('已复制，可粘贴到需求记录或对话中');
      setTimeout(() => { button.textContent = originalLabel; }, 1800);
    } else {
      toast('浏览器未允许复制，请选中文字复制，或下载模板');
    }
  }

  document.querySelectorAll('[role="tab"]').forEach(tab => {
    tab.addEventListener('click', () => {
      setPanel(tab.dataset.panel);
      history.replaceState(null, '', '#' + tab.dataset.panel);
    });
    tab.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const name = event.key === 'Home' ? 'sop' : event.key === 'End' ? 'template' : currentPanel === 'sop' ? 'template' : 'sop';
      document.getElementById('tab-' + name).click();
      document.getElementById('tab-' + name).focus();
    });
  });

  const modes = {
    quick: { description: '适合已知规则的小改动。确认问题与范围，完成相应修改、验收和结果记录；其他步骤按影响合并。', steps: [1, 3, 5, 7, 8] },
    standard: { description: '适合新功能、跨页面流程和业务规则调整。沿八步推进，已有材料直接复用。', steps: [1, 2, 3, 4, 5, 6, 7, 8] },
    explore: { description: '适合需求、商业模式或可行性不清楚的情况。先分析与验证关键假设，再决定是否投入完整交付。', steps: [1, 2, 3, 4] }
  };
  function setMode(name) {
    const mode = modes[name];
    document.querySelectorAll('[data-mode]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.mode === name)));
    document.getElementById('mode-description').textContent = mode.description;
    document.querySelectorAll('.phase-link').forEach(link => link.classList.toggle('is-emphasized', mode.steps.includes(Number(link.dataset.step))));
  }

  document.addEventListener('click', event => {
    const target = event.target.closest('button, a');
    if (!target) return;
    if (target.dataset.mode) setMode(target.dataset.mode);
    if (target.hasAttribute('data-copy-target')) copyText(document.getElementById(target.dataset.copyTarget).textContent, target);
    if (target.hasAttribute('data-copy-template')) copyText(data.template, target);
    if (target.hasAttribute('data-download-template')) {
      const url = URL.createObjectURL(new Blob([data.template], { type: 'text/markdown;charset=utf-8' }));
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = '需求推进模板.md';
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      toast('已发起模板下载，请查看浏览器下载结果');
    }
    if (target.hasAttribute('data-print')) window.print();
    if (target.id === 'menu-toggle') setMenu(!document.body.classList.contains('menu-open'));
    if (target.id === 'close-nav' || target.id === 'nav-backdrop') setMenu(false, true);
    if (target.tagName === 'A' && target.getAttribute('href')?.startsWith('#')) {
      event.preventDefault();
      const hash = target.getAttribute('href');
      if (hash === '#main') { document.getElementById('main').focus(); return; }
      history.pushState(null, '', hash);
      navigateHash();
    }
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && document.body.classList.contains('menu-open')) setMenu(false, true);
    if (event.key === 'Tab' && document.body.classList.contains('menu-open')) {
      const focusable = [...document.querySelectorAll('#sidebar a, #sidebar button')].filter(node => node.offsetParent !== null);
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { last.focus(); event.preventDefault(); }
      else if (!event.shiftKey && document.activeElement === last) { first.focus(); event.preventDefault(); }
    }
  });
  mobile.addEventListener('change', event => { if (!event.matches) setMenu(false); });
  window.addEventListener('hashchange', navigateHash);
  setMode('standard');
  if (location.hash) navigateHash();
  else setPanel('sop');
})();
