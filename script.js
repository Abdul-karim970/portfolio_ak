/**
 * Portfolio v3 — Light Real-Glass
 * Parallax background layers, nav glider, featured slideshows,
 * counters, typing rotator, tilt, filters, contact form.
 */

(() => {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  document.addEventListener("DOMContentLoaded", () => {
    initHeader();
    initProgress();
    initParallax();
    initReveal();
    initCounters();
    initTyping();
    initSlideshows();
    initFilters();
    initTilt();
    initMobileMenu();
    initActiveNav();
    initContactForm();
    initScrollTop();
    initYear();
    initHeroTilt();
    initTheme();
  });

  /* ---------- Theme toggle (light / dark space glass) ---------- */
  function initTheme() {
    var btn = document.getElementById("themeToggle");
    var root = document.documentElement;
    try {
      if (localStorage.getItem("ak-theme") === "dark") root.classList.add("dark");
    } catch (e) { /* private mode */ }

    function sync() {
      var dark = root.classList.contains("dark");
      if (btn) btn.setAttribute("aria-pressed", dark ? "true" : "false");
    }

    if (btn) {
      btn.addEventListener("click", function () {
        root.classList.toggle("dark");
        try {
          localStorage.setItem("ak-theme", root.classList.contains("dark") ? "dark" : "light");
        } catch (e) { /* private mode */ }
        sync();
      });
    }
    sync();
  }

  /* ---------- Header glass state ---------- */
  function initHeader() {
    const header = document.getElementById("header");
    if (!header) return;
    const update = () => header.classList.toggle("scrolled", window.scrollY > 40);
    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  /* ---------- Scroll progress bar ---------- */
  function initProgress() {
    const bar = document.getElementById("progressBar");
    if (!bar) return;
    const update = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = max > 0 ? `${(window.scrollY / max) * 100}%` : "0%";
    };
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
  }

  /* ---------- Parallax background layers (pointer + scroll) ---------- */
  function initParallax() {
    if (reducedMotion || !finePointer) return;
    const layers = Array.from(document.querySelectorAll(".plx[data-depth]"));
    if (!layers.length) return;

    let tx = 0, ty = 0;   // pointer target, normalized -1..1
    let cx = 0, cy = 0;   // current (lerped)
    let lastSy = -1;

    window.addEventListener("pointermove", (e) => {
      tx = (e.clientX / window.innerWidth - 0.5) * 2;
      ty = (e.clientY / window.innerHeight - 0.5) * 2;
    }, { passive: true });

    const frame = () => {
      const sy = window.scrollY;
      cx += (tx - cx) * 0.055;
      cy += (ty - cy) * 0.055;
      if (Math.abs(cx - tx) > 0.0005 || Math.abs(cy - ty) > 0.0005 || sy !== lastSy) {
        layers.forEach((layer) => {
          const d = parseFloat(layer.dataset.depth) || 0;
          layer.style.transform =
            `translate3d(${(cx * d).toFixed(2)}px, ${(cy * d + sy * 0.0009 * d).toFixed(2)}px, 0)`;
        });
        lastSy = sy;
      }
      requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  }

  /* ---------- Reveal on scroll ---------- */
  function initReveal() {
    const els = document.querySelectorAll("[data-reveal]");
    if (!els.length) return;

    if (reducedMotion || !("IntersectionObserver" in window)) {
      els.forEach((el) => el.classList.add("in"));
      return;
    }

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    els.forEach((el) => io.observe(el));
  }

  /* ---------- Animated counters ---------- */
  function initCounters() {
    const counters = document.querySelectorAll("[data-count]");
    if (!counters.length) return;

    const animate = (el) => {
      const target = parseInt(el.dataset.count, 10) || 0;
      if (reducedMotion) {
        el.textContent = target;
        return;
      }
      const duration = 1400;
      const start = performance.now();
      const tick = (now) => {
        const p = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased);
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };

    if (!("IntersectionObserver" in window) || reducedMotion) {
      counters.forEach(animate);
      return;
    }

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animate(entry.target);
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.6 }
    );
    counters.forEach((el) => io.observe(el));
  }

  /* ---------- Typing rotator ---------- */
  function initTyping() {
    const el = document.getElementById("typing");
    if (!el) return;

    const roles = [
      "Senior Flutter Developer",
      "AI-Powered App Development",
      "iOS & Android · One Codebase",
      "40+ Apps Published",
    ];

    if (reducedMotion) {
      el.textContent = roles[0];
      return;
    }

    let roleIndex = 0;
    let charIndex = roles[0].length;
    let deleting = false;

    const tick = () => {
      const current = roles[roleIndex];

      if (!deleting) {
        charIndex++;
        if (charIndex >= current.length) {
          charIndex = current.length;
          el.textContent = current;
          deleting = true;
          setTimeout(tick, 2100);
          return;
        }
      } else {
        charIndex--;
        if (charIndex <= 0) {
          charIndex = 0;
          deleting = false;
          roleIndex = (roleIndex + 1) % roles.length;
        }
      }

      el.textContent = roles[roleIndex].slice(0, charIndex);
      setTimeout(tick, deleting ? 28 : 62);
    };

    setTimeout(tick, 1600);
  }

  /* ---------- Featured slideshows ---------- */
  function initSlideshows() {
    /* phones: no autoplay (battery + jank); manual arrows/dots still work */
    var noAutoplay = window.matchMedia("(max-width: 768px)").matches;
    document.querySelectorAll(".showcase").forEach((showcase) => {
      const slides = Array.from(showcase.querySelectorAll(".showcase__slide"));
      const dotsWrap = showcase.querySelector(".showcase__dots");
      const prevBtn = showcase.querySelector(".showcase__arrow--prev");
      const nextBtn = showcase.querySelector(".showcase__arrow--next");
      const frame = showcase.querySelector(".showcase__frame");
      if (slides.length < 1 || !dotsWrap) return;

      const interval = parseInt(showcase.dataset.interval, 10) || 4400;
      let index = 0;
      let timer = null;

      const dots = slides.map((_, i) => {
        const dot = document.createElement("button");
        dot.type = "button";
        dot.className = "showcase__dot";
        dot.setAttribute("aria-label", `Show slide ${i + 1}`);
        dot.style.setProperty("--dur", `${interval}ms`);
        dot.appendChild(document.createElement("i"));
        dot.addEventListener("click", () => {
          show(i);
          startTimer();
        });
        dotsWrap.appendChild(dot);
        return dot;
      });

      function show(i) {
        index = (i + slides.length) % slides.length;
        slides.forEach((s, n) => s.classList.toggle("is-active", n === index));
        dots.forEach((d, n) => {
          d.classList.toggle("is-active", n === index);
          d.classList.toggle("is-done", n < index);
        });
      }

      function startTimer() {
        stopTimer();
        if (reducedMotion || noAutoplay || slides.length < 2) return;
        timer = setInterval(() => show(index + 1), interval);
      }
      function stopTimer() {
        if (timer) clearInterval(timer);
        timer = null;
      }
      function pause() {
        stopTimer();
        showcase.classList.add("is-paused");
      }
      function resume() {
        showcase.classList.remove("is-paused");
        startTimer();
      }

      if (prevBtn) prevBtn.addEventListener("click", () => { show(index - 1); startTimer(); });
      if (nextBtn) nextBtn.addEventListener("click", () => { show(index + 1); startTimer(); });

      if (frame) {
        frame.addEventListener("mouseenter", pause);
        frame.addEventListener("mouseleave", resume);
        frame.addEventListener("focusin", pause);
        frame.addEventListener("focusout", resume);
      }

      // Only run autoplay while visible
      if ("IntersectionObserver" in window) {
        const io = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting) {
                showcase.classList.remove("is-paused");
                startTimer();
              } else {
                pause();
              }
            });
          },
          { threshold: 0.25 }
        );
        io.observe(frame || showcase);
      } else {
        startTimer();
      }

      show(0);
    });
  }

  /* ---------- Project filters ---------- */
  function initFilters() {
    const buttons = document.querySelectorAll(".filter");
    const cards = document.querySelectorAll("#projectsGrid .pcard");
    if (!buttons.length || !cards.length) return;

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        buttons.forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
        const filter = btn.dataset.filter;

        cards.forEach((card) => {
          const match = filter === "all" || card.dataset.cat === filter;
          card.classList.toggle("is-hidden", !match);
          if (match) {
            card.classList.remove("in");
            requestAnimationFrame(() =>
              requestAnimationFrame(() => card.classList.add("in"))
            );
          }
        });
      });
    });
  }

  /* ---------- Subtle 3D tilt + spotlight ---------- */
  function initTilt() {
    if (reducedMotion || !finePointer) return;

    document.querySelectorAll(".tilt").forEach((card) => {
      let raf = null;

      card.addEventListener("pointermove", (e) => {
        if (raf) return;
        raf = requestAnimationFrame(() => {
          const rect = card.getBoundingClientRect();
          const px = (e.clientX - rect.left) / rect.width;
          const py = (e.clientY - rect.top) / rect.height;
          card.style.setProperty("--ry", `${(px - 0.5) * 6}deg`);
          card.style.setProperty("--rx", `${(0.5 - py) * 6}deg`);
          card.style.setProperty("--mx", `${px * 100}%`);
          card.style.setProperty("--my", `${py * 100}%`);
          raf = null;
        });
      });

      card.addEventListener("pointerleave", () => {
        card.style.setProperty("--rx", "0deg");
        card.style.setProperty("--ry", "0deg");
      });
    });
  }

  /* ---------- Nav glider ---------- */
  function moveGlider(link) {
    const glider = document.querySelector(".nav-glider");
    if (!glider) return;
    if (!link) {
      glider.classList.remove("is-visible");
      return;
    }
    glider.style.width = `${link.offsetWidth}px`;
    glider.style.transform = `translateX(${link.offsetLeft}px)`;
    glider.classList.add("is-visible");
  }

  /* ---------- Mobile menu ---------- */
  function initMobileMenu() {
    const btn = document.getElementById("menuBtn");
    const nav = document.getElementById("navMenu");
    if (!btn || !nav) return;

    const close = () => {
      btn.classList.remove("active");
      nav.classList.remove("open");
      btn.setAttribute("aria-expanded", "false");
      document.body.style.overflow = "";
    };

    btn.addEventListener("click", () => {
      const open = !nav.classList.contains("open");
      btn.classList.toggle("active", open);
      nav.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", String(open));
      document.body.style.overflow = open ? "hidden" : "";
    });

    nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", close));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") close();
    });
    window.addEventListener("resize", () => {
      if (window.innerWidth > 860) close();
    });
  }

  /* ---------- Active nav link + glider ---------- */
  function initActiveNav() {
    const links = Array.from(document.querySelectorAll(".header__link[href^='#']"));
    if (!links.length) return;

    const map = new Map();
    links.forEach((link) => {
      const section = document.querySelector(link.getAttribute("href"));
      if (section) map.set(section, link);
    });
    const hero = document.querySelector(".hero");
    if (hero) map.set(hero, null); // sentinel: no link active at top

    if (!("IntersectionObserver" in window)) return;

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            links.forEach((l) => l.classList.remove("is-active"));
            const link = map.get(entry.target);
            if (link) {
              link.classList.add("is-active");
              moveGlider(link);
            } else {
              moveGlider(null);
            }
          }
        });
      },
      { rootMargin: "-40% 0px -55% 0px" }
    );
    map.forEach((_, section) => io.observe(section));

    // keep glider accurate after layout/font shifts
    const sync = () => moveGlider(document.querySelector(".header__link.is-active"));
    window.addEventListener("resize", sync);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(sync);
  }

  /* ---------- Contact form (mailto + toast) ---------- */
  function initContactForm() {
    const form = document.getElementById("contactForm");
    const toast = document.getElementById("formToast");
    if (!form) return;

    const showToast = (msg, isError = false) => {
      if (!toast) return;
      toast.textContent = msg;
      toast.classList.toggle("is-error", isError);
      toast.classList.add("is-visible");
      setTimeout(() => toast.classList.remove("is-visible"), 4200);
    };

    form.addEventListener("submit", (e) => {
      e.preventDefault();

      const name = document.getElementById("contactName").value.trim();
      const email = document.getElementById("contactEmail").value.trim();
      const subject = document.getElementById("contactSubject").value.trim();
      const message = document.getElementById("contactMessage").value.trim();

      if (!name || !message) {
        showToast("Please add your name and a short message.", true);
        return;
      }
      if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        showToast("That email address doesn't look right.", true);
        return;
      }

      const mailtoSubject = subject
        ? `Project inquiry — ${subject}`
        : "Project inquiry from portfolio";
      const mailtoBody = `Name: ${name}\nEmail: ${email || "—"}\nProject type: ${subject}\n\n${message}`;
      window.location.href = `mailto:abdulkarim3974@gmail.com?subject=${encodeURIComponent(
        mailtoSubject
      )}&body=${encodeURIComponent(mailtoBody)}`;

      showToast("Opening your mail app — talk soon!");
      form.reset();
    });
  }

  /* ---------- Scroll to top ---------- */
  function initScrollTop() {
    const btn = document.getElementById("scrollTop");
    if (!btn) return;

    window.addEventListener(
      "scroll",
      () => btn.classList.toggle("visible", window.scrollY > 500),
      { passive: true }
    );
    btn.addEventListener("click", () =>
      window.scrollTo({ top: 0, behavior: reducedMotion ? "auto" : "smooth" })
    );
  }

  /* ---------- Footer year ---------- */
  function initYear() {
    const el = document.getElementById("year");
    if (el) el.textContent = new Date().getFullYear();
  }

  /* ---------- Hero 3D tilt (multi-layer glass card) ---------- */
  function initHeroTilt() {
    var stage = document.querySelector(".hv-visual");
    if (!stage || reducedMotion || !finePointer) return;
    var card = stage.querySelector(".hv-card");
    if (!card) return;
    var back = card.querySelector(".hv-layer--back");
    var photo = card.querySelector(".hv-photo");
    var front = card.querySelector(".hv-layer--front");
    var raf = null, rx = 0, ry = 0, cy = 0, cx = 0;

    function apply() {
      raf = null;
      card.style.transform =
        "perspective(1100px) rotateX(" + rx.toFixed(2) + "deg) rotateY(" +
        ry.toFixed(2) + "deg) translateY(" + (cy * -12).toFixed(1) + "px)";
      /* depth parallax: back drifts opposite, photo center, front glass leads */
      if (back) back.style.translate = (cx * -7).toFixed(1) + "px " + (cy * -7).toFixed(1) + "px";
      if (photo) photo.style.translate = (cx * 5).toFixed(1) + "px " + (cy * 5).toFixed(1) + "px";
      if (front) front.style.translate = (cx * 14).toFixed(1) + "px " + (cy * 14).toFixed(1) + "px";
    }

    stage.addEventListener("pointermove", function (e) {
      var r = stage.getBoundingClientRect();
      cy = (e.clientY - r.top) / r.height - 0.5;
      cx = (e.clientX - r.left) / r.width - 0.5;
      ry = cx * 10;
      rx = -cy * 8;
      if (!raf) raf = requestAnimationFrame(apply);
    });
    stage.addEventListener("pointerleave", function () {
      rx = ry = cx = cy = 0;
      if (!raf) raf = requestAnimationFrame(apply);
    });
  }
})();
