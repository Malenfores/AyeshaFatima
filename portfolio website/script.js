// =========================================================
// Ayesha Fatima — Premium Portfolio v3 scripts
// =========================================================

document.addEventListener("DOMContentLoaded", () => {
  initLucideIcons();
  setFooterYear();
  setupThemeToggle();
  setupNavToggle();
  setupSmoothNavClose();
  setupActiveNav();
  setupScrollProgress();
  setupScrollReveal();
  setupTerminalTypewriter();
  setupStatCounters();
  setupLightbox();
  setupCvModal();
  setupBackToTop();
});

// Lucide icons ---------------------------------------------------
function initLucideIcons() {
  if (window.lucide && typeof window.lucide.createIcons === "function") {
    window.lucide.createIcons();
  }
}

// Footer year -------------------------------------------------
function setFooterYear() {
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();
}

// Theme toggle (light/dark, persisted) -----------------------------
function setupThemeToggle() {
  const toggle = document.getElementById("themeToggle");
  const root = document.documentElement;
  if (!toggle) return;

  toggle.addEventListener("click", () => {
    const current = root.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try {
      localStorage.setItem("af-theme", next);
    } catch (e) {
      /* localStorage unavailable — theme just won't persist */
    }
  });
}

// Mobile nav toggle ---------------------------------------------
function setupNavToggle() {
  const toggle = document.getElementById("navToggle");
  const menu = document.getElementById("navMenu");
  if (!toggle || !menu) return;

  toggle.addEventListener("click", () => {
    const isOpen = menu.classList.toggle("is-open");
    toggle.classList.toggle("is-open", isOpen);
    toggle.setAttribute("aria-expanded", String(isOpen));
  });
}

// Close mobile menu after a link is tapped -----------------------
function setupSmoothNavClose() {
  const menu = document.getElementById("navMenu");
  const toggle = document.getElementById("navToggle");
  if (!menu) return;

  menu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      menu.classList.remove("is-open");
      if (toggle) {
        toggle.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  });
}

// Active nav link on scroll ---------------------------------------
function setupActiveNav() {
  const links = document.querySelectorAll(".nav__link[data-section]");
  if (!links.length) return;

  const sections = Array.from(links)
    .map((link) => document.getElementById(link.dataset.section))
    .filter(Boolean);

  if (!("IntersectionObserver" in window) || !sections.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          links.forEach((link) => {
            link.classList.toggle("is-active", link.dataset.section === id);
          });
        }
      });
    },
    { rootMargin: "-40% 0px -50% 0px", threshold: 0 }
  );

  sections.forEach((section) => observer.observe(section));
}

// Scroll progress bar under the nav --------------------------------
function setupScrollProgress() {
  const bar = document.getElementById("navProgress");
  if (!bar) return;

  function update() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    bar.style.width = pct + "%";
  }

  window.addEventListener("scroll", update, { passive: true });
  update();
}

// Reveal sections/cards on scroll --------------------------------
function setupScrollReveal() {
  const targets = document.querySelectorAll(".reveal");

  if (!("IntersectionObserver" in window)) {
    targets.forEach((el) => el.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );

  targets.forEach((el) => observer.observe(el));
}

// Animated stat counters -------------------------------------------
function setupStatCounters() {
  const counters = document.querySelectorAll(".stat-card__num[data-count]");
  if (!counters.length) return;

  const animate = (el) => {
    const target = parseFloat(el.dataset.count);
    const isDecimal = el.dataset.decimal === "true";
    const duration = 1400;
    const start = performance.now();

    function tick(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = target * eased;
      el.textContent = isDecimal ? value.toFixed(2) : Math.round(value);
      if (progress < 1) {
        requestAnimationFrame(tick);
      } else {
        el.textContent = isDecimal ? target.toFixed(2) : target;
      }
    }
    requestAnimationFrame(tick);
  };

  if (!("IntersectionObserver" in window)) {
    counters.forEach(animate);
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animate(entry.target);
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.6 }
  );

  counters.forEach((el) => observer.observe(el));
}

