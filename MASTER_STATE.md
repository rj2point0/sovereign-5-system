# 🔮 SACRED NUMBER BLUEPRINT (`5numsystem`) — MASTER PRODUCTION STATE

> **Anti-Context-Rot Checkpoint (Updated: 2026-11-03)**  
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
  - **1-Tap Birth Day Quick-Select Strip (`#quick-day-strip`)**: 11-column × 3-row grid (`1`–`31`) inside `#heroForm` (`"⚡ Fast Track: Tap Your Birth Day (1–31) For An Instant Love Code Preview"`). Tapping any day `1`–`31` fires `quick_day_selected`, populates `#dobDay` (with default Month/Year if not selected yet), and jumps straight to the Teaser + Partner Compatibility screen with `#quick-day-banner` (which includes a 1-tap `💑 Test Partner's Birth Day (1–31) ↓` jump button `#btn-jump-partner-strip`).
  - **1-Tap Partner Birth Day Strip (`#partner-quick-day-strip`), iMessage Blurred "Flip The Chase" Preview (`#flip-chase-preview-bubble`), & Viral Partner Share (`?d1=X&d2=Y` + `#btn-share-partner-match`)**: When arriving via `quick_day_selected`, `#partner-compat-box` (containing `#partner-quick-day-strip`) is rendered directly beneath the compact 3-line `#quick-day-banner` at the top of `view2` so the `1–31` Partner Birth Day Grid sits immediately inside the `390x660` viewport (`bottom <= 635px`) without scrolling. Visitors can tap any Partner Birth Day (`1`–`31`) in 1 tap without needing their crush's birth month or year (`runPartnerQuickDayCheck` -> `runPartnerCompatibilityCheck({ viaQuickDay: true })` -> fires `partner_check_run`). Immediately renders `#flip-chase-preview-bubble` showing the first 7–9 words unblurred for their Partner's Driver (`1`–`9`), 2 lines of realistic blurred SMS text (`filter: blur(5px)`), `#btn-unlock-text-script` routing to `$17` `checkoutMini('unlock_text_script_17')`, and `#btn-share-partner-match` (`"📲 Send This [X]% Match To Them / A Friend"` -> fires `partner_match_shared` and shares `https://blueprint.megavegaventures.com/?d1=[X]&d2=[Y]&utm_source=partner_share`). Visiting `/?d1=19&d2=23` automatically executes `runQuickDayPreview(19)` + `runPartnerQuickDayCheck(23)` and fires `shared_match_opened`.
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
  - **2-Hour Cart Abandonment / High-Intent Partner Check Recovery (`send_cart_recovery.py` + `lead_capture_worker.py`)**: Automatically dispatches a personalized `$17` VIP Unlock email 2 hours after Email #1 for any visitor who triggers `checkout_clicked` or runs `3+` `partner_check_run` checks without completing `purchase_return` (`cart_recovery_sent_at` tracked in `processed_leads_state.json`). Sent to Geet (`geet08190@gmail.com`, `1986-02-19`, tested `Dec 23` `96%`, `Aug 08` `94%`, `Aug 19` `85%`) with subject `"Geet — your 96% match on Dec 23 (and why Aug 19 pulls away) 💔"`.
- **Inline Partner Compatibility Email Capture (`#partner-compat-email-box` in `app.js`) & 10-Second Hesitation Micro-Trigger (`#partner-hesitation-callout`)**:
  - When a visitor tests a Partner/Crush birthday on the Teaser screen (`runPartnerCompatibilityCheck()`) without having entered their email yet (`!state.profile.email`), renders a 1-line inline email capture bar right above the `$17` Mini-Read button (`"📩 Want to save this Partner Compatibility score & see your next 3 relationship turning-point dates for free?"` + `[Email Our Match Report →]`).
  - **10-Second Hesitation Micro-Trigger (`#partner-hesitation-callout`)**: If `10 seconds` (`window.__S5_HESITATION_MS || 10000`) pass after `runPartnerCompatibilityCheck()` and the visitor has NOT clicked `#btn-unlock-text-script` (`$17`) and has NOT submitted `#partner-compat-email-input` (`!state.profile.email`), smoothly reveals `#partner-hesitation-callout` (`"⚡ Not ready for the full $17 unlock yet? Enter your email below and we'll send your [Day X × Day Y] Compatibility Breakdown + Opening Reset Line to your inbox free:"`) and applies `.gold-pulse-highlight` to `#partner-compat-email-box`.
  - Submitting saves `state.profile.email`, fires `lead_submitted` (`trigger: "partner_compat_email_bar"`) with `partner_dob` so `lead_capture_worker.py` immediately sends Email #1 with the **`💑 PARTNER / CRUSH COMPATIBILITY SNAPSHOT`** section, and displays `#partner-compat-email-confirmed`.
