/* ============================================
   POP Assistant — Official Website JS
   Animations & Interactions
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
  createStars();
  initMouseLight();
  initNavbar();
  initMobileMenu();
  initRevealAnimations();
  initSmoothScroll();
});

// ---------- Stars ----------
function createStars() {
  const container = document.getElementById('starfield');
  if (!container) return;
  const count = 120;
  const frag = document.createDocumentFragment();
  for (let i = 0; i < count; i++) {
    const s = document.createElement('div');
    s.className = 'star';
    s.style.cssText = `left:${Math.random()*100}%;top:${Math.random()*100}%;--d:${2+Math.random()*4}s;--dl:${Math.random()*5}s;width:${1+Math.random()*2}px;height:${1+Math.random()*2}px`;
    frag.appendChild(s);
  }
  container.appendChild(frag);
}

// ---------- Mouse Light ----------
function initMouseLight() {
  const light = document.getElementById('mouse-light');
  if (!light) return;
  let mx = -500, my = -500, cx = -500, cy = -500;
  document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });
  document.addEventListener('mouseleave', () => light.style.opacity = '0');
  document.addEventListener('mouseenter', () => light.style.opacity = '1');
  function anim() {
    cx += (mx - cx) * 0.07;
    cy += (my - cy) * 0.07;
    light.style.left = cx + 'px';
    light.style.top = cy + 'px';
    requestAnimationFrame(anim);
  }
  anim();
}

// ---------- Navbar ----------
function initNavbar() {
  const nav = document.getElementById('navbar');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 50);
  });
}

// ---------- Mobile Menu ----------
function initMobileMenu() {
  const toggle = document.getElementById('nav-toggle');
  const links = document.getElementById('nav-links');
  if (!toggle || !links) return;
  toggle.addEventListener('click', () => links.classList.toggle('open'));
  links.querySelectorAll('a').forEach(a => a.addEventListener('click', () => links.classList.remove('open')));
}

// ---------- Reveal on Scroll ----------
function initRevealAnimations() {
  const reveals = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  reveals.forEach(el => observer.observe(el));
}

// ---------- Smooth Scroll ----------
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      e.preventDefault();
      const href = anchor.getAttribute('href');
      if (!href || href === '#') return;
      const target = document.querySelector(href);
      if (target) target.scrollIntoView({ behavior: 'smooth' });
    });
  });
}