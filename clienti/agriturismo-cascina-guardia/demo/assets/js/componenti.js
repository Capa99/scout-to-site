/* Componenti comuni a tutte le demo: menu mobile, animazioni all'ingresso,
   filtri della galleria, lightbox con swipe, mappa caricata su richiesta. */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.add("js");
  var riduci = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Menu mobile */
  var toggle = document.querySelector(".menu-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var aperto = document.body.classList.toggle("menu-open");
      toggle.setAttribute("aria-expanded", aperto ? "true" : "false");
    });
    document.querySelectorAll(".nav a").forEach(function (a) {
      a.addEventListener("click", function () {
        document.body.classList.remove("menu-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* Animazioni all'ingresso */
  var daRivelare = document.querySelectorAll("[data-reveal]");
  if (!riduci && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (voci) {
      voci.forEach(function (v) {
        if (v.isIntersecting) { v.target.classList.add("is-visible"); io.unobserve(v.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    daRivelare.forEach(function (el) { io.observe(el); });
  } else {
    daRivelare.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* Filtri della galleria: <button class="filter" data-filter="sposa"> + <figure data-cat="sposa"> */
  document.querySelectorAll("[data-filters]").forEach(function (gruppo) {
    var galleria = document.querySelector(gruppo.getAttribute("data-filters"));
    if (!galleria) return;
    var bottoni = gruppo.querySelectorAll(".filter");
    function applica(cat) {
      bottoni.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.filter === cat ? "true" : "false"); });
      galleria.querySelectorAll("[data-cat]").forEach(function (el) {
        el.hidden = !(cat === "tutti" || el.dataset.cat.split(" ").indexOf(cat) !== -1);
      });
      if (history.replaceState) history.replaceState(null, "", cat === "tutti" ? location.pathname : "#" + cat);
    }
    bottoni.forEach(function (b) { b.addEventListener("click", function () { applica(b.dataset.filter); }); });
    var iniziale = location.hash.replace("#", "");
    if (iniziale && gruppo.querySelector('[data-filter="' + iniziale + '"]')) applica(iniziale);
  });

  /* Lightbox: qualsiasi elemento con data-lightbox="url-grande" e data-caption opzionale */
  var voci = Array.prototype.slice.call(document.querySelectorAll("[data-lightbox]"));
  if (voci.length) {
    var box = document.createElement("div");
    box.className = "lightbox";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", "Immagine ingrandita");
    box.innerHTML =
      '<img class="lightbox__img" alt="">' +
      '<p class="lightbox__cap"></p>' +
      '<button class="lightbox__btn lightbox__close" aria-label="Chiudi">×</button>' +
      '<button class="lightbox__btn lightbox__prev" aria-label="Precedente">‹</button>' +
      '<button class="lightbox__btn lightbox__next" aria-label="Successiva">›</button>';
    document.body.appendChild(box);
    var img = box.querySelector(".lightbox__img");
    var cap = box.querySelector(".lightbox__cap");
    var attuale = 0, ultimoFocus = null;

    function visibili() { return voci.filter(function (v) { return !v.closest("[hidden]"); }); }
    function mostra(i) {
      var lista = visibili();
      if (!lista.length) return;
      attuale = (i + lista.length) % lista.length;
      var el = lista[attuale];
      img.src = el.getAttribute("data-lightbox");
      img.alt = el.getAttribute("data-caption") || "";
      cap.textContent = el.getAttribute("data-caption") || "";
    }
    function apri(el) {
      ultimoFocus = el;
      mostra(visibili().indexOf(el));
      box.classList.add("is-open");
      document.body.classList.add("lightbox-aperta");
      document.body.style.overflow = "hidden";
      box.querySelector(".lightbox__close").focus();
    }
    function chiudi() {
      box.classList.remove("is-open");
      document.body.classList.remove("lightbox-aperta");
      document.body.style.overflow = "";
      if (ultimoFocus) ultimoFocus.focus();
    }
    voci.forEach(function (v) {
      v.addEventListener("click", function (e) { e.preventDefault(); apri(v); });
    });
    box.querySelector(".lightbox__close").addEventListener("click", chiudi);
    box.querySelector(".lightbox__prev").addEventListener("click", function () { mostra(attuale - 1); });
    box.querySelector(".lightbox__next").addEventListener("click", function () { mostra(attuale + 1); });
    box.addEventListener("click", function (e) { if (e.target === box) chiudi(); });
    document.addEventListener("keydown", function (e) {
      if (!box.classList.contains("is-open")) return;
      if (e.key === "Escape") chiudi();
      if (e.key === "ArrowLeft") mostra(attuale - 1);
      if (e.key === "ArrowRight") mostra(attuale + 1);
    });
    var x0 = null;
    box.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    box.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 50) mostra(attuale + (dx < 0 ? 1 : -1));
      x0 = null;
    });
  }

  /* Mappa caricata solo su richiesta (niente cookie di terze parti finché non si clicca) */
  document.querySelectorAll("[data-mappa]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var contenitore = btn.closest(".map");
      var iframe = document.createElement("iframe");
      iframe.src = "https://www.google.com/maps?q=" + encodeURIComponent(btn.getAttribute("data-mappa")) + "&output=embed";
      iframe.title = "Mappa";
      iframe.loading = "lazy";
      contenitore.appendChild(iframe);
      btn.remove();
    });
  });
})();
