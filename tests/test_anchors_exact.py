import math

def reduce(n):
    x = abs(int(n))
    while x > 9:
        x = sum(int(d) for d in str(x))
    return x

def test_engine_overlap():
    # Simulate Adam Vega 1978-08-19
    sources = [
        {'key': 'lifePath', 'label': 'Life Path', 'system': 'Pythagorean', 'value': 7},
        {'key': 'expression', 'label': 'Expression / Destiny', 'system': 'Pythagorean', 'value': 9},
        {'key': 'soulUrge', 'label': "Soul Urge (Heart's Desire)", 'system': 'Pythagorean', 'value': 8},
        {'key': 'firstNameConsonants', 'label': 'First-Name Consonants', 'system': 'Pythagorean', 'value': 8},
        {'key': 'chaldeanName', 'label': 'Chaldean Full Name (25/7)', 'system': 'Chaldean', 'value': 7},
        {'key': 'moolank', 'label': 'Moolank (Driver)', 'system': 'Vedic', 'value': 1},
        {'key': 'bhagyank', 'label': 'Bhagyank (Conductor)', 'system': 'Vedic', 'value': 7},
        {'key': 'namank', 'label': 'Namank (Name Vibration)', 'system': 'Vedic', 'value': 7},
        {'key': 'loShuDominant', 'label': 'Lo Shu Dominant (Metal)', 'system': 'Lo Shu', 'value': 7},
        {'key': 'chaldeanSurname', 'label': 'Chaldean Surname (Vega 15/6)', 'system': 'Chaldean', 'value': 6},
        {'key': 'birthMonth', 'label': 'Birth Month Vibration (August 8)', 'system': 'Pythagorean', 'value': 8},
        {'key': 'loShuWealthEight', 'label': 'Lo Shu Earth Wealth (8 - Fa)', 'system': 'Lo Shu', 'value': 8},
        {'key': 'consonantBase4', 'label': 'Consonant Structural Base (D=4, M=4, V=4)', 'system': 'Pythagorean', 'value': 4},
        {'key': 'kabbalahChesed', 'label': 'Kabbalistic Abundance Base (Chesed / Dalet-Mem)', 'system': 'Kabbalistic', 'value': 4},
        {'key': 'baguaWealthCorner', 'label': 'Feng Shui Wealth Corner (Southeast Xun)', 'Lo Shu': 'Lo Shu', 'system': 'Lo Shu', 'value': 4},
    ]

    kabbalahNums = {7, 8, 4, 9, 6}
    SYSTEM_ORDER = ['Pythagorean', 'Chaldean', 'Kabbalistic', 'Vedic', 'Lo Shu']
    loShuCounts = {'1': 2, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 3, '8': 2, '9': 3}

    tally = {}
    for n in range(1, 10):
        hits = [s for s in sources if s['value'] == n]
        sys = set(h['system'] for h in hits)
        if n in kabbalahNums:
            sys.add('Kabbalistic')
        tally[n] = {
            'number': n,
            'count': len(hits),
            'systems': [s for s in SYSTEM_ORDER if s in sys],
            'sources': [h['label'] for h in hits],
            'firstIndex': sources.index(hits[0]) if hits else 99,
            'loShuCount': loShuCounts.get(str(n), 0)
        }

    ranking = sorted(tally.values(), key=lambda a: (
        -a['count'],
        -len(a['systems']),
        -a['loShuCount'],
        a['firstIndex'],
        a['number']
    ))

    print("ANCHORS:")
    roles = ['Primary Signature Anchor', 'Secondary Wealth & Strategy Engine', 'Tertiary Structural Foundation']
    for i in range(3):
        a = ranking[i]
        print(f"#{i+1}: {a['number']} ({roles[i]}) - Count: {a['count']}, Systems: {len(a['systems'])} ({', '.join(a['systems'])})")

    print("\nSECONDARY HARMONICS:")
    for i in range(3, 5):
        a = ranking[i]
        print(f"Harmonic: {a['number']} - Count: {a['count']}, Systems: {len(a['systems'])} ({', '.join(a['systems'])})")

test_engine_overlap()
