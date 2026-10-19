# The Sovereign 5-System Blueprint & Rosicrucian Cycles

An interactive high-converting sales funnel and automated 15-page luxury numerology dossier engine. Zero backend dependencies, vanilla JavaScript architecture, ready for immediate browser preview and 60-second static deployment to Vercel, Netlify, or Cloudflare Pages.

---

## Architecture Overview

```
c:\Users\User\5numsystem\
├── index.html       # Single-Page Application shell containing all 3 views
├── styles.css       # Quiet Luxury Obsidian & Gold design system + @media print
├── engine.js        # Deterministic 5-system mathematical engine (pure functions)
├── content.js       # Interpretations library (Archetypes, Sephirot, Chaldean compounds 10–52)
├── app.js           # Funnel controller, checkout, state management, dossier generator
└── tests/           # Playwright automated E2E & mathematical fidelity test suite
```

### The 3 Funnel Views

1. **View 1: Top-of-Funnel Hero Hook**
   - High-converting headline: *"Why Western Numerology Only Gives You 20% of the Code."*
   - Real-time form validation (`Full Name`, `Date of Birth`, `Email Address`).
   - One-click **"Load Founder Sample (Adam Vega)"** quick-fill button.
   - Ritual calculation transition overlay simulating multi-tradition cross-referencing.

2. **View 2: The "20% Free Teaser" + Sales Page**
   - Personalized greeting by first name.
   - Reveals the user's **#1 Master Signature Anchor** and its cross-system recurrence.
   - **5-System Alignment Matrix**: System 1 (Pythagorean) is unlocked; Systems 2–5, the #2 Wealth Engine, and the active 52-Day Cycle are protected by frosted-glass backdrop blur (`backdrop-filter: blur(8px)`) with gold padlock indicators.
   - 9:16 vertical video placeholder for founder VSL.
   - Interactive Checkout Card with dynamic pricing:
     - Base Product: **$37** (*The Complete 5-System Sovereign Blueprint Dossier*).
     - 1-Click Order Bump: **+$47** (*Personalized 365-Day Rosicrucian 52-Day Cycles Calendar*).
     - Dynamic total updates live between **$37** and **$84**.
   - Sticky mobile CTA banner appearing smoothly on scroll.
   - **"Simulate Successful Purchase / Unlock Full Dossier Now (Demo Mode)"** button for testing without live payment gateways.

3. **View 3: The Unlocked 15-Section Dossier & PDF Export**
   - **Section 01:** Luxury Cover Page with Name, Birth Date, and Big Three Master Overlap Medallions.
   - **Section 02:** The 5-System Method & Table of Contents.
   - **Section 03:** Big Three Master Overlap Anchors & 1–9 Frequency Tally.
   - **Section 04:** Primary Signature Anchor Deep-Dive (Core Identity).
   - **Section 05:** Secondary Wealth & Strategy Engine (Abundance Mechanism).
   - **Section 06:** Tertiary Structural Foundation (Grounding & Boundaries).
   - **Section 07:** System I · Pythagorean Core Numbers (Life Path, Expression, Soul Urge, Personality).
   - **Section 08:** System II · Chaldean Compound Analysis (First, Last, Total compounds + 10–52 interpretations).
   - **Section 09:** System III · Kabbalistic Tree of Life (SVG vector diagram with 10 Sephirot & Pillar Balance).
   - **Section 10:** System IV · Vedic Planetary Architecture (Moolank Driver, Bhagyank Conductor, Namank Vibration, Navagraha rulers).
   - **Section 11:** System V · Lo Shu 3×3 Magic Square & Five Elements (Water, Earth with Wealth 8, Wood, Metal, Fire).
   - **Section 12:** Tactical Synthesis (Wealth, Strategy, Social Magnetism + Sovereign Operating Code Table).
   - **Section 13:** Rosicrucian 52-Day Cycle Calendar (all 7 periods with exact dates, progress bar, today highlighted).
   - **Section 14:** Current Cycle Brief & Annual Action Map (Press Edges vs. Preserve Capital directives).
   - **Section 15:** The Sovereign Codex (Full 5-System scorecard & signature affirmation).
   - **1-Click Luxury PDF Export:** Triggered via `window.print()` and formatted with `@media print` rules for 15 book-quality Letter pages.

---

## Quick Start & Local Preview

Run a local HTTP server:
```powershell
python -m http.server 8080
```
Then open your browser to:
```
http://localhost:8080
```

Or open `index.html` directly in any modern browser (`file:///.../index.html`).

---

## Configuration (`app.js`)

Open [app.js](file:///c:/Users/User/5numsystem/app.js) and configure the `CONFIG` object at the top of the file:

```javascript
const CONFIG = {
  // Stripe Payment Links:
  STRIPE_LINK_BASE: 'https://buy.stripe.com/...',   // Redirects to: https://YOUR-SITE.com/?tier=base
  STRIPE_LINK_BUMP: 'https://buy.stripe.com/...',   // Redirects to: https://YOUR-SITE.com/?tier=full
  STRIPE_LINK_UPGRADE: 'https://buy.stripe.com/...',// Redirects to: https://YOUR-SITE.com/?tier=full

  PRICE_BASE: 37,
  PRICE_BUMP: 47,
  PRICE_ANCHOR: 197,
  GUARANTEE_DAYS: 30,

  // Lead capture webhook (Zapier, Make, n8n, ConvertKit, GoHighLevel):
  WEBHOOK_URL: 'https://your-webhook-endpoint.com/lead',

  // Founder VSL video URL (.mp4 or YouTube / Vimeo embed URL):
  VSL_URL: '',

  // Set false before production launch to hide the demo unlock button:
  DEMO_MODE: true,

  SAMPLE: { fullName: 'Adam Vega', birthDate: '1988-11-08', email: 'adam@sovereign5.com' },
};
```

---

## URL Parameters & Deep Linking

- `?unlocked=true` or `?tier=full`: Unlocks the complete 15-page dossier including the Rosicrucian Cycles Calendar.
- `?tier=base`: Unlocks the base 5-system dossier (prompting the user to add the Cycles Calendar for $47).
- `?name=Adam%20Vega&dob=1988-11-08&email=adam@sovereign5.com`: Pre-fills the user profile and generates their dossier automatically.

---

## Automated Test Verification

Run the test suite using Python:
```powershell
python tests/math_verification.py
python tests/test_pdf.py
python tests/e2e_test.py
```
