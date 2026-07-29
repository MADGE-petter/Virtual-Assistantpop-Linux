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

// ---------- Electric Effects ----------
function initElectricEffects() {
  const overlay = document.getElementById('electric-overlay');
  if (!overlay) return;

  function createFlash() {
    const flash = document.createElement('div');
    flash.className = 'electric-flash';
    
    // Random position and rotation
    const x = Math.random() * window.innerWidth;
    const y = Math.random() * window.innerHeight;
    const rot = Math.random() * 360;
    
    flash.style.left = x + 'px';
    flash.style.top = y + 'px';
    flash.style.transform = `rotate(${rot}deg)`;
    
    document.body.appendChild(flash);
    
    // Animation sequence
    setTimeout(() => {
      flash.style.opacity = '0.8';
      flash.style.transition = 'opacity 0.1s ease';
    }, 10);
    
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transition = 'opacity 0.4s ease';
      setTimeout(() => flash.remove(), 500);
    }, 150);
  }

  // Randomly trigger flashes
  function loop() {
    const delay = 3000 + Math.random() * 7000;
    setTimeout(() => {
      createFlash();
      loop();
    }, delay);
  }
  loop();
}

// Update DOMContentLoaded to include new effect
const originalDOMContentLoaded = document.addEventListener('DOMContentLoaded', () => {
  createStars();
  initMouseLight();
  initNavbar();
  initMobileMenu();
  initRevealAnimations();
  initSmoothScroll();
});

// Since we can't easily wrap the existing listener in this tool, 
// I will add a separate call or the user can just add it to the main list.
// Actually, I'll just add the function and a call to it.
document.addEventListener('DOMContentLoaded', initElectricEffects);