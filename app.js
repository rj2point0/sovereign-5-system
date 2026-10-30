/* =====================================================================
   SOVEREIGN 5-SYSTEM — app.js  (funnel + checkout + dossier renderer)
   Bilingual Edition: English (EN) & Spanish (ES)
   ===================================================================== */
const CONFIG = {
  STRIPE_LINK_BASE: 'https://buy.stripe.com/6oU7sLek90MdbVechV38401',
  STRIPE_LINK_BUMP: 'https://buy.stripe.com/eVq28r2Br9iJe3mbdR38402',
  STRIPE_LINK_UPGRADE: 'https://buy.stripe.com/28E6oHb7X3Yp2kEgyb38403',

  PRICE_BASE: 37,
  PRICE_BUMP: 47,
  PRICE_ANCHOR: 197,           // struck-through "value" price
  GUARANTEE_DAYS: 30,          // set 0 to hide the guarantee badge

  WEBHOOK_URL: 'https://ntfy.sh/sovereign_5_leads_mvv_991214754',
  LOCAL_WEBHOOK_URL: (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'))
    ? 'http://127.0.0.1:8788/webhook'
    : '',
  VSL_URL: 'assets/vsl_briefing.mp4',
  VSL_POSTER: 'assets/vsl_poster.jpg',

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
    partnerDob: '',
    bump: false,
    pendingTier: null,
    lang: initialLang,
    isVip: false,
  };

  const DOSSIER_SECTIONS_EN = [
    'Cover & Big Three Master Overlap Medallions',
    'The Secret of the 5 Ancient Lenses (Convergence Mandala)',
    'The 5 Ancient Systems & 20-Page Table of Contents',
    'Your Big Three Master Overlap Anchors & Frequency Tally',
    'The Complete 15-Point Cross-System Calculation Ledger',
    'Anchor #1 Deep-Dive · Soul Magnetism & True Essence',
    'Anchor #2 Deep-Dive · Wealth Engine & Manifestation Flow',
    'Anchor #3 Deep-Dive · Sanctuary & Nervous System Guardrails',
    'System I · Pythagorean Core Numbers & 4-Box Math Breakdown',
    'System II · Babylonian Chaldean Compound Sound Analysis',
    'System III · Kabbalah Part 1: Tree of Life & Pillar Balance',
    'System III · Kabbalah Part 2: Your 5 Illuminated Sephirot',
    'System IV · Vedic Planetary Council (Moolank, Bhagyank, Namank)',
    'System V · Imperial Chinese Lo Shu Magic Square & Wu Xing',
    'Somatic Vitality, Nervous System & 5-Element Health Blueprint',
    'Integration Part 1 · The 4 Sovereign Pillars of Power',
    'Integration Part 2 · Your Daily Sovereign Operating Code',
    'Bonus Module · 365-Day Rosicrucian Cycles Calendar*',
    'Tactical Brief · Active 52-Day Cycle Directives & Annual Action Map*',
    'Closing · The Sovereign Codex Master Seal & Personal Mantra',
  ];

  const DOSSIER_SECTIONS_ES = [
    'Portada y Medallones de Coincidencia Maestra',
    'El Secreto de los 5 Lentes Ancestrales (Mandala de Convergencia)',
    'Los 5 Sistemas y Tabla de Contenidos de 20 Páginas',
    'Tus Tres Anclas de Coincidencia Maestra y Frecuencias',
    'El Registro Completo de 15 Cálculos y Reducciones',
    'Análisis Profundo Ancla #1 · Magnetismo del Alma y Esencia',
    'Análisis Profundo Ancla #2 · Motor de Riqueza y Manifestación',
    'Análisis Profundo Ancla #3 · Santuario y Sistema Nervioso',
    'Sistema I · Números Esenciales Pitagóricos y Desglose Matemático',
    'Sistema II · Análisis de Compuestos Caldeos Babilónicos',
    'Sistema III · Cábala Parte 1: Árbol de la Vida y Columnas',
    'Sistema III · Cábala Parte 2: Tus 5 Esferas Sephirot Iluminadas',
    'Sistema IV · Consejo Planetario Védico (Moolank, Bhagyank, Namank)',
    'Sistema V · Cuadrado Mágico Lo Shu y Cinco Elementos Wu Xing',
    'Vitalidad Somática, Sistema Nervioso y Salud Elemental',
    'Integración Parte 1 · Los 4 Pilares Soberanos de Poder',
    'Integración Parte 2 · Tu Código Operativo Diario y Alineación',
    'Módulo Especial · Calendario Rosacruz de 365 Días (7 Ciclos)*',
    'Informe Táctico · Directivas del Ciclo Activo y Mapa Anual*',
    'Cierre · El Sello Maestro del Códice Soberano y Mantra Personal',
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

    // Re-populate DOB month dropdown labels for current language
    initDobDropdowns();

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
      if (UI[key] !== undefined) {
        el.innerHTML = UI[key].replace('${year}', new Date().getFullYear());
      }
    });

    $$('[data-i18n-ph]').forEach((el) => {
      const key = el.dataset.i18nPh;
      if (UI[key]) el.placeholder = UI[key];
    });

    // Update page title
    document.title = state.lang === 'es'
      ? 'Descubre Tu Patrón Oculto de Pareja y Código de Amor'
      : 'Uncover Your Hidden Relationship Pattern & Love Code';
  }

  /* ---------------- lead capture & funnel telemetry ---------------- */
  function leadId() { return 'lead_' + Math.random().toString(36).slice(2, 9); }
  function sessionId() {
    let sid = store.get('s5_session_id');
    if (!sid) {
      sid = 'sess_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 7);
      store.set('s5_session_id', sid);
    }
    return sid;
  }
  function isAutomatedOrLocalTest() {
    const q = new URLSearchParams(location.search);
    if (q.get('force_telemetry') === '1') return false;
    const host = (location.hostname || '').toLowerCase();
    const isLocal = host === 'localhost' || host === '127.0.0.1' || host === '0.0.0.0' || host === '';
    const isBot = Boolean(navigator.webdriver) || /HeadlessChrome|Playwright|PhantomJS/i.test(navigator.userAgent || '');
    return isLocal || isBot;
  }
  function detectBrowserEnv() {
    const ua = navigator.userAgent || '';
    const isTikTok = /BytedanceWebview|musical_ly|TikTok|trill|ByteLocale/i.test(ua);
    const isIG = /Instagram/i.test(ua);
    const isFB = /FBAN|FBAV/i.test(ua);
    const isIOS = /iPhone|iPad|iPod/i.test(ua);
    const isAndroid = /Android/i.test(ua);
    const isMobile = isIOS || isAndroid || /Mobile/i.test(ua);
    const osTag = isIOS ? 'iOS' : (isAndroid ? 'Android' : (isMobile ? 'Mobile' : 'Desktop'));
    let browserLabel = osTag + ' Browser';
    if (isTikTok) browserLabel = `TikTok In-App (${osTag})`;
    else if (isIG) browserLabel = `Instagram In-App (${osTag})`;
    else if (isFB) browserLabel = `Facebook In-App (${osTag})`;
    else if (/CriOS|Chrome/i.test(ua) && !/Edg/i.test(ua)) browserLabel = `${osTag} Chrome`;
    else if (/Safari/i.test(ua) && !/Chrome|CriOS/i.test(ua)) browserLabel = `${osTag} Safari`;
    return {
      user_agent: ua,
      is_tiktok_inapp: isTikTok,
      is_instagram_inapp: isIG,
      device_type: isMobile ? 'Mobile' : 'Desktop',
      browser_label: browserLabel,
      referrer: document.referrer || 'Direct / Bio Link',
    };
  }
  function utm() {
    const q = new URLSearchParams(location.search);
    const cached = store.get('sovereign5_utm_v1') || {};
    const u = Object.assign({}, cached);
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'cohort', 'ttclid'].forEach((k) => {
      if (q.get(k)) u[k] = q.get(k);
    });
    if (Object.keys(u).length > 0) {
      store.set('sovereign5_utm_v1', u);
    }
    return u;
  }
  function saveProfile(p) {
    store.set(KEYS.profile, p);
    const leads = store.get(KEYS.leads) || [];
    const idx = leads.findIndex((l) => l.id === p.id);
    if (idx >= 0) leads[idx] = p; else leads.push(p);
    store.set(KEYS.leads, leads);
  }
  function sendWebhook(event, extra, customProfile) {
    if (!CONFIG.WEBHOOK_URL && !CONFIG.LOCAL_WEBHOOK_URL) return;
    try {
      const envInfo = detectBrowserEnv();
      const skipPublicRelay = isAutomatedOrLocalTest();
      const activeProf = customProfile || state.profile || {};
      const r = (customProfile && customProfile.fullName && customProfile.birthDate)
        ? E.calculate(customProfile.fullName, customProfile.birthDate)
        : (state.result || (activeProf.fullName && activeProf.birthDate ? E.calculate(activeProf.fullName, activeProf.birthDate) : null));
      const C_LANG = C.get(state.lang || 'en');
      const anchors = r && r.overlap && r.overlap.anchors ? r.overlap.anchors.slice(0, 3).map((a) => ({
        number: a.number,
        archetype: (C_LANG.ARCHETYPES[a.number] || {}).name || ('#' + a.number),
        count: a.count,
        systems: a.systems,
      })) : [];
      const top3Str = anchors.map((a) => a.number).join(', ');
      const activeUtm = Object.assign({}, activeProf.utm || {}, utm());
      const partnerDobVal = (extra && extra.partner_dob) || state.partnerDob || activeProf.partner_dob || activeProf.partnerDob || '';
      const mergedExtra = Object.assign({}, extra || {});
      if (partnerDobVal && !mergedExtra.partner_dob) mergedExtra.partner_dob = partnerDobVal;
      const mergedProfile = Object.assign({}, activeProf, { utm: activeUtm });
      if (partnerDobVal) {
        mergedProfile.partner_dob = partnerDobVal;
        mergedProfile.partnerDob = partnerDobVal;
      }

      const payload = {
        event,
        event_type: event,
        session_id: sessionId(),
        timestamp: new Date().toISOString(),
        lang: state.lang || 'en',
        referrer: envInfo.referrer,
        user_agent: envInfo.user_agent,
        browser_label: envInfo.browser_label,
        is_tiktok_inapp: envInfo.is_tiktok_inapp,
        is_instagram_inapp: envInfo.is_instagram_inapp,
        device_type: envInfo.device_type,
        utm: activeUtm,
        utm_source: activeUtm.utm_source || '',
        utm_medium: activeUtm.utm_medium || '',
        utm_campaign: activeUtm.utm_campaign || '',
        cohort: activeUtm.cohort || '',
        partner_dob: partnerDobVal,
        profile: mergedProfile,
        numbers: r ? {
          top_3_overlap_numbers: top3Str,
          anchors,
          life_path: r.pythagorean.lifePath.display,
          expression: r.pythagorean.expression.display,
          soul_urge: r.pythagorean.soulUrge.display,
          vedic_moolank: `${r.vedic.moolank.value} · ${r.vedic.moolank.ruler.planet} (${r.vedic.moolank.ruler.english})`,
          vedic_bhagyank: `${r.vedic.bhagyank.value} · ${r.vedic.bhagyank.ruler.planet} (${r.vedic.bhagyank.ruler.english})`,
          chaldean_name: r.chaldean.total.display,
          active_cycle: `${r.cycles.current.name} (${r.cycles.daysRemaining}d remaining)`,
        } : {},
        extra: mergedExtra,
      };
      const bodyStr = JSON.stringify(payload);
      const hostNow = (location.hostname || '').toLowerCase();
      const isLocalHostNow = hostNow === 'localhost' || hostNow === '127.0.0.1';
      if (CONFIG.WEBHOOK_URL && !skipPublicRelay) {
        fetch(CONFIG.WEBHOOK_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain;charset=UTF-8', 'Title': `S5 [${event}]: ${activeProf.fullName || envInfo.browser_label}` },
          body: bodyStr,
          keepalive: true,
        }).catch(() => {});
      }
      if (CONFIG.LOCAL_WEBHOOK_URL && isLocalHostNow && !skipPublicRelay) {
        fetch(CONFIG.LOCAL_WEBHOOK_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: bodyStr,
          mode: 'no-cors',
          keepalive: true,
        }).catch(() => {});
      }
    } catch (e) { /* ignore */ }
  }

  function syncDobValueOnly() {
    const mEl = $('#dobMonth');
    const dEl = $('#dobDay');
    const yEl = $('#dobYear');
    const dobInput = $('#birthDate');
    if (!mEl || !dEl || !yEl || !dobInput) return;
    const m = mEl.value;
    const d = dEl.value;
    const y = yEl.value;
    if (m && d && y) {
      dobInput.value = `${y}-${m}-${d}`;
    }
  }

  let _lastPreviewKey = '';
  function maybeFireCalcPreview(triggerSource) {
    try {
      syncDobValueOnly();
      const fNameEl = $('#fullName');
      const dobEl = $('#birthDate');
      if (!fNameEl || !dobEl) return;
      const fName = fNameEl.value.trim();
      const dob = dobEl.value.trim();
      if (!fName || !dob) return;
      const chk = E.validate(fName, dob);
      if (!chk.valid) return;
      const key = `${fName.toLowerCase()}::${dob}`;
      if (key === _lastPreviewKey) return;
      _lastPreviewKey = key;
      const emailEl = $('#email');
      const em = emailEl ? emailEl.value.trim() : '';
      sendWebhook('calc_preview', { trigger: triggerSource || 'field_blur' }, {
        id: (state.profile && state.profile.id) || leadId(),
        fullName: fName,
        birthDate: dob,
        email: em,
        utm: utm(),
      });
    } catch (e) { /* ignore */ }
  }

  /* ---------------- toast ---------------- */
  let toastTimer = null;
  function toast(html, duration) {
    if (window._disableToast) return;
    const el = $('#toast');
    if (!el) return;
    el.innerHTML = html;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('show'), duration || 3600);
  }
  window.toast = toast;

  /* ---------------- viral share ---------------- */
  function shareCode() {
    const anchor1 = state.result && state.result.overlap && state.result.overlap.anchors && state.result.overlap.anchors[0]
      ? state.result.overlap.anchors[0].number
      : (state.profile && state.profile.anchor1 ? state.profile.anchor1 : '7');
    const shareTitle = 'The Sovereign Blueprint';
    const shareUrl = 'https://blueprint.megavegaventures.com/';
    const shareText = state.lang === 'es'
      ? `Acabo de analizar mi nombre y fecha de nacimiento en los 5 sistemas ancestrales — mi Ancla de Coincidencia Maestra es #${anchor1}. Descifra el tuyo aquí:`
      : `I just ran my name and birth date through all 5 ancient numerology systems — my Master Overlap Anchor is #${anchor1}. Run yours here:`;

    if (navigator.share) {
      navigator.share({
        title: shareTitle,
        text: shareText,
        url: shareUrl
      }).catch((err) => {
        if (err && err.name !== 'AbortError') {
          copyShareLink(shareUrl);
        }
      });
    } else {
      copyShareLink(shareUrl);
    }
  }

  function copyShareLink(url) {
    const toastMsg = state.lang === 'es'
      ? '¡Enlace copiado al portapapeles! Compártelo con un amigo o pareja.'
      : 'Link copied to clipboard! Share it with a friend or partner.';
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(() => {
        toast(toastMsg);
      }).catch(() => {
        fallbackCopyText(url, toastMsg);
      });
    } else {
      fallbackCopyText(url, toastMsg);
    }
  }

  function fallbackCopyText(text, toastMsg) {
    try {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      toast(toastMsg);
    } catch (e) {
      toast(text);
    }
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
  const DOB_MONTHS_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const DOB_MONTHS_ES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

  function initDobDropdowns() {
    const mEl = $('#dobMonth');
    const dEl = $('#dobDay');
    const yEl = $('#dobYear');
    if (!mEl || !dEl || !yEl) return;

    const curM = mEl.value;
    const curD = dEl.value;
    const curY = yEl.value;
    const months = state.lang === 'es' ? DOB_MONTHS_ES : DOB_MONTHS_EN;
    const mLabel = state.lang === 'es' ? 'Mes' : 'Month';
    const dLabel = state.lang === 'es' ? 'Día' : 'Day';
    const yLabel = state.lang === 'es' ? 'Año' : 'Year';

    mEl.innerHTML = `<option value="">${mLabel}</option>` + months.map((m, idx) => {
      const val = String(idx + 1).padStart(2, '0');
      return `<option value="${val}">${val} · ${m}</option>`;
    }).join('');

    if (dEl.options.length <= 1) {
      let dHtml = `<option value="">${dLabel}</option>`;
      for (let d = 1; d <= 31; d++) {
        const val = String(d).padStart(2, '0');
        dHtml += `<option value="${val}">${d}</option>`;
      }
      dEl.innerHTML = dHtml;
    } else if (dEl.options[0]) {
      dEl.options[0].textContent = dLabel;
    }

    if (yEl.options.length <= 1) {
      const maxYear = Math.max(2026, new Date().getFullYear());
      let yHtml = `<option value="">${yLabel}</option>`;
      // Start with adult birth years (2006 down to 1930) so 1990 is immediately visible in the initial mobile scroll viewport, followed by 2026–2007
      for (let y = 2006; y >= 1930; y--) {
        yHtml += `<option value="${y}">${y}</option>`;
      }
      for (let y = maxYear; y >= 2007; y--) {
        yHtml += `<option value="${y}">${y}</option>`;
      }
      yEl.innerHTML = yHtml;
    } else if (yEl.options[0]) {
      yEl.options[0].textContent = yLabel;
    }

    if (curM) mEl.value = curM;
    if (curD) dEl.value = curD;
    if (curY) yEl.value = curY;
  }

  function syncDobFromDropdowns(triggerField) {
    const mEl = $('#dobMonth');
    const dEl = $('#dobDay');
    const yEl = $('#dobYear');
    const dobInput = $('#birthDate');
    if (!mEl || !dEl || !yEl || !dobInput) return;

    // Default year dropdown scroll near 1990 when month & day are selected and year is opened/focused
    const m = mEl.value;
    const d = dEl.value;
    const y = yEl.value;
    if (m && d && y) {
      dobInput.value = `${y}-${m}-${d}`;
      showErrors({});
      maybeFireCalcPreview(triggerField || 'dob_select');
    } else {
      dobInput.value = '';
    }
  }

  function syncDropdownsFromDob(isoStr) {
    const mEl = $('#dobMonth');
    const dEl = $('#dobDay');
    const yEl = $('#dobYear');
    if (!mEl || !dEl || !yEl) return;
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(isoStr || '').trim());
    if (match) {
      yEl.value = match[1];
      mEl.value = match[2];
      dEl.value = match[3];
    } else {
      mEl.value = '';
      dEl.value = '';
      yEl.value = '';
    }
  }

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
    syncDropdownsFromDob(p.birthDate || '');
    $('#email').value = p.email || '';
  }

  function showErrors(errs) {
    ['fullName', 'birthDate', 'email'].forEach((k) => {
      const field = $('#' + k);
      const msg = $(`[data-error="${k}"]`);
      if (!field || !msg) return;
      if (errs[k]) {
        field.classList.add('error');
        if (k === 'birthDate') {
          ['#dobMonth', '#dobDay', '#dobYear'].forEach((sel) => { const el = $(sel); if (el) el.classList.add('error'); });
        }
        msg.textContent = errs[k];
      } else {
        field.classList.remove('error');
        if (k === 'birthDate') {
          ['#dobMonth', '#dobDay', '#dobYear'].forEach((sel) => { const el = $(sel); if (el) el.classList.remove('error'); });
        }
        msg.textContent = '';
      }
    });
  }

  async function onSubmit(e) {
    e.preventDefault();
    syncDobValueOnly();
    const data = {
      fullName: $('#fullName').value,
      birthDate: $('#birthDate').value,
      email: $('#email').value.trim(),
    };
    const check = E.validate(data.fullName, data.birthDate);
    const errs = Object.assign({}, check.errors);
    if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
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
    state.result = E.calculate(prof.fullName, prof.birthDate);
    saveProfile(prof);

    if (data.email) {
      sendWebhook('lead_submitted');
    } else {
      sendWebhook('calc_preview', { trigger: 'submit_no_email' });
    }

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
    const vslSrc = CONFIG.VSL_URL || 'assets/vsl_briefing.mp4';
    const vslPoster = CONFIG.VSL_POSTER || 'assets/vsl_poster.jpg';
    if (vslSrc.endsWith('.mp4')) {
      return `<div class="vsl-frame card p-2"><video id="vsl-video" src="${vslSrc}" poster="${vslPoster}" controls playsinline preload="metadata" class="w-full h-full rounded-lg object-cover"></video></div>`;
    }
    return `<div class="vsl-frame card p-2"><iframe src="${vslSrc}" class="w-full h-full rounded-lg" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></div>`;
  }

  const REL_ATTACHMENT_MAP_EN = {
    1: {
      style: 'The Hyper-Independent Protector (Sun)',
      chase: 'You crave a strong equal you don\'t have to babysit, yet the moment a partner tries to lead or control you, your guard shoots up.',
      blindspot: 'Because you handle everything alone, partners assume you don\'t need emotional reassurance—leaving you feeling unseen in love.',
    },
    2: {
      style: 'The Deep-Bonding Empath (Moon)',
      chase: 'You sense a partner\'s shift in tone before they say a word and crave deep, soul-level reassurance.',
      blindspot: 'You absorb your partner\'s unspoken anxiety and over-adapt to keep the peace until your own nervous system shuts down.',
    },
    3: {
      style: 'The Spark & Story Romantic (Jupiter)',
      chase: 'You fall for mental electricity, humor, and deep late-night conversation—boredom is your #1 relationship killer.',
      blindspot: 'When a relationship hits heavy routine without play or vision, you mentally check out or over-analyze what\'s missing.',
    },
    4: {
      style: 'The Loyal Anchor & Builder (Rahu)',
      chase: 'You show love through loyalty, actions, and holding everything together when life gets chaotic.',
      blindspot: 'You attract partners who lean on your stability without reciprocating—leaving you carrying 80% of the emotional weight.',
    },
    5: {
      style: 'The Magnetic Freedom Seeker (Mercury)',
      chase: 'You crave electric chemistry and a partner who feels like an adventure, not a cage.',
      blindspot: 'The second a partner becomes clingy, predictable, or controlling, your nervous system triggers an urge to pull away.',
    },
    6: {
      style: 'The Devoted Healer & Caretaker (Venus)',
      chase: 'You love with your whole chest and instinctively try to heal, elevate, and protect the person you\'re with.',
      blindspot: 'You repeatedly fall for "potential" and end up being the therapist partner with no one checking on you.',
    },
    7: {
      style: 'The Guarded Soul-Seeker (Ketu)',
      chase: 'You crave rare, soul-deep intimacy and hate surface-level small talk, yet you need solitude to process your feelings.',
      blindspot: 'When emotions get overwhelming, you go quiet and retreat inward—which anxious partners misread as losing interest.',
    },
    8: {
      style: 'The All-or-Nothing Protector (Saturn)',
      chase: 'You don\'t do casual half-love; when you commit, you invest your time, loyalty, and future for the long haul.',
      blindspot: 'You test partners silently to see if they\'re trustworthy, and struggle to show vulnerability when you\'re hurting.',
    },
    9: {
      style: 'The Passionate Wounded Healer (Mars)',
      chase: 'You love with fierce intensity and are drawn to deep, transformative connections that feel fated.',
      blindspot: 'You hold onto karmic relationships long after they\'ve expired because letting go feels like giving up.',
    },
  };

  const REL_ATTACHMENT_MAP_ES = {
    1: {
      style: 'Protector Hiper-Independiente (Sol)',
      chase: 'Buscas un par fuerte a quien admirar, pero en cuanto intentan controlarte tu escudo se activa.',
      blindspot: 'Como resuelves todo por tu cuenta, tus parejas asumen que no necesitas contención emocional.',
    },
    2: {
      style: 'Empático de Vínculo Profundo (Luna)',
      chase: 'Percibes cualquier cambio de tono antes de que hablen y anhelas conexión emocional genuina.',
      blindspot: 'Absorbes la ansiedad no dicha de tu pareja hasta agotar tu propio sistema nervioso.',
    },
    3: {
      style: 'Romántico de Chispa y Mente (Júpiter)',
      chase: 'Te enamoras de la electricidad mental y las charlas de madrugada; la rutina apaga tu deseo.',
      blindspot: 'Cuando la relación cae en monotonía sin visión compartida, te desconectas en silencio.',
    },
    4: {
      style: 'Ancla Leal y Constructor (Rahu)',
      chase: 'Demuestras amor con lealtad, hechos y sosteniendo todo cuando hay caos.',
      blindspot: 'Atraes parejas que descansan en tu estabilidad sin sostenerte a ti.',
    },
    5: {
      style: 'Buscador Magnético de Libertad (Mercurio)',
      chase: 'Necesitas química eléctrica y una pareja que se sienta como aventura, no como jaula.',
      blindspot: 'Cuando sientes presión o control, tu sistema nervioso activa el impulso de huir.',
    },
    6: {
      style: 'Sanador y Guardián Devoto (Venus)',
      chase: 'Amas con todo el corazón e intentas elevar, cuidar y sanar a quien tienes al lado.',
      blindspot: 'Te enamoras del "potencial" y terminas siendo el terapeuta de la relación.',
    },
    7: {
      style: 'Buscador Profundo y Reservado (Ketu)',
      chase: 'Anhelas intimidad del alma, pero necesitas silencio y soledad para procesar lo que sientes.',
      blindspot: 'Cuando te saturas te repliegas en silencio, y tu pareja cree que te estás alejando.',
    },
    8: {
      style: 'Protector Todo-o-Nada (Saturno)',
      chase: 'No sabes amar a medias; cuando te comprometes, inviertes lealtad y futuro a largo plazo.',
      blindspot: 'Pones a prueba en silencio la lealtad del otro y te cuesta mostrar vulnerabilidad.',
    },
    9: {
      style: 'Sanador Apasionado e Intenso (Marte)',
      chase: 'Amas con fuego e intensidad y te atraen los vínculos kármicos que transforman tu vida.',
      blindspot: 'Sostienes relaciones que ya cumplieron su ciclo porque soltar te parece rendirte.',
    },
  };

  function getPartnerCompatReport(userRes, partnerMonth, partnerDay, partnerYear, lang) {
    const isEs = lang === 'es';
    const pIso = `${partnerYear}-${String(partnerMonth).padStart(2, '0')}-${String(partnerDay).padStart(2, '0')}`;
    const pCalc = E.calculate('Partner Soul', pIso);
    const uMoolank = userRes.vedic.moolank.value;
    const uLife = userRes.pythagorean.lifePath.value;
    const pMoolank = pCalc.vedic.moolank.value;
    const pLife = pCalc.pythagorean.lifePath.value;
    const pRuler = pCalc.vedic.moolank.ruler.planet;
    const uRuler = userRes.vedic.moolank.ruler.planet;

    // Deterministic magnetism & friction scores based on the 4 core birth numbers
    const seed = (uMoolank * 7 + pMoolank * 13 + uLife * 5 + pLife * 11) % 15;
    const magnetismScore = 82 + seed; // 82% to 96%
    const sharedMissing = userRes.loShu.missing.filter((n) => pCalc.loShu.missing.includes(n));
    const bridgedNums = userRes.loShu.missing.filter((n) => !pCalc.loShu.missing.includes(n));

    const pInfo = (isEs ? REL_ATTACHMENT_MAP_ES : REL_ATTACHMENT_MAP_EN)[pMoolank] || REL_ATTACHMENT_MAP_EN[7];
    const frictionLevel = sharedMissing.length >= 3 ? (isEs ? 'ALTA (Puntos Ciegos Compartidos)' : 'HIGH (Shared Blindspots)') : (isEs ? 'MODERADA-ALTA (Choque de Ritmos)' : 'MODERATE-HIGH (Pacing Clash)');

    return {
      pIso,
      pMoolank,
      pLife,
      pRuler,
      uMoolank,
      uLife,
      uRuler,
      magnetismScore,
      frictionLevel,
      sharedMissingCount: sharedMissing.length,
      bridgedCount: bridgedNums.length,
      pStyle: pInfo.style,
      summary: isEs
        ? `Tu conductor íntimo <b>#${uMoolank} (${uRuler})</b> y su conductor natal <b>#${pMoolank} (${pRuler} — ${pInfo.style})</b> generan un <b>${magnetismScore}% de magnetismo inicial</b>. Tu pareja llena <b>${bridgedNums.length}</b> de tus números faltantes en el Lo Shu Chino, pero comparten <b>${sharedMissing.length} vacíos emocionales idénticos</b> que provocan malentendidos cuando hay estrés.`
        : `Your intimate Birth-Day Driver <b>#${uMoolank} (${uRuler})</b> and their Birth-Day Driver <b>#${pMoolank} (${pRuler} — ${pInfo.style})</b> generate an immediate <b>${magnetismScore}% chemistry &amp; magnetism pull</b>. Their birth chart bridges <b>${bridgedNums.length}</b> of your missing Chinese Lo Shu numbers, but you share <b>${sharedMissing.length} identical emotional blindspots</b> that trigger push-pull silence under stress.`,
    };
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

    const isEs = state.lang === 'es';
    const uMoolank = r.vedic.moolank.value;
    const uRuler = r.vedic.moolank.ruler.planet;
    const uLife = p.lifePath.value;
    const uLifeArch = (C_LANG.ARCHETYPES[uLife] || {}).name || ('#' + uLife);
    const relMap = isEs ? REL_ATTACHMENT_MAP_ES : REL_ATTACHMENT_MAP_EN;
    const attInfo = relMap[uMoolank] || relMap[7];
    const missingCount = r.loShu.missing.length;
    const monthsArr = isEs ? DOB_MONTHS_ES : DOB_MONTHS_EN;
    const pMonthOpts = `<option value="">${isEs ? 'Mes' : 'Month'}</option>` + monthsArr.map((m, idx) => `<option value="${String(idx + 1).padStart(2, '0')}">${String(idx + 1).padStart(2, '0')} · ${m}</option>`).join('');
    let pDayOpts = `<option value="">${isEs ? 'Día' : 'Day'}</option>`;
    for (let d = 1; d <= 31; d++) pDayOpts += `<option value="${String(d).padStart(2, '0')}">${d}</option>`;
    let pYearOpts = `<option value="">${isEs ? 'Año' : 'Year'}</option>`;
    for (let y = 2006; y >= 1940; y--) pYearOpts += `<option value="${y}">${y}</option>`;

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

      <!-- PRIORITY #1A.1 · INSTANT RELATIONSHIP & ATTACHMENT BLINDSPOT REVEAL -->
      <div id="teaser-relationship-clash" class="card mt-6 p-5 sm:p-8 border-gold/50" style="border-color:rgba(212,175,55,.45)">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="badge-gold">${isEs ? '✦ Diagnóstico de Amor y Apego (20% Desbloqueado)' : '✦ Relationship & Attachment Blindspot (20% Unlocked)'}</span>
          <span class="text-[0.68rem] uppercase tracking-[0.16em] text-rose-300 font-semibold">${isEs ? '⚡ Fricción Detectada' : '⚡ Inner Love Clash Detected'}</span>
        </div>
        <h3 class="font-display text-xl sm:text-2xl text-ivory mt-4 leading-snug">
          ${isEs
            ? `Por Qué Tu Sendero Occidental (<span class="text-gold">#${uLife}</span>) Choca Con Tu Conductor Íntimo Védico (<span class="text-gold">#${uMoolank} · ${uRuler}</span>)`
            : `Why Your Western Number (<span class="text-gold">#${uLife}</span>) Clashes With Who You Chase at 2 AM (<span class="text-gold">#${uMoolank} · ${uRuler}</span>)`}
        </h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5 mt-5">
          <div class="card-soft p-4 border border-white/10">
            <p class="text-[0.62rem] uppercase tracking-[0.18em] text-zinc-400 font-semibold">${isEs ? 'Lo Que Crees Que Necesitas (Pitagórico)' : 'Who You Think You Need (Western Life Path)'}</p>
            <div class="font-display text-lg text-champagne mt-1">#${uLife} · ${uLifeArch}</div>
            <p class="text-xs text-zinc-300 mt-2 leading-relaxed">${isEs ? 'Tu estándar consciente en el amor: lo que buscas racionalmente cuando todo está en calma.' : 'Your conscious relationship standard: the partner traits you logically look for on paper.'}</p>
          </div>
          <div class="card-soft p-4 border border-gold/40" style="background:rgba(212,175,55,0.06)">
            <p class="text-[0.62rem] uppercase tracking-[0.18em] text-gold font-semibold">${isEs ? 'Lo Que Persigues a las 2 AM (Día Natal Védico)' : 'Who You Instinctively Chase at 2 AM (Vedic Birth Day)'}</p>
            <div class="font-display text-lg text-ivory mt-1">#${uMoolank} · ${attInfo.style}</div>
            <p class="text-xs text-zinc-200 mt-2 leading-relaxed">${attInfo.chase}</p>
          </div>
        </div>
        <div class="mt-4 p-4 rounded-xl bg-rose-950/30 border border-rose-400/30 text-sm text-zinc-200 leading-relaxed">
          <strong class="text-champagne">${isEs ? 'Tu Punto Ciego Afectivo:' : 'Your Attachment Blindspot:'}</strong> ${attInfo.blindspot}
        </div>
      </div>

      <!-- PRIORITY #1A.2 · OLLIE CARSON'S 3-PROBLEM TRIANGLE MICRO-BRIEFING CARDS -->
      <div id="teaser-problem-triangle" class="mt-8">
        <p class="eyebrow text-center">${isEs ? 'El Triángulo de 3 Problemas en Tu Código de Amor' : 'Your 3-Part Relationship Code Breakdown'}</p>
        <h3 class="font-display text-xl sm:text-2xl text-center text-ivory mt-2">${isEs ? 'Las 3 Piezas Que las Lecturas Occidentales Omiten' : 'The 3 Relationship Answers Hidden in Your Other 80%'}</h3>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3.5 mt-5">
          <!-- Part 1 -->
          <div class="card-soft p-4 sm:p-5 border border-gold/35 flex flex-col justify-between" data-triangle-part="1">
            <div>
              <div class="flex items-center justify-between gap-2">
                <span class="badge-gold !text-[0.6rem]">${isEs ? 'Parte 1 · 45s' : 'Part 1 · 45s Briefing'}</span>
                <span class="text-[0.62rem] text-emerald-300 font-semibold uppercase tracking-wider">${isEs ? 'Vista Previa' : 'Unlocked Preview'}</span>
              </div>
              <h4 class="font-display text-base text-champagne mt-3 leading-snug">${isEs ? '1. Tu Punto Ciego de Apego (Por Qué Anhelas Intimidad Pero Te Alejas)' : '1. Your Attachment Blindspot (Why You Crave Intimacy But Pull Away)'}</h4>
              <p class="text-xs text-zinc-300 mt-2.5 leading-relaxed">${isEs ? `Cómo tu conductor natal #${uMoolank} (${uRuler}) reacciona bajo presión emocional y qué número de pareja calma tu sistema nervioso.` : `How your #${uMoolank} (${uRuler}) Birth-Day Driver reacts under emotional stress—and which partner birth numbers naturally calm your nervous system.`}</p>
            </div>
            <button type="button" data-action="play-triangle-part" data-part="1" class="btn-ghost !py-2 !px-3 mt-4 w-full !text-[0.68rem]">
              ▶ ${isEs ? 'Escuchar / Ver Parte 1' : 'Play Part 1 Audio Briefing'}
            </button>
          </div>

          <!-- Part 2 -->
          <div class="card-soft p-4 sm:p-5 border border-gold/25 flex flex-col justify-between" data-triangle-part="2">
            <div>
              <div class="flex items-center justify-between gap-2">
                <span class="badge-gold !text-[0.6rem]">${isEs ? 'Parte 2 · Lo Shu' : 'Part 2 · Lo Shu Grid'}</span>
                <span class="text-[0.62rem] text-amber-300 font-semibold uppercase tracking-wider">${missingCount} ${isEs ? 'Faltantes' : 'Missing Digits'}</span>
              </div>
              <h4 class="font-display text-base text-champagne mt-3 leading-snug">${isEs ? '2. Tus Flechas de Amor Faltantes en el Lo Shu Chino (Por Qué Hay Malentendidos)' : '2. Your Missing Chinese Lo Shu Love Arrows (Why You & Your Partner Miscommunicate)'}</h4>
              <p class="text-xs text-zinc-300 mt-2.5 leading-relaxed">${isEs ? `Tu fecha de nacimiento deja <b>${missingCount} casillas vacías</b> en tu cuadrícula 3×3—los rasgos exactos que proyectas inconscientemente en tus parejas.` : `Your birth date leaves <b>${missingCount} empty boxes</b> in your 3×3 Chinese Lo Shu square—revealing the exact emotional traits you subconsciously project onto partners.`}</p>
            </div>
            <button type="button" data-action="play-triangle-part" data-part="2" class="btn-ghost !py-2 !px-3 mt-4 w-full !text-[0.68rem]">
              ▶ ${isEs ? 'Escuchar / Ver Parte 2' : 'Play Part 2 Audio Briefing'}
            </button>
          </div>

          <!-- Part 3 -->
          <div class="card-soft p-4 sm:p-5 border border-gold/25 flex flex-col justify-between" data-triangle-part="3">
            <div>
              <div class="flex items-center justify-between gap-2">
                <span class="badge-gold !text-[0.6rem]">${isEs ? 'Parte 3 · Sincronía' : 'Part 3 · Love Timing'}</span>
                <span class="text-[0.62rem] text-rose-300 font-semibold uppercase tracking-wider">${cyc.daysRemaining}d ${isEs ? 'Restantes' : 'Left in Cycle'}</span>
              </div>
              <h4 class="font-display text-base text-champagne mt-3 leading-snug">${isEs ? '3. Tu Ventana de Tiempo de Relación para los Próximos 12 Meses' : '3. Your Next 12 Months Relationship Timing Window'}</h4>
              <p class="text-xs text-zinc-300 mt-2.5 leading-relaxed">${isEs ? `Actualmente estás en tu ciclo planetario de <b>${cyc.current.ruler}</b> (${cyc.daysRemaining} días restantes). Descubre tus fechas exactas de Venus y Luna para el amor.` : `You are currently inside your 52-day <b>${cyc.current.ruler}</b> period (${cyc.daysRemaining} days left). Pinpoint your peak Venus &amp; Moon soulmate windows over the next 12 months.`}</p>
            </div>
            <button type="button" data-action="play-triangle-part" data-part="3" class="btn-ghost !py-2 !px-3 mt-4 w-full !text-[0.68rem]">
              ▶ ${isEs ? 'Escuchar / Ver Parte 3' : 'Play Part 3 Audio Briefing'}
            </button>
          </div>
        </div>
        <div id="triangle-audio-status" class="hidden mt-3 p-3.5 rounded-xl card-soft border border-gold/40 text-xs sm:text-sm text-champagne text-center"></div>
      </div>

      <!-- PRIORITY #1A.3 · OPTIONAL PARTNER / CRUSH BIRTHDAY COMPATIBILITY CHECKER -->
      <div id="partner-compat-box" class="card mt-7 p-5 sm:p-7 border-gold/50" style="border-color:rgba(212,175,55,.5);background:linear-gradient(180deg,rgba(28,25,18,0.92),rgba(14,15,20,0.96))">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="badge-gold">${isEs ? '✦ Escáner de Compatibilidad de Pareja (Opcional)' : '✦ Instant Partner / Crush Compatibility Check (Optional)'}</span>
          <span class="text-[0.65rem] uppercase tracking-[0.15em] text-champagne">${isEs ? 'Sin Costo Extra' : 'Instant Preview'}</span>
        </div>
        <h3 class="font-display text-lg sm:text-2xl text-ivory mt-3">
          ${isEs ? '¿Quieres comprobar tu compatibilidad con tu pareja o alguien especial? Ingresa su fecha de nacimiento (Opcional):' : 'Want to check your compatibility with a partner or crush? Enter their birthday (Optional):'}
        </h3>
        <p class="text-xs sm:text-sm text-zinc-300 mt-1.5">
          ${isEs ? 'Calcularemos al instante su puntaje de magnetismo, dónde chocan sus números natales y qué casillas del Lo Shu Chino completan juntos.' : 'See your instant Magnetism vs. Friction score, how their Birth-Day Driver interacts with yours, and whether their chart fills your missing Lo Shu love numbers.'}
        </p>
        <div class="grid grid-cols-3 gap-2.5 mt-4" id="partner-dob-group">
          <select id="partnerDobMonth" class="field !px-3 !py-2.5 text-sm" aria-label="Partner Birth Month">${pMonthOpts}</select>
          <select id="partnerDobDay" class="field !px-3 !py-2.5 text-sm" aria-label="Partner Birth Day">${pDayOpts}</select>
          <select id="partnerDobYear" class="field !px-3 !py-2.5 text-sm" aria-label="Partner Birth Year">${pYearOpts}</select>
        </div>
        <button type="button" data-action="check-partner-compat" id="btn-partner-compat" class="btn-gold mt-4 !py-3 text-xs sm:text-sm">
          ✦ ${isEs ? 'Calcular Compatibilidad y Fricción con Mi Pareja →' : 'Calculate Our Relationship Compatibility & Friction Score →'}
        </button>
        <div id="partner-compat-result" class="hidden mt-5 pt-5 border-t border-gold/30"></div>
      </div>

      <!-- 1-TAP VIRAL SHARE BUTTON -->
      <div class="mt-4 text-center">
        <button type="button" data-action="share-code" class="btn-ghost w-full sm:w-auto !py-3 !px-6 border-gold/40 hover:border-gold hover:bg-gold/10 text-champagne text-xs sm:text-sm font-semibold transition-all">
          <span data-i18n="share_btn">${UI.share_btn}</span>
        </button>
      </div>

      ${!(state.profile && state.profile.email) ? `
      <!-- 1-STEP MICRO-COMMITMENT EMAIL SAVE BAR -->
      <div id="teaser-email-box" class="card-soft mt-5 p-4 sm:p-5 border border-gold/30 max-w-xl mx-auto text-center">
        <p class="text-xs sm:text-sm text-champagne font-medium">${state.lang === 'es' ? '✦ ¿Quieres recibir este resumen de tus 5 Sistemas y tu Alerta de Fricción en tu correo?' : '✦ Want a copy of your 5-System Summary & Friction Alert emailed to you?'}</p>
        <div class="mt-3 flex flex-col sm:flex-row gap-2">
          <input id="teaser-email-input" type="email" inputmode="email" autocomplete="email" class="field !py-2.5 text-sm flex-1" placeholder="${state.lang === 'es' ? 'Ingresa tu correo electrónico...' : 'Enter your email address...'}" />
          <button type="button" data-action="save-teaser-email" class="btn-gold !py-2.5 !px-5 sm:w-auto text-xs whitespace-nowrap">${state.lang === 'es' ? 'Enviar Mi Resumen Gratis' : 'Email My Free Summary'}</button>
        </div>
      </div>` : ''}

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
          ${lockedCard(state.lang === 'es' ? 'Sistema V · Lo Shu & Vitalidad Somática' : 'System V · Lo Shu & Somatic Vitality', state.lang === 'es' ? 'Cuadrado Mágico 3×3, Cinco Elementos y Salud Somática' : '3×3 Magic Square, Five Elements & Somatic Health', ['◆◆', '◆', '◆◆◆'])}
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
    const total = CONFIG.PRICE_BASE + (state.bump ? CONFIG.PRICE_BUMP : 0);
    const tierLabel = state.bump ? `$${total} Bundle (20-Page Dossier + 52-Day Cycles)` : `$${total} Base (20-Page Dossier)`;
    sendWebhook('checkout_clicked', { bump: state.bump, total, tier: state.bump ? 'full_bundle' : 'base', tier_label: tierLabel });
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
    return `<div class="card-soft py-3 px-1.5 sm:p-4 text-center avoid-break"><div class="text-[0.52rem] sm:text-[0.58rem] tracking-[0.14em] sm:tracking-[0.2em] uppercase text-zinc-500 leading-tight">${label}</div><div class="font-display text-gold-grad mt-1" style="font-size:clamp(1.05rem,4.2vw,1.6rem);">${display}</div>${sub ? `<div class="text-[0.62rem] sm:text-[0.7rem] text-champagne mt-0.5 sm:mt-1">${sub}</div>` : ''}</div>`;
  }
  function interp(title, body) {
    return `<div class="avoid-break border-l border-gold/40 pl-4 py-1" style="border-color:rgba(212,175,55,.4)"><p class="font-display text-[0.95rem] text-champagne">${title}</p><p class="text-sm text-zinc-300 mt-1">${body}</p></div>`;
  }
  function bar(label, count, max, rightLabel) {
    const pct = Math.min(100, Math.round(((count || 0) / (max || 1)) * 100));
    return `<div class="bar-row"><div class="bar-label"><span>${label}</span><span class="bar-val">${rightLabel || count}</span></div><div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div></div>`;
  }
  function chips(letterWords) {
    return `<div class="flex flex-wrap gap-2 my-3">${letterWords.map((w) => `<div class="flex gap-1">${w.letters.map((l) => `<span class="chip ${l.vowel ? 'vowel' : ''}"><span class="ch">${l.ch}</span><span class="val">${l.val}</span></span>`).join('')}</div>`).join('<span class="chip-space"></span>')}</div>`;
  }
  function sentences(text, n) {
    if (!text) return '';
    const m = text.match(/[^.!?]+[.!?]+/g);
    return m ? m.slice(0, n).join(' ') : text;
  }

  function convergenceMandalaSvg(anchors, lang) {
    const [a1, a2, a3] = anchors;
    const sysLabelsEn = ['I · PYTHAGOREAN', 'II · CHALDEAN', 'III · KABBALISTIC', 'IV · VEDIC', 'V · CHINESE LO SHU'];
    const sysLabelsEs = ['I · PITAGÓRICO', 'II · CALDEO', 'III · CABALÍSTICO', 'IV · VÉDICO', 'V · LO SHU CHINO'];
    const labels = lang === 'es' ? sysLabelsEs : sysLabelsEn;

    const centers = [
      { x: 250, y: 82, lx: 250, ly: 22, anchor: 'middle' },
      { x: 315, y: 129, lx: 395, ly: 125, anchor: 'start' },
      { x: 290, y: 205, lx: 360, ly: 260, anchor: 'start' },
      { x: 210, y: 205, lx: 140, ly: 260, anchor: 'end' },
      { x: 185, y: 129, lx: 105, ly: 125, anchor: 'end' },
    ];

    const circles = centers.map((c, i) => `
      <circle cx="${c.x}" cy="${c.y}" r="64" fill="rgba(212,175,55,0.03)" stroke="rgba(212,175,55,0.38)" stroke-width="1.2" />
      <line x1="250" y1="150" x2="${c.x}" y2="${c.y}" stroke="rgba(212,175,55,0.22)" stroke-dasharray="3 3" stroke-width="1" />
      <text x="${c.lx}" y="${c.ly}" text-anchor="${c.anchor}" font-family="'Cinzel', serif" font-size="8" font-weight="600" letter-spacing="1" fill="#D4AF37">${labels[i]}</text>
    `).join('');

    const centerLabel = lang === 'es' ? 'CÓDIGO SOBERANO' : 'SOVEREIGN CODE';
    const subLabel = lang === 'es' ? 'CONVERGENCIA MAESTRA' : 'MASTER CONVERGENCE';

    return `
    <div class="flex justify-center my-3 avoid-break">
      <svg viewBox="0 0 500 285" class="w-full max-w-[460px] h-auto overflow-visible" aria-label="The 5-Ring Sacred Convergence Mandala">
        <defs>
          <radialGradient id="mandalaGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#2a2516" />
            <stop offset="70%" stop-color="#121318" />
            <stop offset="100%" stop-color="#0A0A0C" />
          </radialGradient>
          <radialGradient id="mandalaAura" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="rgba(212,175,55,0.35)" />
            <stop offset="100%" stop-color="transparent" />
          </radialGradient>
        </defs>
        <circle cx="250" cy="150" r="105" fill="url(#mandalaAura)" />
        <circle cx="250" cy="150" r="130" fill="none" stroke="rgba(212,175,55,0.18)" stroke-dasharray="4 6" stroke-width="1" />
        <polygon points="250,82 290,205 185,129 315,129 210,205" fill="none" stroke="rgba(212,175,55,0.18)" stroke-width="0.8" />
        ${circles}
        <circle cx="250" cy="150" r="46" fill="url(#mandalaGlow)" stroke="#D4AF37" stroke-width="1.8" />
        <circle cx="250" cy="150" r="41" fill="none" stroke="rgba(212,175,55,0.4)" stroke-dasharray="2 3" stroke-width="1" />
        <text x="250" y="132" text-anchor="middle" font-family="'Cinzel', serif" font-size="6.5" font-weight="600" letter-spacing="2" fill="#D4AF37">${centerLabel}</text>
        <text x="250" y="156" text-anchor="middle" font-family="'Cinzel', serif" font-size="20" font-weight="700" fill="#F3E5AB">${a1.number} · ${a2.number} · ${a3.number}</text>
        <text x="250" y="171" text-anchor="middle" font-family="'Cinzel', serif" font-size="5.8" font-weight="500" letter-spacing="1.5" fill="rgba(243,229,171,0.7)">${subLabel}</text>
      </svg>
    </div>`;
  }

  function anchorPage(anchor, idx, C_LANG) {
    const UI = C_LANG.UI;
    const A = C_LANG.ARCHETYPES[anchor.number], n = anchor.number, V = E.VEDIC[n], S = E.SEPHIROT[n], el = E.elementOf(n);
    const focus = [A.core, A.wealth, A.foundation][idx];
    const roleTitle = [UI.signature_role, UI.wealth_role, UI.foundation_role][idx];
    const roleSub = [UI.signature_sub, UI.wealth_sub, UI.foundation_sub][idx];

    const sourcesClean = anchor.sources.map(s => translateSource(s));
    const systemsClean = anchor.systems.map(s => translateSystem(s));

    const relInsightsEn = {
      1: 'In intimacy and partnerships, you command devotion through quiet confidence rather than control. You thrive with an equal who respects your autonomy while providing a haven of warm adoration.',
      2: 'Your relational aura is deeply empathic, intuitive, and magnetic. You forge profound emotional bonds by listening deeply, but your growth lies in establishing sacred boundaries to avoid energetic absorption.',
      3: 'You illuminate connections through wit, joy, and creative fire. For you, intellectual play, playful banter, and passionate dialogue are the sacred gateway to enduring devotion.',
      4: 'Your love is grounded in absolute loyalty, quiet dedication, and tangible shelter. You build lasting intimacy not through grand promises, but through faithful action and domestic peace.',
      5: 'You bring electrifying vitality, wit, and novelty to romantic connection. You flourish with a co-explorer who celebrates your freedom and matches your spontaneous appetite for life.',
      6: 'The master archetype of devotion and harmony: you radiate warmth, protective care, and refined elegance. You elevate your partner\'s life and thrive in mutual, sacred reciprocity.',
      7: 'You attract through soul depth, mysterious intellect, and quiet grace. You require a sacred connection where silence is comfortable, thoughts are respected, and trust is absolute.',
      8: 'You project magnetic authority, protective shelter, and unflinching integrity. In partnerships, you look for a true equal: someone who matches your empire-building drive and moral backbone.',
      9: 'You love with cosmic compassion, idealism, and broad horizons. You inspire those around you, drawing partners who share your devotion to leaving the world more luminous than you found it.'
    };

    const relInsightsEs = {
      1: 'En el amor y las relaciones, inspiras devoción a través de una seguridad serena y sin control. Floreces con una pareja que respete tu autonomía y te brinde un santuario de admiración cálida.',
      2: 'Tu aura relacional es profundamente empática, intuitiva y magnética. Creas intimidad escuchando con el alma, pero tu maestría radica en fijar límites energéticos claros.',
      3: 'Iluminas tus vínculos con ingenio, alegría y fuego creativo. Para ti, el juego intelectual, la complicidad verbal y la pasión expresiva son la puerta hacia una devoción duradera.',
      4: 'Tu amor se cimenta en la lealtad inquebrantable, la devoción silenciosa y la seguridad. Construyes relaciones sólidas mediante la fidelidad en los hechos y la paz del hogar.',
      5: 'Aportas vitalidad electrizante, novedad y aventura a los vínculos afectivos. Te expandes junto a un co-explorador que celebre tu libertad y comparta tu apetito por descubrir el mundo.',
      6: 'El arquetipo de la devoción, la armonía y la belleza: irradias calidez, protección y elegancia refinada. Elevas la vida de tu pareja y floreces en la reciprocidad sincera.',
      7: 'Atraes a través de la profundidad del alma, la inteligencia intuitiva y el misterio sereno. Exiges un vínculo donde el silencio sea cómodo y la confianza sea un templo sagrado.',
      8: 'Proyectas una autoridad magnética, protección incondicional y rectitud de carácter. En el amor buscas un igual: alguien con tu misma visión de construir un legado y lealtad total.',
      9: 'Amas con compasión universal, idealismo y visión trascendente. Inspiras a quienes te rodean, atrayendo a almas con propósito que deseen dejar una huella luminosa en el mundo.'
    };

    const relText = state.lang === 'es' ? relInsightsEs[n] : relInsightsEn[n];

    return `
      ${secHead(`${state.lang === 'es' ? 'Coincidencia Maestra · Ancla' : 'Master Overlap · Anchor'} ${idx + 1} ${state.lang === 'es' ? 'de 3' : 'of 3'}`, roleTitle, roleSub)}
      <div class="flex flex-col sm:flex-row gap-5 items-center mt-5 avoid-break">
        ${medal(n, 'lg')}
        <div class="flex-1 text-center sm:text-left">
          <p class="font-display text-2xl">${A.name}</p>
          <p class="text-[0.65rem] tracking-[0.2em] uppercase text-zinc-500 mt-1">${A.keywords.join(' · ')}</p>
          <p class="text-sm text-champagne mt-2.5">${state.lang === 'es' ? 'Frecuencia:' : 'Frequency:'} <b>${anchor.count}×</b> · ${state.lang === 'es' ? 'Sistemas:' : 'Systems:'} ${systemsClean.join(', ') || '—'}</p>
          ${sourcesClean.length ? `<p class="text-xs text-zinc-500 mt-1">${state.lang === 'es' ? 'Identificado en:' : 'Found in:'} ${sourcesClean.join(' · ')}</p>` : `<p class="text-xs text-zinc-500 mt-1">${state.lang === 'es' ? 'Confirmado por frecuencia Lo Shu.' : 'Selected by Lo Shu frequency tie-break.'}</p>`}
        </div>
      </div>
      <p class="lead mt-5 !text-[1.12rem]">${focus}</p>
      <div class="grid sm:grid-cols-3 gap-2.5 mt-5">
        <div class="card-soft p-3.5 avoid-break"><p class="eyebrow !text-[0.55rem]">${state.lang === 'es' ? 'Regente Védico' : 'Vedic Ruler'}</p><p class="font-display text-sm mt-1">${V.planet} · ${V.english}</p><p class="text-xs text-zinc-400 mt-0.5">${V.archetype}</p></div>
        <div class="card-soft p-3.5 avoid-break"><p class="eyebrow !text-[0.55rem]">Sephirah</p><p class="font-display text-sm mt-1">${S.name}</p><p class="text-xs text-zinc-400 mt-0.5">${S.title} · ${S.essence}</p></div>
        <div class="card-soft p-3.5 avoid-break"><p class="eyebrow !text-[0.55rem]">${state.lang === 'es' ? 'Elemento Lo Shu' : 'Lo Shu Element'}</p><p class="font-display text-sm mt-1">${el}</p><p class="text-xs text-zinc-400 mt-0.5">${E.ELEMENTS[el].theme}</p></div>
      </div>
      <div class="grid sm:grid-cols-2 gap-4 mt-5">
        <div class="avoid-break space-y-3">
          <div class="card-soft p-3.5"><p class="eyebrow !text-[0.55rem]">${state.lang === 'es' ? 'Tácticas de Activación' : 'Activation Tactics'}</p><ul class="mt-2 space-y-1.5 text-xs text-zinc-300">${A.tactics.map((t) => `<li class="flex">${CHECK}<span>${t}</span></li>`).join('')}</ul></div>
          <div class="card-soft p-3.5"><p class="eyebrow !text-[0.55rem]">${state.lang === 'es' ? 'Sombra a Dominar' : 'Shadow to Master'}</p><p class="text-xs text-zinc-300 mt-1">${A.shadow}</p></div>
        </div>
        <div class="avoid-break space-y-3">
          <div class="card-soft p-3.5"><p class="eyebrow !text-[0.55rem]">${state.lang === 'es' ? 'Presencia y Magnetismo Personal' : 'Presence & Personal Magnetism'}</p><p class="text-xs text-zinc-300 mt-1">${A.magnetism}</p></div>
          <div class="card-soft p-3.5"><p class="eyebrow !text-[0.55rem] text-gold">${state.lang === 'es' ? 'Amor, Vínculos y Resonancia Relacional' : 'Love, Intimacy & Relational Resonance'}</p><p class="text-xs text-zinc-300 mt-1 leading-relaxed">${relText}</p></div>
        </div>
      </div>`;
  }

  function cycleRow(c, C_LANG) {
    const T = C_LANG.CYCLE_TEXT[c.index];
    const todayBadge = state.lang === 'es' ? 'Activo Hoy' : 'Today';
    return `<tr class="${c.isCurrent ? 'current' : ''}">
      <td><span class="font-display text-gold text-lg mr-1">${c.glyph}</span><span class="font-display text-sm font-semibold">${c.n}</span></td>
      <td><div class="font-display text-[0.85rem] text-ivory leading-snug">${c.name}${c.isCurrent ? ` <span class="badge-gold !py-0.5 !text-[0.55rem] ml-1">${todayBadge}</span>` : ''}</div><div class="text-[0.7rem] text-zinc-500 mt-0.5">${c.theme}</div></td>
      <td class="text-[0.76rem] text-zinc-300">${c.startLabel} – ${c.endLabel}<div class="text-[0.62rem] text-zinc-500 mt-0.5 font-mono">${state.lang === 'es' ? `Días ${c.startDay}–${c.endDay} (~52 días)` : `Days ${c.startDay}–${c.endDay} (~52 days)`}</div></td>
      <td class="text-right"><span class="mode-pill mode-${T.modeTone}">${T.mode}</span></td>
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
    const maxT = Math.max(...Object.values(r.overlap.tally).map((t) => t.count), 1);
    const lb = p.lifePathBreakdown;
    const PA = (n) => C_LANG.ARCHETYPES[n] || null;
    const PIL = k.pillars;
    const birthDigits = r.input.birth.compact.split('');
    const dayDigits = String(r.input.birth.d).split('');
    const daySum = dayDigits.reduce((acc, d) => acc + parseInt(d, 10), 0);
    const moolCalc = r.input.birth.d > 9
      ? `Day ${r.input.birth.d} → ${dayDigits.join(' + ')} = ${daySum}${daySum !== v.moolank.value ? ' → ' + v.moolank.value : ''}`
      : `Day ${r.input.birth.d} → ${v.moolank.value}`;
    const bhagCalc = `${birthDigits.join('+')} = ${v.bhagyank.raw} → ${v.bhagyank.value}`;
    const chalDigits = String(ch.total.raw).split('');
    const chalSum = chalDigits.reduce((acc, d) => acc + parseInt(d, 10), 0);
    const namCalc = ch.total.raw > 9
      ? `Chaldean ${ch.total.raw} → ${chalDigits.join(' + ')} = ${chalSum}${chalSum !== v.namank.value ? ' → ' + v.namank.value : ''}`
      : `Chaldean ${ch.total.raw} → ${v.namank.value}`;

    const maxE = Math.max(...Object.values(l.elements), 1);
    const ET = C_LANG.ELEMENT_TEXT[l.dominantElement];
    const domSomatic = C_LANG.SOMATIC_ELEMENTS[l.dominantElement];
    const weakEl = (l.weakElements && l.weakElements.length) ? l.weakElements[0] : (l.missing.length ? E.elementOf(l.missing[0]) : null);
    const weakSomatic = weakEl ? C_LANG.SOMATIC_ELEMENTS[weakEl] : null;

    const bhag = v.bhagyank.ruler, mool = v.moolank.ruler, curT = C_LANG.CYCLE_TEXT[cy.current.index];
    const jup = cy.periods[4], sat = cy.periods[6], sol = cy.periods[0];
    const soulA = PA(p.soulUrge.value), persA = PA(p.personality.value);
    const ayurMool = C_LANG.AYURVEDA[v.moolank.value];
    const ayurBhag = C_LANG.AYURVEDA[v.bhagyank.value];
    const bioCycle = C_LANG.BIORHYTHM_CYCLES[cy.current.index];

    /* 1 · COVER */
    pages.push({ cover: true, title: state.lang === 'es' ? 'Portada' : 'Cover', html: `
      <div>
        <svg class="seal" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="47" fill="none" stroke="#D4AF37" stroke-width="1"/><circle cx="50" cy="50" r="41" fill="none" stroke="#D4AF37" stroke-width=".5" stroke-dasharray="2 2"/><polygon points="50,14 84,39 71,80 29,80 16,39" fill="none" stroke="#D4AF37" stroke-width="1"/><polygon points="50,80 16,39 84,39 29,80 50,14 71,80" fill="none" stroke="rgba(212,175,55,.5)" stroke-width=".6"/><circle cx="50" cy="50" r="4" fill="#D4AF37"/></svg>
        <p class="eyebrow mt-6">${UI.cover_edition.replace('${year}', new Date().getFullYear())}</p>
      </div>
      <div>
        <p class="font-display text-[0.8rem] tracking-[0.5em] text-zinc-400">${state.lang === 'es' ? 'EL' : 'THE'}</p>
        <h1 class="font-display text-4xl sm:text-6xl text-gold-grad mt-2 leading-tight">${state.lang === 'es' ? 'Plano<br/>Soberano' : 'Sovereign<br/>Blueprint'}</h1>
        <p class="font-serif italic text-xl text-zinc-300 mt-4">${state.lang === 'es' ? 'Dossier de 20 Páginas de Numerología de los 5 Sistemas y Ciclos Rosacruces' : '20-Page 5-System Numerology & Rosicrucian Cycles Dossier'}</p>
        <div class="hairline my-8 mx-auto" style="max-width:260px"></div>
        <p class="text-[0.62rem] tracking-[0.35em] uppercase text-zinc-500">${UI.cover_prepared}</p>
        <p class="font-display text-3xl sm:text-4xl mt-2.5 text-ivory">${name}</p>
        <p class="font-serif text-lg text-champagne mt-1.5">${UI.cover_born.replace('${birthLabel}', birthLabel)}</p>
      </div>
      <div>
        <p class="eyebrow mb-4">${UI.cover_big3}</p>
        <div class="flex justify-center items-end gap-5 sm:gap-8">
          ${[a2, a1, a3].map((a) => `<div class="text-center">${medal(a.number, a === a1 ? 'lg' : 'md', a === a1 ? 'glow-pulse' : '')}<p class="text-[0.58rem] tracking-[0.2em] uppercase text-zinc-400 mt-3">${a === a1 ? (state.lang === 'es' ? 'Firma' : 'Signature') : a === a2 ? (state.lang === 'es' ? 'Riqueza' : 'Wealth') : (state.lang === 'es' ? 'Fundación' : 'Foundation')}</p></div>`).join('')}
        </div>
        <p class="text-[0.6rem] tracking-[0.25em] uppercase text-zinc-600 mt-8">${UI.cover_issued.replace('${generatedLabel}', currentLabel)}</p>
      </div>` });

    /* 2 · THE SECRET OF THE 5 ANCIENT LENSES (METAPHOR + CONVERGENCE MANDALA) */
    pages.push({
      title: state.lang === 'es' ? 'Los 5 Lentes Ancestrales' : 'The 5 Ancient Lenses',
      html: `
      ${secHead(
        state.lang === 'es' ? 'La Convergencia Sagrada' : 'The Sacred Convergence',
        state.lang === 'es' ? 'El Secreto de los 5 Lentes Ancestrales' : 'The Secret of the 5 Ancient Lenses',
        state.lang === 'es'
          ? 'Observar un solo sistema de numerología es como escuchar una única nota de una sinfonía: millones de personas comparten tu mismo Sendero de Vida occidental. A lo largo del mundo antiguo, cinco grandes civilizaciones—Grecia (Pitagórica), Babilonia (Caldea), los Místicos Hebreos (Cábala), la India (Védica) y la China Imperial (Lo Shu)—desarrollaron códigos matemáticos completamente independientes utilizando alfabetos y calendarios distintos. Al pasar la vibración sonora de tu nombre y la fecha exacta de tu nacimiento por los 5 lentes simultáneamente, la mayoría de los números se dispersan. Aguarda el milagro: 3 números específicos resuenan a través de culturas totalmente distintas. Esa intersección sagrada es tu Código Soberano.'
          : 'Looking at a single numerology system is like hearing one note of a song—millions of people share your Western Life Path number. Across the ancient world, five great civilizations—Greece (Pythagorean), Babylon (Chaldean), Hebrew Mystics (Kabbalah), India (Vedic), and Imperial China (Lo Shu)—developed completely independent mathematical codes using different alphabets and calendars. When we pass both the sound vibration of your name and the exact date of your birth through all 5 lenses at once, most numbers scatter. Wait for the miracle: 3 specific numbers echo across completely different cultures. That intersection is your Sovereign Code.'
      )}
      ${convergenceMandalaSvg([a1, a2, a3], state.lang)}
      <div class="grid sm:grid-cols-3 gap-3 mt-3 avoid-break">
        <div class="card-soft p-3.5 text-center" style="border-color:rgba(212,175,55,.45)">
          <div class="flex items-center justify-center gap-1.5 mb-1">
            <span class="badge-gold !text-[0.6rem] !py-0.5">#1</span>
            <span class="font-display text-champagne text-xs font-semibold">${state.lang === 'es' ? 'Ancla de Firma' : 'Signature Anchor'}</span>
          </div>
          <p class="font-display text-gold text-lg font-bold">${a1.number} · ${A1.name}</p>
          <p class="text-[0.68rem] text-zinc-300 font-medium mt-1">${state.lang === 'es' ? 'Tu Magnetismo del Alma y Verdadera Esencia' : 'Your Soul Magnetism & True Essence'}</p>
          <p class="text-[0.65rem] text-zinc-400 mt-1 leading-snug">${state.lang === 'es' ? 'Quién eres sin esfuerzo y la frecuencia natural que otros perciben al entrar en tu presencia.' : 'Who you effortlessly are and how people naturally feel and respond to your presence.'}</p>
        </div>
        <div class="card-soft p-3.5 text-center">
          <div class="flex items-center justify-center gap-1.5 mb-1">
            <span class="badge-gold !text-[0.6rem] !py-0.5">#2</span>
            <span class="font-display text-champagne text-xs font-semibold">${state.lang === 'es' ? 'Motor de Riqueza' : 'Wealth Engine'}</span>
          </div>
          <p class="font-display text-gold text-lg font-bold">${a2.number} · ${A2.name}</p>
          <p class="text-[0.68rem] text-zinc-300 font-medium mt-1">${state.lang === 'es' ? 'Tu Flujo de Abundancia y Manifestación' : 'Your Wealth & Manifestation Flow'}</p>
          <p class="text-[0.65rem] text-zinc-400 mt-1 leading-snug">${state.lang === 'es' ? 'El vehículo exacto mediante el cual el dinero, el capital y las oportunidades te encuentran.' : 'The exact vehicle through which money, career success, and opportunities naturally find you.'}</p>
        </div>
        <div class="card-soft p-3.5 text-center">
          <div class="flex items-center justify-center gap-1.5 mb-1">
            <span class="badge-gold !text-[0.6rem] !py-0.5">#3</span>
            <span class="font-display text-champagne text-xs font-semibold">${state.lang === 'es' ? 'Fundación Estructural' : 'Structural Foundation'}</span>
          </div>
          <p class="font-display text-gold text-lg font-bold">${a3.number} · ${A3.name}</p>
          <p class="text-[0.68rem] text-zinc-300 font-medium mt-1">${state.lang === 'es' ? 'Tu Santuario, Límites y Sistema Nervioso' : 'Your Sanctuary & Nervous System'}</p>
          <p class="text-[0.65rem] text-zinc-400 mt-1 leading-snug">${state.lang === 'es' ? 'Lo que protege tu paz interior, tus relaciones y la estabilidad de tu energía vital diaria.' : 'What protects your inner peace, intimate relationships, and daily vital energy.'}</p>
        </div>
      </div>`
    });

    /* 3 · SYSTEMS ROADMAP & 20-PAGE TABLE OF CONTENTS (Placeholder - populated in renderDossier) */
    pages.push({ title: state.lang === 'es' ? 'Sistemas y Contenido' : 'Systems & Contents', contents: true });

    /* 4 · BIG THREE MASTER OVERLAP + SECONDARY HARMONICS + TALLY (1-9) */
    pages.push({ title: state.lang === 'es' ? 'Coincidencia Maestra' : 'Master Overlap', html: `
      ${secHead(UI.overlap_eyebrow, UI.overlap_title, UI.overlap_lead.replace('${totalSources}', r.overlap.totalSources))}
      <div class="grid sm:grid-cols-3 gap-3.5 mt-6">
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
      <div class="mt-4 p-3.5 rounded-xl border border-gold/25 bg-charcoal/70 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs avoid-break">
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

      <!-- Frequency Tally 1-9 in 2 balanced columns -->
      <div class="mt-6 avoid-break">
        <p class="eyebrow mb-3">${UI.frequency_tally}</p>
        <div class="grid sm:grid-cols-2 gap-x-6 gap-y-2.5">
          ${[1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => bar(`<span class="font-display text-champagne mr-2">${n}</span>${C_LANG.ARCHETYPES[n].name}`, r.overlap.tally[n].count, maxT, r.overlap.tally[n].count + '×')).join('')}
        </div>
        <p class="text-[0.72rem] text-zinc-500 mt-4 leading-relaxed">${state.lang === 'es' ? 'Los números con mayor frecuencia acumulada forman tus anclas operativas primarias, secundarias y armónicas.' : 'The numbers with highest accumulated frequency constitute your primary, secondary, and harmonic operational anchors.'}</p>
      </div>` });

    /* 5 · COMPLETE 15-POINT SOURCE CALCULATIONS LEDGER */
    pages.push({ title: state.lang === 'es' ? 'Registro de Cálculos' : 'Source Calculations', html: `
      ${secHead(
        state.lang === 'es' ? 'Auditoría Matemática Inter-Sistemas' : 'Cross-System Mathematical Audit',
        state.lang === 'es' ? 'Las 15 Fuentes de Cálculo y Reducciones' : 'The Complete 15-Point Calculation Ledger',
        state.lang === 'es' ? 'Cada número extraído de tu nombre y fecha de nacimiento a través de las 5 tradiciones. Fórmulas transparentes de reducción compuesta a raíz que demuestran el origen exacto de tu código.' : 'Every calculation extracted from your birth name and date across the five traditions. Transparent compound-to-root reductions showing the exact mathematical origin of your blueprint.'
      )}
      <div class="mt-6 avoid-break">
        <table class="lux-table mt-1"><thead><tr><th style="width:28%">${state.lang === 'es' ? 'Fuente' : 'Source'}</th><th style="width:44%">${state.lang === 'es' ? 'Fórmula / Reducción' : 'Formula / Reduction'}</th><th style="width:18%">${state.lang === 'es' ? 'Sistema' : 'System'}</th><th style="width:10%;text-align:right">#</th></tr></thead><tbody>
          ${r.overlap.sources.map((s) => `<tr><td class="text-zinc-300 text-[0.78rem] font-medium leading-snug">${translateSource(s.label)}</td><td class="font-mono text-champagne text-[0.74rem] leading-snug">${s.formula || `${s.value}`}</td><td class="text-zinc-400 text-[0.74rem]">${translateSystem(s.system)}</td><td class="font-display text-gold text-right font-bold text-[0.98rem]">${s.value}</td></tr>`).join('')}
        </tbody></table>
        <div class="card-soft p-4 mt-5 avoid-break">
          <p class="eyebrow !text-[0.55rem]">${state.lang === 'es' ? 'Determinismo Matemático y Resonancia' : 'Mathematical Determinism & Resonance'}</p>
          <p class="text-[0.78rem] text-zinc-300 mt-1.5 leading-relaxed">${state.lang === 'es' ? 'Al procesar tu perfil a través de cinco alfabetos, métodos de reducción y calendarios independientes, se aísla el ruido arbitrario. Las recurrencias observadas en tus anclas no son coincidencias estadísticas, sino patrones armónicos universales que definen tu impronta soberana.' : 'By evaluating your profile across five independent alphabets, reduction methodologies, and calendars, statistical noise is eliminated. The recurrences in your anchors represent deterministic harmonic intersections that define your Sovereign Code.'}</p>
        </div>
      </div>` });

    /* 6–8 · ANCHORS DEEP-DIVE */
    r.overlap.anchors.forEach((a, i) => pages.push({
      title: state.lang === 'es'
        ? ['Ancla de Firma', 'Motor de Riqueza', 'Fundación Estructural'][i]
        : ['Signature Anchor', 'Wealth Engine', 'Foundation'][i],
      html: anchorPage(a, i, C_LANG)
    }));

    /* 9 · SYSTEM I · PYTHAGOREAN */
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
        <div class="grid sm:grid-cols-2 gap-3 mt-3">
          <div class="card-soft p-3 avoid-break">
            <div class="flex items-center justify-between">
              <span class="text-[0.62rem] uppercase tracking-wider text-zinc-400 font-semibold">${state.lang === 'es' ? 'Expresión Total' : 'Full Name Expression'}</span>
              <span class="badge-gold !text-[0.68rem] font-mono">${p.expression.display}</span>
            </div>
            <p class="font-mono text-[0.72rem] text-champagne mt-1 break-all">${p.mathBreakdown ? p.mathBreakdown.exprFormula : ''} = ${p.expression.raw} → <b class="text-gold">${p.expression.value}</b></p>
            <p class="text-[0.65rem] text-zinc-500 mt-0.5">${state.lang === 'es' ? 'Suma de todas las letras del nombre completo' : 'Sum of all letters across full birth name'}</p>
          </div>
          <div class="card-soft p-3 avoid-break">
            <div class="flex items-center justify-between">
              <span class="text-[0.62rem] uppercase tracking-wider text-gold font-semibold">${state.lang === 'es' ? 'Deseo del Alma (Vocales)' : 'Soul Urge (Vowels)'}</span>
              <span class="badge-gold !text-[0.68rem] font-mono">${p.soulUrge.display}</span>
            </div>
            <p class="font-mono text-[0.72rem] text-champagne mt-1 break-all">${p.mathBreakdown ? p.mathBreakdown.vowelFormula : ''} = ${p.soulUrge.raw}${p.soulUrge.raw > 9 ? ' → <b class="text-gold">' + p.soulUrge.value + '</b>' : ''}</p>
            <p class="text-[0.65rem] text-zinc-500 mt-0.5">${state.lang === 'es' ? 'Suma de las vocales (enmarcadas en oro)' : 'Sum of vowel vibrations (gold outlines)'}</p>
          </div>
          <div class="card-soft p-3 avoid-break">
            <div class="flex items-center justify-between">
              <span class="text-[0.62rem] uppercase tracking-wider text-zinc-400 font-semibold">${state.lang === 'es' ? 'Personalidad (Consonantes)' : 'Personality (Consonants)'}</span>
              <span class="badge-gold !text-[0.68rem] font-mono">${p.personality.display}</span>
            </div>
            <p class="font-mono text-[0.72rem] text-champagne mt-1 break-all">${p.mathBreakdown ? p.mathBreakdown.consFormula : ''} = ${p.personality.raw}${p.personality.raw > 9 ? ' → <b class="text-gold">' + p.personality.value + '</b>' : ''}</p>
            <p class="text-[0.65rem] text-zinc-500 mt-0.5">${state.lang === 'es' ? 'Suma de todas las consonantes exteriores' : 'Sum of all outer consonant vibrations'}</p>
          </div>
          <div class="card-soft p-3 avoid-break">
            <div class="flex items-center justify-between">
              <span class="text-[0.62rem] uppercase tracking-wider text-zinc-400 font-semibold">${state.lang === 'es' ? 'Consonantes Primer Nombre' : 'First-Name Consonants'}</span>
              <span class="badge-gold !text-[0.68rem] font-mono">${p.firstNameConsonants.display}</span>
            </div>
            <p class="font-mono text-[0.72rem] text-champagne mt-1 break-all">${p.mathBreakdown ? p.mathBreakdown.firstConsFormula : ''} = ${p.firstNameConsonants.raw}${p.firstNameConsonants.raw > 9 ? ' → <b class="text-gold">' + p.firstNameConsonants.value + '</b>' : ''}</p>
            <p class="text-[0.65rem] text-zinc-500 mt-0.5">${state.lang === 'es' ? 'Fundación estructural de acción e iniciativa' : 'Structural foundation of action & initiative'}</p>
          </div>
        </div>
      </div>
      <div class="space-y-4 mt-6">
        ${PA(p.lifePath.value) ? interp(`${state.lang === 'es' ? 'Sendero de Vida' : 'Life Path'} ${p.lifePath.value} · ${state.lang === 'es' ? 'El Camino' : 'The Road'}`, sentences(PA(p.lifePath.value).core, 2)) : ''}
        ${PA(p.expression.value) ? interp(`${state.lang === 'es' ? 'Expresión' : 'Expression'} ${p.expression.value} · ${state.lang === 'es' ? 'El Instrumental' : 'The Toolkit'}`, state.lang === 'es' ? `Tus instrumentos naturales son ${PA(p.expression.value).keywords.join(', ').toLowerCase()}. ${sentences(PA(p.expression.value).wealth, 1)}` : `Your natural instruments are ${PA(p.expression.value).keywords.join(', ').toLowerCase()}. ${sentences(PA(p.expression.value).wealth, 1)}`) : ''}
        ${PA(p.soulUrge.value) ? interp(`${state.lang === 'es' ? 'Deseo del Alma' : 'Soul Urge'} ${p.soulUrge.value} · ${state.lang === 'es' ? 'El Anhelo Profundo' : 'The Hunger'}`, PA(p.soulUrge.value).soul) : interp(state.lang === 'es' ? 'Deseo del Alma · Silente' : 'Soul Urge · Silent', state.lang === 'es' ? 'El deseo del alma fluye como una corriente íntima y serena.' : 'The Soul Urge reads as a silent, inward current.')}
        ${PA(p.personality.value) ? interp(`${state.lang === 'es' ? 'Personalidad' : 'Personality'} ${p.personality.value} · ${state.lang === 'es' ? 'La Máscara' : 'The Mask'}`, PA(p.personality.value).persona) : ''}
      </div>` });

    /* 10 · SYSTEM II · CHALDEAN */
    const compounds = [
      [state.lang === 'es' ? 'Primer Nombre' : 'First Name', ch.firstName],
      [state.lang === 'es' ? 'Apellido' : 'Last Name', ch.lastName],
      [state.lang === 'es' ? 'Nombre Completo' : 'Full Name', ch.total]
    ];
    const seenC = new Set();
    pages.push({ title: state.lang === 'es' ? 'Sistema II · Caldeo' : 'System II · Chaldean', html: `
      ${secHead(state.lang === 'es' ? 'Sistema II · Babilonia' : 'System II · Babylon', state.lang === 'es' ? 'Análisis de Compuestos Caldeos' : 'Chaldean Compound Analysis', state.lang === 'es' ? 'El sistema numérico más antiguo clasifica las letras por vibración sonora del 1 al 8. El nueve es sagrado y jamás se asigna. El número compuesto revela la historia profunda y el destino oculto; el reducido expresa la manifestación externa.' : 'The oldest numerical system on record assigns letters by sound vibration, using only 1–8. Nine is sacred and never assigned. The compound number (before reduction) reveals the hidden story; the root reveals the outer expression.')}
      <div class="grid grid-cols-3 gap-1.5 sm:gap-3 mt-6">
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

    /* 11 · SYSTEM III · KABBALAH PART 1 — TREE OF LIFE & PILLARS */
    pages.push({ title: state.lang === 'es' ? 'Cábala · Árbol de la Vida' : 'Kabbalah · Tree of Life', html: `
      ${secHead(state.lang === 'es' ? 'Sistema III · Mística Hebrea' : 'System III · Hebrew Mysticism', state.lang === 'es' ? 'El Árbol de la Vida y Balance de Columnas' : 'The Tree of Life & Pillar Balance', state.lang === 'es' ? 'Tus números esenciales se ubican en las diez Sephirot del Árbol de la Vida. La columna hacia la que se inclinan revela cómo la fuerza se transmuta en forma en tu vida.' : 'Your core numbers are placed on the ten Sephirot of the Tree of Life. The pillar they lean toward reveals how force becomes form in your life.')}
      <div class="grid sm:grid-cols-5 gap-6 mt-6 items-start">
        <div class="sm:col-span-2 avoid-break">${treeSvg(new Set(k.activeSephirot))}</div>
        <div class="sm:col-span-3 space-y-4 pt-1">
          <div class="card-soft p-4 avoid-break">
            <p class="eyebrow !text-[0.55rem]">${state.lang === 'es' ? 'Columna Dominante en Tu Matriz' : 'Dominant Pillar in Your Matrix'}</p>
            <p class="font-display text-champagne text-lg mt-1">${k.dominantPillar === 'Mercy' ? (state.lang === 'es' ? 'Columna de la Misericordia (Expansión)' : 'Pillar of Mercy (Expansion)') : k.dominantPillar === 'Severity' ? (state.lang === 'es' ? 'Columna del Rigor (Forma y Juicio)' : 'Pillar of Severity (Form & Judgment)') : (state.lang === 'es' ? 'Columna del Equilibrio (Mildness)' : 'Pillar of Mildness (Equilibrium)')}</p>
            <p class="lead mt-2 !text-[1.05rem] leading-relaxed">${C_LANG.PILLAR_TEXT[k.dominantPillar]}</p>
          </div>
          <div class="card-soft p-4 avoid-break">
            <p class="eyebrow !text-[0.55rem]">${state.lang === 'es' ? 'La Dinámica de las Tres Columnas' : 'The Three Pillars Dynamics'}</p>
            <p class="text-xs text-zinc-300 mt-1.5 leading-relaxed">${state.lang === 'es' ? 'La Columna Derecha (Misericordia) canaliza la fuerza, la creatividad y la iniciativa. La Columna Izquierda (Rigor) aporta contención, estructura y límites. La Columna Central (Equilibrio) sintetiza ambas en conciencia soberana y armonía.' : 'The Right Pillar of Mercy channels force, visionary fire, and expansion. The Left Pillar of Severity provides structure, critical discernment, and containment. The Middle Pillar of Equilibrium integrates both into conscious sovereignty.'}</p>
          </div>
        </div>
      </div>
      <div class="mt-6 avoid-break">
        <p class="eyebrow">${state.lang === 'es' ? 'Equilibrio de Columnas' : 'Pillar Balance'}</p>
        <div class="grid sm:grid-cols-3 gap-3.5 mt-3">
          ${[
            { key: 'Mercy', enName: 'Pillar of Mercy', esName: 'Columna de la Misericordia', nums: '(2, 4, 7)' },
            { key: 'Mildness', enName: 'Pillar of Mildness / Equilibrium', esName: 'Columna del Equilibrio', nums: '(1, 6, 9)' },
            { key: 'Severity', enName: 'Pillar of Severity', esName: 'Columna del Rigor', nums: '(3, 5, 8)' }
          ].map((p) => {
            const pData = PIL[p.key];
            const pName = state.lang === 'es' ? p.esName : p.enName;
            const pct = Math.min(100, Math.round(((pData.count || 0) / (k.placements.length || 1)) * 100));
            return `
              <div class="card-soft p-3.5 avoid-break flex flex-col justify-between">
                <div>
                  <div class="flex items-start justify-between gap-2">
                    <span class="font-display text-[0.8rem] text-ivory leading-snug">${pName}</span>
                    <span class="font-display text-gold text-sm font-bold shrink-0">${pData.count} / ${k.placements.length}</span>
                  </div>
                  <div class="mt-1 flex items-center justify-between text-[0.72rem]">
                    <span class="text-zinc-500">${state.lang === 'es' ? 'Esferas Activas:' : 'Active Spheres:'}</span>
                    <span class="text-gold font-mono font-semibold tracking-wider">${p.nums}</span>
                  </div>
                </div>
                <div class="bar-track mt-3">
                  <div class="bar-fill" style="width:${pct}%"></div>
                </div>
              </div>`;
          }).join('')}
        </div>
      </div>` });

    /* 12 · SYSTEM III · KABBALAH PART 2 — 5 ILLUMINATED SEPHIROT */
    pages.push({ title: state.lang === 'es' ? 'Cábala · Sephirot Iluminadas' : 'Kabbalah · Illuminated Sephirot', html: `
      ${secHead(
        state.lang === 'es' ? 'Sistema III · Los Senderos de la Luz' : 'System III · Paths of Illumination',
        state.lang === 'es' ? 'Tus 5 Esferas Sephirot Iluminadas' : 'Your 5 Illuminated Sephirot Spheres',
        state.lang === 'es' ? 'Las cinco emanaciones divinas activadas por tu Sendero de Vida, Expresión, Nombre Caldeo, Impulso del Alma y Apellido.' : 'The five divine emanations illuminated by your Life Path, Expression, Chaldean Name, Soul Urge, and Surname.'
      )}
      <div class="space-y-3 mt-5 avoid-break">
        ${k.placements.map((pl) => `
          <div class="card-soft p-3.5 avoid-break flex gap-3.5 items-start">
            ${medal(pl.value, 'sm')}
            <div class="flex-1">
              <div class="flex items-baseline justify-between gap-2">
                <p class="font-display text-[0.95rem] text-champagne">${pl.sephirah.name} · ${pl.sephirah.title}</p>
                <span class="text-[0.58rem] tracking-[0.18em] uppercase text-zinc-500">${translateSource(pl.label)}</span>
              </div>
              <p class="text-[0.78rem] text-zinc-300 mt-1 leading-snug">${C_LANG.SEPHIROT_TEXT[pl.value]}</p>
            </div>
          </div>`).join('')}
      </div>
      <div class="card-soft p-4 sm:p-5 mt-5 border border-gold/30 avoid-break" style="border-color:rgba(212,175,55,.35)">
        <p class="eyebrow !text-gold">${state.lang === 'es' ? 'Alineación Cabalística del Alma y Alquimia Relacional' : 'Kabbalistic Soul Alignment & Relationship Alchemy'}</p>
        <p class="text-xs text-zinc-300 mt-2 leading-relaxed">
          ${state.lang === 'es'
            ? 'La tradición cabalística enseña que la fuerza no manifestada desciende desde las esferas superiores a través de Tiphareth (el Centro del Corazón) y Yesod (el Espejo Emocional) antes de plasmarse en Malkuth (el Mundo Físico). Cuando tus vínculos íntimos y decisiones diarias honran tus esferas activas, el flujo energético es limpio, magnético y autorregenerativo; cuando operas desde la sombra o reprimes tus esferas, surge fricción o agotamiento.'
            : 'Kabbalistic wisdom teaches that divine creative force descends from the upper supernals through Tiphareth (the Heart Center) and Yesod (the Emotional Mirror) before materializing into Malkuth (Physical Reality). When your intimate relationships and daily choices honor your illuminated spheres, energetic flow is clean, magnetic, and self-replenishing; when operating from their shadow, friction and emotional leakage occur.'}
        </p>
      </div>` });

    /* 13 · SYSTEM IV · VEDIC */
    const vRows = [
      [state.lang === 'es' ? 'Moolank' : 'Moolank', state.lang === 'es' ? 'Psíquico / Conductor' : 'Psychic / Driver', v.moolank, moolCalc],
      [state.lang === 'es' ? 'Bhagyank' : 'Bhagyank', state.lang === 'es' ? 'Destino / Conductor' : 'Destiny / Conductor', v.bhagyank, bhagCalc],
      [state.lang === 'es' ? 'Namank' : 'Namank', state.lang === 'es' ? 'Vibración del Nombre' : 'Name Vibration', v.namank, namCalc]
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
        ${vRows.map(([t, sub, n, calcBadge]) => `
          <div class="card-soft p-4 sm:p-5 avoid-break flex gap-4 items-start">
            ${medal(n.value, 'md')}
            <div class="flex-1">
              <div class="flex flex-wrap items-baseline justify-between gap-2">
                <div class="flex flex-wrap items-baseline gap-x-3">
                  <p class="font-display text-lg text-ivory">${t}</p>
                  <p class="text-[0.6rem] tracking-[0.2em] uppercase text-zinc-500">${sub}</p>
                </div>
                <span class="badge-gold !text-[0.68rem] font-mono font-semibold py-0.5 px-2.5">${calcBadge}</span>
              </div>
              <p class="font-display text-champagne mt-1">${n.ruler.planet} · ${n.ruler.english} <span class="text-zinc-500 font-sans text-xs">· ${n.ruler.archetype}</span></p>
              <p class="text-[0.82rem] text-zinc-300 mt-2">${C_LANG.VEDIC_TEXT[n.value]}</p>
              <p class="text-[0.7rem] text-zinc-500 mt-2">${state.lang === 'es' ? 'Día de poder:' : 'Power day:'} <span class="text-champagne">${n.ruler.day}</span> · ${state.lang === 'es' ? 'Gema:' : 'Gem:'} <span class="text-champagne">${n.ruler.gem}</span> · ${state.lang === 'es' ? 'Colores:' : 'Colours:'} <span class="text-champagne">${n.ruler.color}</span></p>
            </div>
          </div>`).join('')}
      </div>
      <div class="space-y-4 mt-6">${interp(state.lang === 'es' ? 'Psíquico × Destino' : 'Driver × Conductor', vNote)}${interp(state.lang === 'es' ? 'Resonancia del Nombre' : 'Name Resonance', nNote)}</div>` });

    /* 14 · SYSTEM V · CHINESE LO SHU */
    pages.push({ title: state.lang === 'es' ? 'Sistema V · Lo Shu' : 'System V · Lo Shu', html: `
      ${secHead(state.lang === 'es' ? 'Sistema V · China Imperial' : 'System V · Imperial China', state.lang === 'es' ? 'Cuadrado Mágico Lo Shu y Cinco Elementos' : 'Lo Shu Magic Square & Five Elements', state.lang === 'es' ? `Cada dígito de tu fecha de nacimiento (${r.input.birth.compact}) más tu Sendero de Vida (${p.lifePath.value}), Expresión (${p.expression.value}) y Nombre Caldeo (${ch.total.value}) se ubica en el cuadrado Lo Shu 3×3, cuyas filas y columnas suman 15.` : `Every digit of your birth date (${r.input.birth.compact}) plus your Life Path (${p.lifePath.value}), Expression (${p.expression.value}) and Chaldean Name (${ch.total.value}) is placed into the 3×3 Lo Shu square, whose rows, columns and diagonals all sum to 15.`)}
      <div class="grid sm:grid-cols-2 gap-7 mt-6 items-start">
        <div class="avoid-break">
          <div class="mb-3.5 p-2.5 rounded-lg border border-gold/25 bg-charcoal/60 text-xs">
            <p class="text-[0.6rem] uppercase tracking-widest text-zinc-400 font-semibold mb-1">${state.lang === 'es' ? 'Dígitos de Entrada en la Matriz:' : 'Matrix Input Digits:'}</p>
            <div class="font-mono text-[0.72rem] text-champagne flex flex-wrap gap-x-2.5 gap-y-1">
              <span><b>${state.lang === 'es' ? 'Fecha:' : 'Birth Date:'}</b> <span class="text-gold font-semibold">${r.input.birth.compact.split('').join(', ')}</span></span>
              <span><b>${state.lang === 'es' ? 'Esenciales:' : 'Core Numbers:'}</b> <span class="text-gold font-semibold">LP ${p.lifePath.value}, EXP ${p.expression.value}, CH ${ch.total.value}</span></span>
            </div>
          </div>
          ${loShuGrid(l)}
          <p class="text-[0.68rem] text-zinc-500 mt-3">${state.lang === 'es' ? 'Ausentes:' : 'Missing:'} ${l.missing.length ? l.missing.join(', ') : (state.lang === 'es' ? 'ninguno' : 'none')} · ${state.lang === 'es' ? 'Repetidos:' : 'Repeated:'} ${l.repeated.length ? l.repeated.map((n) => `${n}×${l.counts[n]}`).join(', ') : (state.lang === 'es' ? 'ninguno' : 'none')}</p>
        </div>
        <div class="space-y-3 avoid-break">
          <p class="eyebrow">${state.lang === 'es' ? 'Cinco Elementos' : 'Five Elements'}</p>
          ${Object.keys(l.elements).map((e) => bar(`${e} <span class="text-zinc-600">· ${E.ELEMENTS[e].theme}</span>`, l.elements[e], maxE, l.elements[e] + '×')).join('')}
          <div class="card-soft p-4 mt-3"><p class="font-display text-champagne">${state.lang === 'es' ? 'Dominante:' : 'Dominant:'} ${l.dominantElement} <span class="text-zinc-500 text-xs font-sans">(${l.dominantNumber})</span></p><p class="text-[0.8rem] text-zinc-300 mt-1">${ET.text}</p><p class="text-[0.75rem] text-zinc-400 mt-2"><b class="text-gold">${state.lang === 'es' ? 'Activar:' : 'Activate:'}</b> ${ET.activate}</p></div>
        </div>
      </div>
      <div class="grid sm:grid-cols-2 gap-5 mt-6">
        <div class="avoid-break"><p class="eyebrow">${state.lang === 'es' ? 'Flechas de Fortaleza' : 'Arrows of Strength'}</p>${l.arrowsOfStrength.length ? l.arrowsOfStrength.map((a) => `<p class="text-sm mt-2"><span class="text-champagne">${a.name}</span> <span class="text-zinc-600">(${a.nums.join('-')})</span><br/><span class="text-zinc-400 text-[0.8rem]">${C_LANG.ARROW_TEXT[a.key].strong}</span></p>`).join('') : `<p class="text-sm text-zinc-500 mt-2">${state.lang === 'es' ? 'Fortalezas distribuidas de manera equilibrada.' : 'No complete arrows. Strengths are distributed.'}</p>`}</div>
        <div class="avoid-break"><p class="eyebrow">${state.lang === 'es' ? 'Flechas a Desarrollar' : 'Arrows to Develop'}</p>${l.arrowsOfWeakness.length ? l.arrowsOfWeakness.map((a) => `<p class="text-sm mt-2"><span class="text-champagne">${a.name}</span> <span class="text-zinc-600">(${a.nums.join('-')})</span><br/><span class="text-zinc-400 text-[0.8rem]">${C_LANG.ARROW_TEXT[a.key].weak}</span></p>`).join('') : `<p class="text-sm text-zinc-500 mt-2">${state.lang === 'es' ? 'Ningún plano de tu matriz está totalmente ausente.' : 'No empty arrows. Grid is complete.'}</p>`}</div>
      </div>
      ${interp(l.hasWealthEight ? (state.lang === 'es' ? 'El Número de Suprema Riqueza Está Activo' : 'The Supreme Wealth Number Is Present') : (state.lang === 'es' ? 'La Riqueza Debe Forjarse Metódicamente' : 'The Wealth Number Must Be Built'), l.hasWealthEight ? (state.lang === 'es' ? `El 8 (Fa, 發) se manifiesta ${l.counts[8]}× en tu matriz, señalando un canal natural hacia la prosperidad material a través de la Tierra: paciencia, activos reales y la resistencia inquebrantable de la Montaña.` : `The 8 (Fa, 發) appears ${l.counts[8]}× in your grid, signalling a natural channel for prosperity through Earth: patience, real assets and the Mountain's endurance.`) : (state.lang === 'es' ? 'Tu matriz no cuenta con 8 directo. La riqueza se construye activando deliberadamente el elemento Tierra, presupuestos estructurados y vehículos sólidos de acumulación.' : 'Your grid holds no 8. Prosperity is cultivated consciously: activate the Earth element, formalize savings, and work with 8-ruled timing.'))}` });

    /* 15 · FULL PAGE SOMATIC VITALITY & NERVOUS SYSTEM ARCHITECTURE */
    pages.push({ title: state.lang === 'es' ? 'Salud y Vitalidad Somática' : 'Somatic Vitality & Health', html: `
      ${secHead(
        state.lang === 'es' ? 'Arquitectura de Salud y Biorritmo' : 'Health, Vitality & Nervous System Architecture',
        state.lang === 'es' ? 'Tu Constitución Somática y Vitalidad' : 'Your Somatic Vitality & Energy Blueprint',
        state.lang === 'es'
          ? 'Sintetizando la medicina tradicional china (Wu Xing), la constitución ayurvédica védica (Doshas) y tus ciclos bio-rítmicos de 52 días para optimizar tu energía, recuperación y longevidad.'
          : 'Synthesizing Chinese Five-Element medicine (Wu Xing), Vedic Ayurvedic constitutional typing (Doshas), and 52-day bio-rhythmic cycles to optimize vitality, nervous system regulation, and peak longevity.'
      )}
      <div class="grid sm:grid-cols-2 gap-4 mt-6">
        <div class="card-soft p-5 avoid-break">
          <p class="eyebrow !text-gold">${state.lang === 'es' ? 'I · Sistema Orgánico Dominante (Wu Xing)' : 'I · Dominant Organ System (Wu Xing)'}</p>
          <p class="font-display text-champagne text-base mt-2">${state.lang === 'es' ? 'Elemento' : 'Element'}: <span class="text-gold font-bold">${l.dominantElement}</span></p>
          <p class="text-xs text-zinc-400 mt-1"><b class="text-zinc-300">${state.lang === 'es' ? 'Sistemas Gobernados:' : 'Governed Systems:'}</b> ${domSomatic.organs}</p>
          <p class="text-xs text-zinc-300 mt-2 leading-relaxed">${domSomatic.power}</p>
        </div>

        <div class="card-soft p-5 avoid-break">
          <p class="eyebrow !text-rose-300/80">${state.lang === 'es' ? 'II · Punto de Agotamiento y Recarga' : 'II · Stress Depletion & Rebalance'}</p>
          <p class="font-display text-champagne text-base mt-2">${state.lang === 'es' ? 'Elemento Vulnerable' : 'Vulnerable Element'}: <span class="text-rose-300 font-bold">${weakEl || (state.lang === 'es' ? 'Equilibrado' : 'Balanced')}</span></p>
          ${weakSomatic ? `
            <p class="text-xs text-zinc-400 mt-1">${weakSomatic.depletion}</p>
            <p class="text-xs text-zinc-300 mt-2 leading-relaxed"><b class="text-gold">${state.lang === 'es' ? 'Protocolo de Recarga:' : 'Rebalance Protocol:'}</b> ${weakSomatic.rebalance}</p>
          ` : `
            <p class="text-xs text-zinc-400 mt-2">${state.lang === 'es' ? 'Tu matriz sostiene una distribución armónica de los cinco elementos.' : 'Your matrix maintains an equitable harmonic distribution of the five elements.'}</p>
          `}
        </div>

        <div class="card-soft p-5 avoid-break">
          <p class="eyebrow">${state.lang === 'es' ? 'III · Constitución Ayurvédica Védica' : 'III · Ayurvedic Energy Profile'}</p>
          <p class="font-display text-champagne text-base mt-2">${ayurMool.dosha} <span class="text-zinc-500 font-sans text-xs">(${ayurMool.title})</span></p>
          <p class="text-xs text-zinc-300 mt-2 leading-relaxed">${ayurMool.profile}</p>
          <p class="text-xs text-zinc-300 mt-2 leading-relaxed"><b class="text-gold">${state.lang === 'es' ? 'Regulación del Sistema Nervioso:' : 'Nervous System Reset:'}</b> ${ayurMool.protocolShort}</p>
        </div>

        <div class="card-soft p-5 avoid-break">
          <p class="eyebrow">${state.lang === 'es' ? 'IV · Biorritmo Físico y Recuperación Activa' : 'IV · Active Bio-Rhythm & Cellular Recovery'}</p>
          <p class="font-display text-champagne text-base mt-2">${cy.current.name} · <span class="mode-pill mode-${curT.modeTone}">${bioCycle.mode}</span></p>
          <p class="text-xs text-zinc-300 mt-2 leading-relaxed">${bioCycle.protocol}</p>
          <p class="text-xs text-zinc-400 mt-2 leading-relaxed"><b class="text-champagne">${state.lang === 'es' ? 'Directiva de Sueño y Brillo:' : 'Sleep & Radiance Directive:'}</b> ${state.lang === 'es' ? 'Mantén un ritmo circadiano constante y reduce la sobreestimulación sensorial en las 2 horas previas al descanso.' : 'Prioritize circadian light alignment and eliminate sensory overstimulation in the final 2 hours before restorative sleep.'}</p>
        </div>
      </div>
      <p class="text-[0.65rem] text-zinc-500 mt-6 leading-relaxed text-center avoid-break">
        ${state.lang === 'es'
          ? 'Aviso de bienestar holístico: Esta sección sintetiza tradiciones metafísicas milenarias (Medicina Tradicional China Wu Xing, Ayurveda Védica y Ciclos Rosacruces) para el autoconocimiento y la optimización de energía. No constituye diagnóstico ni tratamiento médico.'
          : 'Holistic vitality note: This section synthesizes ancient constitutional traditions (Traditional Chinese Medicine Wu Xing, Ayurvedic Doshas, and Rosicrucian Biorhythms) for self-reflection and lifestyle alignment. It does not provide medical diagnosis or treatment.'}
      </p>` });

    /* 16 · INTEGRATION PART 1 — THE 4 SOVEREIGN PILLARS */
    pages.push({ title: state.lang === 'es' ? 'Los 4 Pilares Soberanos' : 'The 4 Sovereign Pillars', html: `
      ${secHead(state.lang === 'es' ? 'Integración Estratégica · Parte 1' : 'Strategic Integration · Part 1', state.lang === 'es' ? 'Los Cuatro Pilares Soberanos' : 'The Four Sovereign Pillars', state.lang === 'es' ? 'Riqueza, mando estratégico, magnetismo relacional y vitalidad biológica sintetizados en cuatro pilares fundamentales.' : 'Wealth, command, relational magnetism, and biological vitality, synthesized into four foundational pillars.')}
      <div class="grid sm:grid-cols-2 gap-4 mt-6">
        <div class="card-soft p-5 avoid-break">
          <p class="eyebrow">${state.lang === 'es' ? 'I · Arquitectura de Riqueza y Capital' : 'I · Wealth & Capital Architecture'}</p>
          <p class="text-sm text-zinc-300 mt-2">${state.lang === 'es' ? `Tu Motor Secundario es <b class="text-champagne">${a2.number} · ${A2.name}</b>. ${A2.wealth}` : `Your Secondary Engine is <b class="text-champagne">${a2.number} · ${A2.name}</b>. ${A2.wealth}`}</p>
          <p class="text-sm text-zinc-300 mt-2">${state.lang === 'es' ? `Tu regente védico <b class="text-champagne">${bhag.planet}</b> complementa: ${C_LANG.VEDIC_TEXT[v.bhagyank.value]} Tu elemento dominante <b class="text-champagne">${l.dominantElement}</b> orienta tu sector de riqueza hacia el <b class="text-champagne">${ET.direction}</b>.` : `Your Vedic Conductor, <b class="text-champagne">${bhag.planet}</b>, adds: ${C_LANG.VEDIC_TEXT[v.bhagyank.value]} Your dominant <b class="text-champagne">${l.dominantElement}</b> element points your wealth corner to the <b class="text-champagne">${ET.direction}</b>.`}</p>
        </div>

        <div class="card-soft p-5 avoid-break">
          <p class="eyebrow">${state.lang === 'es' ? 'II · Mando y Estrategia Soberana' : 'II · Strategy & Sovereign Command'}</p>
          <p class="text-sm text-zinc-300 mt-2">${state.lang === 'es' ? `Lidera desde tu Ancla de Firma <b class="text-champagne">${a1.number} · ${A1.name}</b>. ${A1.tactics[0]} ${A1.tactics[1]} Apóyate en tu Fundación <b class="text-champagne">${a3.number} · ${A3.name}</b>: ${sentences(A3.foundation, 2)}` : `Lead from your Signature Anchor <b class="text-champagne">${a1.number} · ${A1.name}</b>. ${A1.tactics[0]} ${A1.tactics[1]} Ground every campaign in your Foundation <b class="text-champagne">${a3.number} · ${A3.name}</b>: ${sentences(A3.foundation, 2)}`}</p>
          <p class="text-sm text-zinc-300 mt-2">${state.lang === 'es' ? `En este momento te encuentras en <b class="text-champagne">${cy.current.name}</b>, una ventana en modo <span class="mode-pill mode-${curT.modeTone}">${curT.mode}</span>.` : `Right now you are in <b class="text-champagne">${cy.current.name}</b>, a <span class="mode-pill mode-${curT.modeTone}">${curT.mode}</span> window.`}</p>
        </div>

        <div class="card-soft p-5 avoid-break">
          <p class="eyebrow">${state.lang === 'es' ? 'III · Amor, Vínculos y Magnetismo Social' : 'III · Love, Relationships & Social Magnetism'}</p>
          <p class="text-sm text-zinc-300 mt-2">${soulA ? soulA.soul + ' ' : ''}${persA ? persA.persona + ' ' : ''}${A1.magnetism}</p>
          <p class="text-sm text-zinc-400 mt-2">${state.lang === 'es' ? `Tu campo social se polariza favorablemente proyectando la certeza serena de tu arquetipo <b class="text-champagne">${A1.name}</b>.` : `Your social aura commands authority when operating from the grounded certainty of <b class="text-champagne">${A1.name}</b>.`}</p>
        </div>

        <div class="card-soft p-5 avoid-break">
          <p class="eyebrow">${C_LANG.UI.vitality_pillar_title}</p>
          <p class="text-sm text-zinc-300 mt-2">${state.lang === 'es' ? `Constitución Védica: <b class="text-champagne">${ayurMool.dosha}</b> (${ayurMool.title}), modulada por tu sendero <b class="text-champagne">${ayurBhag.dosha}</b>. ${ayurMool.profile}` : `Ayurvedic Energy: <b class="text-champagne">${ayurMool.dosha}</b> (${ayurMool.title}), modulated by conductor <b class="text-champagne">${ayurBhag.dosha}</b>. ${ayurMool.profile}`}</p>
          <p class="text-sm text-zinc-300 mt-2"><b class="text-gold">${state.lang === 'es' ? 'Biorritmo Activo:' : 'Active Bio-Rhythm:'}</b> ${state.lang === 'es' ? `En tu ciclo actual (${cy.current.name}), tu cuerpo opera en modo <span class="mode-pill mode-${curT.modeTone}">${bioCycle.mode}</span>. ${bioCycle.protocol}` : `In your current cycle (${cy.current.name}), your physical vessel operates in <span class="mode-pill mode-${curT.modeTone}">${bioCycle.mode}</span> mode. ${bioCycle.protocol}`}</p>
        </div>
      </div>` });

    /* 17 · INTEGRATION PART 2 — SOVEREIGN OPERATING CODE */
    pages.push({ title: state.lang === 'es' ? 'Código Operativo' : 'Sovereign Operating Code', html: `
      ${secHead(
        state.lang === 'es' ? 'Integración Estratégica · Parte 2' : 'Strategic Integration · Part 2',
        state.lang === 'es' ? 'Tu Código Operativo Soberano Diario' : 'Your Daily Sovereign Operating Code',
        state.lang === 'es' ? 'Tu hoja de referencia diaria de frecuencias, direcciones de poder, ventanas anuales y rituales de alineación.' : 'Your master daily reference ledger of frequencies, power directions, annual timing windows, and alignment rituals.'
      )}
      <div class="mt-6 avoid-break">
        <table class="lux-table mt-1"><tbody>
          <tr><td class="text-zinc-500 w-[42%]">${state.lang === 'es' ? 'Día Primario de Poder' : 'Primary Power Day'}</td><td class="text-champagne">${mool.day} <span class="text-zinc-500">(${mool.planet})</span></td></tr>
          <tr><td class="text-zinc-500">${state.lang === 'es' ? 'Día de Destino' : 'Destiny Day'}</td><td class="text-champagne">${bhag.day} <span class="text-zinc-500">(${bhag.planet})</span></td></tr>
          <tr><td class="text-zinc-500">${state.lang === 'es' ? 'Gema y Colores de Poder' : 'Power Gem · Colours'}</td><td class="text-champagne">${mool.gem} · ${mool.color}</td></tr>
          <tr><td class="text-zinc-500">${C_LANG.UI.ayurvedic_dosha}</td><td class="text-champagne">${ayurMool.dosha} <span class="text-zinc-500">(${ayurMool.title})</span></td></tr>
          <tr><td class="text-zinc-500">${C_LANG.UI.peak_recovery_protocol}</td><td class="text-champagne text-xs">${ayurMool.protocolShort}</td></tr>
          <tr><td class="text-zinc-500">${state.lang === 'es' ? 'Dirección de Riqueza (Feng Shui)' : 'Wealth Direction (Feng Shui)'}</td><td class="text-champagne">${ET.direction} <span class="text-zinc-500">(${l.dominantElement})</span></td></tr>
          <tr><td class="text-zinc-500">${state.lang === 'es' ? 'Dirección de Amor y Alianzas' : 'Love & Partnerships Direction'}</td><td class="text-champagne">${state.lang === 'es' ? 'Suroeste (Tierra / Armonía)' : 'Southwest (Earth / Harmony)'}</td></tr>
          <tr><td class="text-zinc-500">${state.lang === 'es' ? 'Año Personal' : 'Personal Year'} ${r.personalYear.year}</td><td class="text-champagne">${r.personalYear.value} <span class="text-zinc-500">· ${C_LANG.PERSONAL_YEAR[r.personalYear.value]}</span></td></tr>
          <tr><td class="text-zinc-500">${state.lang === 'es' ? 'Ventana Anual de Riqueza' : 'Annual Wealth Window'}</td><td class="text-champagne">${full ? `${jup.startLabel} – ${jup.endLabel}` : `${LOCK_SVG.replace('width="16" height="16"', 'width="11" height="11"')} Módulo de Ciclos`}</td></tr>
          <tr><td class="text-zinc-500">${state.lang === 'es' ? 'Ventana de Preservación de Capital' : 'Capital Preservation Window'}</td><td class="text-champagne">${full ? `${sat.startLabel} – ${sat.endLabel}` : `${LOCK_SVG.replace('width="16" height="16"', 'width="11" height="11"')} Módulo de Ciclos`}</td></tr>
        </tbody></table>
      </div>
      <div class="card-soft p-4 sm:p-5 mt-6 avoid-break">
        <p class="eyebrow !text-gold">${state.lang === 'es' ? 'Rituales Diarios de Sintonía Matutina y Vespertina' : 'Daily Morning & Evening Alignment Rituals'}</p>
        <p class="text-xs text-zinc-300 mt-2 leading-relaxed">
          ${state.lang === 'es'
            ? `<b class="text-champagne">Ritual Matutino (Activación):</b> Inicia cada jornada afirmando la certeza serena de tu Ancla de Firma <b>${a1.number} (${A1.name})</b>. Antes de revisar notificaciones o demandas externas, dedica 3 minutos a enfocar tu intención en tu dirección de riqueza (${ET.direction}).<br/><b class="text-champagne mt-2 block">Ritual Vespertino (Preservación):</b> Desconecta mediante tu Fundación <b>${a3.number} (${A3.name})</b>. Cierra ciclos abiertos, apaga pantallas 60 minutos antes de dormir y aplica tu protocolo ayurvédico de reseteo del sistema nervioso.`
            : `<b class="text-champagne">Morning Alignment (Activation):</b> Open every day by centering on the quiet certainty of your Signature Anchor <b>${a1.number} (${A1.name})</b>. Before checking notifications or external demands, spend 3 minutes setting daily intention facing your wealth direction (${ET.direction}).<br/><b class="text-champagne mt-2 block">Evening Grounding (Preservation):</b> Unwind through your Foundation Anchor <b>${a3.number} (${A3.name})</b>. Close open loops, disconnect screens 60 minutes prior to rest, and apply your Ayurvedic nervous system reset protocol.`
          }
        </p>
      </div>` });

    /* 18–19 · CYCLES */
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
        <table class="lux-table table-cycles mt-6"><thead><tr><th style="width:10%">#</th><th style="width:34%">${state.lang === 'es' ? 'Período' : 'Period'}</th><th style="width:28%">${state.lang === 'es' ? 'Fechas y Días' : 'Dates & Days'}</th><th style="width:28%;text-align:right">${state.lang === 'es' ? 'Modo Táctico' : 'Mode'}</th></tr></thead><tbody>${cy.periods.map(c => cycleRow(c, C_LANG)).join('')}</tbody></table>` });

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

    /* 20 · CODEX */
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

    // Systems & Table of Contents page (index 2)
    pages[2].html = `
      ${secHead(
        state.lang === 'es' ? 'Orientación y Mapa de Ruta' : 'Orientation & Roadmap',
        state.lang === 'es' ? 'Los 5 Sistemas y Cómo Usar Tu Dossier' : 'The 5 Ancient Systems & Blueprint Guide',
        state.lang === 'es' ? 'Cada tradición antigua codificó una dimensión distinta de tu destino. A continuación, el mapa de tus 20 páginas de sabiduría personalizada.' : 'Each ancient tradition encoded a distinct dimension of your destiny. Below is the master roadmap of your 20-page personalized blueprint.'
      )}
      <div class="grid sm:grid-cols-5 gap-2 mt-5">
        ${C_LANG.SYSTEM_INFO.map((s, i) => `<div class="card-soft p-3 avoid-break"><p class="font-display text-gold">${ROMAN[i]}</p><p class="font-display text-[0.8rem] mt-1">${s.name}</p><p class="text-[0.68rem] text-zinc-500 mt-1 leading-snug">${s.blurb}</p></div>`).join('')}
      </div>
      <p class="eyebrow mt-6">${UI.contents_eyebrow}</p>
      <div class="card-soft p-4 mt-2.5 avoid-break">
        <div class="grid sm:grid-cols-2 gap-x-8 gap-y-1 text-xs text-zinc-300">
          <ol class="space-y-1">
            ${pages.slice(0, 10).map((p, i) => `
              <li class="flex justify-between items-baseline border-b border-white/5 py-1">
                <span class="text-zinc-400"><b class="font-mono text-gold mr-2">${String(i + 1).padStart(2, '0')}</b> ${p.title}</span>
                <span class="font-mono text-[0.7rem] text-zinc-600">${state.lang === 'es' ? 'Pág.' : 'Page'} ${i + 1}</span>
              </li>`).join('')}
          </ol>
          <ol class="space-y-1" start="11">
            ${pages.slice(10, 20).map((p, i) => `
              <li class="flex justify-between items-baseline border-b border-white/5 py-1">
                <span class="text-zinc-400"><b class="font-mono text-gold mr-2">${String(i + 11).padStart(2, '0')}</b> ${p.title}</span>
                <span class="font-mono text-[0.7rem] text-zinc-600">${state.lang === 'es' ? 'Pág.' : 'Page'} ${i + 11}</span>
              </li>`).join('')}
          </ol>
        </div>
      </div>`;

    const html = pages.map((p, i) => {
      const isCover = p.cover;
      const head = isCover ? '' : `<div class="page-head"><span>${state.lang === 'es' ? 'EL PLANO SOBERANO' : 'SOVEREIGN 5-SYSTEM'}</span><span class="hidden sm:inline">${name}</span><span>${p.title}</span></div>`;
      const foot = isCover ? '' : `<div class="page-foot"><span>${state.lang === 'es' ? 'CONFIDENCIAL' : 'CONFIDENTIAL'}</span><span>${state.lang === 'es' ? 'PÁG.' : 'PAGE'} ${i + 1} / ${total}</span></div>`;
      return `
      <article class="page ${isCover ? 'cover' : ''}" data-page="${i + 1}">
        ${head}
        <div class="page-body">
          ${p.html}
        </div>
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
        ? 'Descubre Tu Patrón Oculto de Pareja y Código de Amor'
        : 'Uncover Your Hidden Relationship Pattern & Love Code';
    }
    else if (a === 'checkout') checkout();
    else if (a === 'check-partner-compat') {
      runPartnerCompatibilityCheck();
    }
    else if (a === 'play-triangle-part') {
      const partNum = t.dataset.part || '1';
      playTriangleBriefing(partNum);
    }
    else if (a === 'save-teaser-email') {
      const emInput = $('#teaser-email-input');
      const emVal = emInput ? emInput.value.trim() : '';
      if (!emVal || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emVal)) {
        toast(state.lang === 'es' ? 'Ingresa un correo electrónico válido.' : 'Please enter a valid email address.');
        return;
      }
      if (state.profile) {
        state.profile.email = emVal;
        saveProfile(state.profile);
        sendWebhook('lead_submitted', { trigger: 'teaser_email_bar' });
        const box = $('#teaser-email-box');
        if (box) {
          box.innerHTML = `<p class="text-xs sm:text-sm text-gold font-medium">${state.lang === 'es' ? '✦ ¡Resumen enviado a ' + esc(emVal) + '! Revisa tu bandeja de entrada.' : '✦ Summary sent to ' + esc(emVal) + '! Check your inbox.'}</p>`;
        }
        toast(state.lang === 'es' ? '✦ ¡Resumen de 5 Sistemas enviado a tu correo!' : '✦ 5-System Summary emailed to you!');
      }
    }
    else if (a === 'demo-unlock') demoUnlock();
    else if (a === 'print') window.print();
    else if (a === 'share-code') shareCode();
    else if (a === 'scroll-checkout') $('#checkout').scrollIntoView({ behavior: 'smooth', block: 'start' });
    else if (a === 'partner-checkout') {
      const pDob = state.partnerDob || (state.profile && (state.profile.partner_dob || state.profile.partnerDob)) || '';
      if (state.profile && pDob) {
        state.profile.partner_dob = pDob;
        state.profile.partnerDob = pDob;
        saveProfile(state.profile);
      }
      const coEl = $('#checkout');
      if (coEl && pDob) {
        let banner = $('#checkout-partner-banner');
        if (!banner) {
          banner = document.createElement('div');
          banner.id = 'checkout-partner-banner';
          banner.className = 'mt-4 p-3 rounded-xl border border-gold/50 bg-gold/10 text-xs sm:text-sm text-champagne text-center font-medium';
          coEl.insertBefore(banner, coEl.children[2] || null);
        }
        banner.innerHTML = state.lang === 'es'
          ? `✦ <b>Sinastría de Pareja Activada:</b> Fecha de pareja (<b>${esc(pDob)}</b>) vinculada a tu Dossier de 20 Páginas y Calendario de Sincronía.`
          : `✦ <b>Partner Synastry Linked:</b> Partner birthday (<b>${esc(pDob)}</b>) saved to your 20-Page Dossier &amp; Soulmate Timing Report.`;
      }
      const total = CONFIG.PRICE_BASE + (state.bump ? CONFIG.PRICE_BUMP : 0);
      sendWebhook('checkout_clicked', {
        trigger: 'partner_compat_cta',
        partner_dob: pDob,
        bump: state.bump,
        total,
        tier: state.bump ? 'full_bundle' : 'base',
        tier_label: `Partner Synastry CTA ($${total})`,
      });
      if (coEl) coEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    else if (a === 'upgrade') {
      sendWebhook('checkout_clicked', { bump: true, total: CONFIG.PRICE_BUMP, tier: 'upgrade_cycles', tier_label: `$${CONFIG.PRICE_BUMP} Upgrade (52-Day Cycles Add-On)` });
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

  function runPartnerCompatibilityCheck() {
    if (!state.result) return;
    const mEl = $('#partnerDobMonth');
    const dEl = $('#partnerDobDay');
    const yEl = $('#partnerDobYear');
    const resBox = $('#partner-compat-result');
    if (!mEl || !dEl || !yEl || !resBox) return;
    const m = mEl.value;
    const d = dEl.value;
    const y = yEl.value;
    const isEs = state.lang === 'es';
    if (!m || !d || !y) {
      toast(isEs ? 'Selecciona el Mes, Día y Año de nacimiento de tu pareja.' : 'Please select your partner or crush\'s Birth Month, Day, and Year.');
      return;
    }
    const rep = getPartnerCompatReport(state.result, m, d, y, state.lang);
    state.partnerDob = rep.pIso;
    if (state.profile) {
      state.profile.partner_dob = rep.pIso;
      state.profile.partnerDob = rep.pIso;
      saveProfile(state.profile);
    }
    const userDobStr = (state.result && state.result.input && state.result.input.birthDate) || (state.profile && state.profile.birthDate) || '';
    sendWebhook('partner_check_run', {
      user_dob: userDobStr,
      partner_dob: rep.pIso,
      compatibility_score: rep.magnetismScore,
      magnetism_score: rep.magnetismScore,
      partner_moolank: rep.pMoolank,
      partner_lifepath: rep.pLife,
    });
    resBox.classList.remove('hidden');
    resBox.innerHTML = `
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center">
        <div class="card-soft p-3.5 border border-gold/40">
          <div class="text-[0.6rem] uppercase tracking-[0.16em] text-zinc-400">${isEs ? 'Química y Magnetismo' : 'Chemistry & Magnetism'}</div>
          <div class="font-display text-2xl sm:text-3xl text-gold mt-1">${rep.magnetismScore}%</div>
          <div class="text-[0.65rem] text-emerald-300 mt-0.5">${isEs ? 'Atracción Inmediata' : 'High Initial Pull'}</div>
        </div>
        <div class="card-soft p-3.5 border border-white/10">
          <div class="text-[0.6rem] uppercase tracking-[0.16em] text-zinc-400">${isEs ? 'Conductor Natal de Tu Pareja' : 'Their Birth-Day Driver'}</div>
          <div class="font-display text-xl text-champagne mt-1">#${rep.pMoolank} · ${rep.pRuler}</div>
          <div class="text-[0.65rem] text-zinc-400 mt-0.5">${isEs ? 'Sendero Occidental' : 'Western Life Path'} #${rep.pLife}</div>
        </div>
        <div class="card-soft p-3.5 border border-rose-400/35 bg-rose-950/20">
          <div class="text-[0.6rem] uppercase tracking-[0.16em] text-rose-300">${isEs ? 'Riesgo de Fricción Oculta' : 'Unresolved Friction Risk'}</div>
          <div class="font-display text-sm sm:text-base text-rose-200 mt-1.5">${rep.frictionLevel}</div>
          <div class="text-[0.65rem] text-zinc-300 mt-0.5">${rep.sharedMissingCount} ${isEs ? 'Vacíos Lo Shu Compartidos' : 'Shared Lo Shu Blindspots'}</div>
        </div>
      </div>
      <p class="text-xs sm:text-sm text-zinc-200 leading-relaxed mt-4">${rep.summary}</p>
      <div class="mt-4 p-4 rounded-xl bg-gold/10 border border-gold/40">
        <p class="text-xs sm:text-sm text-champagne text-left leading-relaxed">
          🔒 <b>${isEs ? 'Desbloquea Su Sinastría Completa en el Dossier de 20 Páginas:' : 'Locked Inside Your Full 20-Page Sovereign Dossier:'}</b>
          ${isEs ? 'Descubre cómo comunicarte con un #' + rep.pMoolank + ' (' + rep.pRuler + ') sin activar su escudo defensivo y qué fechas exactas favorecen su unión en los próximos 12 meses.' : 'See the exact communication rules for a #' + rep.pMoolank + ' (' + rep.pRuler + ') partner so neither of you pulls away—plus your peak relationship dates over the next 12 months.'}
        </p>
        <button type="button" id="btn-partner-checkout-cta" data-action="partner-checkout" class="btn-gold mt-3.5 !py-3.5 !px-5 w-full text-xs sm:text-sm font-bold tracking-wide">
          ${isEs ? 'Unlock Full 5-System Partner Compatibility & Soulmate Timing Report →' : 'Unlock Full 5-System Partner Compatibility & Soulmate Timing Report →'}
        </button>
      </div>
    `;
  }

  function playTriangleBriefing(partNum) {
    if (!state.result) return;
    const isEs = state.lang === 'es';
    const r = state.result;
    const uMoolank = r.vedic.moolank.value;
    const uRuler = r.vedic.moolank.ruler.planet;
    const uLife = r.pythagorean.lifePath.value;
    const missingStr = r.loShu.missing.join(', ');
    const statusBox = $('#triangle-audio-status');
    const scripts = {
      '1': isEs
        ? `🔊 Parte 1 (Punto Ciego de Apego): Tu número occidental es #${uLife}, pero tu día de nacimiento está regido por #${uMoolank} (${uRuler}). Por eso buscas estabilidad conscientemente, pero a las 2 AM te atraen vínculos intensos que activan tu miedo a no ser escuchado.`
        : `🔊 Part 1 Audio Briefing (Attachment Blindspot): Your Western Life Path is #${uLife}, but your Vedic Birth-Day Driver is #${uMoolank} (${uRuler}). That inner split is why you crave deep intimacy yet instinctively pull back the second a partner feels overwhelming or inconsistent.`,
      '2': isEs
        ? `🔊 Parte 2 (Flechas de Amor Lo Shu): Tu fecha de nacimiento tiene ${r.loShu.missing.length} casillas vacías en el cuadrado chino Lo Shu. Esos números faltantes son lo que inconscientemente pides que tu pareja compense por ti.`
        : `🔊 Part 2 Audio Briefing (Missing Lo Shu Love Arrows): Your birth date leaves ${r.loShu.missing.length} empty boxes in the 3×3 Chinese Lo Shu grid. Those missing numbers are the exact emotional traits you subconsciously project onto partners during arguments.`,
      '3': isEs
        ? `🔊 Parte 3 (Ventana de Tiempo en el Amor): Hoy estás dentro de tu ciclo de 52 días de ${r.cycles.current.ruler} (${r.cycles.daysRemaining} días restantes). Alinear tus conversaciones importantes con tus ciclos de Venus y Luna evita rupturas innecesarias.`
        : `🔊 Part 3 Audio Briefing (12-Month Relationship Timing): You are currently inside your 52-day ${r.cycles.current.ruler} cycle (${r.cycles.daysRemaining} days left). Knowing when your Venus and Moon windows open tells you the exact weeks for commitment, reconciliation, and deep talks.`,
    };
    const msg = scripts[String(partNum)] || scripts['1'];
    if (statusBox) {
      statusBox.classList.remove('hidden');
      statusBox.innerHTML = msg;
    }
    try {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(msg.replace('🔊 ', ''));
        u.lang = isEs ? 'es-ES' : 'en-US';
        u.rate = 1.04;
        window.speechSynthesis.speak(u);
      }
    } catch (e) { /* ignore */ }
    sendWebhook('triangle_briefing_played', { part: partNum });
  }

  document.addEventListener('change', (e) => {
    if (!e.target) return;
    if (e.target.id === 'bump') updateTotal();
    if (['partnerDobMonth', 'partnerDobDay', 'partnerDobYear'].includes(e.target.id)) {
      const mEl = $('#partnerDobMonth');
      const dEl = $('#partnerDobDay');
      const yEl = $('#partnerDobYear');
      if (mEl && dEl && yEl && mEl.value && dEl.value && yEl.value) {
        runPartnerCompatibilityCheck();
      }
    }
  });

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
    utm();

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

    // Conditionally display Founder Sample button:
    // ONLY display if URL contains ?vip=adam, ?demo=1, or on localhost / 127.0.0.1
    const host = (location.hostname || '').toLowerCase();
    const isLocal = host === 'localhost' || host === '127.0.0.1' || host === '0.0.0.0' || host === '';
    const showFounderSample = (
      q.get('vip') === 'adam' ||
      q.get('demo') === '1' ||
      (isLocal && q.get('public_test') !== '1')
    );

    const sampleBtn = $('#btn-sample') || $('[data-action="sample"]');
    const sampleRow = $('#sample-row') || (sampleBtn ? sampleBtn.parentElement : null);
    if (sampleBtn) {
      if (showFounderSample) {
        sampleBtn.classList.remove('hidden');
        sampleBtn.style.display = '';
        if (sampleRow) {
          sampleRow.classList.remove('justify-center');
          sampleRow.classList.add('justify-between');
        }
      } else {
        sampleBtn.classList.add('hidden');
        sampleBtn.style.display = 'none';
        if (sampleRow) {
          sampleRow.classList.remove('justify-between');
          sampleRow.classList.add('justify-center');
        }
      }
    }

    // Set initial language
    setLanguage(state.lang);

    $('#calc-form').addEventListener('submit', onSubmit);

    // Real-time funnel telemetry: calc_started, granular field_progress & instant calc_preview
    let _calcStartedFired = false;
    const _fieldsTouched = new Set();
    const getFieldProgressSnapshot = () => {
      const mEl = $('#dobMonth');
      const dEl = $('#dobDay');
      const yEl = $('#dobYear');
      const nEl = $('#fullName');
      const m = mEl && mEl.value ? mEl.value : '--';
      const d = dEl && dEl.value ? dEl.value : '--';
      const y = yEl && yEl.value ? yEl.value : '----';
      return {
        dob_preview: `${y}-${m}-${d}`,
        name_length: nEl && nEl.value ? nEl.value.trim().length : 0,
      };
    };
    const fireFieldTelemetry = (fieldKey, isValueChange) => {
      const snap = getFieldProgressSnapshot();
      if (!_calcStartedFired) {
        _calcStartedFired = true;
        _fieldsTouched.add(fieldKey);
        sendWebhook('calc_started', Object.assign({ field: fieldKey, fields_touched: Array.from(_fieldsTouched) }, snap));
        return;
      }
      if (!_fieldsTouched.has(fieldKey) || isValueChange) {
        _fieldsTouched.add(fieldKey);
        if (_fieldsTouched.size > 1) {
          sendWebhook('field_progress', Object.assign({ field: fieldKey, fields_touched: Array.from(_fieldsTouched) }, snap));
        }
      }
    };

    const fullNameEl = $('#fullName');
    if (fullNameEl) {
      fullNameEl.addEventListener('focus', () => fireFieldTelemetry('name', false), { once: true });
      fullNameEl.addEventListener('input', () => {
        syncDobValueOnly();
        fireFieldTelemetry('name', false);
        maybeFireCalcPreview('name_input');
      });
      fullNameEl.addEventListener('change', () => {
        syncDobValueOnly();
        fireFieldTelemetry('name', true);
        maybeFireCalcPreview('name_change');
      });
      fullNameEl.addEventListener('blur', () => {
        syncDobValueOnly();
        maybeFireCalcPreview('name_blur');
      });
    }

    const birthDateEl = $('#birthDate');
    if (birthDateEl) {
      birthDateEl.addEventListener('input', () => {
        syncDropdownsFromDob(birthDateEl.value);
        fireFieldTelemetry('dob', true);
        maybeFireCalcPreview('dob_input');
      });
      birthDateEl.addEventListener('change', () => {
        syncDropdownsFromDob(birthDateEl.value);
        fireFieldTelemetry('dob', true);
        maybeFireCalcPreview('dob_change');
      });
    }

    [
      ['dobMonth', 'dob_month'],
      ['dobDay', 'dob_day'],
      ['dobYear', 'dob_year'],
    ].forEach(([selId, telemetryKey]) => {
      const sel = $('#' + selId);
      if (!sel) return;
      sel.addEventListener('focus', () => fireFieldTelemetry(telemetryKey, false), { once: true });
      const onDobSelectUpdate = () => {
        syncDobFromDropdowns(telemetryKey);
        fireFieldTelemetry(telemetryKey, true);
        maybeFireCalcPreview(telemetryKey);
      };
      sel.addEventListener('change', onDobSelectUpdate);
      sel.addEventListener('input', onDobSelectUpdate);
    });

    // Fire page_view telemetry on load for real visitor sessions
    sendWebhook('page_view', { path: location.pathname + location.search });

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
    // Optional deep-link prefill & cross-browser session restore: ?view=teaser&name=Cowen+Airo+Celestin+Vega&dob=2017-07-07&email=...
    const qName = (q.get('name') || '').trim();
    let qDob = (q.get('dob') || '').trim();
    const mUsDob = /^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})$/.exec(qDob);
    if (mUsDob) {
      qDob = `${mUsDob[3]}-${String(mUsDob[1]).padStart(2, '0')}-${String(mUsDob[2]).padStart(2, '0')}`;
    }
    const hasUrlProfile = Boolean(qName && qDob && E.validate(qName, qDob).valid);
    if (hasUrlProfile) {
      const same = prof && prof.fullName === qName && prof.birthDate === qDob;
      prof = same ? Object.assign({}, prof, { email: q.get('email') || prof.email || '' }) : {
        id: leadId(),
        fullName: qName,
        birthDate: qDob,
        email: q.get('email') || '',
        tier: urlTier || (same && prof ? prof.tier : null) || null,
        createdAt: new Date().toISOString(),
        utm: utm(),
      };
    }

    // If the visitor clicked our bio link (?utm_source=ig_bio or ?utm_source=tiktok) without explicit view/vip/paid params,
    // always land cleanly on the fresh Hero Input Form instead of restoring a cached dossier from localStorage!
    const isFreshBioLanding = Boolean(
      q.get('utm_source') &&
      !q.get('view') &&
      !q.get('vip') &&
      !q.get('paid') &&
      !q.get('tier') &&
      !isUnlockedParam &&
      !hasUrlProfile
    );
    if (isFreshBioLanding) {
      fillForm({});
      showView('hero');
      return;
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
      } else if (q.get('view') === 'teaser' || hasUrlProfile) {
        state.result = E.calculate(prof.fullName, prof.birthDate);
        openTeaser();
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
