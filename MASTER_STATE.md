# 🔮 SACRED NUMBER BLUEPRINT (`5numsystem`) — MASTER PRODUCTION STATE

> **Anti-Context-Rot Checkpoint (Updated: 2026-11-01)**  
> Read this file first at the start of any session in `c:\Users\User\5numsystem` to load the complete production architecture, live URLs, Stripe Payment Links, background daemons, and social video pipeline state in 5 seconds.
>
> **Workspace Isolation Rule**: This workspace (`c:\Users\User\5numsystem`) is strictly dedicated to **Project 1: Sacred Number Blueprint (`@sacrednumberblueprint`)**. Project 2 (**KC Chocolatier / Brad Yater**) lives in its own isolated workspace at `c:\Users\User\kc_chocolatier`.

---

## 1. Live Production Domain & Funnel Architecture

- **Primary Production URL (HTTPS Enforced via GitHub Pages + Namecheap CNAME)**:  
  `https://blueprint.megavegaventures.com/`
- **Legacy GitHub Pages URL (301 Redirects to Primary Domain)**:  
  `https://rj2point0.github.io/sovereign-5-system/`
- **TikTok Bio Link**:  
  `https://blueprint.megavegaventures.com/?utm_source=tiktok_bio&cohort=tiktok`
- **Instagram Bio Link**:  
  `https://blueprint.megavegaventures.com/?utm_source=ig_bio&cohort=ig_reels`
- **Founder VIP Bypass URL (Unlocks Full 20-Page Dossier + Shows Sample Button)**:  
  `https://blueprint.megavegaventures.com/?vip=adam`

### Target Demographic & Copy Framework
- **Core Avatar**: Women 18–38 ("The Anxious Romantic / Seeker").
- **Hero Copy Formula**: Problem-First → Solution → Certainty:
  - **H1**: *"Stop Falling For Partners Who Pull Away—See Who You're Actually Meant To Be With."*
  - **Subhead**: *"You attract partners who pull away! Find out right now which birthdays are your true soulmate match, and what the next 12 months hold for your love life. (Standard horoscopes only check 1 system—we check all 5 to give you a full picture and complete understanding so you know with certainty what to do next.)"*
- **TikTok In-App Browser (`390x660`) Viewport Compliance & Zero-Keyboard Friction**:
  - `.system-strip` is hidden on mobile (`@media (max-width: 600px)`).
  - `#hero-email-block` is collapsed by default on mobile behind `#btn-toggle-hero-email` (`"✉ Optional: Send a copy to my email"`).
  - `#fullName` is **optional** on initial Hero submit (`Your First Name (Optional)` — defaults to `"Your Reading"` / `"Tu Lectura"` when left blank so visitors can submit with only Month/Day/Year dropdowns).
  - **1-Tap Birth Day Quick-Select Strip (`#quick-day-strip`)**: 11-column × 3-row grid (`1`–`31`) inside `#heroForm` (`"⚡ Fast Track: Tap Your Birth Day (1–31) For An Instant Love Code Preview"`). Tapping any day `1`–`31` fires `quick_day_selected`, populates `#dobDay` (with default Month/Year if not selected yet), and jumps straight to the Teaser + Partner Compatibility screen with `#quick-day-banner`.
  - All Hero interactive elements (`#fullName` `296.8px`, `#dobMonth`/`#dobDay`/`#dobYear` `351.5px`, `#heroForm button[type="submit"]` `399.0px`, `#quick-day-strip` `492.4px`, `#hero-micro-badge` `524.8px`, and `#btn-instant-demo` `557.9px`) sit strictly `<= 635px` on a `390x660` TikTok In-App Browser viewport without scrolling.
- **1-Tap Instant Sample Reading (`#btn-instant-demo`)**:
  - Previews Chloe (`1998-07-16`) × Partner (`1996-04-13`), fires `demo_preview_clicked`, renders the Teaser + Partner Compatibility result with a sticky `#sample-reading-banner`, and returns to a cleared `#fullName` input when `#btn-enter-real-birthday` is tapped.

---

## 2. Live 3-Tier Stripe Ascension Checkout Links

| Tier ID | Offer Name | Price | Live Stripe Payment Link | Post-Payment Redirect URL |
| :--- | :--- | :--- | :--- | :--- |
| `love_mini` | **Partner Synastry & 90-Day Love Timing Mini-Read** *(Impulse Tier)* | **$17.00 USD** | `https://buy.stripe.com/dRm8wP7VL0Md1gA0zd38404` | `https://blueprint.megavegaventures.com/?tier=love_mini&unlocked=true` |
| `base` | **Complete 20-Page 5-System Blueprint + Partner Compatibility** *(MOST POPULAR)* | **$37.00 USD** | `https://buy.stripe.com/00w8wP5NDbrR2kE5Tx38402` | `https://blueprint.megavegaventures.com/?tier=base&unlocked=true` |
| `full` | **Complete VIP Sovereign Bundle + 365-Day Calendar** | **$84.00 USD** | `https://buy.stripe.com/8x200jcb1brR9N6chV38403` | `https://blueprint.megavegaventures.com/?tier=full&unlocked=true` |

---

## 3. Telemetry, Lead Capture & Email Drip Infrastructure

