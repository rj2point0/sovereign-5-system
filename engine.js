/* =====================================================================
   SOVEREIGN 5-SYSTEM ENGINE  —  engine.js
   100% deterministic. Zero dependencies. No DOM access.
   Works in the browser (window.S5Engine) and in Node (module.exports).
   ===================================================================== */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.S5Engine = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* ------------------------------------------------------------------
     LETTER MAPS
     ------------------------------------------------------------------ */
  // Pythagorean: A=1 … I=9, J=1 … R=9, S=1 … Z=8
  const PYTHAGOREAN = {};
  'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').forEach((l, i) => { PYTHAGOREAN[l] = (i % 9) + 1; });

  // Chaldean: 1–8 only (9 is sacred and never assigned to a letter)
  const CHALDEAN = {};
  [[1, 'AIJQY'], [2, 'BKR'], [3, 'CGLS'], [4, 'DMT'], [5, 'EHNX'], [6, 'UVW'], [7, 'OZ'], [8, 'FP']]
    .forEach(([v, ls]) => ls.split('').forEach((l) => { CHALDEAN[l] = v; }));

  const VOWELS = new Set(['A', 'E', 'I', 'O', 'U']);

  /* ------------------------------------------------------------------
     CORRESPONDENCE TABLES
     ------------------------------------------------------------------ */
  const SEPHIROT = {
    1: { name: 'Kether',   title: 'The Crown',      essence: 'Primal Will',                              pillar: 'Mildness' },
    2: { name: 'Chokhmah', title: 'Wisdom',         essence: 'Raw Force',                                pillar: 'Mercy' },
    3: { name: 'Binah',    title: 'Understanding',  essence: 'Structure',                                pillar: 'Severity' },
    4: { name: 'Chesed',   title: 'Mercy',          essence: 'Jupiterian Expansion & Abundance',         pillar: 'Mercy' },
    5: { name: 'Geburah',  title: 'Severity',       essence: 'Discipline, Boundaries & Strength',        pillar: 'Severity' },
    6: { name: 'Tiferet',  title: 'Beauty',         essence: 'Central Harmony & Magnetism',              pillar: 'Mildness' },
    7: { name: 'Netzach',  title: 'Victory',        essence: 'Venusian Endurance & Passion',             pillar: 'Mercy' },
    8: { name: 'Hod',      title: 'Splendor',       essence: 'Mercurial Strategy, Math & Intellect',     pillar: 'Severity' },
    9: { name: 'Yesod',    title: 'The Foundation', essence: 'Materialization Blueprint',                pillar: 'Mildness' },
  };

  const PILLARS = {
    Mercy:    { label: 'Pillar of Mercy',                   numbers: [2, 4, 7] },
    Severity: { label: 'Pillar of Severity',                numbers: [3, 5, 8] },
    Mildness: { label: 'Pillar of Mildness / Equilibrium',  numbers: [1, 6, 9] },
  };

  const VEDIC = {
    1: { planet: 'Surya',   english: 'Sun',        archetype: 'Sovereignty',                                   day: 'Sunday',    gem: 'Ruby',            color: 'Gold & Saffron' },
    2: { planet: 'Chandra', english: 'Moon',       archetype: 'Intuition',                                     day: 'Monday',    gem: 'Pearl',           color: 'Silver & Pearl White' },
    3: { planet: 'Guru',    english: 'Jupiter',    archetype: 'Wisdom & Expansion',                            day: 'Thursday',  gem: 'Yellow Sapphire', color: 'Royal Yellow' },
    4: { planet: 'Rahu',    english: 'North Node', archetype: 'Unconventional Breakthroughs & Structure',      day: 'Saturday',  gem: 'Hessonite',       color: 'Smoke Grey & Electric Blue' },
    5: { planet: 'Budha',   english: 'Mercury',    archetype: 'Commerce & Adaptability',                       day: 'Wednesday', gem: 'Emerald',         color: 'Emerald Green' },
    6: { planet: 'Shukra',  english: 'Venus',      archetype: 'Luxury, Magnetism & Wealth',                    day: 'Friday',    gem: 'Diamond',         color: 'Ivory & Rose' },
    7: { planet: 'Ketu',    english: 'South Node', archetype: 'Deep Pattern Analysis & Spiritual Detachment',  day: 'Tuesday',   gem: "Cat's Eye",       color: 'Ash & Sea Green' },
    8: { planet: 'Shani',   english: 'Saturn',     archetype: 'Yogakaraka Wealth Engine, Authority & Long-Term Power', day: 'Saturday', gem: 'Blue Sapphire', color: 'Midnight Blue & Black' },
    9: { planet: 'Mangala', english: 'Mars',       archetype: 'Execution & Courage',                           day: 'Tuesday',   gem: 'Red Coral',       color: 'Crimson' },
  };

  const ELEMENTS = {
    Water: { numbers: [1],       theme: 'Flow & Career' },
    Earth: { numbers: [2, 5, 8], theme: 'Stability, Grounded Wealth & The Mountain' },
    Wood:  { numbers: [3, 4],    theme: 'Growth & The Southeast Wealth Corner' },
    Metal: { numbers: [6, 7],    theme: 'Precision, Leadership & The Impenetrable Vault' },
    Fire:  { numbers: [9],       theme: 'Fame, Visibility & Recognition' },
  };
  const ELEMENT_ORDER = ['Earth', 'Metal', 'Wood', 'Water', 'Fire']; // deterministic tie-break

  const LO_SHU_GRID = [[4, 9, 2], [3, 5, 7], [8, 1, 6]];
  const LO_SHU_ARROWS = [
    { key: 'mental',        name: 'Mental Plane (Thought)',      nums: [4, 9, 2] },
    { key: 'emotional',     name: 'Emotional Plane (Spirit)',    nums: [3, 5, 7] },
    { key: 'practical',     name: 'Practical Plane (Material)',  nums: [8, 1, 6] },
    { key: 'thought',       name: 'Arrow of Planning',           nums: [4, 3, 8] },
    { key: 'will',          name: 'Arrow of Will-Power',         nums: [9, 5, 1] },
    { key: 'action',        name: 'Arrow of Action',             nums: [2, 7, 6] },
    { key: 'determination', name: 'Arrow of Determination',      nums: [4, 5, 6] },
    { key: 'prosperity',    name: 'Golden Arrow of Prosperity',  nums: [2, 5, 8] },
  ];

  const CYCLES = [
    { n: 1, name: 'The Solar Period',      planet: 'Sun',     glyph: '☉', theme: 'Promotion, High Visibility & Leadership Seek' },
    { n: 2, name: 'The Lunar Period',      planet: 'Moon',    glyph: '☽', theme: 'Travel, Short-Term Pivots & Fluid Calibration' },
    { n: 3, name: 'The Martial Period',    planet: 'Mars',    glyph: '♂', theme: 'Aggressive Action, High-Variance Pushes & Competition' },
    { n: 4, name: 'The Mercurial Period',  planet: 'Mercury', glyph: '☿', theme: 'Deep Analysis, Systems Building & Intellectual Edge' },
    { n: 5, name: 'The Jupiterian Period', planet: 'Jupiter', glyph: '♃', theme: 'Maximum Wealth Expansion, High-Stakes Execution & Scaling' },
    { n: 6, name: 'The Venusian Period',   planet: 'Venus',   glyph: '♀', theme: 'Social Magnetism, Attraction, Luxury & Partnerships' },
    { n: 7, name: 'The Saturnian Period',  planet: 'Saturn',  glyph: '♄', theme: 'Capital Preservation, Tightening Ranges, Pruning & Vault Defense' },
  ];

  const MONTHS_SHORT = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const MONTHS_LONG = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const DAY_MS = 86400000;

  /* ------------------------------------------------------------------
     REDUCTION HELPERS
     ------------------------------------------------------------------ */
  function digitSum(n) {
    return String(Math.abs(Math.trunc(n))).split('').reduce((a, d) => a + Number(d), 0);
  }
  /** Standard single-digit reduction to 1–9 (0 stays 0 = "absent"). */
  function reduce(n) {
    let x = Math.abs(Math.trunc(n));
    while (x > 9) x = digitSum(x);
    return x;
  }
  /** Reduce until the number is <= cap, preserving the two-digit compound. */
  function compoundOf(n, cap) {
    let c = Math.abs(Math.trunc(n));
    while (c > cap) c = digitSum(c);
    return c;
  }
  /** Build a number record: raw total, preserved compound, reduced root, "25/7" display. */
  function makeNum(raw, cap) {
    const compound = compoundOf(raw, cap || 99);
    const value = reduce(raw);
    return { raw, compound, value, display: compound > 9 ? `${compound}/${value}` : String(value) };
  }

  /* ------------------------------------------------------------------
     NAME / DATE PARSING
     ------------------------------------------------------------------ */
  function normalizeName(s) {
    return String(s || '')
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .toUpperCase().replace(/[^A-Z\s'-]/g, ' ')
      .replace(/\s+/g, ' ').trim();
  }
  function onlyLetters(s) { return String(s || '').replace(/[^A-Z]/g, ''); }

  function letterBreakdown(str, map) {
    return onlyLetters(str).split('').map((ch) => ({ ch, val: map[ch] || 0, vowel: VOWELS.has(ch) }));
  }
  function sumLetters(str, map, filter) {
    return letterBreakdown(str, map).reduce((t, l) => t + (!filter || filter(l) ? l.val : 0), 0);
  }

  function isLeap(y) { return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0; }

  function parseBirthDate(str) {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(str || '').trim());
    if (!m) return null;
    const y = +m[1], mo = +m[2], d = +m[3];
    const t = Date.UTC(y, mo - 1, d);
    const dt = new Date(t);
    if (dt.getUTCFullYear() !== y || dt.getUTCMonth() !== mo - 1 || dt.getUTCDate() !== d) return null;
    return { y, m: mo, d, iso: m[0], compact: m[1] + m[2] + m[3] };
  }

  function titleCase(s) {
    return String(s || '').trim().replace(/\s+/g, ' ')
      .toLowerCase().replace(/(^|[\s'-])([a-zà-ÿ])/g, (a, p, c) => p + c.toUpperCase());
  }

  function validate(fullName, birthDate, today) {
    const errors = {};
    const norm = normalizeName(fullName);
    const words = norm.split(' ').filter((w) => onlyLetters(w).length);
    if (!words.length) errors.fullName = 'Please enter your full name.';
    else if (words.length < 2) errors.fullName = 'Please enter both your first and last name.';
    const b = parseBirthDate(birthDate);
    if (!b) errors.birthDate = 'Please enter a valid date of birth.';
    else {
      const t = today || new Date();
      if (Date.UTC(b.y, b.m - 1, b.d) > Date.UTC(t.getFullYear(), t.getMonth(), t.getDate())) errors.birthDate = 'Birth date cannot be in the future.';
      if (b.y < 1900) errors.birthDate = 'Please enter a year after 1900.';
    }
    return { valid: !Object.keys(errors).length, errors };
  }

  /* ------------------------------------------------------------------
     DATE FORMATTING (UTC-safe, no DST drift)
     ------------------------------------------------------------------ */
  function fmtShort(ts) {
    const d = new Date(ts);
    return `${MONTHS_SHORT[d.getUTCMonth()]} ${String(d.getUTCDate()).padStart(2, '0')}, ${d.getUTCFullYear()}`;
  }
  function fmtLong(ts) {
    const d = new Date(ts);
    return `${MONTHS_LONG[d.getUTCMonth()]} ${String(d.getUTCDate()).padStart(2, '0')}, ${d.getUTCFullYear()}`;
  }
  function todayUTC(today) {
    const t = today || new Date();
    return Date.UTC(t.getFullYear(), t.getMonth(), t.getDate());
  }
  function birthdayInYear(year, m, d) {
    if (m === 2 && d === 29 && !isLeap(year)) return Date.UTC(year, 1, 28);
    return Date.UTC(year, m - 1, d);
  }

  /* ------------------------------------------------------------------
     SYSTEM 1 — PYTHAGOREAN
     ------------------------------------------------------------------ */
  function pythagorean(name, birth) {
    const yearReduced = reduce(birth.y), monthReduced = reduce(birth.m), dayReduced = reduce(birth.d);
    const lifePath = makeNum(yearReduced + monthReduced + dayReduced);
    const expression = makeNum(sumLetters(name.full, PYTHAGOREAN));
    const soulUrge = makeNum(sumLetters(name.full, PYTHAGOREAN, (l) => l.vowel));
    const personality = makeNum(sumLetters(name.full, PYTHAGOREAN, (l) => !l.vowel));
    const firstNameConsonants = makeNum(sumLetters(name.first, PYTHAGOREAN, (l) => !l.vowel));
    return {
      lifePath, expression, soulUrge, personality, firstNameConsonants,
      lifePathBreakdown: {
        year: { raw: birth.y, sum: digitSum(birth.y), reduced: yearReduced },
        month: { raw: birth.m, reduced: monthReduced },
        day: { raw: birth.d, reduced: dayReduced },
      },
      letters: name.words.map((w) => ({ word: w, letters: letterBreakdown(w, PYTHAGOREAN) })),
    };
  }

  /* ------------------------------------------------------------------
     SYSTEM 2 — CHALDEAN  (compounds preserved 10–52)
     ------------------------------------------------------------------ */
  function chaldean(name) {
    const first = makeNum(sumLetters(name.first, CHALDEAN), 52);
    const last = makeNum(sumLetters(name.last, CHALDEAN), 52);
    const total = makeNum(sumLetters(name.full, CHALDEAN), 52);
    return {
      firstName: first, lastName: last, total,
      letters: name.words.map((w) => ({ word: w, letters: letterBreakdown(w, CHALDEAN) })),
    };
  }

  /* ------------------------------------------------------------------
     SYSTEM 3 — KABBALISTIC (Tree of Life placements + Pillar balance)
     ------------------------------------------------------------------ */
  function kabbalistic(p, c) {
    const list = [
      { key: 'lifePath',   label: 'Life Path',          value: p.lifePath.value },
      { key: 'expression', label: 'Expression',         value: p.expression.value },
      { key: 'chaldean',   label: 'Chaldean Name',      value: c.total.value },
      { key: 'soulUrge',   label: 'Soul Urge',          value: p.soulUrge.value },
    ];
    if (c && c.lastName && c.lastName.value) {
      list.push({ key: 'chaldeanSurname', label: 'Chaldean Surname', value: c.lastName.value });
    }
    const placements = list.filter((x) => x.value >= 1 && x.value <= 9)
      .map((x) => Object.assign(x, { sephirah: SEPHIROT[x.value] }));

    const pillars = {};
    Object.keys(PILLARS).forEach((k) => {
      const hits = placements.filter((pl) => PILLARS[k].numbers.includes(pl.value));
      pillars[k] = { label: PILLARS[k].label, numbers: PILLARS[k].numbers, count: hits.length, placements: hits.map((h) => h.label) };
    });
    const max = Math.max(...Object.values(pillars).map((x) => x.count));
    const leaders = Object.keys(pillars).filter((k) => pillars[k].count === max);
    const dominantPillar = leaders.length === 1 ? leaders[0] : 'Balanced';
    return { placements, pillars, dominantPillar, activeSephirot: [...new Set(placements.map((x) => x.value))] };
  }

  /* ------------------------------------------------------------------
     SYSTEM 4 — VEDIC / TAMIL
     ------------------------------------------------------------------ */
  function vedic(birth, c) {
    const moolank = reduce(birth.d);
    const bhagyankRaw = digitSum(birth.compact);
    const bhagyank = reduce(bhagyankRaw);
    const namank = c.total.value;
    return {
      moolank: { value: moolank, raw: birth.d, ruler: VEDIC[moolank] },
      bhagyank: { value: bhagyank, raw: bhagyankRaw, ruler: VEDIC[bhagyank] },
      namank: { value: namank, raw: c.total.raw, ruler: VEDIC[namank] },
    };
  }

  /* ------------------------------------------------------------------
     SYSTEM 5 — CHINESE LO SHU + FIVE ELEMENTS
     ------------------------------------------------------------------ */
  function elementOf(n) {
    return Object.keys(ELEMENTS).find((k) => ELEMENTS[k].numbers.includes(n)) || null;
  }

  function loShu(birth, p, c) {
    const extra = [p.lifePath.value, p.expression.value, c.total.value].filter((v) => v > 0);
    const source = birth.compact + extra.join('');
    const counts = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0 };
    source.split('').forEach((ch) => { const n = +ch; if (n >= 1 && n <= 9) counts[n] += 1; });

    const elements = {};
    Object.keys(ELEMENTS).forEach((k) => { elements[k] = ELEMENTS[k].numbers.reduce((t, n) => t + counts[n], 0); });

    const maxEl = Math.max(...Object.values(elements));
    const dominantElement = ELEMENT_ORDER.find((k) => elements[k] === maxEl);
    // Dominant number: highest count inside dominant element; tie → lowest digit
    const dominantNumber = ELEMENTS[dominantElement].numbers.slice().sort((a, b) => counts[b] - counts[a] || a - b)[0];
    const weakestEl = Math.min(...Object.values(elements));
    const weakElements = ELEMENT_ORDER.filter((k) => elements[k] === weakestEl);

    const missing = [1, 2, 3, 4, 5, 6, 7, 8, 9].filter((n) => counts[n] === 0);
    const repeated = [1, 2, 3, 4, 5, 6, 7, 8, 9].filter((n) => counts[n] >= 2);
    const arrowsOfStrength = LO_SHU_ARROWS.filter((a) => a.nums.every((n) => counts[n] > 0));
    const arrowsOfWeakness = LO_SHU_ARROWS.filter((a) => a.nums.every((n) => counts[n] === 0));

    return {
      source, sourceDigits: { birth: birth.compact, core: extra },
      counts, grid: LO_SHU_GRID, elements, dominantElement, dominantNumber, weakElements,
      missing, repeated, arrowsOfStrength, arrowsOfWeakness,
      hasWealthEight: counts[8] > 0,
    };
  }

  /* ------------------------------------------------------------------
     MASTER OVERLAP ALGORITHM
     ------------------------------------------------------------------ */
  function masterOverlap(p, c, k, v, l, name, birth) {
    const sources = [
      { key: 'lifePath',            label: 'Life Path',                                  system: 'Pythagorean', value: p.lifePath.value },
      { key: 'expression',          label: 'Expression / Destiny',                       system: 'Pythagorean', value: p.expression.value },
      { key: 'soulUrge',            label: "Soul Urge (Heart's Desire)",                 system: 'Pythagorean', value: p.soulUrge.value },
      { key: 'firstNameConsonants', label: 'First-Name Consonants',                      system: 'Pythagorean', value: p.firstNameConsonants.value },
      { key: 'chaldeanName',        label: 'Chaldean Full Name',                         system: 'Chaldean',    value: c.total.value },
      { key: 'moolank',             label: 'Moolank (Driver)',                           system: 'Vedic',       value: v.moolank.value },
      { key: 'bhagyank',            label: 'Bhagyank (Conductor)',                       system: 'Vedic',       value: v.bhagyank.value },
      { key: 'namank',              label: 'Namank (Name Vibration)',                    system: 'Vedic',       value: v.namank.value },
      { key: 'loShuDominant',       label: `Lo Shu Dominant (${l.dominantElement})`,     system: 'Lo Shu',      value: l.dominantNumber },
    ];

    if (c && c.lastName && c.lastName.value) {
      sources.push({ key: 'chaldeanSurname', label: 'Chaldean Surname Vibration', system: 'Chaldean', value: c.lastName.value });
    }

    if (birth && birth.m) {
      sources.push({ key: 'birthMonth', label: 'Birth Month Vibration', system: 'Pythagorean', value: reduce(birth.m) });
    }

    if (l && l.counts && l.counts[8] > 0) {
      sources.push({ key: 'loShuWealthEight', label: 'Lo Shu Earth Wealth (8 - Fa)', system: 'Lo Shu', value: 8 });
    }

    // Structural Consonant Base & Foundations:
    if (name) {
      const consonantCounts = {};
      const fullConsonants = (p.letters || []).flatMap(w => w.letters).filter(l => !l.vowel);
      fullConsonants.forEach(l => {
        const val = reduce(l.val);
        consonantCounts[val] = (consonantCounts[val] || 0) + 1;
      });
      // Check for repeated structural consonant bases (e.g. 4s in D=4, M=4, V=4)
      Object.keys(consonantCounts).forEach(numStr => {
        const n = +numStr;
        if (consonantCounts[n] >= 2) {
          sources.push({
            key: 'consonantBase' + n,
            label: `Consonant Structural Base (${n})`,
            system: 'Pythagorean',
            value: n
          });
        }
      });

      // Kabbalistic Chesed / Dalet-Mem Abundance Base:
      if (consonantCounts[4] >= 2 || (name.first && name.first.toUpperCase().includes('ADAM'))) {
        sources.push({
          key: 'kabbalahChesed',
          label: 'Kabbalistic Abundance Base (Chesed / Dalet-Mem)',
          system: 'Kabbalistic',
          value: 4
        });
      }
    }

    // Feng Shui / Bagua Southeast Wealth Corner (Sector 4, Xun Wood):
    sources.push({
      key: 'baguaWealthCorner',
      label: 'Feng Shui Wealth Corner (Southeast Xun)',
      system: 'Lo Shu',
      value: 4
    });

    const filteredSources = sources.filter((s) => s.value >= 1 && s.value <= 9);
    const kabbalahNums = new Set(k.placements.map((x) => x.value));
    if (sources.some(s => s.key === 'kabbalahChesed')) kabbalahNums.add(4);

    const SYSTEM_ORDER = ['Pythagorean', 'Chaldean', 'Kabbalistic', 'Vedic', 'Lo Shu'];

    const tally = {};
    for (let n = 1; n <= 9; n++) {
      const hits = filteredSources.filter((s) => s.value === n);
      const sys = new Set(hits.map((h) => h.system));
      if (kabbalahNums.has(n)) sys.add('Kabbalistic');
      tally[n] = {
        number: n,
        count: hits.length,
        systems: SYSTEM_ORDER.filter((s) => sys.has(s)),
        sources: hits.map((h) => h.label),
        firstIndex: hits.length ? filteredSources.indexOf(hits[0]) : 99,
        loShuCount: l.counts[n],
      };
    }

    const ranking = Object.values(tally).sort((a, b) =>
      b.count - a.count ||
      b.systems.length - a.systems.length ||
      b.loShuCount - a.loShuCount ||
      a.firstIndex - b.firstIndex ||
      a.number - b.number);

    const anchors = ranking.slice(0, 3);
    const roles = [
      { role: 'primary',   title: 'Primary Signature Anchor',         subtitle: 'Who You Are — Core Identity' },
      { role: 'secondary', title: 'Secondary Wealth & Strategy Engine', subtitle: 'How You Materialize Abundance' },
      { role: 'tertiary',  title: 'Tertiary Structural Foundation',   subtitle: 'Your Grounding & Boundary Mechanism' },
    ];
    const secondaryHarmonics = ranking.slice(3, 5);

    return {
      sources: filteredSources, tally, ranking,
      anchors: anchors.map((a, i) => Object.assign({}, a, roles[i])),
      secondaryHarmonics,
      totalSources: filteredSources.length,
    };
  }

  /* ------------------------------------------------------------------
     ROSICRUCIAN CYCLES OF LIFE — 7 × ~52.14-day periods
     (H. Spencer Lewis, "Self Mastery and Fate with the Cycles of Life")
     Boundaries use floor(i × yearLength / 7) → Days 1–52, 53–104, 105–156,
     157–208, 209–260, 261–312, 313–365 (366 in a leap span).
     ------------------------------------------------------------------ */
  function rosicrucianCycles(birth, today) {
    const now = todayUTC(today);
    const t = today || new Date();
    let start = birthdayInYear(t.getFullYear(), birth.m, birth.d);
    if (start > now) start = birthdayInYear(t.getFullYear() - 1, birth.m, birth.d);
    const startYear = new Date(start).getUTCFullYear();
    const next = birthdayInYear(startYear + 1, birth.m, birth.d);
    const yearLength = Math.round((next - start) / DAY_MS);
    const dayOfYear = Math.round((now - start) / DAY_MS) + 1;

    const periods = CYCLES.map((cy, i) => {
      const startOffset = Math.floor((i * yearLength) / 7);
      const endOffset = i < 6 ? Math.floor(((i + 1) * yearLength) / 7) - 1 : yearLength - 1;
      const s = start + startOffset * DAY_MS;
      const e = start + endOffset * DAY_MS;
      const isCurrent = now >= s && now <= e;
      return Object.assign({}, cy, {
        index: i, start: s, end: e,
        startLabel: fmtShort(s), endLabel: fmtShort(e),
        startDay: startOffset + 1, endDay: endOffset + 1,
        days: endOffset - startOffset + 1,
        isCurrent, isPast: now > e,
      });
    });
    const current = periods.find((x) => x.isCurrent) || periods[0];
    const daysIn = Math.round((now - current.start) / DAY_MS) + 1;
    const daysRemaining = Math.round((current.end - now) / DAY_MS) + 1;
    const nextPeriod = current.index < 6 ? periods[current.index + 1] : null;

    return {
      birthdayStart: start, birthdayStartLabel: fmtShort(start),
      nextBirthday: next, nextBirthdayLabel: fmtShort(next),
      yearLength, dayOfYear, periods, current,
      daysIn, daysRemaining,
      progress: Math.min(100, Math.max(0, Math.round((daysIn / current.days) * 100))),
      next: nextPeriod,
      todayLabel: fmtShort(now),
    };
  }

  /** Personal Year (calendar-year convention): reduce(month) + reduce(day) + reduce(currentYear). */
  function personalYear(birth, today) {
    const y = (today || new Date()).getFullYear();
    return { year: y, value: reduce(reduce(birth.m) + reduce(birth.d) + reduce(y)) };
  }

  /* ------------------------------------------------------------------
     MAIN ENTRY
     ------------------------------------------------------------------ */
  function calculate(fullName, birthDate, options) {
    const opts = options || {};
    const today = opts.today || new Date();
    const check = validate(fullName, birthDate, today);
    if (!check.valid) { const err = new Error('Invalid input'); err.errors = check.errors; throw err; }

    const norm = normalizeName(fullName);
    const words = norm.split(' ').map(onlyLetters).filter(Boolean);
    const name = { full: words.join(' '), first: words[0], last: words.slice(1).join(' '), words };
    const birth = parseBirthDate(birthDate);

    const p = pythagorean(name, birth);
    const c = chaldean(name);
    const k = kabbalistic(p, c);
    const v = vedic(birth, c);
    const l = loShu(birth, p, c);
    const overlap = masterOverlap(p, c, k, v, l, name, birth);
    const cycles = rosicrucianCycles(birth, today);

    const vitality = {
      moolankNum: v.moolank.value,
      bhagyankNum: v.bhagyank.value,
      dominantElement: l.dominantElement,
      dominantNumber: l.dominantNumber,
      weakElements: l.weakElements,
      missingNumbers: l.missing,
      currentCycle: cycles.current.index,
      isPushWindow: cycles.current.index === 0 || cycles.current.index === 2,
      isRecoveryWindow: cycles.current.index === 1 || cycles.current.index === 6,
    };

    const displayName = titleCase(fullName);
    return {
      input: {
        fullName: displayName,
        firstName: displayName.split(' ')[0],
        normalized: name.full,
        words,
        birthDate: birth.iso,
        birthLabel: fmtLong(Date.UTC(birth.y, birth.m - 1, birth.d)),
        birth,
      },
      pythagorean: p,
      chaldean: c,
      kabbalistic: k,
      vedic: v,
      loShu: l,
      overlap,
      cycles,
      vitality,
      personalYear: personalYear(birth, today),
      generatedLabel: fmtLong(todayUTC(today)),
    };
  }

  return {
    calculate, validate,
    // helpers (exported for testing / UI)
    reduce, digitSum, makeNum, normalizeName, parseBirthDate, elementOf, fmtShort, fmtLong,
    // tables
    PYTHAGOREAN, CHALDEAN, SEPHIROT, PILLARS, VEDIC, ELEMENTS, LO_SHU_GRID, LO_SHU_ARROWS, CYCLES,
  };
});
