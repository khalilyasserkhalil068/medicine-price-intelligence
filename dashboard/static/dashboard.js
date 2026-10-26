/* =============================================================================
   Medicine Price & Alternatives Dashboard — front-end logic
   Talks to the Flask JSON API in dashboard/app.py.
   ========================================================================== */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };
  var state = { medicine: null, alternatives: [], charts: {} };

  /* ------------------------------ helpers ------------------------------ */
  function fmt(v, d) {
    if (v === null || v === undefined || v === "" || isNaN(Number(v))) return "\u2014";
    d = (d === undefined) ? 2 : d;
    return Number(v).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function fmtInt(v) {
    if (v === null || v === undefined || v === "") return "\u2014";
    return Number(v).toLocaleString("en-US");
  }
  function bdt(v) {
    if (v === null || v === undefined) return "No price data";
    return fmt(v) + " BDT";
  }
  function pct(v, d) {
    if (v === null || v === undefined) return "\u2014";
    return fmt(v, d === undefined ? 1 : d) + "%";
  }
  function esc(s) {
    return String(s === null || s === undefined ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }
  function note(el, kind, html) {
    if (!el) return;
    if (!html) { el.innerHTML = ""; el.classList.add("hidden"); return; }
    el.innerHTML = '<div class="alert ' + kind + '">' + html + "</div>";
    el.classList.remove("hidden");
  }
  async function api(url, options) {
    var res = await fetch(url, options);
    var data = null;
    try { data = await res.json(); } catch (e) { data = null; }
    if (!res.ok) {
      var msg = (data && data.error) ? data.error : "Request failed (" + res.status + ")";
      throw new Error(msg);
    }
    return data;
  }
  function debounce(fn, ms) {
    var t;
    return function () {
      var args = arguments, self = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(self, args); }, ms);
    };
  }

  /* ------------------------------- theme ------------------------------- */
  var THEME_KEY = "meddashboard-theme";
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    var btn = $("theme-toggle");
    if (btn) {
      btn.innerHTML = theme === "dark" ? "&#9728;" : "&#9789;";
      btn.setAttribute("aria-label", theme === "dark" ? "Switch to light theme" : "Switch to dark theme");
    }
    try { localStorage.setItem(THEME_KEY, theme); } catch (e) { /* ignore */ }
    refreshChartTheme();
  }
  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }
  function chartColors() {
    var dark = currentTheme() === "dark";
    return {
      grid: dark ? "rgba(255,255,255,0.08)" : "rgba(82,45,96,0.08)",
      tick: dark ? "#BCA9C9" : "#6B5872",
      text: dark ? "#F3EBF8" : "#241430",
      tooltipBg: dark ? "#33254A" : "#3D1C49",
      ok: "#0E9F6E",
      bad: "#D64545",
      neutral: dark ? "#A3588E" : "#80426E",
      accent: "#F2A67B",
      palette: ["#522D60", "#80426E", "#F2A67B", "#FFD38B", "#A3588E", "#D9845B"]
    };
  }

  /* -------------------------------- tabs -------------------------------- */
  function switchTab(name) {
    Array.prototype.forEach.call(document.querySelectorAll(".tab"), function (b) {
      b.classList.toggle("active", b.dataset.tab === name);
    });
    Array.prototype.forEach.call(document.querySelectorAll(".panel"), function (p) {
      p.classList.toggle("active", p.id === "panel-" + name);
    });
    if (name === "manufacturers") buildManufacturerChart();
    if (name === "market") buildMarketChart();
  }

  /* -------------------------------- KPIs -------------------------------- */
  async function loadKpis() {
    try {
      var k = await api("/api/kpi");
      $("kpi-medicines").textContent = fmtInt(k.total_medicines);
      $("kpi-medicines-sub").textContent = fmtInt(k.total_generics) + " generics registered";

      $("kpi-coverage").textContent = fmt(k.price_coverage_pct, 2) + "%";
      $("kpi-coverage-sub").textContent = fmtInt(k.priced_medicines) + " medicines with a validated price";

      $("kpi-median-saving").textContent = fmt(k.median_savings_pct, 1) + "%";
      $("kpi-median-saving-sub").textContent = "mean " + fmt(k.average_savings_pct, 1) + "% \u00b7 " +
        fmt(k.non_cheapest_share_pct, 1) + "% priced above their group minimum";

      $("kpi-groups").textContent = fmtInt(k.total_comparable_groups);
      $("kpi-groups-sub").textContent = "identical generic + form + strength";

      $("kpi-manufacturers").textContent = fmtInt(k.total_manufacturers);
      $("kpi-manufacturers-sub").textContent = "companies in the dataset";

      $("chip-dataset").innerHTML = "Dataset &middot; <b>" + fmtInt(k.total_medicines) + "</b> medicines";
    } catch (e) {
      note($("alternatives-alert"), "bad", "Could not load the key figures: " + esc(e.message));
      $("chip-dataset").textContent = "Dataset unavailable";
    }
  }

  /* ------------------------------- search ------------------------------- */
  function wireSearch(inputId, dropId, onPick) {
    var input = $(inputId), drop = $(dropId), items = [], active = -1;

    function close() { drop.classList.remove("open"); drop.innerHTML = ""; items = []; active = -1; }
    function draw() {
      if (!items.length) { close(); return; }
      drop.innerHTML = items.map(function (it, i) {
        return '<div class="sd-item' + (i === active ? " hl" : "") + '" data-i="' + i + '" role="option">' +
          '<div class="sd-main"><div class="sd-name">' + esc(it.brand_name) + "</div>" +
          '<div class="sd-meta">' + esc(it.generic_name) + " &middot; " + esc(it.dosage_form_name) +
          (it.strength_normalized ? " &middot; " + esc(it.strength_normalized) : "") +
          " &middot; " + esc(it.manufacturer_name) + "</div></div>" +
          '<div class="sd-price">' + (it.price === null ? "no price" : fmt(it.price) + " BDT") + "</div>" +
          "</div>";
      }).join("");
      drop.classList.add("open");
      Array.prototype.forEach.call(drop.querySelectorAll(".sd-item"), function (el) {
        el.addEventListener("mousedown", function (ev) {
          ev.preventDefault();
          onPick(items[Number(el.dataset.i)]);
          close();
        });
      });
    }
    var run = debounce(async function (q) {
      if (!q || q.trim().length < 2) { close(); return; }
      try {
        var rows = await api("/api/search?q=" + encodeURIComponent(q.trim()));
        items = rows || [];
        if (!items.length) {
          drop.innerHTML = '<div class="sd-empty">No brand or generic matched &ldquo;' + esc(q) + "&rdquo;.</div>";
          drop.classList.add("open");
          return;
        }
        active = -1;
        draw();
      } catch (e) {
        drop.innerHTML = '<div class="sd-empty">Search failed: ' + esc(e.message) + "</div>";
        drop.classList.add("open");
      }
    }, 220);

    input.addEventListener("input", function () { run(input.value); });
    input.addEventListener("keydown", function (ev) {
      if (!drop.classList.contains("open") || !items.length) return;
      if (ev.key === "ArrowDown") { active = Math.min(active + 1, items.length - 1); draw(); ev.preventDefault(); }
      else if (ev.key === "ArrowUp") { active = Math.max(active - 1, 0); draw(); ev.preventDefault(); }
      else if (ev.key === "Enter") {
        if (active >= 0) { onPick(items[active]); close(); ev.preventDefault(); }
        else if (items.length) { onPick(items[0]); close(); ev.preventDefault(); }
      } else if (ev.key === "Escape") { close(); }
    });
    input.addEventListener("blur", function () { setTimeout(close, 140); });
    document.addEventListener("click", function (ev) {
      if (!drop.contains(ev.target) && ev.target !== input) close();
    });
  }

  /* --------------------------- medicine detail -------------------------- */
  async function selectMedicine(brandId, stayOnTab) {
    try {
      var med = await api("/api/medicine/" + brandId);
      var alt = await api("/api/alternatives/" + brandId);
      state.medicine = med;
      state.alternatives = (alt && alt.alternatives) ? alt.alternatives : [];
      state.alternativesMessage = (alt && alt.message) ? alt.message : "";
      renderMedicine();
      renderAlternatives();
      $("calc-medicine").value = med.brand_name +
        (med.dosage_form_name ? " \u00b7 " + med.dosage_form_name : "") +
        (med.strength_normalized ? " \u00b7 " + med.strength_normalized : "");

      // A medicine with no recorded unit price cannot be compared, so the
      // calculator is disabled instead of failing after the user clicks.
      var priced = med.price !== null && med.price !== undefined;
      $("btn-calculate").disabled = !priced;
      if (!priced) {
        note($("calc-alert"), "info",
          "This brand has no recorded unit price, so a savings comparison is not possible. " +
          "Pick a priced brand from the alternatives list instead.");
      } else {
        note($("calc-alert"), "info", "");
      }
      if (!stayOnTab) switchTab("search");
    } catch (e) {
      note($("alternatives-alert"), "bad", "Could not load that medicine: " + esc(e.message));
    }
  }

  function renderMedicine() {
    var m = state.medicine;
    if (!m) return;
    $("medicine-panel").classList.remove("hidden");
    $("med-name").textContent = m.brand_name + (m.type ? " (" + m.type + ")" : "");
    $("med-generic").textContent = m.generic_name || "\u2014";
    $("med-form").textContent = m.dosage_form_name || "\u2014";
    $("med-strength").textContent = m.strength_normalized || "\u2014";
    $("med-manufacturer").textContent = m.manufacturer_name || "\u2014";
    $("med-price").textContent = bdt(m.price);
    $("med-class").textContent = m.drug_class_name || "\u2014";
    $("med-package").textContent = m.package_description || "\u2014";

    var g = m.group_stats, badge = $("med-badge");
    if (g && g.min_price !== null && g.max_price !== null) {
      $("med-range").textContent = fmt(g.min_price) + " \u2013 " + fmt(g.max_price) + " BDT";
    } else {
      $("med-range").textContent = "Not available";
    }
    badge.className = "pill neutral";
    if (m.price === null || m.price === undefined) {
      badge.textContent = "No price recorded";
    } else if (g && g.min_price !== null && Number(m.price) === Number(g.min_price)) {
      badge.className = "pill ok";
      badge.textContent = "Cheapest in its group";
    } else if (g && g.median_price !== null && Number(m.price) > Number(g.median_price)) {
      badge.className = "pill warn";
      badge.textContent = "Above the group median";
    } else if (g) {
      badge.className = "pill neutral";
      badge.textContent = "Below the group median";
    } else {
      badge.textContent = "No comparable group";
    }
  }

  function renderAlternatives() {
    var body = $("alternatives-body");
    var rows = state.alternatives || [];
    var current = state.medicine || {};
    var currentPrice = (current.price === null || current.price === undefined) ? null : Number(current.price);

    note($("alternatives-alert"), "info", state.alternativesMessage ? esc(state.alternativesMessage) : "");
    $("alternatives-count").textContent = Math.max(0, rows.length - 1) + " alternative" +
      (Math.max(0, rows.length - 1) === 1 ? "" : "s");

    if (!rows.length) {
      body.innerHTML = '<tr><td colspan="8" class="sub-line" style="padding:22px;text-align:center">' +
        "No equivalent brand found for this medicine with the strict matching rule.</td></tr>";
      return;
    }
    body.innerHTML = rows.map(function (a) {
      var savingPct = a.saving_pct;
      var barW = (savingPct === null || savingPct === undefined || currentPrice === null) ? 0 : Math.max(0, Math.min(100, savingPct));
      var pills = "";
      if (a.is_current) pills += ' <span class="pill you">Selected</span>';
      if (a.is_cheapest) pills += ' <span class="pill ok">Cheapest</span>';
      var gap = (a.price_diff === null || a.price_diff === undefined) ? "\u2014"
        : (a.price_diff > 0 ? "+" + fmt(a.price_diff) : fmt(a.price_diff));
      var pkg = a.package_description ? esc(a.package_description) : "\u2014";
      return "<tr>" +
        '<td><span class="bd">' + esc(a.brand_name) + "</span>" + pills + "</td>" +
        "<td>" + esc(a.manufacturer_name || "\u2014") + "</td>" +
        '<td class="num">' + (a.price === null ? "\u2014" : fmt(a.price)) + "</td>" +
        '<td class="num">' + gap + "</td>" +
        '<td class="num">' + (savingPct === null || savingPct === undefined ? "\u2014" : pct(savingPct)) + "</td>" +
        '<td><div class="bar"><span style="width:' + barW + '%"></span></div></td>' +
        '<td class="sub-line">' + pkg + "</td>" +
        '<td><button class="btn ghost sm" data-pick="' + a.brand_id + '" type="button">Select</button></td>' +
        "</tr>";
    }).join("");

    Array.prototype.forEach.call(body.querySelectorAll("[data-pick]"), function (b) {
      b.addEventListener("click", function () { selectMedicine(Number(b.dataset.pick)); });
    });
  }

  /* ----------------------------- calculator ----------------------------- */
  async function calculate() {
    var med = state.medicine;
    var alertEl = $("calc-alert");
    if (!med) { note(alertEl, "bad", "Select a medicine first."); return; }
    if (med.price === null || med.price === undefined) {
      note(alertEl, "bad", "This brand has no recorded unit price, so it cannot be compared. Pick a priced brand instead.");
      return;
    }
    var units = Number($("calc-units").value);
    if (!units || units <= 0 || isNaN(units)) { note(alertEl, "bad", "Enter a whole number of units greater than zero."); return; }

    var btn = $("btn-calculate");
    btn.disabled = true;
    var original = btn.textContent;
    btn.innerHTML = '<span class="spinner"></span> Calculating';
    note(alertEl, "info", "");
    try {
      var r = await api("/api/calculator", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brand_id: med.brand_id, units: units })
      });
      $("calc-placeholder").classList.add("hidden");
      $("calc-result").classList.remove("hidden");
      $("calc-units-echo").textContent = fmtInt(r.units) + " units for the whole course";

      $("res-current-total").textContent = fmt(r.current_medicine.total_cost) + " BDT";
      $("res-current-name").textContent = r.current_medicine.brand_name + " \u00b7 " + fmt(r.current_medicine.unit_price) + " BDT/unit";
      $("res-cheap-total").textContent = fmt(r.cheapest_alternative.total_cost) + " BDT";
      $("res-cheap-name").textContent = r.cheapest_alternative.brand_name + " \u00b7 " + fmt(r.cheapest_alternative.unit_price) + " BDT/unit";
      $("res-saving").textContent = fmt(r.net_savings_bdt) + " BDT";
      $("res-saving-pct").textContent = r.is_already_cheapest
        ? "The selected brand is already the cheapest option"
        : pct(r.saving_percentage, 2) + " lower than the selected brand";

      if (r.is_already_cheapest) {
        note(alertEl, "ok", "The selected brand is already the cheapest equivalent, so there is nothing to save on this prescription.");
      }

      $("calc-table-body").innerHTML =
        '<tr><td><span class="pill you">Selected</span></td><td class="bd">' + esc(r.current_medicine.brand_name) + "</td>" +
        "<td>" + esc(r.current_medicine.manufacturer_name || "\u2014") + '</td><td class="num">' + fmt(r.current_medicine.unit_price) + '</td><td class="num bd">' + fmt(r.current_medicine.total_cost) + "</td></tr>" +
        '<tr><td><span class="pill ok">Cheapest</span></td><td class="bd">' + esc(r.cheapest_alternative.brand_name) + "</td>" +
        "<td>" + esc(r.cheapest_alternative.manufacturer_name || "\u2014") + '</td><td class="num">' + fmt(r.cheapest_alternative.unit_price) + '</td><td class="num bd">' + fmt(r.cheapest_alternative.total_cost) + "</td></tr>";
    } catch (e) {
      note(alertEl, "bad", esc(e.message));
      $("calc-result").classList.add("hidden");
      $("calc-placeholder").classList.remove("hidden");
    } finally {
      btn.disabled = false;
      btn.textContent = original;
    }
  }

  /* ---------------------------- manufacturers --------------------------- */
  var mfrCache = null;
  function classify(idx) {
    if (idx === null || idx === undefined) return { label: "Unknown", cls: "neutral" };
    if (idx < 0.95) return { label: "Budget", cls: "ok" };
    if (idx > 1.05) return { label: "Premium", cls: "bad" };
    return { label: "At market median", cls: "neutral" };
  }
  function renderManufacturerTable() {
    if (!mfrCache) return;
    var q = ($("mfr-filter").value || "").trim().toLowerCase();
    var rows = mfrCache.filter(function (m) { return !q || m.manufacturer_name.toLowerCase().indexOf(q) !== -1; });
    $("mfr-count").textContent = rows.length + " of " + mfrCache.length + " companies shown";
    $("mfr-body").innerHTML = rows.map(function (m) {
      var c = classify(m.median_index);
      return "<tr>" +
        '<td class="bd">' + esc(m.manufacturer_name) + "</td>" +
        '<td class="num">' + fmtInt(m.n) + "</td>" +
        '<td class="num">' + fmt(m.median_index, 2) + "</td>" +
        '<td class="num">' + fmt(m.pct_cheapest, 1) + "%</td>" +
        '<td><span class="pill ' + c.cls + '">' + c.label + "</span></td>" +
        "</tr>";
    }).join("") || '<tr><td colspan="5" class="sub-line" style="padding:20px;text-align:center">No manufacturer matches that filter.</td></tr>';
  }
  async function loadManufacturers() {
    try {
      mfrCache = (await api("/api/manufacturers")) || [];
      renderManufacturerTable();
      buildManufacturerChart();
    } catch (e) {
      $("mfr-body").innerHTML = '<tr><td colspan="5" class="sub-line" style="padding:20px;text-align:center">Could not load manufacturers: ' + esc(e.message) + "</td></tr>";
    }
  }
  function buildManufacturerChart() {
    if (!mfrCache || !mfrCache.length) return;
    var c = chartColors();
    // Plotting the largest portfolios made every bar look identical, because
    // their price indexes all cluster around 1.0. Showing the 7 cheapest and
    // the 7 most expensive companies (with at least 20 comparable medicines,
    // to avoid small-sample noise) actually shows the market spread.
    var eligible = mfrCache
      .filter(function (m) { return m.n >= 20 && m.median_index !== null; })
      .sort(function (a, b) { return a.median_index - b.median_index; });
    var top = eligible.length >= 14
      ? eligible.slice(0, 7).concat(eligible.slice(-7))
      : eligible;
    var labels = top.map(function (m) {
      return m.manufacturer_name.length > 32 ? m.manufacturer_name.slice(0, 30) + "\u2026" : m.manufacturer_name;
    });
    var colors = top.map(function (m) {
      var t = classify(m.median_index).label;
      if (t === "Budget") return c.ok;
      if (t === "Premium") return c.bad;
      return c.neutral;
    });
    if (state.charts.mfr) state.charts.mfr.destroy();
    // dashed reference line at the market median (index = 1.00)
    var refLine = {
      id: "refLine",
      afterDatasetsDraw: function (chart) {
        var x = chart.scales.x.getPixelForValue(1);
        if (!isFinite(x)) return;
        var g = chart.ctx;
        g.save();
        g.beginPath();
        g.setLineDash([5, 4]);
        g.moveTo(x, chart.chartArea.top);
        g.lineTo(x, chart.chartArea.bottom);
        g.lineWidth = 1.5;
        g.strokeStyle = c.tick;
        g.stroke();
        g.restore();
      }
    };
    state.charts.mfr = new Chart($("chart-manufacturers"), {
      type: "bar",
      plugins: [refLine],
      data: {
        labels: labels,
        datasets: [{
          label: "Price index",
          data: top.map(function (m) { return m.median_index; }),
          backgroundColor: colors,
          borderRadius: 5,
          maxBarThickness: 26
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: c.tooltipBg,
            callbacks: {
              afterLabel: function (ctx) {
                var m = top[ctx.dataIndex];
                return [fmtInt(m.n) + " comparable medicines", "cheapest share " + fmt(m.pct_cheapest, 1) + "%"];
              }
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            grid: { color: c.grid },
            ticks: { color: c.tick, font: { size: 11 } },
            title: { display: true, text: "Median price index (1.00 = market median)", color: c.tick, font: { size: 11 } }
          },
          y: { grid: { display: false }, ticks: { color: c.tick, font: { size: 11 } } }
        }
      }
    });
  }

  /* -------------------------------- market ------------------------------ */
  var marketCache = null;
  async function loadMarket() {
    try {
      var res = await Promise.all([api("/api/drug_classes"), api("/api/top_groups")]);
      marketCache = { classes: res[0] || [], groups: res[1] || [] };
      renderGroupsTable();
      buildMarketChart();
    } catch (e) {
      $("groups-body").innerHTML = '<tr><td colspan="9" class="sub-line" style="padding:20px;text-align:center">Could not load the market data: ' + esc(e.message) + "</td></tr>";
    }
  }
  function renderGroupsTable() {
    if (!marketCache) return;
    var rows = marketCache.groups.slice().sort(function (a, b) { return (b.spread_x || 0) - (a.spread_x || 0); }).slice(0, 15);
    $("groups-body").innerHTML = rows.map(function (g) {
      return "<tr>" +
        '<td class="bd">' + esc(g.generic_name) + "</td>" +
        "<td>" + esc(g.dosage_form_name || "\u2014") + "</td>" +
        "<td>" + esc(g.strength_normalized || "\u2014") + "</td>" +
        '<td class="num">' + fmtInt(g.brands) + "</td>" +
        '<td class="num">' + fmt(g.min_price) + "</td>" +
        '<td class="num">' + fmt(g.median_price) + "</td>" +
        '<td class="num">' + fmt(g.max_price) + "</td>" +
        '<td class="num"><span class="pill ' + (g.spread_x >= 2 ? "bad" : "neutral") + '">' + fmt(g.spread_x, 2) + "&times;</span></td>" +
        '<td class="num bd">' + pct(g.max_saving_pct) + "</td>" +
        "</tr>";
    }).join("") || '<tr><td colspan="9" class="sub-line" style="padding:20px;text-align:center">No group data available.</td></tr>';
  }
  function buildMarketChart() {
    if (!marketCache || !marketCache.classes.length) return;
    var c = chartColors();
    var top = marketCache.classes.slice(0, 12);
    if (state.charts.cls) state.charts.cls.destroy();
    state.charts.cls = new Chart($("chart-classes"), {
      type: "bar",
      data: {
        labels: top.map(function (d) {
          return d.drug_class_name.length > 30 ? d.drug_class_name.slice(0, 28) + "\u2026" : d.drug_class_name;
        }),
        datasets: [{
          label: "Branded products",
          data: top.map(function (d) { return d.total_brands; }),
          backgroundColor: c.accent,
          hoverBackgroundColor: c.neutral,
          borderRadius: 5,
          maxBarThickness: 34
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: c.tooltipBg,
            callbacks: {
              afterLabel: function (ctx) {
                var d = top[ctx.dataIndex];
                return "average price " + fmt(d.avg_price) + " BDT (" + fmt(d.min_price) + " \u2013 " + fmt(d.max_price) + ")";
              }
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: c.tick, font: { size: 10 }, maxRotation: 45, minRotation: 0 } },
          y: { beginAtZero: true, grid: { color: c.grid }, ticks: { color: c.tick, font: { size: 11 } } }
        }
      }
    });
  }

  function refreshChartTheme() {
    if (state.charts.mfr) buildManufacturerChart();
    if (state.charts.cls) buildMarketChart();
  }

  /* -------------------------------- wiring ------------------------------ */
  document.addEventListener("DOMContentLoaded", function () {
    var saved = "light";
    try { saved = localStorage.getItem(THEME_KEY) || "light"; } catch (e) { /* ignore */ }
    applyTheme(saved);

    Array.prototype.forEach.call(document.querySelectorAll(".tab"), function (b) {
      b.addEventListener("click", function () { switchTab(b.dataset.tab); });
    });
    $("theme-toggle").addEventListener("click", function () {
      applyTheme(currentTheme() === "dark" ? "light" : "dark");
    });

    wireSearch("search-input", "search-dropdown", function (item) { selectMedicine(item.brand_id); });
    wireSearch("calc-search", "calc-dropdown", function (item) { selectMedicine(item.brand_id, true); });

    Array.prototype.forEach.call(document.querySelectorAll("[data-quick]"), function (b) {
      b.addEventListener("click", function () {
        $("search-input").value = b.dataset.quick;
        $("search-input").dispatchEvent(new Event("input"));
      });
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-units]"), function (b) {
      b.addEventListener("click", function () {
        $("calc-units").value = b.dataset.units;
        Array.prototype.forEach.call(document.querySelectorAll("[data-units]"), function (o) {
          o.style.borderColor = "";
        });
        b.style.borderColor = "var(--accent-400)";
      });
    });
    $("btn-calculate").addEventListener("click", calculate);
    $("calc-units").addEventListener("keydown", function (ev) { if (ev.key === "Enter") calculate(); });
    $("btn-to-calc").addEventListener("click", function () { switchTab("calc"); });
    $("mfr-filter").addEventListener("input", debounce(renderManufacturerTable, 150));

    loadKpis();
    loadManufacturers();
    loadMarket();
  });
})();
