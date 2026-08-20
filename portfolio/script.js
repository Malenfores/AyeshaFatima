// =========================================================
// Ayesha Fatima — Portfolio scripts
// =========================================================

document.addEventListener("DOMContentLoaded", () => {
  setFooterYear();
  setupNavToggle();
  setupSmoothNavClose();
  setupScrollReveal();
  setupTerminalTypewriter();
});

// Footer year -------------------------------------------------
function setFooterYear() {
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();
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

// Reveal sections/cards on scroll --------------------------------
function setupScrollReveal() {
  const targets = document.querySelectorAll(
    ".section, .card, .cert, .timeline__item, .stat"
  );
  targets.forEach((el) => el.classList.add("reveal"));

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

// Hero terminal typewriter ----------------------------------------
function setupTerminalTypewriter() {
  const body = document.getElementById("terminalBody");
  if (!body) return;

  const script = [
    { type: "prompt", text: "whoami" },
    { type: "out", text: "Ayesha Fatima" },
    { type: "prompt", text: "cat role.txt" },
    { type: "out", text: "BS Computer Science Student" },
    { type: "prompt", text: "cat status.txt" },
    { type: "out", text: "Open to remote internships & junior roles" },
    { type: "prompt", text: "ls focus_areas/" },
    { type: "out", text: "web-development  data-entry  data-analysis" },
    { type: "prompt", text: "cat education.txt" },
    { type: "out", text: "BS CS — UCP Lahore | 6 sem | CGPA 3.81" },
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
      window.setTimeout(typeNextChar, line.type === "prompt" ? 32 : 14);
    } else {
      lineIndex++;
      charIndex = 0;
      window.setTimeout(typeNextChar, line.type === "prompt" ? 150 : 380);
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