// Lightbox for project screenshots ---------------------------------
function setupLightbox() {
  const lightbox = document.getElementById("lightbox");
  const lightboxImg = document.getElementById("lightboxImg");
  const closeBtn = document.getElementById("lightboxClose");
  const triggers = document.querySelectorAll("[data-lightbox-src]");
  if (!lightbox || !lightboxImg || !triggers.length) return;

  function openLightbox(src, alt) {
    lightboxImg.src = src;
    lightboxImg.alt = alt || "";
    lightbox.classList.add("is-open");
    lightbox.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeLightbox() {
    lightbox.classList.remove("is-open");
    lightbox.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  triggers.forEach((trigger) => {
    trigger.addEventListener("click", () => {
      openLightbox(trigger.dataset.lightboxSrc, trigger.dataset.lightboxAlt);
    });
  });

  closeBtn.addEventListener("click", closeLightbox);
  lightbox.addEventListener("click", (e) => {
    if (e.target === lightbox) closeLightbox();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && lightbox.classList.contains("is-open")) closeLightbox();
  });
}

// CV preview modal --------------------------------------------------
function setupCvModal() {
  const modal = document.getElementById("cvModal");
  const frame = document.getElementById("cvModalFrame");
  const closeBtn = document.getElementById("cvModalClose");
  const triggers = document.querySelectorAll("[data-cv-view]");
  if (!modal || !frame || !triggers.length) return;

  const cvSrc = "assets/Ayesha_Fatima_CV.pdf";

  function openModal() {
    if (!frame.src) frame.src = cvSrc;
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  triggers.forEach((trigger) => {
    trigger.addEventListener("click", openModal);
  });

  closeBtn.addEventListener("click", closeModal);
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("is-open")) closeModal();
  });
}

// Back to top button -------------------------------------------------
function setupBackToTop() {
  const btn = document.getElementById("backToTop");
  if (!btn) return;

  window.addEventListener(
    "scroll",
    () => {
      btn.classList.toggle("is-visible", window.scrollY > 500);
    },
    { passive: true }
  );

  btn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

// Hero terminal typewriter ----------------------------------------
function setupTerminalTypewriter() {
  const body = document.getElementById("terminalBody");
  if (!body) return;

  const script = [
    { type: "prompt", text: "whoami" },
    { type: "out", text: "Ayesha Fatima" },
    { type: "prompt", text: "cat role.txt" },
    { type: "out", text: "BS Computer Science Student" },
    { type: "prompt", text: "cat cgpa.txt" },
    { type: "out", text: "3.84 / 4.00" },
    { type: "prompt", text: "cat status.txt" },
    { type: "out", text: "Open to internships & remote roles" },
    { type: "prompt", text: "ls focus_areas/" },
    { type: "out", text: "python  web-development  data-entry" },
  ];

  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  if (prefersReducedMotion) {
    renderTerminalInstant(body, script);
    return;
  }

  renderTerminalTyped(body, script);
}

function renderTerminalInstant(body, script) {
  const frag = document.createDocumentFragment();
  script.forEach((line) => {
    const p = document.createElement("p");
    p.style.margin = "0";
    if (line.type === "prompt") {
      p.innerHTML = `<span class="line-prompt">$</span> ${escapeHtml(line.text)}`;
    } else {
      p.innerHTML = `<span class="line-out">${escapeHtml(line.text)}</span>`;
    }
    frag.appendChild(p);
  });
  body.appendChild(frag);
}

function renderTerminalTyped(body, script) {
  let lineIndex = 0;
  let charIndex = 0;
  let currentP = null;

  function typeNextChar() {
    if (lineIndex >= script.length) {
      appendCursorLine(body);
      return;
    }

    const line = script[lineIndex];
    const prefix = line.type === "prompt" ? "$ " : "";
    const fullText = prefix + line.text;

    if (charIndex === 0) {
      currentP = document.createElement("p");
      currentP.style.margin = "0";
      currentP.className = line.type === "prompt" ? "line-prompt" : "line-out";
      body.appendChild(currentP);
    }

    charIndex++;
    currentP.textContent = fullText.slice(0, charIndex);

    if (charIndex < fullText.length) {
      window.setTimeout(typeNextChar, line.type === "prompt" ? 30 : 13);
    } else {
      lineIndex++;
      charIndex = 0;
      window.setTimeout(typeNextChar, line.type === "prompt" ? 140 : 340);
    }
  }

  typeNextChar();
}

function appendCursorLine(body) {
  const p = document.createElement("p");
  p.style.margin = "0";
  p.innerHTML = `<span class="line-prompt">$</span> <span class="terminal__cursor" aria-hidden="true"></span>`;
  body.appendChild(p);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
