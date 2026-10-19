# Test overlap tally logic
def test_overlap():
    sources = [
        # 7s
        ('lifePath', 'Life Path', 'Pythagorean', 7),
        ('chaldeanName', 'Chaldean Full Name (25/7)', 'Chaldean', 7),
        ('bhagyank', 'Bhagyank (Conductor)', 'Vedic', 7),
        ('namank', 'Namank (Name Vibration)', 'Vedic', 7),
        ('loShuDominant', 'Lo Shu Dominant (Metal)', 'Lo Shu', 7),
        # 8s
        ('soulUrge', "Soul Urge (Heart's Desire)", 'Pythagorean', 8),
        ('firstNameConsonants', 'First-Name Consonants (D+M=8)', 'Pythagorean', 8),
        ('pythagoreanSurname', 'Surname Base (Vega 17/8)', 'Pythagorean', 8),
        # 4s
        ('consonantBase', 'Consonant Structural Base (D=4, M=4, V=4)', 'Pythagorean', 4),
        ('kabbalahChesed', 'Kabbalistic Abundance Base (Chesed / Dalet-Mem)', 'Kabbalistic', 4),
        ('fengShuiCorner', 'Feng Shui Wealth Corner (Southeast Xun)', 'Lo Shu', 4),
        # 9s
        ('expression', 'Expression / Destiny', 'Pythagorean', 9),
        # 6s
        ('chaldeanSurname', 'Chaldean Surname (Vega 15/6)', 'Chaldean', 6),
        # 1s
        ('moolank', 'Moolank (Driver)', 'Vedic', 1),
    ]

    kabbalah_active = {7, 8, 4, 9, 6} # Netzach, Hod, Chesed, Yesod, Tiferet
    SYSTEM_ORDER = ['Pythagorean', 'Chaldean', 'Kabbalistic', 'Vedic', 'Lo Shu']

    tally = {}
    for n in range(1, 10):
        hits = [s for s in sources if s[3] == n]
        sys = set(h[2] for h in hits)
        if n in kabbalah_active:
            sys.add('Kabbalistic')
        tally[n] = {
            'number': n,
            'count': len(hits),
            'systems': [s for s in SYSTEM_ORDER if s in sys],
            'sources': [h[1] for h in hits]
        }

    ranking = sorted(tally.values(), key=lambda x: (x['count'], len(x['systems'])), reverse=True)
    print("RANKING:")
    for i, r in enumerate(ranking):
        print(f"#{i+1}: Number {r['number']} - count={r['count']}, systems={r['systems']}")

test_overlap()
