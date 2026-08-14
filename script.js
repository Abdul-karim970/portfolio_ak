/**
 * Portfolio - Scroll animations, header behavior, scroll-to-top
 */

document.addEventListener("DOMContentLoaded", () => {
  initHeader();
  initReveal();
  initConfidentialAnimation();
  initScrollTop();
  initSmoothScroll();
  initMobileMenu();
  initContactForm();
});

/**
 * Contact form: opens mailto with pre-filled data
 */
function initContactForm() {
  const form = document.getElementById("contactForm");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const name = document.getElementById("contactName").value.trim();
    const email = document.getElementById("contactEmail").value.trim();
    const subject = document.getElementById("contactSubject").value.trim();
    const message = document.getElementById("contactMessage").value.trim();

    const mailtoSubject = subject ? encodeURIComponent(subject) : encodeURIComponent("Portfolio Contact");
    const mailtoBody = encodeURIComponent(
      `Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`
    );
    const mailtoUrl = `mailto:abdulkarim3974@gmail.com?subject=${mailtoSubject}&body=${mailtoBody}`;

    window.location.href = mailtoUrl;
  });
}

function initMobileMenu() {
  const btn = document.getElementById("menuBtn");
  const nav = document.querySelector(".header__nav");
  if (!btn || !nav) return;

  btn.addEventListener("click", () => {
    btn.classList.toggle("active");
    nav.classList.toggle("open");
    document.body.style.overflow = nav.classList.contains("open") ? "hidden" : "";
  });

  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      btn.classList.remove("active");
      nav.classList.remove("open");
      document.body.style.overflow = "";
    });
  });
}

/**
 * Header: add scrolled class on scroll
 */
function initHeader() {
  const header = document.getElementById("header");
  if (!header) return;

  const handleScroll = () => {
    if (window.scrollY > 50) {
      header.classList.add("scrolled");
    } else {
      header.classList.remove("scrolled");
    }
  };

  window.addEventListener("scroll", handleScroll, { passive: true });
}

/**
 * Reveal animations via IntersectionObserver
 */
function initReveal() {
  const reveals = document.querySelectorAll(".reveal");
  if (!reveals.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
        }
      });
    },
    {
      threshold: 0.1,
      rootMargin: "0px 0px 0px 0px",
    }
  );

  reveals.forEach((el) => observer.observe(el));
}

/**
 * Animated gradient border for confidential box
 */
function initConfidentialAnimation() {
  const confidentialBox = document.querySelector(".confidential__box");
  if (!confidentialBox) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
        } else {
          entry.target.classList.remove("visible");
        }
      });
    },
    {
      threshold: 0.3,
    }
  );

  observer.observe(confidentialBox);
}

/**
 * Scroll to top button
 */
function initScrollTop() {
  const btn = document.getElementById("scrollTop");
  if (!btn) return;

  const toggleVisibility = () => {
    if (window.scrollY > 400) {
      btn.classList.add("visible");
    } else {
      btn.classList.remove("visible");
    }
  };

  btn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  window.addEventListener("scroll", toggleVisibility, { passive: true });
}

/**
 * Smooth scroll for anchor links
 */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const href = this.getAttribute("href");
      if (href === "#") return;

      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
}
