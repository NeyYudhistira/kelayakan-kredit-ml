/**
 * KreditSmart — script.js
 * Supports: index.html & result.html
 */

document.addEventListener("DOMContentLoaded", function () {

  /* ── 1. SMOOTH SCROLL untuk nav-links ──────────── */
  document.querySelectorAll(".nav-links a[href^='#']").forEach(function (link) {
    link.addEventListener("click", function (e) {
      const href = this.getAttribute("href");
      if (href === "#") return;
      const target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  /* ── 2. SMOOTH SCROLL pada halaman result (/#section) ── */
  document.querySelectorAll("a[href^='/#']").forEach(function (anchor) {
    anchor.addEventListener("click", function (e) {
      const hash = this.getAttribute("href");
      if (!hash || hash === "/#") return;
      e.preventDefault();
      window.location.href = hash;
    });
  });

  /* ── 3. ACTIVE NAV LINK berdasarkan posisi scroll ── */
  const sections = document.querySelectorAll("section[id], .hero-section[id]");
  const navLinks = document.querySelectorAll(".nav-links a");

  if (sections.length && navLinks.length) {
    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            navLinks.forEach(function (link) {
              link.classList.remove("active");
              if (link.getAttribute("href") === "#" + entry.target.id) {
                link.classList.add("active");
              }
            });
          }
        });
      },
      { rootMargin: "-30% 0px -60% 0px", threshold: 0 }
    );

    sections.forEach(function (sec) { observer.observe(sec); });
  }

  /* ── 4. ANIMASI CONFIDENCE BAR (result page) ─────── */
  var fills = document.querySelectorAll(".confidence-fill");
  if (fills.length) {
    fills.forEach(function (fill) {
      var target = fill.style.width;
      fill.style.width = "0%";
      setTimeout(function () {
        fill.style.width = target;
      }, 300);
    });
  }

  /* ── 5. FORMAT INPUT ANGKA dengan pemisah ribuan ─── */
  var numberInputs = document.querySelectorAll(
    "input[name='pendapatan_tahunan'], input[name='aset_tabungan'], " +
    "input[name='hutang_saat_ini'], input[name='jumlah_pinjaman']"
  );

  numberInputs.forEach(function (input) {
    /* Tampilkan hint di placeholder saat fokus */
    input.addEventListener("focus", function () {
      this.dataset.origPlaceholder = this.placeholder;
    });

    input.addEventListener("blur", function () {
      if (this.dataset.origPlaceholder) {
        this.placeholder = this.dataset.origPlaceholder;
      }
    });
  });

  /* ── 6. FORM VALIDATION FEEDBACK ─────────────────── */
  var form = document.querySelector(".predict-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      var fields = form.querySelectorAll("input[required], select[required]");
      var firstError = null;

      fields.forEach(function (field) {
        field.classList.remove("field-error");
        if (!field.value.trim()) {
          field.classList.add("field-error");
          if (!firstError) firstError = field;
        }
      });

      if (firstError) {
        e.preventDefault();
        firstError.scrollIntoView({ behavior: "smooth", block: "center" });
        firstError.focus();
      } else {
        /* Tampilkan loading state pada tombol submit */
        var submitBtn = form.querySelector("button[type='submit']");
        if (submitBtn) {
          submitBtn.textContent = "⏳ Menganalisis...";
          submitBtn.disabled = true;
        }
      }
    });

    /* Hapus error class saat user mulai mengisi */
    form.querySelectorAll("input, select").forEach(function (field) {
      field.addEventListener("input", function () {
        this.classList.remove("field-error");
      });
    });
  }

  /* ── 7. SCROLL-REVEAL ANIMATION ──────────────────── */
  var revealTargets = document.querySelectorAll(
    ".card, .tech-card, .form-field, .result-card, .input-item"
  );

  if ("IntersectionObserver" in window && revealTargets.length) {
    revealTargets.forEach(function (el) {
      el.style.opacity = "0";
      el.style.transform = "translateY(16px)";
      el.style.transition = "opacity 0.4s ease, transform 0.4s ease";
    });

    var revealObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.style.opacity = "1";
            entry.target.style.transform = "translateY(0)";
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 }
    );

    revealTargets.forEach(function (el) { revealObserver.observe(el); });
  }

});


/* ── CSS tambahan untuk field-error (inject via JS) ── */
(function () {
  var style = document.createElement("style");
  style.textContent = [
    ".field-error {",
    "  border-color: #dc2626 !important;",
    "  box-shadow: 0 0 0 3px rgba(220,38,38,0.12) !important;",
    "  background-color: #fff1f2 !important;",
    "}",
    ".nav-links a.active {",
    "  color: #2563eb;",
    "  background-color: #eff6ff;",
    "}"
  ].join("\n");
  document.head.appendChild(style);
})();