- **Real-Time Birth-Day Compatibility % Comment Responder (`comment_reply_engine.py` + `tiktok_comment_responder.py` + `ig_comment_responder.py`)**:
  - `parse_birth_days_from_comment(text)` detects 1 or 2 birth days (`1`–`31`) in viewer comments (`"14th and 23rd"`, `"me 7 him 19"`, `"Oct 12 and May 4"`, `"Born on the 19th"`, `"7"`, `"25th"`).
  - **2 Birth Days (`A_PAIR_COMPAT`)**: Computes real Vedic Driver numbers (`1`–`9`), compatibility percentage (`81%–97%`), and dynamic label (`Twin-Spark Lock`, `Soulmate Lock`, `Push-Pull Magnet`, `Karmic Fire`), replying (`<= 140 chars`, zero URLs) with their exact score and a callout to check their `X×Y` text script in our bio link.
  - **1 Birth Day (`A_SINGLE_DAY_COMPAT`)**: Replies (`<= 140 chars`, zero URLs) with their Vedic Driver archetype + their #1 soulmate & #1 karmic trap birth days, inviting them to test their crush's day in our bio link.
- **AI Comment Listening Pass (`ai_listening_pass.py` + `AI_Comment_Listening_Pass_Report.md`)**:
  - Analyzes 88+ real viewer comments across viral relationship attachment, situationship, and birthday compatibility posts (`viral_outliers.db` -> `viewer_comments`).
  - Injected the #1 requested deliverable (**"The Exact 'Flip The Chase' Text Script For Their Birth Number"**) directly into `#tier-card-mini` (`$17`), `#tier-card-base` (`$37`), `#partner-compat-result`, and `buildLoveMiniUnlockedHtml` (`app.js`).

---

## 4. Dual-Platform Social Automation & Video Pipeline (`short_01`–`short_30`)

- **Authenticated Browser Profiles & Verified Logged-Out Mobile Bio Links**:
  - TikTok (`@sacrednumberblueprint` — Display Name: `Love & Birthday Compatibility` · Bio: `Why do they pull away? 💔 Test your birthday & theirs across 5 systems 👇` · Publicly Clickable Bio Link `[data-e2e="user-link"]`: `blueprint.megavegaventures.com/?utm_source=tiktok&cohort=bio` verified in logged-out iPhone 14 mobile view): `C:\Users\User\.gemini\antigravity\tiktok_browser_profile`
  - Instagram (`@sacrednumberblueprint` — Name: `Love & Birthday Compatibility` · Bio: `Why do they pull away? 💔 Test your birthday & theirs across 5 systems 👇` · Publicly Clickable Bio Link: `blueprint.megavegaventures.com/?utm_source=ig_bio&cohort=ig_reels`): `C:\Users\User\.gemini\antigravity\ig_browser_profile`
- **20-Clip Real Human 9:16 B-Roll Library (`broll_library/`)**:
  - Managed by `fetch_human_broll.py` (`broll_01` through `broll_20`).
- **Video Generator (`generate_broll_story_tiktoks.py`)**:
  - Enforces Jenny Hoyos's 5th-Grade Readability Gate (`Flesch-Kincaid Grade <= 5.5`, zero academic jargon, `But/Therefore` twist connector, `<= 0.35s` tail hold).
  - Renders **giant `68px` bold 3–6 word Poster Headlines (`grid_headline`)** + `38px` crimson subtitle (`grid_sub`) on Frame 1 so every thumbnail is readable in the 3-column mobile profile grid.
  - Renders the **Interactive Partner Match Card (`Born 19th × Born 23rd → 96% SOULMATE LOCK` + 1-Tap Birth Day Strip) & Blurred iMessage "Flip The Chase" Text Script Bubble (`draw_imessage_match_reveal_card`)** during `4.6s–7.5s` on all 7.5-second shorts, plus a persistent bottom CTA pill (`draw_final_5s_cta_pill`) showing both `Tap @sacrednumberblueprint (Link in Bio)` and `Test Both Birthdays Free → Blueprint.MegaVegaVentures.com`.
- **Interactive "2-Birthday Match % Bait" Seeded First Comments (`seed_first_comments.py` & IG Reels) + Social Proof Sample Match Follow-Up (`seed_sample_reading_replies.py`)**:
  - All `short_18` through `short_30` videos on TikTok and Instagram Reels use the 2-birthday comment bait (`"Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '19 & 23') and I'll reply with your Compatibility % score! 👇"`, `124 chars`, 100% automod-safe) to directly feed `parse_birth_days_from_comment(text)` (`A_PAIR_COMPAT`).
  - `seed_sample_reading_replies.py` posts a 138-char creator follow-up comment (`"📌 Top pair asked in DMs today: Day 19 × Day 23 = 96% Twin-Spark Lock 🔥 Intense pull, but one goes quiet when stressed! Drop your 2 days 👇"`) on `short_20`, `short_22`, `short_25`, and `short_28` across TikTok and Instagram Reels so cold scrollers see a live compatibility reading in the comment thread.