- **Cloud Relay Topic (`ntfy.sh`)**: `https://ntfy.sh/sovereign_5_leads_mvv_991214754`
- **Background Worker (`lead_capture_worker.py --daemon`)**:
  - Listens on `ntfy.sh` + local port `8788` (registered in Windows Task Scheduler as `\Sovereign5LeadCaptureWorker`).
  - Logs all telemetry events (`page_view`, `calc_started`, `field_progress`, `calc_preview`, `demo_preview_clicked`, `partner_check_run`, `lead_submitted`, `checkout_clicked`) to `telemetry_events.json` and `G:\My Drive\MVV_Memory_Vault\03-Projects\Leads_Captured_Dashboard.md`.
  - Logs captured leads to `leads_captured.csv`, `G:\My Drive\5_System_Numerology_MVP\leads_captured.csv`, and Supabase (`public.numerology_leads`).
  - Sends the 3-part HTML drip sequence via `adamvega@megavegaventures.com` Workspace SMTP (Email #1 instant teaser + partner compatibility personalization + `$17`/`$37` CTAs; Email #2 at 24h; Email #3 at 48h).
- **Inline Partner Compatibility Email Capture (`#partner-compat-email-box` in `app.js`)**:
  - When a visitor tests a Partner/Crush birthday on the Teaser screen (`runPartnerCompatibilityCheck()`) without having entered their email yet (`!state.profile.email`), renders a 1-line inline email capture bar right above the `$17` Mini-Read button (`"📩 Want to save this Partner Compatibility score & see your next 3 relationship turning-point dates for free?"` + `[Email Our Match Report →]`).
  - Submitting saves `state.profile.email`, fires `lead_submitted` (`trigger: "partner_compat_email_bar"`) with `partner_dob` so `lead_capture_worker.py` immediately sends Email #1 with the **`💑 PARTNER / CRUSH COMPATIBILITY SNAPSHOT`** section, and displays `#partner-compat-email-confirmed`.

---

## 4. Dual-Platform Social Automation & Video Pipeline (`short_01`–`short_21`)

- **Authenticated Browser Profiles**:
  - TikTok (`@sacrednumberblueprint` — Display Name: `Love & Birthday Compatibility` · Bio: `Why do they pull away? 💔 Test your birthday & theirs across 5 systems 👇`): `C:\Users\User\.gemini\antigravity\tiktok_browser_profile`
  - Instagram (`@sacrednumberblueprint` — Name: `Love & Birthday Compatibility` · Bio: `Why do they pull away? 💔 Test your birthday & theirs across 5 systems 👇`): `C:\Users\User\.gemini\antigravity\ig_browser_profile`
- **20-Clip Real Human 9:16 B-Roll Library (`broll_library/`)**:
  - Managed by `fetch_human_broll.py` (`broll_01` through `broll_20`).
- **Video Generator (`generate_broll_story_tiktoks.py`)**:
  - Enforces Jenny Hoyos's 5th-Grade Readability Gate (`Flesch-Kincaid Grade <= 5.5`, zero academic jargon, `But/Therefore` twist connector, `<= 0.35s` tail hold).
  - Renders **giant `68px` bold 3–6 word Poster Headlines (`grid_headline`)** + `38px` crimson subtitle (`grid_sub`) on Frame 1 (`0.0s–4.2s`) so every thumbnail is readable in the 3-column mobile profile grid.
- **Current Video Status (`uploaded_videos.json` & `uploaded_ig_reels.json`)**:
  - `short_01`–`short_15`: **Published Live** on both TikTok and Instagram Reels with automod-safe first comments seeded (`seeded_first_comments.json`; `short_14` `7702844507703823629` and `short_15` `7703342845494562061` verified `ModalIntact=True`).
  - `short_16` (`BEGGING FOR / CRUMBS`): Upgraded `68px` version Live on Instagram Reels (`/reel/DfLqhT9Obuc/`); **Scheduled on TikTok Studio for `2026-11-01 18:30`**.
  - `short_17` (`3-MONTH / SITUATIONSHIP`): Upgraded `68px` version Live on Instagram Reels (`/reel/DfLqpclukZh/`); **Scheduled on TikTok Studio for `2026-11-02 11:00`**.
  - `short_18` (`STOPPED ACCEPTING / BARE MINIMUM`): Upgraded `68px` version Live on Instagram Reels (`/reel/DfLqxxBO1JV/`); **Scheduled on TikTok Studio for `2026-11-02 18:30`**.
  - `short_19` (`WHY THEY LEAVE / YOU ON READ`, `FK=2.62`): Live on Instagram Reels (`/reel/DfN3TH1OR7s/`); **Scheduled on TikTok Studio for `2026-11-03 11:00` (`7703341562952043789`)**.
  - `short_20` (`THE 3 BIRTHDAYS / TO AVOID DATING`, `FK=2.54`): Live on Instagram Reels (`/reel/DfN3fVRul_X/`); **Scheduled on TikTok Studio for `2026-11-03 18:30` (`7703341818120768781`)**.
  - `short_21` (`YOUR NOVEMBER / LOVE SHIFT`, `FK=2.13`): Live on Instagram Reels (`/reel/DfN3scQOV9B/`); **Scheduled on TikTok Studio for `2026-11-04 11:00` (`7703342010752601357`)**.
  - Early `<100` view prototype tests (`45`, `67`, `74`, `95` views) set to **Private (`Only me`)** on TikTok Studio.
- **Automated 2-Hour Social Sync (`social_auto_sync.py` / `\Sovereign5SocialAutoSync`)**:
  - Runs `seed_first_comments.py`, `tiktok_comment_responder.py --live --limit 15`, and `ig_comment_responder.py --live --limit 15`.
- **Viral Outlier Hook Finder (`viral_outlier_finder.py` + `viral_outliers.db`)**:
  - Ranks 4x–20x outlier hooks across relationship/attachment/numerology niches and exports to `G:\My Drive\MVV_Memory_Vault\03-Projects\Viral_Outlier_Hooks_Report.md`.

---

## 5. End-to-End Verification Suites

- **Local Production Suite**: `python tests/test_production_readiness.py` (requires `python -m http.server 8080`)
- **Live Domain Suite**: `python tests/test_live_production.py` (verifies `https://blueprint.megavegaventures.com/` directly)
