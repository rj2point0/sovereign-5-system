/* =====================================================================
   SOVEREIGN 5-SYSTEM — app.js  (funnel + checkout + dossier renderer)
   Bilingual Edition: English (EN) & Spanish (ES)
   ===================================================================== */
const CONFIG = {
  STRIPE_LINK_BASE: '',
  STRIPE_LINK_BUMP: '',
  STRIPE_LINK_UPGRADE: '',

  PRICE_BASE: 37,
  PRICE_BUMP: 47,
  PRICE_ANCHOR: 197,           // struck-through "value" price
  GUARANTEE_DAYS: 30,          // set 0 to hide the guarantee badge

  WEBHOOK_URL: '',
  VSL_URL: '',

  DEMO_MODE: false,

  // Real Founder Profile: Adam Vega (Aug 19, 1978 · Double 7 Life Path/Chaldean · 7-8-4 Core Anchors)
  SAMPLE: { fullName: 'Adam Vega', birthDate: '1978-08-19', email: 'adam@sovereign5.com' },
  BRAND: 'Sovereign 5-System',
};

(function () {
  'use strict';
  const E = window.S5Engine;
  const C = window.S5Content;

  /* ---------------- utils ---------------- */
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const money = (n) => '$' + n;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const KEYS = { profile: 's5_profile', leads: 's5_leads', pending: 's5_pending_tier', lang: 's5_lang', vip: 's5_vip' };
  const store = {
    get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } },
    del(k) { try { localStorage.removeItem(k); } catch (e) { /* noop */ } },
  };
  const TIER_RANK = { base: 1, full: 2 };
  const maxTier = (a, b) => ((TIER_RANK[a] || 0) >= (TIER_RANK[b] || 0) ? a : b) || null;

  const LOCK_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>';
  const CHECK = '<span class="text-gold mr-2">✦</span>';

  // Read initial language from query param (?lang=es), localStorage, or default 'en'
  const urlLang = new URLSearchParams(window.location.search).get('lang');
  const initialLang = (urlLang === 'es' || urlLang === 'en') ? urlLang : (localStorage.getItem(KEYS.lang) || 'en');

  const state = {
    profile: null,
    result: null,
    bump: false,
    pendingTier: null,
    lang: initialLang,
    isVip: false,
  };

  const DOSSIER_SECTIONS_EN = [
    'Cover & Big Three Master Overlap Badge', 'The 5-System Method & Contents', 'Your Big Three Master Overlap Anchors',
    'Primary Signature Anchor Deep-Dive', 'Secondary Wealth & Strategy Engine', 'Tertiary Structural Foundation',
    'System I · Pythagorean Core Numbers', 'System II · Chaldean Compound Analysis', 'System III · Kabbalistic Placement & Tree of Life',
    'System IV · Vedic Planetary Architecture', 'System V · Lo Shu Magic Square & Five Elements', 'Tactical Synthesis · Wealth, Strategy & Magnetism',
    'Bonus Module · Rosicrucian 365-Day Cycles Calendar*', 'Bonus Module · Active Cycle Tactical Directives*',
    'The Sovereign Codex · One-Page Operating Blueprint',
  ];

  const DOSSIER_SECTIONS_ES = [
    'Portada y Medallón de Coincidencia Maestra', 'El Método de los 5 Sistemas y Contenido', 'Tus Tres Anclas de Coincidencia Maestra',
    'Análisis Profundo del Ancla de Firma Primaria', 'Motor Secundario de Riqueza y Estrategia', 'Fundación Estructural Terciaria',
    'Sistema I · Números Esenciales Pitagóricos', 'Sistema II · Análisis de Compuestos Caldeos', 'Sistema III · Ubicación Cabalística y Árbol de la Vida',
    'Sistema IV · Arquitectura Planetaria Védica', 'Sistema V · Cuadrado Mágico Lo Shu y Cinco Elementos', 'Síntesis Táctica · Riqueza, Estrategia y Magnetismo',
    'Módulo Especial · Calendario Rosacruz de 365 Días*', 'Módulo Especial · Directivas Tácticas del Ciclo Activo*',
    'El Códice Soberano · Plano Operativo en Una Sola Página',
  ];

  const SYS_NAMES = {
    en: { Pythagorean: 'Pythagorean', Chaldean: 'Chaldean', Kabbalistic: 'Kabbalistic', Vedic: 'Vedic', 'Lo Shu': 'Lo Shu' },
    es: { Pythagorean: 'Pitagórico', Chaldean: 'Caldeo', Kabbalistic: 'Cabalístico', Vedic: 'Védico', 'Lo Shu': 'Lo Shu Chino' },
  };

  const SOURCE_LABELS_ES = {
    'Life Path': 'Sendero de Vida',
    'Expression / Destiny': 'Expresión / Destino',
    "Soul Urge (Heart's Desire)": 'Deseo del Alma (Impulso Íntimo)',
    'First-Name Consonants': 'Consonantes del Primer Nombre',
    'Chaldean Full Name': 'Nombre Completo Caldeo',
    'Moolank (Driver)': 'Moolank (Psíquico / Conductor)',
    'Bhagyank (Conductor)': 'Bhagyank (Destino / Guía)',
    'Namank (Name Vibration)': 'Namank (Vibración del Nombre)',
    'Lo Shu Dominant (Metal)': 'Lo Shu Dominante (Metal)',
    'Chaldean Surname Vibration': 'Vibración del Apellido Caldeo',
    'Birth Month Vibration': 'Vibración del Mes de Nacimiento',
    'Lo Shu Earth Wealth (8 - Fa)': 'Riqueza Lo Shu Tierra (8 - Fa)',
    'Consonant Structural Base (4)': 'Base Estructural de Consonantes (4)',
    'Kabbalistic Abundance Base (Chesed / Dalet-Mem)': 'Base de Abundancia Cabalística (Chesed)',
    'Feng Shui Wealth Corner (Southeast Xun)': 'Esquina de Riqueza Feng Shui (Sureste Xun)',
  };

  function translateSystem(s) {
    const table = SYS_NAMES[state.lang] || SYS_NAMES.en;
    return table[s] || s;
  }

  function translateSource(label) {
    if (state.lang === 'es') {
      return SOURCE_LABELS_ES[label] || label;
    }
    return label;
  }

  function formatBirthDate(isoStr) {
    if (!isoStr) return '';
    const [y, m, d] = isoStr.split('-').map(Number);
    if (state.lang === 'es') {
      const MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
      return `${d} de ${MESES[m - 1]} de ${y}`;
    } else {
      const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
      return `${MONTHS[m - 1]} ${d}, ${y}`;
    }
  }

  function formatCurrentDate() {
    const now = new Date();
    if (state.lang === 'es') {
      const MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
      return `${now.getUTCDate()} de ${MESES[now.getUTCMonth()]} de ${now.getUTCFullYear()}`;
    } else {
      const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
      return `${MONTHS[now.getUTCMonth()]} ${now.getUTCDate()}, ${now.getUTCFullYear()}`;
    }
  }

  /* ---------------- Language Management ---------------- */
  function setLanguage(lang) {
    state.lang = lang === 'es' ? 'es' : 'en';
    localStorage.setItem(KEYS.lang, state.lang);
    document.documentElement.lang = state.lang;

    // Update URL query parameter without page reload
    try {
      const url = new URL(window.location);
      if (state.lang === 'es') url.searchParams.set('lang', 'es');
      else url.searchParams.delete('lang');
      window.history.replaceState({}, '', url);
    } catch (e) { /* ignore */ }

    // Update nav toggle buttons
    $$('.lang-switch button').forEach((b) => {
      b.classList.toggle('active', b.dataset.lang === state.lang);
    });

    // Update DOM static i18n text
    applyI18nToDOM();

    // Re-render systems strip
    renderSystemsStrip();

    // Re-render current view if data is present
    const view = document.body.dataset.view;
    if (view === 'teaser' && state.result) {
      renderTeaser();
    } else if (view === 'dossier' && state.result) {
      renderDossier();
    }
  }

  function applyI18nToDOM() {
    const C_LANG = C.get(state.lang);
    const UI = C_LANG.UI;

    $$('[data-i18n]').forEach((el) => {
      const key = el.dataset.i18n;
      if (UI[key]) {
        el.innerHTML = UI[key].replace('${year}', new Date().getFullYear());
      }
    });

    $$('[data-i18n-ph]').forEach((el) => {
      const key = el.dataset.i18nPh;
      if (UI[key]) el.placeholder = UI[key];
    });

    // Update page title
    document.title = state.lang === 'es'
      ? 'El Plano Soberano · Numerología de los 5 Sistemas y Ciclos Rosacruces'
      : 'The Sovereign 5-System Blueprint · Numerology & Rosicrucian Cycles';
  }

  /* ---------------- lead capture ---------------- */
  function leadId() { return 'lead_' + Math.random().toString(36).slice(2, 9); }
  function utm() {
    const q = new URLSearchParams(location.search);
    const u = {};
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'].forEach((k) => {
      if (q.get(k)) u[k] = q.get(k);
    });
    return u;
  }
  function saveProfile(p) {
    store.set(KEYS.profile, p);
    const leads = store.get(KEYS.leads) || [];
    const idx = leads.findIndex((l) => l.id === p.id);
    if (idx >= 0) leads[idx] = p; else leads.push(p);
    store.set(KEYS.leads, leads);
  }
  function sendWebhook(event, extra) {
    if (!CONFIG.WEBHOOK_URL) return;
    try {
      const payload = {
        event,
        timestamp: new Date().toISOString(),
        profile: state.profile,
        extra: extra || {},
      };
      if (navigator.sendBeacon) {
        navigator.sendBeacon(CONFIG.WEBHOOK_URL, JSON.stringify(payload));
      } else {
        fetch(CONFIG.WEBHOOK_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), mode: 'no-cors' }).catch(() => {});
      }
    } catch (e) { /* ignore */ }
  }

  /* ---------------- toast ---------------- */
  let toastTimer = null;
  function toast(html, duration) {
    const el = $('#toast');
    if (!el) return;
    el.innerHTML = html;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('show'), duration || 3600);
  }

  /* ---------------- views ---------------- */
  function showView(name) {
    document.body.dataset.view = name;
    $('#view-hero').classList.toggle('hidden', name !== 'hero');
    $('#view-teaser').classList.toggle('hidden', name !== 'teaser');
    $('#view-dossier').classList.toggle('hidden', name !== 'dossier');
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  /* ---------------- hero ---------------- */
  function renderSystemsStrip() {
    const C_LANG = C.get(state.lang);
    $('#systems-strip').innerHTML = C_LANG.SYSTEM_INFO.map((s, i) => `
      <div class="card-soft p-4 text-left sm:text-center">
        <div class="font-display text-gold text-lg">${['I', 'II', 'III', 'IV', 'V'][i]}</div>
        <div class="font-display text-sm mt-1 text-ivory">${s.name}</div>
        <div class="text-[0.62rem] tracking-[0.14em] uppercase text-zinc-500 mt-1">${s.origin}</div>
      </div>`).join('');
  }

  function fillForm(p) {
    $('#fullName').value = p.fullName || '';
    $('#birthDate').value = p.birthDate || '';
    $('#email').value = p.email || '';
  }

  function showErrors(errs) {
    ['fullName', 'birthDate', 'email'].forEach((k) => {
      const field = $('#' + k);
      const msg = $(`[data-error="${k}"]`);
      if (errs[k]) {
        field.classList.add('error');
        msg.textContent = errs[k];
      } else {
        field.classList.remove('error');
        msg.textContent = '';
      }
    });
  }

  async function onSubmit(e) {
    e.preventDefault();
    const data = {
      fullName: $('#fullName').value,
      birthDate: $('#birthDate').value,
      email: $('#email').value.trim(),
    };
    const check = E.validate(data.fullName, data.birthDate);
    const errs = Object.assign({}, check.errors);
    if (!data.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      errs.email = state.lang === 'es' ? 'Ingresa un correo electrónico válido' : 'Enter a valid email address';
    }
    showErrors(errs);
    if (Object.keys(errs).length) return;

    let prof = state.profile && state.profile.fullName === data.fullName && state.profile.birthDate === data.birthDate
      ? state.profile
      : { id: leadId(), fullName: data.fullName, birthDate: data.birthDate, email: data.email, tier: state.pendingTier || null, createdAt: new Date().toISOString(), utm: utm() };
    prof.email = data.email;
    if (state.pendingTier) prof.tier = maxTier(prof.tier, state.pendingTier);
    state.profile = prof;
    saveProfile(prof);

    sendWebhook('lead_capture');

    // Calculation ritual
    const ritual = $('#ritual');
    const ritualText = $('#ritual-text');
    ritual.classList.add('show');
    const steps = state.lang === 'es'
      ? ['Alineando los 5 sistemas…', 'Mapeando las 10 Sephirot del Árbol de la Vida…', 'Calculando el ciclo rosacruz de 52 días…', 'Aislando tus Números de Coincidencia Maestra…']
      : ['Aligning the systems…', 'Mapping the 10 Sephirot of the Tree of Life…', 'Computing your 52-day Rosicrucian cycle…', 'Isolating your Master Overlap Numbers…'];
    ritualText.textContent = steps[0];
    await sleep(400); ritualText.textContent = steps[1];
    await sleep(450); ritualText.textContent = steps[2];
    await sleep(450); ritualText.textContent = steps[3];
    await sleep(350);

    state.result = E.calculate(prof.fullName, prof.birthDate);
    ritual.classList.remove('show');

    if (prof.tier) {
      openDossier();
    } else {
      openTeaser();
    }
  }

  /* ---------------- teaser / sales ---------------- */
  function medal(num, size, extraClass) {
    const s = size === 'lg' ? 'medallion-lg' : size === 'md' ? 'medallion-md' : 'medallion-sm';
    const font = size === 'lg' ? 'text-4xl sm:text-5xl' : size === 'md' ? 'text-2xl sm:text-3xl' : 'text-base';
    return `<div class="medallion ${s} ${extraClass || ''}"><span class="font-display text-gold ${font}">${num}</span></div>`;
  }

  function lockedCard(title, sub, pills, alert) {
    const badgeText = state.lang === 'es' ? 'Bloqueado' : 'Locked';
    return `
    <div class="card-soft p-4 sm:p-5 locked rounded-xl avoid-break">
      <div class="locked-content">
        <div class="flex items-center justify-between"><p class="eyebrow">${title}</p><span class="badge-gold">${badgeText}</span></div>
        <p class="text-xs text-zinc-500 mt-1">${sub}</p>
        <div class="flex gap-2 mt-4">${pills.map((p) => `<div class="card-soft px-3 py-2 text-center text-xs font-display text-champagne">${p}</div>`).join('')}</div>
      </div>
      <div class="lock-overlay">
        <div class="lock-icon">${LOCK_SVG}</div>
        <p class="text-xs font-medium text-champagne tracking-wider uppercase">${title}</p>
        ${alert ? `<p class="text-[0.68rem] text-rose-300 font-medium">${alert}</p>` : ''}
      </div>
    </div>`;
  }

  function vslHtml() {
    if (CONFIG.VSL_URL) {
      if (CONFIG.VSL_URL.endsWith('.mp4')) {
        return `<div class="vsl-frame card p-2"><video src="${CONFIG.VSL_URL}" controls playsinline class="w-full h-full rounded-lg object-cover"></video></div>`;
      }
      return `<div class="vsl-frame card p-2"><iframe src="${CONFIG.VSL_URL}" class="w-full h-full rounded-lg" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></div>`;
    }
    const briefingText = state.lang === 'es'
      ? '<p class="font-display text-champagne text-base">Sesión con el Fundador</p><p class="text-xs text-zinc-400 mt-2 max-w-xs leading-relaxed">Configura un video vertical en <code>CONFIG.VSL_URL</code> dentro de app.js para insertar tu explicación en video.</p>'
      : '<p class="font-display text-champagne text-base">Founder Video Briefing</p><p class="text-xs text-zinc-400 mt-2 max-w-xs leading-relaxed">Add a vertical video or embed URL to <code>CONFIG.VSL_URL</code> in app.js to place your presentation here.</p>';
    return `
    <div class="vsl-frame card p-6 flex flex-col items-center justify-center text-center">
      <div class="w-14 h-14 rounded-full grid place-items-center mb-3" style="border:1px solid rgba(212,175,55,.6);background:rgba(212,175,55,.1)">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="#D4AF37"><polygon points="6,3 20,12 6,21"/></svg>
      </div>
      ${briefingText}
    </div>`;
  }

  function renderTeaser() {
    const C_LANG = C.get(state.lang);
    const UI = C_LANG.UI;
    const r = state.result, a = r.overlap.anchors[0], A = C_LANG.ARCHETYPES[a.number], p = r.pythagorean;
    const first = esc(r.input.firstName);
    const cyc = r.cycles;
    const birthLabel = formatBirthDate(r.input.birthDate);
    const sections = state.lang === 'es' ? DOSSIER_SECTIONS_ES : DOSSIER_SECTIONS_EN;

    const decodedSub = UI.decoded_sub
      .replace('${fullName}', esc(r.input.fullName))
      .replace('${birthLabel}', birthLabel)
      .replace('${totalSources}', r.overlap.totalSources);

    const appearedText = UI.appeared_text
      .replace('${count}', a.count)
      .replace('${systemsCount}', a.systems.length);

    const probP3 = UI.problem_p3
      .replace('${anchorNum}', a.number);

    const windowAlert = state.lang === 'es'
      ? `⚠ Tu ciclo activo de 52 días concluye en ${cyc.daysRemaining} día${cyc.daysRemaining === 1 ? '' : 's'}`
      : `⚠ Your current 52-day window closes in ${cyc.daysRemaining} day${cyc.daysRemaining === 1 ? '' : 's'}`;

    $('#teaser-root').innerHTML = `
    <div class="reveal">
      <div class="text-center pt-3">
        <span class="badge-olive">${UI.scan_complete}</span>
        <h1 class="font-display text-[1.9rem] leading-tight sm:text-4xl mt-4">${UI.decoded_title.replace('${first}', first)}</h1>
        <p class="text-zinc-400 mt-3 text-sm sm:text-base max-w-xl mx-auto">${decodedSub}</p>
      </div>

      <!-- #1 ANCHOR -->
      <div class="card mt-7 p-6 sm:p-9 text-center">
        <p class="eyebrow">${UI.anchor_1_eyebrow}</p>
        <div class="mt-6 flex justify-center">${medal(a.number, 'lg', 'glow-pulse')}</div>
        <h2 class="font-display text-2xl sm:text-3xl mt-6">${A.name}</h2>
        <p class="text-[0.68rem] tracking-[0.22em] uppercase text-zinc-500 mt-2">${A.keywords.join(' · ')}</p>
        <p class="mt-5 text-sm text-champagne">${appearedText}</p>
        <div class="flex flex-wrap justify-center gap-2 mt-3">${a.systems.map((s) => `<span class="badge-gold">${translateSystem(s)}</span>`).join('')}</div>
        <div class="hairline my-6"></div>
        <p class="font-serif text-[1.18rem] sm:text-[1.3rem] leading-relaxed text-zinc-200 text-left sm:text-center">${A.core}</p>
      </div>

      <!-- MATRIX -->
      <div class="mt-12">
        <p class="eyebrow text-center">${UI.matrix_eyebrow}</p>
        <h3 class="font-display text-xl sm:text-2xl text-center mt-2">${UI.matrix_title}</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-6">
          <div class="card-soft p-5 border-gold/40" style="border-color:rgba(212,175,55,.4)">
            <div class="flex items-center justify-between"><p class="eyebrow">${state.lang === 'es' ? 'Sistema I · Pitagórico' : 'System I · Pythagorean'}</p><span class="badge-olive">${UI.unlocked_badge}</span></div>
            <p class="text-xs text-zinc-500 mt-1">${state.lang === 'es' ? 'Sistema matemático occidental' : 'Western mathematical system'}</p>
            <div class="grid grid-cols-4 gap-2 mt-4">
              ${[
                [state.lang === 'es' ? 'Sendero' : 'Life Path', p.lifePath],
                [state.lang === 'es' ? 'Expresión' : 'Expression', p.expression],
                [state.lang === 'es' ? 'Alma' : 'Soul Urge', p.soulUrge],
                [state.lang === 'es' ? 'Persona' : 'Persona', p.personality]
              ].map(([l, n]) => `
                <div class="card-soft p-2 text-center"><div class="font-display text-lg text-champagne">${n.display}</div><div class="text-[0.52rem] uppercase tracking-wider text-zinc-500 mt-0.5">${l}</div></div>`).join('')}
            </div>
          </div>
          ${lockedCard(state.lang === 'es' ? 'Sistema II · Caldeo' : 'System II · Chaldean', state.lang === 'es' ? 'Vibración del nombre babilónico y números compuestos' : 'Babylonian compound name vibration', ['◆◆/◆', '◆◆/◆', '◆◆/◆'])}
          ${lockedCard(state.lang === 'es' ? 'Sistema III · Cabalístico' : 'System III · Kabbalistic', state.lang === 'es' ? 'Árbol de la Vida y Balance de Columnas' : 'Tree of Life & Pillar Balance', ['◆', '◆', '◆'])}
          ${lockedCard(state.lang === 'es' ? 'Sistema IV · Védico' : 'System IV · Vedic', state.lang === 'es' ? 'Moolank · Bhagyank · Namank' : 'Moolank · Bhagyank · Namank', ['◆', '◆', '◆'])}
          ${lockedCard(state.lang === 'es' ? 'Sistema V · Lo Shu' : 'System V · Lo Shu', state.lang === 'es' ? 'Cuadrado Mágico 3×3 y Cinco Elementos' : '3×3 Magic Square & Five Elements', ['◆◆', '◆', '◆◆◆'])}
          ${lockedCard(state.lang === 'es' ? '#2 Motor de Riqueza y Estrategia' : '#2 Wealth & Strategy Engine', state.lang === 'es' ? 'Cómo estás diseñado para materializar abundancia' : 'How you materialize abundance', ['◆', '◆◆', '◆'])}
        </div>
        <div class="mt-3">${lockedCard(state.lang === 'es' ? 'Tu Ciclo Rosacruz Activo de 52 Días' : 'Your Current Rosicrucian 52-Day Cycle', state.lang === 'es' ? '¿Ventana de máxima expansión o de preservación de capital?' : 'Press-edges window or capital-preservation window?', ['◆◆◆', '◆◆', '◆◆◆'], windowAlert)}</div>
      </div>

      <!-- PROBLEM / AGITATE -->
      <div class="mt-14 max-w-2xl mx-auto">
        <p class="eyebrow">${UI.problem_eyebrow}</p>
        <h3 class="font-display text-2xl sm:text-3xl mt-3 leading-snug">${UI.problem_title}</h3>
        <div class="mt-5 space-y-4 text-zinc-300 leading-relaxed">
          <p>${UI.problem_p1}</p>
          <p>${UI.problem_p2}</p>
          <p>${probP3}</p>
        </div>
      </div>

      <!-- VSL -->
      <div class="mt-14 text-center">
        <p class="eyebrow">${UI.vsl_eyebrow}</p>
        <h3 class="font-display text-xl sm:text-2xl mt-2 mb-6">${UI.vsl_title}</h3>
        ${vslHtml()}
      </div>

      <!-- WHAT'S INSIDE -->
      <div class="card mt-14 p-6 sm:p-8">
        <p class="eyebrow">${UI.inside_eyebrow}</p>
        <h3 class="font-display text-xl sm:text-2xl mt-2">${UI.inside_title}</h3>
        <ul class="mt-5 grid sm:grid-cols-2 gap-x-6 gap-y-2.5 text-sm text-zinc-300">
          ${sections.map((s) => `<li class="flex">${CHECK}<span>${s.replace('*', '')}${s.includes('*') ? ` <span class="text-gold text-[0.65rem]">(${state.lang === 'es' ? 'con módulo de ciclos' : 'with Cycles add-on'})</span>` : ''}</span></li>`).join('')}
        </ul>
      </div>

      <!-- CHECKOUT -->
      <div id="checkout" class="card mt-10 p-5 sm:p-8" style="border-color:rgba(212,175,55,.45)">
        <p class="eyebrow text-center">${UI.checkout_eyebrow}</p>
        <h3 class="font-display text-2xl sm:text-3xl text-center mt-2">${UI.checkout_title}</h3>

        <div class="mt-6 flex gap-4 items-start card-soft p-4">
          <div class="shrink-0 w-16 h-20 rounded-md grid place-items-center" style="background:linear-gradient(160deg,#1c1a12,#0b0b0d);border:1px solid rgba(212,175,55,.5)">
            <span class="font-display text-gold text-xl">${a.number}</span>
          </div>
          <div class="flex-1">
            <p class="font-semibold text-ivory text-[0.95rem] leading-snug">${UI.checkout_product}</p>
            <p class="text-xs text-zinc-400 mt-1">${UI.checkout_product_sub.replace('${first}', first)}</p>
          </div>
          <div class="text-right shrink-0">
            <div class="text-xs text-zinc-500 line-through">${money(CONFIG.PRICE_ANCHOR)}</div>
            <div class="font-display text-2xl text-champagne">${money(CONFIG.PRICE_BASE)}</div>
          </div>
        </div>

        <label id="bump-box" class="bump mt-4 flex gap-3 items-start cursor-pointer">
          <input id="bump" type="checkbox" />
          <span class="text-sm leading-relaxed">
            <span class="block font-bold text-gold uppercase tracking-wider text-[0.78rem] mb-1">${UI.bump_title.replace('${bumpPrice}', CONFIG.PRICE_BUMP)}</span>
            <span class="text-ivory">${UI.bump_text}</span>
          </span>
        </label>

        <div class="flex items-center justify-between mt-6 px-1">
          <span class="text-sm text-zinc-400 uppercase tracking-[0.18em]">${UI.total_today}</span>
          <span class="font-display text-3xl text-gold-grad" data-total>${money(CONFIG.PRICE_BASE)}</span>
        </div>

        <button type="button" data-action="checkout" class="btn-gold mt-4 !py-[1.15rem] !text-base">
          <span>${UI.unlock_cta}</span><span data-total>${money(CONFIG.PRICE_BASE)}</span>
        </button>

        <div class="mt-4 grid grid-cols-3 gap-2 text-center text-[0.62rem] uppercase tracking-[0.12em] text-zinc-500">
          <div class="card-soft py-2.5">${UI.secure_badge}</div>
          <div class="card-soft py-2.5">${UI.instant_badge}</div>
          <div class="card-soft py-2.5">${CONFIG.GUARANTEE_DAYS ? UI.guarantee_badge : UI.pdf_badge}</div>
        </div>

        ${(CONFIG.DEMO_MODE || state.isVip) ? `
        <div class="mt-6 pt-5 border-t border-white/5">
          <button type="button" data-action="demo-unlock" class="btn-demo">${state.isVip ? (state.lang === 'es' ? '★ Desbloquear Dossier Completo (Bypass VIP Fundador)' : '★ Unlock Full Dossier Now (Founder VIP Bypass)') : UI.demo_btn}</button>
          <p class="text-[0.65rem] text-zinc-600 text-center mt-2">${state.isVip ? (state.lang === 'es' ? 'Bypass VIP Fundador Activo (?vip=adam)' : 'Founder VIP Bypass Active (?vip=adam)') : (state.lang === 'es' ? 'Prueba del propietario. Desactiva mediante CONFIG.DEMO_MODE.' : 'Owner testing only. Disable via CONFIG.DEMO_MODE.')}</p>
        </div>` : ''}
      </div>

      <!-- FAQ -->
      <div class="mt-12 max-w-2xl mx-auto space-y-2.5">
        <p class="eyebrow text-center mb-4">${UI.questions_eyebrow}</p>
        ${(state.lang === 'es' ? [
          ['¿Es esto una suscripción?', 'No. Es un pago único con acceso instantáneo a tu dossier personalizado para siempre.'],
          ['¿En qué se diferencia de las apps gratuitas?', 'Las apps gratuitas ejecutan un solo sistema (Pitagórico). Tu dossier cruza cinco sistemas matemáticos antiguos e independientes, aislando los números que se repiten: tu Coincidencia Maestra.'],
          ['¿Cómo lo recibo?', 'De inmediato en tu navegador. Un solo clic lo exporta como un dossier PDF de lujo de múltiples páginas que puedes guardar, imprimir o compartir.'],
          ['¿Qué es el Calendario de Ciclos de 52 Días?', 'Basado en "Las Leyes del Éxito y los Ciclos de la Vida" de H. Spencer Lewis (Rosacruz), tu año personal de cumpleaños a cumpleaños se divide en siete períodos planetarios de ~52 días. Tu calendario detalla las fechas exactas de cada uno, marca tus Ventanas de Máxima Riqueza y Ventanas de Preservación de Capital, y muestra en cuál estás situado hoy.'],
        ] : [
          ['Is this a subscription?', 'No. It is a single one-time payment with instant access to your personalized dossier.'],
          ['How is this different from free numerology apps?', 'Free apps run one system (Pythagorean). Your dossier cross-references five independent ancient systems and isolates the numbers that repeat across them: your Master Overlap.'],
          ['How do I receive it?', 'Instantly, right here in your browser. One click exports it as a multi-page luxury PDF you can keep, print or share.'],
          ['What is the 52-Day Cycles Calendar?', 'Based on H. Spencer Lewis\' Rosicrucian "Cycles of Life", your personal year from birthday to birthday is divided into seven ~52-day periods. Your calendar lists the exact dates of each, flags your High-Wealth Action Windows and Capital Preservation Windows, and shows which one you are in today.'],
        ]).map(([q, ans]) => `<details class="card-soft p-4 group"><summary class="cursor-pointer font-medium text-ivory list-none flex justify-between items-center gap-3">${q}<span class="text-gold group-open:rotate-45 transition-transform text-xl leading-none">+</span></summary><p class="text-sm text-zinc-400 mt-3 leading-relaxed">${ans}</p></details>`).join('')}
      </div>

      <div class="text-center mt-10">
        <button type="button" data-action="home" class="text-xs text-zinc-500 underline underline-offset-4">${UI.run_different}</button>
      </div>
    </div>`;

    $('#bump').checked = state.bump;
    updateTotal();
    setupStickyCta();
  }

  function updateTotal() {
    const box = $('#bump');
    state.bump = !!(box && box.checked);
    const total = CONFIG.PRICE_BASE + (state.bump ? CONFIG.PRICE_BUMP : 0);
    $$('[data-total]').forEach((el) => { el.textContent = money(total); });
    const bb = $('#bump-box');
    if (bb) bb.classList.toggle('checked', state.bump);
  }

  let stickyObs = null;
  function setupStickyCta() {
    const cta = $('#sticky-cta'), co = $('#checkout');
    if (stickyObs) stickyObs.disconnect();
    let checkoutVisible = false;
    stickyObs = new IntersectionObserver((ents) => { checkoutVisible = ents[0].isIntersecting; onScroll(); }, { threshold: 0.05 });
    stickyObs.observe(co);
    function onScroll() {
      if (document.body.dataset.view !== 'teaser') { cta.classList.remove('show'); return; }
      cta.classList.toggle('show', window.scrollY > 520 && !checkoutVisible);
    }
    window.removeEventListener('scroll', onScroll);
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  function openTeaser() {
    showView('teaser');
    renderTeaser();
  }

  function checkout() {
    const link = state.bump ? CONFIG.STRIPE_LINK_BUMP : CONFIG.STRIPE_LINK_BASE;
    sendWebhook('checkout_click', { bump: state.bump, total: CONFIG.PRICE_BASE + (state.bump ? CONFIG.PRICE_BUMP : 0) });
    if (!link) {
      const msg = state.lang === 'es'
        ? '<b class="text-gold">Enlace de Stripe no configurado.</b><br/>Pega tus enlaces de pago en <code>CONFIG</code> dentro de app.js' + (CONFIG.DEMO_MODE ? ', o usa el Modo Demo abajo para desbloquear el dossier completo.' : '.')
        : '<b class="text-gold">Stripe link not configured.</b><br/>Paste your Payment Links into <code>CONFIG</code> in app.js' + (CONFIG.DEMO_MODE ? ', or use Demo Mode below to preview the full dossier.' : '.');
      toast(msg, 5500);
      return;
    }
    goToStripe(link, state.bump ? 'full' : 'base');
  }

  function goToStripe(link, tier) {
    store.set(KEYS.pending, tier);
    let url;
    try { url = new URL(link); } catch (e) { toast('Invalid Stripe link in CONFIG.'); return; }
    if (state.profile && state.profile.email) url.searchParams.set('prefilled_email', state.profile.email);
    if (state.profile && state.profile.id) url.searchParams.set('client_reference_id', state.profile.id);
    location.href = url.toString();
  }

  function demoUnlock() {
    state.profile.tier = 'full';
    saveProfile(state.profile);
    sendWebhook('demo_unlock');
    try {
      const u = new URL(location.href);
      u.searchParams.set('unlocked', 'true');
      history.replaceState(null, '', u);
    } catch (e) { /* file:// */ }
    openDossier();
    toast(state.lang === 'es' ? '✦ Compra simulada exitosa. Dossier completo desbloqueado.' : '✦ Demo purchase simulated. Full dossier unlocked.');
  }

  /* =====================================================================
     VIEW 3 · DOSSIER RENDERER
     ===================================================================== */
  const ROMAN = ['I', 'II', 'III', 'IV', 'V'];
  const TREE_POS = { 1: [150, 42], 2: [255, 108], 3: [45, 108], 4: [255, 228], 5: [45, 228], 6: [150, 284], 7: [255, 372], 8: [45, 372], 9: [150, 440], 10: [150, 508] };
  const TREE_PATHS = [[1, 2], [1, 3], [1, 6], [2, 3], [2, 4], [2, 6], [3, 5], [3, 6], [4, 5], [4, 6], [4, 7], [5, 6], [5, 8], [6, 7], [6, 8], [6, 9], [7, 8], [7, 9], [7, 10], [8, 9], [8, 10], [9, 10]];

  function treeSvg(active) {
    const lines = TREE_PATHS.map(([a, b]) => {
      const [x1, y1] = TREE_POS[a], [x2, y2] = TREE_POS[b];
      const on = active.has(a) && active.has(b);
      return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${on ? '#D4AF37' : 'rgba(212,175,55,.22)'}" stroke-width="${on ? 2.2 : 1.2}"/>`;
    }).join('');
    const nodes = Object.keys(TREE_POS).map((k) => {
      const n = +k, [x, y] = TREE_POS[n], on = active.has(n);
      const name = n === 10 ? 'Malkuth' : E.SEPHIROT[n].name;
      return `<g>
        <circle cx="${x}" cy="${y}" r="23" fill="${on ? 'url(#gg)' : '#0E0F13'}" stroke="${on ? '#F3E5AB' : 'rgba(212,175,55,.45)'}" stroke-width="${on ? 1.5 : 1}"/>
        <text x="${x}" y="${y + 6}" text-anchor="middle" font-family="Cinzel" font-size="17" fill="${on ? '#141108' : '#8a8571'}">${n === 10 ? '10' : n}</text>
        <text x="${x}" y="${y + 38}" text-anchor="middle" font-family="Inter" font-size="9.5" letter-spacing="1.2" fill="${on ? '#F3E5AB' : '#6b6b73'}">${name.toUpperCase()}</text>
      </g>`;
    }).join('');

    const sevLabel = state.lang === 'es' ? 'RIGOR' : 'SEVERITY';
    const milLabel = state.lang === 'es' ? 'EQUILIBRIO' : 'MILDNESS';
    const merLabel = state.lang === 'es' ? 'MISERICORDIA' : 'MERCY';

    return `<svg viewBox="0 0 300 560" class="w-full max-w-[260px] mx-auto" role="img" aria-label="Tree of Life">
      <defs><radialGradient id="gg" cx="35%" cy="30%"><stop offset="0%" stop-color="#F3E5AB"/><stop offset="60%" stop-color="#D4AF37"/><stop offset="100%" stop-color="#8f7020"/></radialGradient></defs>
      <text x="45" y="14" text-anchor="middle" font-family="Inter" font-size="8" letter-spacing="2" fill="#D4AF37">${sevLabel}</text>
      <text x="150" y="14" text-anchor="middle" font-family="Inter" font-size="8" letter-spacing="2" fill="#D4AF37">${milLabel}</text>
      <text x="255" y="14" text-anchor="middle" font-family="Inter" font-size="8" letter-spacing="2" fill="#D4AF37">${merLabel}</text>
      ${lines}${nodes}</svg>`;
  }

  function loShuGrid(l) {
    return `<div class="loshu">${l.grid.flat().map((n) => {
      const c = l.counts[n];
      return `<div class="loshu-cell ${c ? 'on' : ''}"><span class="pos">${n}</span><span class="digits">${c ? String(n).repeat(Math.min(c, 4)) + (c > 4 ? '+' : '') : '<span class="text-zinc-700">·</span>'}</span><span class="el">${E.elementOf(n)}</span></div>`;
    }).join('')}</div>`;
  }

  function secHead(eyebrow, title, lead) {
    return `<p class="eyebrow">${eyebrow}</p><h2 class="sec-title">${title}</h2><div class="hairline my-4" style="max-width:120px;margin-left:0"></div>${lead ? `<p class="lead">${lead}</p>` : ''}`;
  }
  function statCard(label, display, sub) {
    return `<div class="card-soft p-4 text-center avoid-break"><div class="text-[0.58rem] tracking-[0.2em] uppercase text-zinc-500">${label}</div><div class="font-display text-3xl text-gold-grad mt-1.5">${display}</div>${sub ? `<div class="text-[0.7rem] text-champagne mt-1">${sub}</div>` : ''}</div>`;
  }
  function interp(title, body) {
    return `<div class="avoid-break border-l border-gold/40 pl-4 py-1" style="border-color:rgba(212,175,55,.4)"><p class="font-display text-[0.95rem] text-champagne">${title}</p><p class="text-sm text-zinc-300 mt-1">${body}</p></div>`;
  }
  function bar(label, count, max, rightLabel) {
    const pct = Math.min(100, Math.round(((count || 0) / (max || 1)) * 100));
    return `<div class="bar-row"><div class="bar-label"><span>${label}</span><span>${rightLabel || count}</span></div><div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div></div>`;
  }
  function chips(letterWords) {
    return `<div class="flex flex-wrap gap-2 my-3">${letterWords.map((w) => `<div class="flex gap-1">${w.letters.map((l) => `<span class="chip ${l.vowel ? 'vowel' : ''}"><span class="ch">${l.ch}</span><span class="val">${l.val}</span></span>`).join('')}</div>`).join('<span class="chip-space"></span>')}</div>`;
  }
  function sentences(text, n) {
    if (!text) return '';
    const m = text.match(/[^.!?]+[.!?]+/g);
    return m ? m.slice(0, n).join(' ') : text;
  }

  function anchorPage(anchor, idx, C_LANG) {
    const UI = C_LANG.UI;
    const A = C_LANG.ARCHETYPES[anchor.number], n = anchor.number, V = E.VEDIC[n], S = E.SEPHIROT[n], el = E.elementOf(n);
    const focus = [A.core, A.wealth, A.foundation][idx];
    const roleTitle = [UI.signature_role, UI.wealth_role, UI.foundation_role][idx];
    const roleSub = [UI.signature_sub, UI.wealth_sub, UI.foundation_sub][idx];

    const sourcesClean = anchor.sources.map(s => translateSource(s));
    const systemsClean = anchor.systems.map(s => translateSystem(s));

    return `
      ${secHead(`${state.lang === 'es' ? 'Coincidencia Maestra · Ancla' : 'Master Overlap · Anchor'} ${idx + 1} ${state.lang === 'es' ? 'de 3' : 'of 3'}`, roleTitle, roleSub)}
      <div class="flex flex-col sm:flex-row gap-6 items-center mt-6 avoid-break">
        ${medal(n, 'lg')}
        <div class="flex-1 text-center sm:text-left">
          <p class="font-display text-2xl">${A.name}</p>
          <p class="text-[0.65rem] tracking-[0.2em] uppercase text-zinc-500 mt-1">${A.keywords.join(' · ')}</p>
          <p class="text-sm text-champagne mt-3">${state.lang === 'es' ? 'Frecuencia:' : 'Frequency:'} <b>${anchor.count}×</b> · ${state.lang === 'es' ? 'Sistemas:' : 'Systems:'} ${systemsClean.join(', ') || '—'}</p>
          ${sourcesClean.length ? `<p class="text-xs text-zinc-500 mt-1">${state.lang === 'es' ? 'Identificado en:' : 'Found in:'} ${sourcesClean.join(' · ')}</p>` : `<p class="text-xs text-zinc-500 mt-1">${state.lang === 'es' ? 'Confirmado por frecuencia Lo Shu.' : 'Selected by Lo Shu frequency tie-break.'}</p>`}
        </div>
      </div>
      <p class="lead mt-7">${focus}</p>
      <div class="grid sm:grid-cols-3 gap-3 mt-7">
        <div class="card-soft p-4 avoid-break"><p class="eyebrow !text-[0.55rem]">${state.lang === 'es' ? 'Regente Védico' : 'Vedic Ruler'}</p><p class="font-display mt-1">${V.planet} · ${V.english}</p><p class="text-xs text-zinc-400 mt-1">${V.archetype}</p></div>
        <div class="card-soft p-4 avoid-break"><p class="eyebrow !text-[0.55rem]">Sephirah</p><p class="font-display mt-1">${S.name}</p><p class="text-xs text-zinc-400 mt-1">${S.title} · ${S.essence}</p></div>
        <div class="card-soft p-4 avoid-break"><p class="eyebrow !text-[0.55rem]">${state.lang === 'es' ? 'Elemento Lo Shu' : 'Lo Shu Element'}</p><p class="font-display mt-1">${el}</p><p class="text-xs text-zinc-400 mt-1">${E.ELEMENTS[el].theme}</p></div>
      </div>
      <div class="grid sm:grid-cols-2 gap-5 mt-7">
        <div class="avoid-break"><p class="eyebrow">${state.lang === 'es' ? 'Tácticas de Activación' : 'Activation Tactics'}</p><ul class="mt-3 space-y-2 text-sm text-zinc-300">${A.tactics.map((t) => `<li class="flex">${CHECK}<span>${t}</span></li>`).join('')}</ul></div>
        <div class="avoid-break"><p class="eyebrow">${state.lang === 'es' ? 'Sombra a Dominar' : 'Shadow to Master'}</p><p class="text-sm text-zinc-300 mt-3">${A.shadow}</p><p class="eyebrow mt-5">${state.lang === 'es' ? 'Clave de Magnetismo' : 'Magnetism Key'}</p><p class="text-sm text-zinc-300 mt-3">${A.magnetism}</p></div>
      </div>`;
  }

  function cycleRow(c, C_LANG) {
    const T = C_LANG.CYCLE_TEXT[c.index];
    const todayBadge = state.lang === 'es' ? 'Activo Hoy' : 'Today';
    return `<tr class="${c.isCurrent ? 'current' : ''}">
      <td class="whitespace-nowrap"><span class="font-display text-gold text-lg mr-1.5">${c.glyph}</span><span class="font-display text-sm">${c.n}</span></td>
      <td><div class="font-display text-[0.85rem] text-ivory">${c.name}${c.isCurrent ? ` <span class="badge-gold !py-0.5 !text-[0.55rem] ml-1">${todayBadge}</span>` : ''}</div><div class="text-[0.72rem] text-zinc-500 mt-0.5">${c.theme}</div></td>
      <td class="whitespace-nowrap text-[0.78rem] text-zinc-300">${c.startLabel}<br/>${c.endLabel}<div class="text-[0.6rem] text-zinc-600">${state.lang === 'es' ? `Días ${c.startDay}–${c.endDay}` : `Days ${c.startDay}–${c.endDay}`}</div></td>
      <td><span class="mode-pill mode-${T.modeTone}">${T.mode}</span></td>
    </tr>`;
  }

  function buildDossierPages(r, tier) {
    const full = tier === 'full';
    const C_LANG = C.get(state.lang);
    const UI = C_LANG.UI;
    const [a1, a2, a3] = r.overlap.anchors;
    const A1 = C_LANG.ARCHETYPES[a1.number], A2 = C_LANG.ARCHETYPES[a2.number], A3 = C_LANG.ARCHETYPES[a3.number];
    const p = r.pythagorean, ch = r.chaldean, k = r.kabbalistic, v = r.vedic, l = r.loShu, cy = r.cycles;
    const name = esc(r.input.fullName);
    const pages = [];

    const birthLabel = formatBirthDate(r.input.birthDate);
    const currentLabel = formatCurrentDate();

    /* 1 · COVER */
    pages.push({ cover: true, title: state.lang === 'es' ? 'Portada' : 'Cover', html: `
      <div>
        <svg class="seal" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="47" fill="none" stroke="#D4AF37" stroke-width="1"/><circle cx="50" cy="50" r="41" fill="none" stroke="#D4AF37" stroke-width=".5" stroke-dasharray="2 2"/><polygon points="50,14 84,39 71,80 29,80 16,39" fill="none" stroke="#D4AF37" stroke-width="1"/><polygon points="50,80 16,39 84,39 29,80 50,14 71,80" fill="none" stroke="rgba(212,175,55,.5)" stroke-width=".6"/><circle cx="50" cy="50" r="4" fill="#D4AF37"/></svg>
        <p class="eyebrow mt-6">${UI.cover_edition.replace('${year}', new Date().getFullYear())}</p>
      </div>
      <div>
        <p class="font-display text-[0.8rem] tracking-[0.5em] text-zinc-400">${state.lang === 'es' ? 'EL' : 'THE'}</p>
        <h1 class="font-display text-4xl sm:text-6xl text-gold-grad mt-2 leading-tight">${state.lang === 'es' ? 'Plano<br/>Soberano' : 'Sovereign<br/>Blueprint'}</h1>
        <p class="font-serif italic text-xl text-zinc-300 mt-4">${state.lang === 'es' ? 'Dossier de Numerología de los 5 Sistemas y Ciclos Rosacruces' : '5-System Numerology & Rosicrucian Cycles Dossier'}</p>
        <div class="hairline my-10 mx-auto" style="max-width:260px"></div>
        <p class="text-[0.62rem] tracking-[0.35em] uppercase text-zinc-500">${UI.cover_prepared}</p>
        <p class="font-display text-3xl sm:text-4xl mt-3 text-ivory">${name}</p>
        <p class="font-serif text-lg text-champagne mt-2">${UI.cover_born.replace('${birthLabel}', birthLabel)}</p>
      </div>
      <div>
        <p class="eyebrow mb-5">${UI.cover_big3}</p>
        <div class="flex justify-center items-end gap-5 sm:gap-8">
          ${[a2, a1, a3].map((a) => `<div class="text-center">${medal(a.number, a === a1 ? 'lg' : 'md', a === a1 ? 'glow-pulse' : '')}<p class="text-[0.58rem] tracking-[0.2em] uppercase text-zinc-400 mt-3">${a === a1 ? (state.lang === 'es' ? 'Firma' : 'Signature') : a === a2 ? (state.lang === 'es' ? 'Riqueza' : 'Wealth') : (state.lang === 'es' ? 'Fundación' : 'Foundation')}</p></div>`).join('')}
        </div>
        <p class="text-[0.6rem] tracking-[0.25em] uppercase text-zinc-600 mt-10">${UI.cover_issued.replace('${generatedLabel}', currentLabel)}</p>
      </div>` });

    /* 2 · METHOD + CONTENTS */
    pages.push({ title: state.lang === 'es' ? 'El Método' : 'The Method', contents: true });

    /* 3 · BIG THREE MASTER OVERLAP + SECONDARY HARMONICS */
    const maxT = Math.max(...Object.values(r.overlap.tally).map((t) => t.count), 1);
    pages.push({ title: state.lang === 'es' ? 'Coincidencia Maestra' : 'Master Overlap', html: `
      ${secHead(UI.overlap_eyebrow, UI.overlap_title, UI.overlap_lead.replace('${totalSources}', r.overlap.totalSources))}
      <div class="grid sm:grid-cols-3 gap-3 mt-7">
        ${r.overlap.anchors.map((a, i) => {
          const roleTitle = [UI.signature_role, UI.wealth_role, UI.foundation_role][i];
          const roleSub = [UI.signature_sub, UI.wealth_sub, UI.foundation_sub][i];
          return `
          <div class="card-soft p-5 text-center avoid-break" ${i === 0 ? 'style="border-color:rgba(212,175,55,.55)"' : ''}>
            <p class="text-[0.55rem] tracking-[0.2em] uppercase text-gold">${['#1', '#2', '#3'][i]} · ${roleTitle}</p>
            <div class="flex justify-center mt-3">${medal(a.number, 'md')}</div>
            <p class="font-display mt-3">${C_LANG.ARCHETYPES[a.number].name}</p>
            <p class="text-[0.7rem] text-zinc-400 mt-1">${roleSub}</p>
            <p class="text-[0.7rem] text-champagne mt-2">${a.count}× · ${a.systems.length} ${state.lang === 'es' ? (a.systems.length === 1 ? 'sistema' : 'sistemas') : (a.systems.length === 1 ? 'system' : 'systems')}</p>
          </div>`;
        }).join('')}
      </div>

      <!-- Secondary Harmonics Callout -->
      <div class="mt-4 p-3 rounded-xl border border-gold/25 bg-charcoal/70 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs avoid-break">
        <div class="flex items-center gap-2">
          <span class="badge-gold !text-[0.6rem] !py-0.5">${UI.secondary_harmonics}</span>
          <span class="text-zinc-400 text-[0.7rem] hidden sm:inline">${UI.sec_harmonics_desc}</span>
        </div>
        <div class="flex items-center gap-4">
          ${r.overlap.secondaryHarmonics.map(h => `
            <span class="text-zinc-200 flex items-center gap-1.5">
              <span class="font-display text-gold text-sm font-bold">${h.number}</span>
              <span class="text-champagne font-medium">${C_LANG.ARCHETYPES[h.number].name}</span>
              <span class="text-zinc-500 text-[0.68rem]">(${h.count}× · ${h.systems.map(s => translateSystem(s)).join(', ')})</span>
            </span>`).join('')}
        </div>
      </div>

      <div class="grid sm:grid-cols-2 gap-7 mt-6">
        <div class="space-y-3 avoid-break">
          <p class="eyebrow">${UI.frequency_tally}</p>
          ${[1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => bar(`<span class="font-display text-champagne mr-2">${n}</span>${C_LANG.ARCHETYPES[n].name}`, r.overlap.tally[n].count, maxT, r.overlap.tally[n].count + '×')).join('')}
        </div>
        <div class="avoid-break">
          <p class="eyebrow">${UI.source_calcs}</p>
          <table class="lux-table mt-2"><thead><tr><th>${state.lang === 'es' ? 'Resultado' : 'Output'}</th><th>${state.lang === 'es' ? 'Sistema' : 'System'}</th><th>#</th></tr></thead><tbody>
            ${r.overlap.sources.map((s) => `<tr><td class="text-zinc-300">${translateSource(s.label)}</td><td class="text-zinc-500 text-xs">${translateSystem(s.system)}</td><td class="font-display text-gold">${s.value}</td></tr>`).join('')}
          </tbody></table>
          <p class="text-[0.7rem] text-zinc-500 mt-3">${state.lang === 'es' ? 'La coincidencia cabalística se acredita cuando un número ocupa una Sephirah a través de tu Sendero de Vida, Expresión, Nombre Caldeo o Impulso del Alma.' : 'Kabbalistic overlap is credited when a number occupies a Sephirah via your Life Path, Expression, Chaldean Name or Soul Urge.'}</p>
        </div>
      </div>` });

    /* 4–6 · ANCHORS DEEP-DIVE */
    r.overlap.anchors.forEach((a, i) => pages.push({
      title: state.lang === 'es'
        ? ['Ancla de Firma', 'Motor de Riqueza', 'Fundación Estructural'][i]
        : ['Signature Anchor', 'Wealth Engine', 'Foundation'][i],
      html: anchorPage(a, i, C_LANG)
    }));

    /* 7 · PYTHAGOREAN */
    const lb = p.lifePathBreakdown;
    const PA = (n) => C_LANG.ARCHETYPES[n] || null;
    pages.push({ title: state.lang === 'es' ? 'Sistema I · Pitagórico' : 'System I · Pythagorean', html: `
      ${secHead(state.lang === 'es' ? 'Sistema I · Antigua Grecia' : 'System I · Ancient Greece', state.lang === 'es' ? 'Números Esenciales Pitagóricos' : 'Pythagorean Core Numbers', state.lang === 'es' ? 'El sistema matemático occidental asigna el alfabeto del 1 al 9 en secuencia. Revela el camino que transitas, tus herramientas innatas, lo que tu alma anhela y la faz que muestras al mundo.' : 'The Western mathematical system maps the alphabet sequentially to 1–9. It reveals the road you walk, the tools you carry, what your heart hungers for, and the mask the world sees.')}
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
        ${statCard(state.lang === 'es' ? 'Sendero de Vida' : 'Life Path', p.lifePath.display, PA(p.lifePath.value) ? PA(p.lifePath.value).name : '')}
        ${statCard(state.lang === 'es' ? 'Expresión' : 'Expression', p.expression.display, PA(p.expression.value) ? PA(p.expression.value).name : '')}
        ${statCard(state.lang === 'es' ? 'Deseo del Alma' : 'Soul Urge', p.soulUrge.display || '—', PA(p.soulUrge.value) ? PA(p.soulUrge.value).name : '')}
        ${statCard(state.lang === 'es' ? 'Personalidad' : 'Personality', p.personality.display, PA(p.personality.value) ? PA(p.personality.value).name : '')}
      </div>
      <div class="card-soft p-4 mt-5 text-sm avoid-break">
        <p class="eyebrow !text-[0.55rem]">${state.lang === 'es' ? 'Cálculo del Sendero de Vida' : 'Life Path Calculation'}</p>
        <p class="text-zinc-300 mt-2 font-mono text-[0.78rem] leading-6">
          ${state.lang === 'es' ? 'Año' : 'Year'} ${lb.year.raw} → ${lb.year.sum}${lb.year.sum > 9 ? ' → ' + lb.year.reduced : ''} &nbsp;·&nbsp; ${state.lang === 'es' ? 'Mes' : 'Month'} ${lb.month.raw} → ${lb.month.reduced} &nbsp;·&nbsp; ${state.lang === 'es' ? 'Día' : 'Day'} ${lb.day.raw} → ${lb.day.reduced}<br/>
          ${lb.year.reduced} + ${lb.month.reduced} + ${lb.day.reduced} = ${p.lifePath.raw}${p.lifePath.raw > 9 ? ' → ' + p.lifePath.value : ''}
        </p>
      </div>
      <div class="mt-5 avoid-break">
        <p class="eyebrow !text-[0.55rem] mb-2">${state.lang === 'es' ? 'Valores de Letras (vocales enmarcadas en oro)' : 'Letter Values (vowels outlined in gold)'}</p>
        ${chips(p.letters)}
        <p class="text-[0.72rem] text-zinc-500">${state.lang === 'es' ? 'Total Expresión' : 'Total'} ${p.expression.raw} → ${p.expression.display} · ${state.lang === 'es' ? 'Vocales' : 'Vowels'} ${p.soulUrge.raw} → ${p.soulUrge.display} · ${state.lang === 'es' ? 'Consonantes' : 'Consonants'} ${p.personality.raw} → ${p.personality.display} · ${state.lang === 'es' ? 'Consonantes del primer nombre' : 'First-name consonants'} ${p.firstNameConsonants.raw} → ${p.firstNameConsonants.display}</p>
      </div>
      <div class="space-y-4 mt-6">
        ${PA(p.lifePath.value) ? interp(`${state.lang === 'es' ? 'Sendero de Vida' : 'Life Path'} ${p.lifePath.value} · ${state.lang === 'es' ? 'El Camino' : 'The Road'}`, sentences(PA(p.lifePath.value).core, 2)) : ''}
        ${PA(p.expression.value) ? interp(`${state.lang === 'es' ? 'Expresión' : 'Expression'} ${p.expression.value} · ${state.lang === 'es' ? 'El Instrumental' : 'The Toolkit'}`, state.lang === 'es' ? `Tus instrumentos naturales son ${PA(p.expression.value).keywords.join(', ').toLowerCase()}. ${sentences(PA(p.expression.value).wealth, 1)}` : `Your natural instruments are ${PA(p.expression.value).keywords.join(', ').toLowerCase()}. ${sentences(PA(p.expression.value).wealth, 1)}`) : ''}
        ${PA(p.soulUrge.value) ? interp(`${state.lang === 'es' ? 'Deseo del Alma' : 'Soul Urge'} ${p.soulUrge.value} · ${state.lang === 'es' ? 'El Anhelo Profundo' : 'The Hunger'}`, PA(p.soulUrge.value).soul) : interp(state.lang === 'es' ? 'Deseo del Alma · Silente' : 'Soul Urge · Silent', state.lang === 'es' ? 'El deseo del alma fluye como una corriente íntima y serena.' : 'The Soul Urge reads as a silent, inward current.')}
        ${PA(p.personality.value) ? interp(`${state.lang === 'es' ? 'Personalidad' : 'Personality'} ${p.personality.value} · ${state.lang === 'es' ? 'La Máscara' : 'The Mask'}`, PA(p.personality.value).persona) : ''}
      </div>` });

    /* 8 · CHALDEAN */
    const compounds = [
      [state.lang === 'es' ? 'Primer Nombre' : 'First Name', ch.firstName],
      [state.lang === 'es' ? 'Apellido' : 'Last Name', ch.lastName],
      [state.lang === 'es' ? 'Nombre Completo' : 'Full Name', ch.total]
    ];
    const seenC = new Set();
    pages.push({ title: state.lang === 'es' ? 'Sistema II · Caldeo' : 'System II · Chaldean', html: `
      ${secHead(state.lang === 'es' ? 'Sistema II · Babilonia' : 'System II · Babylon', state.lang === 'es' ? 'Análisis de Compuestos Caldeos' : 'Chaldean Compound Analysis', state.lang === 'es' ? 'El sistema numérico más antiguo clasifica las letras por vibración sonora del 1 al 8. El nueve es sagrado y jamás se asigna. El número compuesto revela la historia profunda y el destino oculto; el reducido expresa la manifestación externa.' : 'The oldest numerical system on record assigns letters by sound vibration, using only 1–8. Nine is sacred and never assigned. The compound number (before reduction) reveals the hidden story; the root reveals the outer expression.')}
      <div class="grid grid-cols-3 gap-3 mt-6">
        ${compounds.map(([lab, n]) => statCard(lab, n.display, `${state.lang === 'es' ? 'Total bruto' : 'Total'} ${n.raw}`)).join('')}
      </div>
      <div class="mt-5 avoid-break"><p class="eyebrow !text-[0.55rem] mb-2">${state.lang === 'es' ? 'Valores de Letras Caldeas' : 'Chaldean Letter Values'}</p>${chips(ch.letters)}</div>
      <div class="space-y-4 mt-6">
        ${compounds.map(([lab, n]) => {
          const cc = C_LANG.compound(n.compound);
          if (!cc) return interp(`${lab} · Root ${n.value}`, `${state.lang === 'es' ? 'Vibración pura de raíz' : 'A pure single-digit vibration of'} ${n.value} (${C_LANG.ARCHETYPES[n.value] ? C_LANG.ARCHETYPES[n.value].name : ''}).`);
          const dup = seenC.has(n.compound); seenC.add(n.compound);
          return interp(`${lab} · ${n.display} · ${cc.title}`, dup ? (state.lang === 'es' ? 'Mismo compuesto que el anterior, duplicando su influencia en tu nombre.' : 'Same compound as above, doubling its influence in your name.') : `${cc.text} <span class="text-[0.65rem] uppercase tracking-widest ${cc.tone === 'favorable' ? 'text-lime-300/80' : cc.tone === 'caution' ? 'text-rose-300/80' : 'text-gold'}">· ${cc.tone}</span>`);
        }).join('')}
      </div>
      <div class="card-soft p-4 mt-6 avoid-break">
        <p class="eyebrow !text-[0.55rem]">${state.lang === 'es' ? 'Veredicto de Vibración del Nombre' : 'Name Vibration Verdict'}</p>
        <p class="text-sm text-zinc-300 mt-2">${state.lang === 'es' ? `Tu nombre completo resuelve en <b class="text-champagne">${ch.total.display}</b>, la frecuencia de <b class="text-champagne">${C_LANG.ARCHETYPES[ch.total.value].name}</b>. En la tradición caldea, esta es la vibración que otros sienten al pronunciar tu nombre, y es el número que opera como tu <i>Namank</i> védico.` : `Your full name resolves to <b class="text-champagne">${ch.total.display}</b>, the vibration of <b class="text-champagne">${C_LANG.ARCHETYPES[ch.total.value].name}</b>. In the Chaldean tradition this is the frequency others feel when they hear your name, and it is the number used as your Vedic <i>Namank</i>.`}</p>
      </div>` });

    /* 9 · KABBALAH */
    const PIL = k.pillars;
    pages.push({ title: state.lang === 'es' ? 'Sistema III · Cábala' : 'System III · Kabbalah', html: `
      ${secHead(state.lang === 'es' ? 'Sistema III · El Árbol de la Vida' : 'System III · The Tree of Life', state.lang === 'es' ? 'Ubicación Cabalística y Balance de Columnas' : 'Kabbalistic Placement & Pillar Balance', state.lang === 'es' ? 'Tus cuatro números esenciales se ubican en las diez Sephirot del Árbol de la Vida. Las esferas que activan y la columna hacia la que se inclinan revelan cómo la fuerza se transmuta en forma en tu vida.' : 'Your four core numbers are placed on the ten Sephirot of the Tree of Life. The spheres they illuminate, and the pillar they lean toward, reveal how force becomes form in your life.')}
      <div class="grid sm:grid-cols-5 gap-6 mt-6 items-start">
        <div class="sm:col-span-2 avoid-break">${treeSvg(new Set(k.activeSephirot))}</div>
        <div class="sm:col-span-3 space-y-3">
          ${k.placements.map((pl) => `
            <div class="card-soft p-3.5 avoid-break flex gap-3 items-start">
              ${medal(pl.value, 'sm')}
              <div><p class="text-[0.58rem] tracking-[0.18em] uppercase text-zinc-500">${translateSource(pl.label)}</p><p class="font-display text-[0.95rem] text-champagne">${pl.sephirah.name} · ${pl.sephirah.title}</p><p class="text-[0.78rem] text-zinc-400 mt-1">${C_LANG.SEPHIROT_TEXT[pl.value]}</p></div>
            </div>`).join('')}
        </div>
      </div>
      <div class="mt-6 avoid-break">
        <p class="eyebrow">${state.lang === 'es' ? 'Equilibrio de Columnas' : 'Pillar Balance'}</p>
        <div class="grid sm:grid-cols-3 gap-4 mt-3">
          ${['Mercy', 'Mildness', 'Severity'].map((key) => {
            const label = state.lang === 'es' ? (key === 'Mercy' ? 'Misericordia' : key === 'Severity' ? 'Rigor' : 'Equilibrio') : PIL[key].label;
            return bar(`${label} <span class="text-zinc-600">(${PIL[key].numbers.join(', ')})</span>`, PIL[key].count, k.placements.length, PIL[key].count + ' / ' + k.placements.length);
          }).join('')}
        </div>
        <p class="lead mt-5 !text-[1.08rem]">${C_LANG.PILLAR_TEXT[k.dominantPillar]}</p>
      </div>` });

    /* 10 · VEDIC */
    const vRows = [
      [state.lang === 'es' ? 'Moolank' : 'Moolank', state.lang === 'es' ? 'Psíquico / Conductor' : 'Psychic / Driver', v.moolank, `${state.lang === 'es' ? 'Día de nacimiento' : 'Day of birth'} ${v.moolank.raw} → ${v.moolank.value}`],
      [state.lang === 'es' ? 'Bhagyank' : 'Bhagyank', state.lang === 'es' ? 'Destino / Conductor' : 'Destiny / Conductor', v.bhagyank, `${r.input.birth.compact} → ${v.bhagyank.raw} → ${v.bhagyank.value}`],
      [state.lang === 'es' ? 'Namank' : 'Namank', state.lang === 'es' ? 'Vibración del Nombre' : 'Name Vibration', v.namank, `${state.lang === 'es' ? 'Total Caldeo' : 'Chaldean total'} ${v.namank.raw} → ${v.namank.value}`]
    ];
    const vNote = state.lang === 'es'
      ? (v.moolank.value === v.bhagyank.value
        ? `Tu Psíquico y Destino son idénticos (${v.moolank.value}, ${v.moolank.ruler.planet}). Esta firma unificada es sumamente escasa: lo que buscas instintivamente y hacia donde la vida te conduce apuntan en la misma dirección.`
        : `Tu Conductor Psíquico (${v.moolank.value}, ${v.moolank.ruler.planet}) moldea tus instintos y juventud. Tu Conductor de Destino (${v.bhagyank.value}, ${v.bhagyank.ruler.planet}) gobierna tu madurez y se fortalece marcadamente a partir de los 35 años. La maestría radica en que el Psíquico sirva al Destino.`)
      : (v.moolank.value === v.bhagyank.value
        ? `Your Driver and Conductor are identical (${v.moolank.value}, ${v.moolank.ruler.planet}). This unified signature is rare: what you instinctively want and what life is steering you toward point in the same direction.`
        : `Your Driver (${v.moolank.value}, ${v.moolank.ruler.planet}) shapes your instincts, personality and early life. Your Conductor (${v.bhagyank.value}, ${v.bhagyank.ruler.planet}) governs your destiny and strengthens markedly from your mid-thirties onward. Mastery comes from letting the Driver serve the Conductor.`);

    const nNote = state.lang === 'es'
      ? ((v.namank.value === v.moolank.value || v.namank.value === v.bhagyank.value)
        ? `Tu Namank (${v.namank.value}) resuena con tus cifras de nacimiento, por lo que tu nombre amplifica tu arquitectura planetaria natal.`
        : `Tu Namank (${v.namank.value}, ${v.namank.ruler.planet}) introduce una tercera frecuencia planetaria, ampliando tu versatilidad pero exigiendo integración consciente.`)
      : ((v.namank.value === v.moolank.value || v.namank.value === v.bhagyank.value)
        ? `Your Namank (${v.namank.value}) resonates with your birth numbers, so your name amplifies your natal planetary architecture.`
        : `Your Namank (${v.namank.value}, ${v.namank.ruler.planet}) introduces a third, distinct planetary frequency, widening your range but requiring conscious integration.`);

    pages.push({ title: state.lang === 'es' ? 'Sistema IV · Védico' : 'System IV · Vedic', html: `
      ${secHead(state.lang === 'es' ? 'Sistema IV · India Antigua' : 'System IV · Ancient India', state.lang === 'es' ? 'Arquitectura Planetaria Védica' : 'Vedic Planetary Architecture', state.lang === 'es' ? 'En la astro-numerología védica y tamil, cada número está gobernado por uno de los Navagraha, las nueve inteligencias planetarias. Tus números Psíquico, Destino y Nombre conforman tu consejo cósmico personal.' : 'In Vedic and Tamil astro-numerology, each number is governed by one of the Navagraha, the nine planetary intelligences. Your Driver, Conductor and Name numbers form your personal planetary council.')}
      <div class="space-y-3 mt-6">
        ${vRows.map(([t, sub, n, calc]) => `
          <div class="card-soft p-4 sm:p-5 avoid-break flex gap-4 items-start">
            ${medal(n.value, 'md')}
            <div class="flex-1">
              <div class="flex flex-wrap items-baseline gap-x-3"><p class="font-display text-lg text-ivory">${t}</p><p class="text-[0.6rem] tracking-[0.2em] uppercase text-zinc-500">${sub}</p></div>
              <p class="font-display text-champagne mt-1">${n.ruler.planet} · ${n.ruler.english} <span class="text-zinc-500 font-sans text-xs">· ${n.ruler.archetype}</span></p>
              <p class="text-[0.82rem] text-zinc-300 mt-2">${C_LANG.VEDIC_TEXT[n.value]}</p>
              <p class="text-[0.7rem] text-zinc-500 mt-2">${state.lang === 'es' ? 'Día de poder:' : 'Power day:'} <span class="text-champagne">${n.ruler.day}</span> · ${state.lang === 'es' ? 'Gema:' : 'Gem:'} <span class="text-champagne">${n.ruler.gem}</span> · ${state.lang === 'es' ? 'Colores:' : 'Colours:'} <span class="text-champagne">${n.ruler.color}</span> · <span class="font-mono">${calc}</span></p>
            </div>
          </div>`).join('')}
      </div>
      <div class="space-y-4 mt-6">${interp(state.lang === 'es' ? 'Psíquico × Destino' : 'Driver × Conductor', vNote)}${interp(state.lang === 'es' ? 'Resonancia del Nombre' : 'Name Resonance', nNote)}</div>` });

    /* 11 · LO SHU */
    const maxE = Math.max(...Object.values(l.elements), 1);
    const ET = C_LANG.ELEMENT_TEXT[l.dominantElement];
    pages.push({ title: state.lang === 'es' ? 'Sistema V · Lo Shu' : 'System V · Lo Shu', html: `
      ${secHead(state.lang === 'es' ? 'Sistema V · China Antigua' : 'System V · Ancient China', state.lang === 'es' ? 'Cuadrado Mágico Lo Shu y Cinco Elementos' : 'Lo Shu Magic Square & Five Elements', state.lang === 'es' ? `Cada dígito de tu fecha de nacimiento (${r.input.birth.compact}) más tu Sendero de Vida (${p.lifePath.value}), Expresión (${p.expression.value}) y Nombre Caldeo (${ch.total.value}) se ubica en el cuadrado Lo Shu 3×3, cuyas filas y columnas suman 15.` : `Every digit of your birth date (${r.input.birth.compact}) plus your Life Path (${p.lifePath.value}), Expression (${p.expression.value}) and Chaldean Name (${ch.total.value}) is placed into the 3×3 Lo Shu square, whose rows, columns and diagonals all sum to 15.`)}
      <div class="grid sm:grid-cols-2 gap-7 mt-6 items-start">
        <div class="avoid-break">${loShuGrid(l)}<p class="text-[0.68rem] text-zinc-500 mt-3">${state.lang === 'es' ? 'Ausentes:' : 'Missing:'} ${l.missing.length ? l.missing.join(', ') : (state.lang === 'es' ? 'ninguno' : 'none')} · ${state.lang === 'es' ? 'Repetidos:' : 'Repeated:'} ${l.repeated.length ? l.repeated.map((n) => `${n}×${l.counts[n]}`).join(', ') : (state.lang === 'es' ? 'ninguno' : 'none')}</p></div>
        <div class="space-y-3 avoid-break">
          <p class="eyebrow">${state.lang === 'es' ? 'Cinco Elementos' : 'Five Elements'}</p>
          ${Object.keys(l.elements).map((e) => bar(`${e} <span class="text-zinc-600">· ${E.ELEMENTS[e].theme}</span>`, l.elements[e], maxE)).join('')}
          <div class="card-soft p-4 mt-3"><p class="font-display text-champagne">${state.lang === 'es' ? 'Dominante:' : 'Dominant:'} ${l.dominantElement} <span class="text-zinc-500 text-xs font-sans">(${l.dominantNumber})</span></p><p class="text-[0.8rem] text-zinc-300 mt-1">${ET.text}</p><p class="text-[0.75rem] text-zinc-400 mt-2"><b class="text-gold">${state.lang === 'es' ? 'Activar:' : 'Activate:'}</b> ${ET.activate}</p></div>
        </div>
      </div>
      <div class="grid sm:grid-cols-2 gap-5 mt-6">
        <div class="avoid-break"><p class="eyebrow">${state.lang === 'es' ? 'Flechas de Fortaleza' : 'Arrows of Strength'}</p>${l.arrowsOfStrength.length ? l.arrowsOfStrength.map((a) => `<p class="text-sm mt-2"><span class="text-champagne">${a.name}</span> <span class="text-zinc-600">(${a.nums.join('-')})</span><br/><span class="text-zinc-400 text-[0.8rem]">${C_LANG.ARROW_TEXT[a.key].strong}</span></p>`).join('') : `<p class="text-sm text-zinc-500 mt-2">${state.lang === 'es' ? 'Fortalezas distribuidas de manera equilibrada.' : 'No complete arrows. Strengths are distributed.'}</p>`}</div>
        <div class="avoid-break"><p class="eyebrow">${state.lang === 'es' ? 'Flechas a Desarrollar' : 'Arrows to Develop'}</p>${l.arrowsOfWeakness.length ? l.arrowsOfWeakness.map((a) => `<p class="text-sm mt-2"><span class="text-champagne">${a.name}</span> <span class="text-zinc-600">(${a.nums.join('-')})</span><br/><span class="text-zinc-400 text-[0.8rem]">${C_LANG.ARROW_TEXT[a.key].weak}</span></p>`).join('') : `<p class="text-sm text-zinc-500 mt-2">${state.lang === 'es' ? 'Ningún plano de tu matriz está totalmente ausente.' : 'No empty arrows. Grid is complete.'}</p>`}</div>
      </div>
      ${interp(l.hasWealthEight ? (state.lang === 'es' ? 'El Número de Suprema Riqueza Está Activo' : 'The Supreme Wealth Number Is Present') : (state.lang === 'es' ? 'La Riqueza Debe Forjarse Metódicamente' : 'The Wealth Number Must Be Built'), l.hasWealthEight ? (state.lang === 'es' ? `El 8 (Fa, 發) se manifiesta ${l.counts[8]}× en tu matriz, señalando un canal natural hacia la prosperidad material a través de la Tierra: paciencia, activos reales y la resistencia inquebrantable de la Montaña.` : `The 8 (Fa, 發) appears ${l.counts[8]}× in your grid, signalling a natural channel for prosperity through Earth: patience, real assets and the Mountain's endurance.`) : (state.lang === 'es' ? 'Tu matriz no cuenta con 8 directo. La riqueza se construye activando deliberadamente el elemento Tierra, presupuestos estructurados y vehículos sólidos de acumulación.' : 'Your grid holds no 8. Prosperity is cultivated consciously: activate the Earth element, formalize savings, and work with 8-ruled timing.'))}` });

    /* 12 · SYNTHESIS */
    const bhag = v.bhagyank.ruler, mool = v.moolank.ruler, curT = C_LANG.CYCLE_TEXT[cy.current.index];
    const jup = cy.periods[4], sat = cy.periods[6], sol = cy.periods[0];
    const soulA = PA(p.soulUrge.value), persA = PA(p.personality.value);
    pages.push({ title: state.lang === 'es' ? 'Síntesis Táctica' : 'Tactical Synthesis', html: `
      ${secHead(state.lang === 'es' ? 'Integración Estratégica' : 'Integration', state.lang === 'es' ? 'Cómo Operar con Tu Código' : 'How to Use Your Numbers', state.lang === 'es' ? 'Riqueza, estrategia y magnetismo social sintetizados en un solo código operativo unificado.' : 'Wealth, strategy and social magnetism, synthesized across all five systems into one operating code.')}
      <div class="space-y-5 mt-6">
        <div class="card-soft p-5 avoid-break"><p class="eyebrow">${state.lang === 'es' ? 'I · Arquitectura de Riqueza' : 'I · Wealth'}</p><p class="text-sm text-zinc-300 mt-2">${state.lang === 'es' ? `Tu Motor Secundario es <b class="text-champagne">${a2.number} · ${A2.name}</b>. ${A2.wealth}` : `Your Secondary Engine is <b class="text-champagne">${a2.number} · ${A2.name}</b>. ${A2.wealth}`}</p><p class="text-sm text-zinc-300 mt-2">${state.lang === 'es' ? `Tu regente védico <b class="text-champagne">${bhag.planet}</b> complementa: ${C_LANG.VEDIC_TEXT[v.bhagyank.value]} Tu elemento dominante <b class="text-champagne">${l.dominantElement}</b> orienta tu sector de riqueza hacia el <b class="text-champagne">${ET.direction}</b>.` : `Your Vedic Conductor, <b class="text-champagne">${bhag.planet}</b>, adds: ${C_LANG.VEDIC_TEXT[v.bhagyank.value]} Your dominant <b class="text-champagne">${l.dominantElement}</b> element points your wealth corner to the <b class="text-champagne">${ET.direction}</b>.`}</p></div>
        <div class="card-soft p-5 avoid-break"><p class="eyebrow">${state.lang === 'es' ? 'II · Mando y Estrategia' : 'II · Strategy'}</p><p class="text-sm text-zinc-300 mt-2">${state.lang === 'es' ? `Lidera desde tu Ancla de Firma <b class="text-champagne">${a1.number} · ${A1.name}</b>. ${A1.tactics[0]} ${A1.tactics[1]} Apóyate en tu Fundación <b class="text-champagne">${a3.number} · ${A3.name}</b>: ${sentences(A3.foundation, 2)}` : `Lead from your Signature Anchor <b class="text-champagne">${a1.number} · ${A1.name}</b>. ${A1.tactics[0]} ${A1.tactics[1]} Ground every campaign in your Foundation <b class="text-champagne">${a3.number} · ${A3.name}</b>: ${sentences(A3.foundation, 2)}`}</p><p class="text-sm text-zinc-300 mt-2">${state.lang === 'es' ? `En este momento te encuentras en <b class="text-champagne">${cy.current.name}</b>, una ventana en modo <span class="mode-pill mode-${curT.modeTone}">${curT.mode}</span>.` : `Right now you are in <b class="text-champagne">${cy.current.name}</b>, a <span class="mode-pill mode-${curT.modeTone}">${curT.mode}</span> window.`}</p></div>
        <div class="card-soft p-5 avoid-break"><p class="eyebrow">${state.lang === 'es' ? 'III · Magnetismo Social' : 'III · Social Magnetism'}</p><p class="text-sm text-zinc-300 mt-2">${soulA ? soulA.soul + ' ' : ''}${persA ? persA.persona + ' ' : ''}${A1.magnetism}</p></div>
      </div>
      <div class="mt-6 avoid-break">
        <p class="eyebrow">${state.lang === 'es' ? 'Tu Código Operativo Soberano' : 'Your Sovereign Operating Code'}</p>
        <table class="lux-table mt-2"><tbody>
          <tr><td class="text-zinc-500 w-[42%]">${state.lang === 'es' ? 'Día Primario de Poder' : 'Primary Power Day'}</td><td class="text-champagne">${mool.day} <span class="text-zinc-500">(${mool.planet})</span></td></tr>
          <tr><td class="text-zinc-500">${state.lang === 'es' ? 'Día de Destino' : 'Destiny Day'}</td><td class="text-champagne">${bhag.day} <span class="text-zinc-500">(${bhag.planet})</span></td></tr>
          <tr><td class="text-zinc-500">${state.lang === 'es' ? 'Gema y Colores de Poder' : 'Power Gem · Colours'}</td><td class="text-champagne">${mool.gem} · ${mool.color}</td></tr>
          <tr><td class="text-zinc-500">${state.lang === 'es' ? 'Dirección de Riqueza' : 'Wealth Direction'}</td><td class="text-champagne">${ET.direction} <span class="text-zinc-500">(${l.dominantElement})</span></td></tr>
          <tr><td class="text-zinc-500">${state.lang === 'es' ? 'Año Personal' : 'Personal Year'} ${r.personalYear.year}</td><td class="text-champagne">${r.personalYear.value} <span class="text-zinc-500">· ${C_LANG.PERSONAL_YEAR[r.personalYear.value]}</span></td></tr>
          <tr><td class="text-zinc-500">${state.lang === 'es' ? 'Ventana Anual de Riqueza' : 'Annual Wealth Window'}</td><td class="text-champagne">${full ? `${jup.startLabel} – ${jup.endLabel}` : `${LOCK_SVG.replace('width="16" height="16"', 'width="11" height="11"')} Módulo de Ciclos`}</td></tr>
          <tr><td class="text-zinc-500">${state.lang === 'es' ? 'Ventana de Preservación de Capital' : 'Capital Preservation Window'}</td><td class="text-champagne">${full ? `${sat.startLabel} – ${sat.endLabel}` : `${LOCK_SVG.replace('width="16" height="16"', 'width="11" height="11"')} Módulo de Ciclos`}</td></tr>
        </tbody></table>
      </div>` });

    /* 13–14 · CYCLES */
    if (full) {
      const nx = cy.next;
      pages.push({ title: state.lang === 'es' ? 'Ciclos Rosacruces' : 'Rosicrucian Cycles', html: `
        ${secHead(state.lang === 'es' ? 'Módulo Especial · Los Ciclos de la Vida' : 'Bonus Module · The Cycles of Life', state.lang === 'es' ? 'Tu Calendario Rosacruz de 365 Días' : 'Your 365-Day Rosicrucian Calendar', state.lang === 'es' ? `Basado en H. Spencer Lewis, <i>Las Leyes del Éxito y los Ciclos de la Vida</i>. Tu año personal transcurre de ${cy.birthdayStartLabel} a ${cy.nextBirthdayLabel} dividido en siete períodos planetarios de ~52 días.` : `After H. Spencer Lewis, <i>Self Mastery and Fate with the Cycles of Life</i>. Your personal year runs from ${cy.birthdayStartLabel} to ${cy.nextBirthdayLabel} and is divided into seven ~52-day periods, each governed by a planetary influence.`)}
        <div class="card-soft p-5 mt-6 avoid-break" style="border-color:rgba(212,175,55,.5)">
          <div class="flex flex-col sm:flex-row sm:items-center gap-4">
            <div class="text-5xl text-gold font-display leading-none">${cy.current.glyph}</div>
            <div class="flex-1">
              <p class="text-[0.58rem] tracking-[0.22em] uppercase text-gold">${state.lang === 'es' ? 'Activo Hoy' : 'Active Today'} · ${currentLabel} · ${state.lang === 'es' ? `Día ${cy.dayOfYear} de ${cy.yearLength}` : `Day ${cy.dayOfYear} of ${cy.yearLength}`}</p>
              <p class="font-display text-xl mt-1">${state.lang === 'es' ? 'Ciclo' : 'Cycle'} ${cy.current.n}: ${cy.current.name}</p>
              <p class="text-xs text-zinc-400 mt-0.5">${cy.current.startLabel} – ${cy.current.endLabel} · ${cy.daysRemaining} ${state.lang === 'es' ? (cy.daysRemaining === 1 ? 'día restante' : 'días restantes') : (cy.daysRemaining === 1 ? 'day remaining' : 'days remaining')}</p>
            </div>
            <span class="mode-pill mode-${curT.modeTone} self-start sm:self-center">${curT.mode}</span>
          </div>
          <div class="bar-track mt-4"><div class="bar-fill" style="width:${cy.progress}%"></div></div>
        </div>
        <table class="lux-table mt-6"><thead><tr><th></th><th>${state.lang === 'es' ? 'Período' : 'Period'}</th><th>${state.lang === 'es' ? 'Fechas' : 'Dates'}</th><th>${state.lang === 'es' ? 'Modo Táctico' : 'Mode'}</th></tr></thead><tbody>${cy.periods.map(c => cycleRow(c, C_LANG)).join('')}</tbody></table>` });

      pages.push({ title: state.lang === 'es' ? 'Directivas del Ciclo Activo' : 'Current Cycle Brief', html: `
        ${secHead(state.lang === 'es' ? `Informe Táctico · Ciclo ${cy.current.n} de 7` : `Tactical Brief · Cycle ${cy.current.n} of 7`, `${cy.current.name}: ${state.lang === 'es' ? 'Tus Directivas' : 'Your Directives'}`, curT.directive)}
        <div class="grid sm:grid-cols-2 gap-4 mt-6">
          <div class="card-soft p-5 avoid-break"><p class="eyebrow">${state.lang === 'es' ? 'Avanzar / Ejecutar' : 'Press / Execute'}</p><ul class="mt-3 space-y-2 text-sm text-zinc-300">${curT.do.map((d) => `<li class="flex">${CHECK}<span>${d}</span></li>`).join('')}</ul></div>
          <div class="card-soft p-5 avoid-break"><p class="eyebrow !text-rose-300/80">${state.lang === 'es' ? 'Evitar / Proteger' : 'Avoid'}</p><ul class="mt-3 space-y-2 text-sm text-zinc-300">${curT.avoid.map((d) => `<li class="flex"><span class="text-rose-300/70 mr-2">✕</span><span>${d}</span></li>`).join('')}</ul></div>
        </div>
        ${interp(state.lang === 'es' ? 'Alineación Estratégica' : 'Personalized Overlay', state.lang === 'es' ? `Filtra este ciclo a través de tu Ancla de Firma ${a1.number} (${A1.name}): ${A1.tactics[2]} Permite que tu Motor de Riqueza ${a2.number} (${A2.name}) trace el vehículo, y tu Fundación ${a3.number} (${A3.name}) fije los límites inquebrantables.` : `Run this cycle through your Signature Anchor ${a1.number} (${A1.name}): ${A1.tactics[2]} Let your Wealth Engine ${a2.number} (${A2.name}) set the vehicle, and your Foundation ${a3.number} (${A3.name}) set the guardrails.`)}
        ${nx ? `<div class="card-soft p-4 mt-5 avoid-break"><p class="text-[0.58rem] tracking-[0.2em] uppercase text-zinc-500">${state.lang === 'es' ? 'Siguiente período · inicia' : 'Next · begins'} ${nx.startLabel}</p><p class="font-display text-champagne mt-1">${nx.glyph} ${nx.name} <span class="mode-pill mode-${C_LANG.CYCLE_TEXT[nx.index].modeTone} ml-2">${C_LANG.CYCLE_TEXT[nx.index].mode}</span></p><p class="text-[0.8rem] text-zinc-400 mt-1">${nx.theme}</p></div>` : `<div class="card-soft p-4 mt-5 avoid-break"><p class="text-[0.58rem] tracking-[0.2em] uppercase text-zinc-500">${state.lang === 'es' ? 'Siguiente ciclo · inicia' : 'Next · begins'} ${cy.nextBirthdayLabel}</p><p class="font-display text-champagne mt-1">☉ ${state.lang === 'es' ? 'Un nuevo Período Solar inaugurará tu próximo año personal.' : 'A new Solar Period opens your next personal year.'}</p></div>`}
        <div class="mt-7 avoid-break">
          <p class="eyebrow">${state.lang === 'es' ? 'Mapa Anual de Acción' : 'Annual Action Map'}</p>
          <div class="grid sm:grid-cols-2 gap-4 mt-3">
            <div class="card-soft p-4"><p class="font-display text-champagne text-sm">${state.lang === 'es' ? 'Ventanas de Máxima Expansión' : 'High-Wealth Action Windows'}</p>${[sol, cy.periods[2], jup].map((c) => `<p class="text-[0.8rem] text-zinc-300 mt-2">${c.glyph} ${c.name.replace('The ', '').replace('El ', '')}<br/><span class="text-zinc-500 text-[0.72rem]">${c.startLabel} – ${c.endLabel}</span></p>`).join('')}</div>
            <div class="card-soft p-4"><p class="font-display text-champagne text-sm">${state.lang === 'es' ? 'Calibrar · Construir · Preservar' : 'Calibrate · Build · Preserve'}</p>${[cy.periods[1], cy.periods[3], cy.periods[5], sat].map((c) => `<p class="text-[0.8rem] text-zinc-300 mt-2">${c.glyph} ${c.name.replace('The ', '').replace('El ', '')} <span class="mode-pill mode-${C_LANG.CYCLE_TEXT[c.index].modeTone} !text-[0.5rem] ml-1">${C_LANG.CYCLE_TEXT[c.index].mode}</span><br/><span class="text-zinc-500 text-[0.72rem]">${c.startLabel} – ${c.endLabel}</span></p>`).join('')}</div>
          </div>
        </div>` });
    } else {
      pages.push({ title: state.lang === 'es' ? 'Ciclos Rosacruces' : 'Rosicrucian Cycles', html: `
        ${secHead(state.lang === 'es' ? 'Módulo Especial · Los Ciclos de la Vida' : 'Bonus Module · The Cycles of Life', state.lang === 'es' ? 'Tu Calendario Rosacruz de 365 Días' : 'Your 365-Day Rosicrucian Calendar', state.lang === 'es' ? 'Siete períodos planetarios de ~52 días de cumpleaños a cumpleaños. Conoce con precisión cuándo avanzar con audacia y cuándo proteger la bóveda.' : 'Seven ~52-day planetary periods running from birthday to birthday. Know exactly when to press edges and when to protect the vault.')}
        <div class="locked mt-8 rounded-xl">
          <div class="locked-content"><table class="lux-table"><tbody>${E.CYCLES.map((c) => `<tr><td class="font-display text-gold">${c.glyph}</td><td>${c.name}<div class="text-xs text-zinc-500">${c.theme}</div></td><td class="text-xs">◆◆◆ ◆◆, ◆◆◆◆</td></tr>`).join('')}</tbody></table></div>
          <div class="lock-overlay">
            <div class="lock-icon">${LOCK_SVG}</div>
            <p class="font-display text-champagne">${state.lang === 'es' ? 'Calendario de Ciclos No Incluido' : 'Cycles Calendar Not Included'}</p>
            <p class="text-xs text-zinc-400 max-w-xs">${state.lang === 'es' ? `Tu ciclo activo concluye en <b class="text-gold">${cy.daysRemaining} días</b>. Añade tu calendario con fechas y directivas personalizadas.` : `Your current window closes in <b class="text-gold">${cy.daysRemaining} days</b>. Add your personalized calendar with exact dates and directives.`}</p>
            <button type="button" data-action="upgrade" class="btn-gold no-print !w-auto !py-3 !px-5 mt-2">${state.lang === 'es' ? 'Añadir Calendario de Ciclos · ' : 'Add Cycles Calendar · '}${money(CONFIG.PRICE_BUMP)}</button>
          </div>
        </div>` });
    }

    /* 15 · CODEX */
    const coreRows = [
      [state.lang === 'es' ? 'Sendero de Vida' : 'Life Path', 'Pythagorean', p.lifePath.display],
      [state.lang === 'es' ? 'Expresión' : 'Expression', 'Pythagorean', p.expression.display],
      [state.lang === 'es' ? 'Deseo del Alma' : 'Soul Urge', 'Pythagorean', p.soulUrge.display],
      [state.lang === 'es' ? 'Personalidad' : 'Personality', 'Pythagorean', p.personality.display],
      [state.lang === 'es' ? 'Nombre Completo' : 'Full Name', 'Chaldean', ch.total.display],
      [state.lang === 'es' ? 'Moolank · Bhagyank · Namank' : 'Moolank · Bhagyank · Namank', 'Vedic', `${v.moolank.value} · ${v.bhagyank.value} · ${v.namank.value}`],
      [state.lang === 'es' ? 'Columna Dominante' : 'Dominant Pillar', 'Kabbalistic', k.dominantPillar],
      [state.lang === 'es' ? 'Elemento Dominante' : 'Dominant Element', 'Lo Shu', `${l.dominantElement} (${l.dominantNumber})`],
    ];

    const codexQuote = state.lang === 'es'
      ? `“Soy ${A1.name}. Construyo mediante ${A2.keywords[0].toLowerCase()}, y me sostengo en ${A3.keywords[0].toLowerCase()}. Me muevo con mis ciclos, nunca contra ellos.”`
      : `“I am ${A1.name.replace('The ', 'the ')}. I build through ${A2.keywords[0].toLowerCase()}, and I stand on ${A3.keywords[0].toLowerCase()}. I move with my cycles, not against them.”`;

    pages.push({ title: state.lang === 'es' ? 'El Códice Soberano' : 'The Sovereign Codex', html: `
      ${secHead(UI.codex_eyebrow, UI.codex_title, UI.codex_lead)}
      <div class="flex justify-center gap-6 sm:gap-10 mt-8 avoid-break">
        ${r.overlap.anchors.map((a, i) => `
          <div class="text-center">
            ${medal(a.number, 'md')}
            <p class="font-display text-[0.8rem] mt-3">${C_LANG.ARCHETYPES[a.number].name}</p>
            <p class="text-[0.55rem] tracking-[0.2em] uppercase text-zinc-500">${[UI.signature_role, UI.wealth_role, UI.foundation_role][i]}</p>
          </div>`).join('')}
      </div>

      <!-- Codex Secondary Harmonics -->
      <div class="flex justify-center items-center gap-6 mt-4 py-2 border-y border-gold/15 text-xs text-zinc-400 avoid-break">
        <span class="text-[0.65rem] uppercase tracking-widest text-gold font-semibold">${UI.secondary_harmonics}:</span>
        ${r.overlap.secondaryHarmonics.map(h => `
          <span class="text-zinc-300"><b class="text-champagne font-display mr-1">${h.number}</b> ${C_LANG.ARCHETYPES[h.number].name} <span class="text-zinc-500 text-[0.7rem]">(${h.count}×)</span></span>
        `).join('')}
      </div>

      <table class="lux-table mt-6"><thead><tr><th>${state.lang === 'es' ? 'Cifra' : 'Number'}</th><th>${state.lang === 'es' ? 'Sistema' : 'System'}</th><th>${state.lang === 'es' ? 'Valor' : 'Value'}</th></tr></thead><tbody>${coreRows.map((rw) => `<tr><td class="text-zinc-300">${rw[0]}</td><td class="text-zinc-500 text-xs">${translateSystem(rw[1])}</td><td class="font-display text-gold">${rw[2]}</td></tr>`).join('')}</tbody></table>
      <div class="text-center mt-8 avoid-break">
        <p class="font-serif italic text-2xl text-champagne leading-snug">${codexQuote}</p>
        <div class="hairline my-6 mx-auto" style="max-width:200px"></div>
        <p class="font-display tracking-[0.3em] text-sm text-gold">${name.toUpperCase()}</p>
      </div>
      <p class="text-[0.62rem] text-zinc-600 mt-8 leading-relaxed text-center">${UI.codex_disclaimer}</p>` });

    return pages;
  }

  function renderDossier() {
    const r = state.result, tier = state.profile.tier || 'full';
    const C_LANG = C.get(state.lang);
    const UI = C_LANG.UI;
    const pages = buildDossierPages(r, tier);
    const total = pages.length;
    const name = esc(r.input.fullName);

    // Contents page (index 1)
    pages[1].html = `
      ${secHead(UI.method_eyebrow, UI.method_title, UI.method_lead)}
      <div class="grid sm:grid-cols-5 gap-2 mt-6">
        ${C_LANG.SYSTEM_INFO.map((s, i) => `<div class="card-soft p-3 avoid-break"><p class="font-display text-gold">${ROMAN[i]}</p><p class="font-display text-[0.8rem] mt-1">${s.name}</p><p class="text-[0.68rem] text-zinc-500 mt-1 leading-snug">${s.blurb}</p></div>`).join('')}
      </div>
      <p class="eyebrow mt-9">${UI.contents_eyebrow}</p>
      <div class="card-soft p-4 mt-3 avoid-break">
        <ol class="space-y-1.5 text-xs text-zinc-300">
          ${pages.map((p, i) => `
            <li class="flex justify-between items-baseline border-b border-white/5 py-1">
              <span class="text-zinc-400"><b class="font-mono text-gold mr-2">${String(i + 1).padStart(2, '0')}</b> ${p.title}</span>
              <span class="font-mono text-[0.7rem] text-zinc-600">${state.lang === 'es' ? 'Pág.' : 'Page'} ${i + 1}</span>
            </li>`).join('')}
        </ol>
      </div>`;

    const html = pages.map((p, i) => {
      const isCover = p.cover;
      const head = isCover ? '' : `<div class="page-head"><span>${state.lang === 'es' ? 'EL PLANO SOBERANO' : 'SOVEREIGN 5-SYSTEM'}</span><span class="hidden sm:inline">${name}</span><span>${p.title}</span></div>`;
      const foot = isCover ? '' : `<div class="page-foot"><span>${state.lang === 'es' ? 'CONFIDENCIAL' : 'CONFIDENTIAL'}</span><span>${state.lang === 'es' ? 'PÁG.' : 'PAGE'} ${i + 1} / ${total}</span></div>`;
      return `
      <article class="page ${isCover ? 'cover' : ''}" data-page="${i + 1}">
        ${head}
        ${p.html}
        ${foot}
      </article>`;
    }).join('');

    $('#dossier-root').innerHTML = html;
  }

  function openDossier() {
    showView('dossier');
    renderDossier();
  }

  /* =====================================================================
     EVENTS + INIT
     ===================================================================== */
  document.addEventListener('click', (e) => {
    // Language switcher buttons
    const langBtn = e.target.closest('[data-lang]');
    if (langBtn) {
      setLanguage(langBtn.dataset.lang);
      return;
    }

    const t = e.target.closest('[data-action]');
    if (!t) return;
    const a = t.dataset.action;
    if (a === 'sample') { fillForm(CONFIG.SAMPLE); showErrors({}); }
    else if (a === 'home') { if (state.profile) fillForm(state.profile); showView('hero'); }
    else if (a === 'restart') {
      fillForm({});
      showView('hero');
      document.title = state.lang === 'es'
        ? 'El Plano Soberano · Numerología de los 5 Sistemas y Ciclos Rosacruces'
        : 'The Sovereign 5-System Blueprint';
    }
    else if (a === 'checkout') checkout();
    else if (a === 'demo-unlock') demoUnlock();
    else if (a === 'print') window.print();
    else if (a === 'scroll-checkout') $('#checkout').scrollIntoView({ behavior: 'smooth', block: 'start' });
    else if (a === 'upgrade') {
      if (CONFIG.STRIPE_LINK_UPGRADE) goToStripe(CONFIG.STRIPE_LINK_UPGRADE, 'full');
      else if (CONFIG.DEMO_MODE) {
        state.profile.tier = 'full';
        saveProfile(state.profile);
        renderDossier();
        toast(state.lang === 'es' ? '✦ Demo: Calendario de Ciclos desbloqueado.' : '✦ Demo: Cycles Calendar unlocked.');
      }
      else toast('Upgrade link not configured (CONFIG.STRIPE_LINK_UPGRADE).');
    }
  });

  document.addEventListener('change', (e) => { if (e.target && e.target.id === 'bump') updateTotal(); });

  // Handle claim form submission (for paying customers on a new device or without localStorage)
  const claimForm = $('#claim-form');
  if (claimForm) {
    claimForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const cName = $('#claimFullName').value.trim();
      const cDob = $('#claimBirthDate').value;
      const chk = E.validate(cName, cDob);
      if (!chk.valid) {
        toast(state.lang === 'es' ? 'Por favor ingresa un nombre y fecha de nacimiento válidos.' : 'Please enter a valid name and birth date.');
        return;
      }
      const prof = {
        id: leadId(),
        fullName: cName,
        birthDate: cDob,
        email: '',
        tier: state.pendingTier || 'full',
        createdAt: new Date().toISOString(),
        utm: utm(),
      };
      state.profile = prof;
      saveProfile(prof);
      state.result = E.calculate(prof.fullName, prof.birthDate);
      $('#claim-bar').classList.add('hidden');
      $('#dossier-actions').classList.remove('hidden');
      renderDossier();
      toast(state.lang === 'es' ? '✦ ¡Dossier generado con éxito! Haz clic en "Descargar / Imprimir PDF" para guardar tu archivo.' : '✦ Dossier generated successfully! Click "Download / Print Luxury PDF" to save your file.', 6000);
    });
  }

  function init() {
    $('#year').textContent = new Date().getFullYear();

    // Check VIP Founder access (?vip=adam)
    const q = new URLSearchParams(location.search);
    if (q.get('vip') === 'adam') {
      store.set(KEYS.vip, true);
      state.isVip = true;
    } else if (store.get(KEYS.vip) === true) {
      state.isVip = true;
    }

    if (state.isVip) {
      const headerNav = $('.lang-switch') ? $('.lang-switch').parentElement : null;
      if (headerNav && !$('#vip-badge')) {
        const vipSpan = document.createElement('span');
        vipSpan.id = 'vip-badge';
        vipSpan.className = 'badge-gold !text-[0.62rem] !py-0.5 hidden sm:inline-flex';
        vipSpan.textContent = '★ VIP Founder';
        headerNav.insertBefore(vipSpan, headerNav.firstChild);
      }
    }

    // Set initial language
    setLanguage(state.lang);

    $('#calc-form').addEventListener('submit', onSubmit);

    // Determine target tier from URL (?tier=base&unlocked=true, ?tier=full&unlocked=true)
    const isUnlockedParam = q.get('unlocked') === 'true';
    const tierParam = q.get('tier'); // 'base' | 'full'
    let urlTier = null;
    if (tierParam === 'full') urlTier = 'full';
    else if (tierParam === 'base') urlTier = 'base';
    else if (isUnlockedParam) urlTier = store.get(KEYS.pending) || 'full';

    if (urlTier === 'base' && store.get(KEYS.pending) === 'full') urlTier = 'full';
    if (urlTier) store.del(KEYS.pending);

    let prof = store.get(KEYS.profile);
    // Optional deep-link prefill: ?name=Adam%20Vega&dob=1978-08-19&email=...
    if (q.get('name') && q.get('dob') && E.validate(q.get('name'), q.get('dob')).valid) {
      const same = prof && prof.fullName === q.get('name') && prof.birthDate === q.get('dob');
      prof = same ? prof : { id: leadId(), fullName: q.get('name'), birthDate: q.get('dob'), email: q.get('email') || '', tier: urlTier || null, createdAt: new Date().toISOString(), utm: utm() };
    }

    if (prof && E.validate(prof.fullName, prof.birthDate).valid) {
      fillForm(prof);
      if (urlTier) prof.tier = maxTier(prof.tier, urlTier);
      state.profile = prof;
      saveProfile(prof);
      if (prof.tier) {
        state.result = E.calculate(prof.fullName, prof.birthDate);
        if (urlTier) sendWebhook('purchase_return');
        openDossier();
        if (urlTier) {
          toast(state.lang === 'es' ? '✦ ¡Acceso confirmado! Haz clic en "Descargar / Imprimir PDF" para guardar tu dossier.' : '✦ Access confirmed! Click "Download / Print Luxury PDF" to save your dossier.', 6000);
        }
        return;
      }
    } else if (urlTier) {
      // Paying customer arrived with unlocked=true or tier=base/full on a device WITHOUT localStorage!
      state.pendingTier = urlTier;
      showView('dossier');
      $('#claim-bar').classList.remove('hidden');
      $('#dossier-actions').classList.add('hidden');
      $('#dossier-root').innerHTML = '';
      toast(state.lang === 'es' ? '✦ Pago confirmado. Ingresa tus datos para generar tu PDF desbloqueado.' : '✦ Payment confirmed. Enter your details to generate your unlocked PDF.', 6000);
      return;
    }
    showView('hero');
  }

  init();
})();
