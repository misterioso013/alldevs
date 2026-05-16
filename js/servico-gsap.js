/* =========================================================
   AllDevs · servico-gsap.js
   Animação completa das páginas de serviço.
   Depende de: gsap, ScrollTrigger.
   ========================================================= */

(function () {
  if (typeof gsap === 'undefined') return;
  gsap.registerPlugin(ScrollTrigger);

  // Respeitar usuários que pediram redução de movimento
  const REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- UTILS ----------
  const $  = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  // Divide um elemento de texto em palavras com máscaras (para reveal)
  function splitToWords(el) {
    if (!el || el.dataset.split === '1') return;
    const text = el.textContent.trim();
    const parts = text.split(/(\s+)/); // mantém espaços
    el.innerHTML = parts.map(p => {
      if (/^\s+$/.test(p)) return p;
      return `<span class="sw-mask"><span class="sw-word">${p}</span></span>`;
    }).join('');
    el.dataset.split = '1';
  }

  // ---------- 0. INJETA ELEMENTOS DE CHROME (progress bar + cursor) ----------
  function injectChrome() {
    // Scroll progress bar
    if (!$('.scroll-progress')) {
      const bar = document.createElement('div');
      bar.className = 'scroll-progress';
      bar.innerHTML = '<div class="scroll-progress-fill"></div>';
      document.body.appendChild(bar);
    }
    // Cursor glow (desktop only)
    if (window.matchMedia('(pointer:fine)').matches && !$('.cursor-glow')) {
      const g = document.createElement('div');
      g.className = 'cursor-glow';
      document.body.appendChild(g);
    }
    // Aura de fundo no hero
    const hero = $('.servico-hero');
    if (hero && !$('.hero-aura', hero)) {
      const aura = document.createElement('div');
      aura.className = 'hero-aura';
      aura.innerHTML = `
        <span class="hero-aura-blob hero-aura-blob--1"></span>
        <span class="hero-aura-blob hero-aura-blob--2"></span>
        <span class="hero-aura-grid"></span>
      `;
      hero.prepend(aura);
    }
  }

  // ---------- 1. PAGE FADE-IN ----------
  function pageFadeIn() {
    document.body.classList.add('gsap-ready');
    gsap.fromTo(document.body, { opacity: 0 }, { opacity: 1, duration: 0.5, ease: 'power2.out' });
  }

  // ---------- 2. SCROLL PROGRESS BAR ----------
  function scrollProgress() {
    const fill = $('.scroll-progress-fill');
    if (!fill) return;
    gsap.to(fill, {
      scaleX: 1,
      ease: 'none',
      scrollTrigger: { trigger: document.body, start: 'top top', end: 'bottom bottom', scrub: 0.2 }
    });
  }

  // ---------- 3. CURSOR FOLLOWER ----------
  function cursorFollower() {
    const g = $('.cursor-glow');
    if (!g) return;
    let x = window.innerWidth / 2, y = window.innerHeight / 2;
    let tx = x, ty = y;
    window.addEventListener('mousemove', e => { tx = e.clientX; ty = e.clientY; });
    function loop() {
      x += (tx - x) * 0.12;
      y += (ty - y) * 0.12;
      g.style.transform = `translate3d(${x}px, ${y}px, 0) translate(-50%,-50%)`;
      requestAnimationFrame(loop);
    }
    loop();
    // Hover sobre links/botões aumenta a aura
    $$('a, button').forEach(el => {
      el.addEventListener('mouseenter', () => g.classList.add('cursor-glow--big'));
      el.addEventListener('mouseleave', () => g.classList.remove('cursor-glow--big'));
    });
  }

  // ---------- 4. HERO ENTRANCE ----------
  function heroEntrance() {
    const tag    = $('.servico-tag');
    const h1     = $('.servico-h1');
    const lead   = $('.servico-lead');
    const badge  = $('.servico-preco-badge');
    const bread  = $('.breadcrumb');

    if (h1) splitToWords(h1);

    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

    if (bread)  tl.from(bread,  { y: -10, opacity: 0, duration: 0.5 }, 0.05);
    if (tag)    tl.from(tag,    { y: 14,  opacity: 0, duration: 0.55 }, 0.15);
    if (h1) {
      tl.from(h1.querySelectorAll('.sw-word'), {
        yPercent: 110, opacity: 0, rotate: 2,
        duration: 0.9, stagger: 0.045, ease: 'expo.out'
      }, 0.2);
    }
    if (lead)   tl.from(lead,   { y: 18, opacity: 0, duration: 0.7 }, '-=0.45');
    if (badge)  tl.from(badge,  { scale: 0.85, opacity: 0, duration: 0.6, ease: 'back.out(2)' }, '-=0.35');

    // Aura: floats lentos
    const blob1 = $('.hero-aura-blob--1');
    const blob2 = $('.hero-aura-blob--2');
    if (blob1) gsap.to(blob1, { x: 60, y: 30, scale: 1.15, duration: 9, yoyo: true, repeat: -1, ease: 'sine.inOut' });
    if (blob2) gsap.to(blob2, { x: -40, y: -20, scale: 1.1, duration: 11, yoyo: true, repeat: -1, ease: 'sine.inOut' });

    // Parallax no mouse (apenas desktop)
    if (window.matchMedia('(pointer:fine)').matches) {
      window.addEventListener('mousemove', e => {
        const nx = (e.clientX / window.innerWidth  - 0.5);
        const ny = (e.clientY / window.innerHeight - 0.5);
        if (blob1) gsap.to(blob1, { x: 60 + nx * 40, y: 30 + ny * 30, duration: 1.5, overwrite: 'auto' });
        if (blob2) gsap.to(blob2, { x: -40 - nx * 30, y: -20 - ny * 20, duration: 1.5, overwrite: 'auto' });
      });
    }
  }

  // ---------- 5. SECTION HEADINGS (H2) reveal por palavras ----------
  function headingsReveal() {
    $$('.servico-body h2').forEach(h => {
      splitToWords(h);
      gsap.from(h.querySelectorAll('.sw-word'), {
        yPercent: 110, opacity: 0, skewY: 4,
        duration: 0.85, stagger: 0.05, ease: 'expo.out',
        scrollTrigger: { trigger: h, start: 'top 85%' }
      });
    });

    // Parágrafos de texto fade-up
    $$('.servico-body > p').forEach(p => {
      gsap.from(p, {
        y: 24, opacity: 0, duration: 0.7, ease: 'power3.out',
        scrollTrigger: { trigger: p, start: 'top 90%' }
      });
    });
  }

  // ---------- 6. PROCESSO (STEPS) com linha e count-up ----------
  function processSteps() {
    const wrap = $('.processo-steps');
    if (!wrap) return;
    wrap.classList.add('with-line');

    // Linha vertical que desenha conforme scroll
    if (!$('.processo-line', wrap)) {
      const line = document.createElement('div');
      line.className = 'processo-line';
      line.innerHTML = '<div class="processo-line-fill"></div>';
      wrap.appendChild(line);
    }

    gsap.to('.processo-line-fill', {
      scaleY: 1, ease: 'none',
      scrollTrigger: { trigger: wrap, start: 'top 75%', end: 'bottom 70%', scrub: 0.5 }
    });

    $$('.step-item', wrap).forEach((item, i) => {
      const num = $('.step-num', item);
      const content = $('.step-content', item);

      // Entrada do item
      gsap.from(item, {
        x: -36, opacity: 0, duration: 0.75, ease: 'power3.out',
        scrollTrigger: { trigger: item, start: 'top 85%' }
      });

      // Count-up do número
      if (num) {
        const target = parseInt(num.textContent.replace(/\D/g, ''), 10) || (i + 1);
        const orig = num.textContent;
        ScrollTrigger.create({
          trigger: item, start: 'top 80%', once: true,
          onEnter: () => {
            const obj = { v: 0 };
            gsap.to(obj, {
              v: target, duration: 0.9, ease: 'power2.out',
              onUpdate: () => { num.textContent = String(Math.round(obj.v)).padStart(orig.length, '0'); }
            });
          }
        });
      }

      // Pequeno realce no hover
      item.addEventListener('mouseenter', () => gsap.to(item, { x: 6, duration: 0.4, ease: 'power2.out' }));
      item.addEventListener('mouseleave', () => gsap.to(item, { x: 0, duration: 0.4, ease: 'power2.out' }));
    });
  }

  // ---------- 7. TECH PILLS bouncy ----------
  function techPills() {
    const grid = $('.tech-grid');
    if (!grid) return;
    gsap.from(grid.querySelectorAll('.tech-pill'), {
      y: 20, scale: 0.8, opacity: 0, rotate: -3,
      duration: 0.55, ease: 'back.out(1.8)', stagger: 0.06,
      scrollTrigger: { trigger: grid, start: 'top 85%' }
    });

    // hover: levitar
    $$('.tech-pill', grid).forEach(p => {
      p.addEventListener('mouseenter', () => gsap.to(p, { y: -4, scale: 1.04, duration: 0.25, ease: 'power2.out' }));
      p.addEventListener('mouseleave', () => gsap.to(p, { y: 0,  scale: 1,    duration: 0.3,  ease: 'power2.out' }));
    });
  }

  // ---------- 8. BENEFITS com checkmark draw ----------
  function benefits() {
    const list = $('.benefits-list');
    if (!list) return;

    // Substitui o ✓ por SVG animável
    $$('.benefit-icon', list).forEach(icon => {
      if (icon.querySelector('svg')) return;
      icon.innerHTML = '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12l5 5L20 6" /></svg>';
    });

    $$('.benefit-item', list).forEach((item, i) => {
      const path = item.querySelector('svg path');
      if (path) {
        const len = path.getTotalLength();
        path.style.strokeDasharray = len;
        path.style.strokeDashoffset = len;
      }
      gsap.from(item, {
        x: -20, opacity: 0, duration: 0.55, ease: 'power3.out',
        scrollTrigger: { trigger: item, start: 'top 90%' }
      });
      if (path) {
        gsap.to(path, {
          strokeDashoffset: 0, duration: 0.6, ease: 'power2.inOut', delay: 0.1,
          scrollTrigger: { trigger: item, start: 'top 88%' }
        });
      }
    });
  }

  // ---------- 9. FAQ smooth height (sobrepõe o CSS-only) ----------
  function faqSmooth() {
    const items = $$('.faq-item');
    if (!items.length) return;

    items.forEach(item => {
      const btn = $('.faq-question', item);
      const ans = $('.faq-answer', item);
      if (!btn || !ans) return;

      // Estado inicial via GSAP — neutralizamos max-height do CSS para tomar controle total
      gsap.set(ans, { maxHeight: 'none', height: 0, opacity: 0, overflow: 'hidden', paddingTop: 0, paddingBottom: 0 });

      // Substitui handler CSS
      btn.addEventListener('click', e => {
        e.stopImmediatePropagation();
        const isOpen = item.classList.contains('open');

        // Fecha os outros
        items.forEach(other => {
          if (other !== item && other.classList.contains('open')) {
            const oAns = $('.faq-answer', other);
            other.classList.remove('open');
            $('.faq-question', other).setAttribute('aria-expanded', 'false');
            gsap.to(oAns, { height: 0, opacity: 0, paddingTop: 0, paddingBottom: 0, duration: 0.4, ease: 'power3.inOut' });
          }
        });

        if (isOpen) {
          item.classList.remove('open');
          btn.setAttribute('aria-expanded', 'false');
          gsap.to(ans, { height: 0, opacity: 0, paddingTop: 0, paddingBottom: 0, duration: 0.4, ease: 'power3.inOut' });
        } else {
          item.classList.add('open');
          btn.setAttribute('aria-expanded', 'true');
          // Medir altura natural — garantimos maxHeight: none antes
          gsap.set(ans, { maxHeight: 'none', height: 'auto', paddingTop: 0, paddingBottom: 18 });
          const h = ans.offsetHeight;
          gsap.fromTo(ans,
            { maxHeight: 'none', height: 0, opacity: 0, paddingTop: 0, paddingBottom: 0 },
            { maxHeight: 'none', height: h, opacity: 1, paddingTop: 0, paddingBottom: 18, duration: 0.5, ease: 'power3.out' }
          );
        }
      });

      // Reveal de entrada
      gsap.from(item, {
        y: 16, opacity: 0, duration: 0.55, ease: 'power3.out',
        scrollTrigger: { trigger: item, start: 'top 90%' }
      });
    });
  }

  // ---------- 10. CTA BLOCO com glow parallax + magnetic button ----------
  function ctaBlock() {
    const cta = $('.servico-cta');
    if (!cta) return;

    // Glow que segue mouse
    if (!$('.cta-glow', cta)) {
      const glow = document.createElement('div');
      glow.className = 'cta-glow';
      cta.prepend(glow);
    }
    const glow = $('.cta-glow', cta);

    cta.addEventListener('mousemove', e => {
      const r = cta.getBoundingClientRect();
      const px = ((e.clientX - r.left) / r.width)  * 100;
      const py = ((e.clientY - r.top)  / r.height) * 100;
      glow.style.background = `radial-gradient(circle at ${px}% ${py}%, rgba(124,58,237,0.35), transparent 60%)`;
    });

    // Entrada
    gsap.from(cta, {
      y: 50, opacity: 0, scale: 0.97, duration: 0.85, ease: 'power3.out',
      scrollTrigger: { trigger: cta, start: 'top 85%' }
    });

    // Magnetic effect nos botões primary/ghost dentro do CTA
    $$('.btn-primary, .btn-ghost', cta).forEach(btn => {
      btn.addEventListener('mousemove', e => {
        const r = btn.getBoundingClientRect();
        const dx = e.clientX - (r.left + r.width / 2);
        const dy = e.clientY - (r.top + r.height / 2);
        gsap.to(btn, { x: dx * 0.25, y: dy * 0.4, duration: 0.4, ease: 'power3.out' });
      });
      btn.addEventListener('mouseleave', () => {
        gsap.to(btn, { x: 0, y: 0, duration: 0.6, ease: 'elastic.out(1, 0.4)' });
      });
    });
  }

  // ---------- 11. RELATED CARDS 3D tilt + stagger ----------
  function relatedCards() {
    const grid = $('.relacionados-grid');
    if (!grid) return;

    gsap.from(grid.querySelectorAll('.relacionado-card'), {
      y: 28, opacity: 0, duration: 0.65, ease: 'power3.out', stagger: 0.08,
      scrollTrigger: { trigger: grid, start: 'top 88%' }
    });

    $$('.relacionado-card', grid).forEach(card => {
      card.addEventListener('mousemove', e => {
        const r = card.getBoundingClientRect();
        const nx = ((e.clientX - r.left) / r.width  - 0.5);
        const ny = ((e.clientY - r.top)  / r.height - 0.5);
        gsap.to(card, {
          rotateY: nx * 8, rotateX: -ny * 8,
          y: -4, duration: 0.4, ease: 'power2.out',
          transformPerspective: 800, transformOrigin: 'center'
        });
      });
      card.addEventListener('mouseleave', () => {
        gsap.to(card, { rotateY: 0, rotateX: 0, y: 0, duration: 0.6, ease: 'power3.out' });
      });
    });
  }

  // ---------- 12. NAV scrolled state ----------
  function navScroll() {
    const nav = $('#main-nav');
    if (!nav) return;
    ScrollTrigger.create({
      start: 40, end: 99999,
      onUpdate: self => nav.classList.toggle('scrolled', self.scroll() > 40),
      onLeaveBack: () => nav.classList.remove('scrolled')
    });
    // Esconder ao descer rápido, mostrar ao subir
    let lastY = 0;
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      if (Math.abs(y - lastY) < 6) return;
      if (y > lastY && y > 200) nav.classList.add('nav-hidden');
      else nav.classList.remove('nav-hidden');
      lastY = y;
    }, { passive: true });
  }

  // ---------- 13. FOOTER reveal ----------
  function footerReveal() {
    const f = $('footer.site-footer');
    if (!f) return;
    gsap.from(f.querySelectorAll('.footer-brand, .footer-col'), {
      y: 24, opacity: 0, duration: 0.65, stagger: 0.08, ease: 'power3.out',
      scrollTrigger: { trigger: f, start: 'top 90%' }
    });
  }

  // ---------- 14. WHATSAPP FLOAT pulse mais vivo + entrada ----------
  function waFloat() {
    const wa = $('.wa-float');
    if (!wa) return;
    gsap.from(wa, { scale: 0, rotation: -180, duration: 0.9, ease: 'back.out(2)', delay: 1.2 });
  }

  // ---------- INIT ----------
  function init() {
    injectChrome();
    pageFadeIn();
    if (REDUCED) {
      // Versão sem animações fortes: apenas chrome
      $$('.sw-word').forEach(w => gsap.set(w, { clearProps: 'all' }));
      navScroll();
      faqSmooth();
      return;
    }
    scrollProgress();
    cursorFollower();
    heroEntrance();
    headingsReveal();
    processSteps();
    techPills();
    benefits();
    faqSmooth();
    ctaBlock();
    relatedCards();
    navScroll();
    footerReveal();
    waFloat();

    // Refresh ScrollTrigger após carregamento de fonts
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => ScrollTrigger.refresh());
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