- **Current Video Status (`uploaded_videos.json` & `uploaded_ig_reels.json`)**:
  - `short_01`–`short_20`: **Published Live** on both TikTok and Instagram Reels with automod-safe first comments seeded (`seeded_first_comments.json`; `short_14` `7702844507703823629`, `short_15` `7703342845494562061`, `short_16` `7702844640541641997`, `short_17` `7703623597469748493`, `short_18` `7702844869877828877`, `short_19` `7703341562952043789` / `7703990124526210318`, and `short_20` `7703341818120768781` verified `ModalIntact=True`).
  - `short_21` (`YOUR NOVEMBER / LOVE SHIFT`, `7.54s`, `FK=1.85`): Upgraded to 7.5-second `draw_imessage_match_reveal_card()` format; Live on Instagram Reels; **Scheduled on TikTok Studio for `2026-11-04 11:00`**.
  - `short_22` (`DAYS THAT GO / COLD FAST`, `7.56s`, `FK=0.59`): **Published Live** on both Instagram Reels (`/reel/DfPp_HOOJS3/`) and TikTok (`7703622747489963278`, **`155 views` — #1 video on account**, 2-birthday comment seeded & `ModalIntact=True`).
  - `short_23` (`NEVER DOUBLE / TEXT THEM`, `7.54s`, `FK=0.67`): Upgraded with `draw_imessage_match_reveal_card()` (`4.6s–7.5s`); Live on Instagram Reels (`/reel/DfPqHCVucCA/` with 2-birthday comment seeded); **Scheduled on TikTok Studio for `2026-11-05 11:00` (`7703990374565498125`)**.
  - `short_24` (`YOUR TRUE / SOULMATE DAY`, `7.54s`, `FK=-0.64`): Upgraded with `draw_imessage_match_reveal_card()` (`4.6s–7.5s`); Live on Instagram Reels (`/reel/DfPqO5wupcl/`, `103 views`, 2-birthday comment seeded); **Scheduled on TikTok Studio for `2026-11-05 18:30` (`7703990588911193357`)**.
  - `short_25` (`SOULMATE OR / KARMIC TRAP?`, `7.54s`, `FK=1.54`): **Published Live** on both Instagram Reels (`/reel/DfP3a8aOUPF/`, `125 views`, 2-birthday comment seeded) and TikTok (`7703630255013104910`, `101 views`, 2-birthday comment seeded & `ModalIntact=True`).
  - `short_26` (`DO THEY MISS YOU / IN NO CONTACT?`, `7.70s`, `FK=3.56`): Live on Instagram Reels (`/reel/DfP3jR_OPp6/`, 2-birthday comment seeded); **Scheduled on TikTok Studio for `2026-11-06 11:00` (`7703630452141067534`)**.
  - `short_27` (`3 LOVE DATES / TO WATCH NEXT`, `7.54s`, `FK=-0.41`): Live on Instagram Reels (`/reel/DfP3rbpu_81/`, 2-birthday comment seeded); **Scheduled on TikTok Studio for `2026-11-06 18:30` (`7703630711911206157`)**.
  - `short_28` (`WHO CHASES WHO / BY BIRTH DAY`, `8.11s`, `FK=0.79`): **Published Live** on both TikTok (`7704068444592950541`, 2-birthday comment seeded & `ModalIntact=True`) and Instagram Reels (`/reel/DfS6Iu5OEhv/`, 2-birthday comment seeded).
  - `short_29` (`BIRTH DAYS THAT / GO SILENT`, `8.47s`, `FK=1.76`): Live on Instagram Reels (`/reel/DfS6QdAuGPY/`, 2-birthday comment seeded); **Scheduled on TikTok Studio for `2026-11-07 11:00`**.
  - `short_30` (`ARE YOUR BIRTHDAYS / ENDGAME?`, `7.54s`, `FK=3.49`): Live on Instagram Reels (`/reel/DfS6YOPO8hJ/`, 2-birthday comment seeded); **Scheduled on TikTok Studio for `2026-11-07 18:30`**.
  - Early `<100` view prototype tests (`45`, `67`, `74`, `95` views) set to **Private (`Only me`)** on TikTok Studio.
- **Automated 2-Hour Social Sync (`social_auto_sync.py` / `\Sovereign5SocialAutoSync`)**:
  - Runs `seed_first_comments.py`, `tiktok_comment_responder.py --live --limit 15`, and `ig_comment_responder.py --live --limit 15`.
- **Viral Outlier Hook Finder (`viral_outlier_finder.py` + `viral_outliers.db`)**:
  - Ranks 4x–20x outlier hooks across relationship/attachment/numerology niches and exports to `G:\My Drive\MVV_Memory_Vault\03-Projects\Viral_Outlier_Hooks_Report.md`.

---

## 5. End-to-End Verification Suites

- **Local Production Suite**: `python tests/test_production_readiness.py` (requires `python -m http.server 8080`)
- **Live Domain Suite**: `python tests/test_live_production.py` (verifies `https://blueprint.megavegaventures.com/` directly)
