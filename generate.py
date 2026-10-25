#!/usr/bin/env python3
"""
Generuje pliki kalendarza (.ics) i data.js na podstawie harmonogramu
wywozu odpadów komunalnych – miasto i gmina Ślesin, rok 2026.

Użycie:  python3 generate.py
Wynik:   katalog ics/ (150 plików) oraz plik data.js

Daty są przepisane z PDF-a dokładnie tak, jak w nim stoją (łącznie z
terminami przesuniętymi przez święta). Każdy ciąg liczb to dni miesiąca
od stycznia do czerwca (H1) lub od lipca do grudnia (H2). Nowy miesiąc
zaczyna się tam, gdzie liczba maleje.
"""
import datetime as dt
import json
import os
import shutil

YEAR = 2026
HERE = os.path.dirname(os.path.abspath(__file__))

TYPES = [
    # id, bit, nazwa w interfejsie, krótka nazwa w kalendarzu, opis do wydarzenia
    ("nies", 1, "Niesegregowane", "niesegregowane", "Niesegregowane (pojemniki lub worki koloru czerwonego)", "#C8332B"),
    ("popiol", 2, "Popiół i żużel", "popiół i żużel", "Popiół i żużel z palenisk domowych", "#5E6A63"),
    ("papier", 4, "Papier i plastik", "papier i plastik", "Segregowane: papier, plastik", "#2F6DB5"),
    ("szklo", 8, "Szkło", "szkło", "Segregowane: szkło", "#2E8B57"),
    ("bio", 16, "Biodegradowalne", "bio", "Biodegradowalne (worki koloru brązowego)", "#7B4A2A"),
]
FULL_MASK = sum(t[1] for t in TYPES)

DAYS_PL = ["poniedziałek", "wtorek", "środa", "czwartek", "piątek"]
DAYS_ACC = ["w poniedziałki", "we wtorki", "w środy", "w czwartki", "w piątki"]

# Miejscowości w zbiorach (kolejność jak w harmonogramie)
GROUPS = {
    "pon": dict(weekday=0, places=[
        "Osiedle Powstańców Wielkopolskich", "Osiedle „Stare Miasto”",
        "Osiedle „Północ”", "Osiedle Krzyżka"]),
    "wto": dict(weekday=1, places=[
        "Honoratka", "Władysławów", "Rębowo", "Lubomyśle", "Dąbrowa Duża",
        "Dąbrowa Mała", "Biele", "Goranin", "Goraninek", "Lizawy", "Mikorzyn",
        "Różnowo", "Biskupie Sarnowskie", "Sarnowa", "Florentynowo"]),
    "sro": dict(weekday=2, places=[
        "Biskupie", "Kolonia Sarnowa", "Ostrowąż", "Giętkowo", "Ostrowąż-Kolonia",
        "Kijowiec", "Kijowskie Nowiny", "Ściany", "Kijowiec-Szyszynek", "Szyszynek",
        "Marianowo", "Szyszyn", "Helenowo", "Pole B", "Teodorowo",
        "Szyszyńskie Holendry", "Konstantynowo", "Konstantynówek", "Ostrowy",
        "Stanisławowo", "Żółwieniec"]),
    "czw": dict(weekday=3, places=[
        "Licheń Stary", "Julia", "Kępa", "Niedźwiady Małe", "Niedźwiady Duże",
        "Półwiosek Stary", "Półwiosek Nowy", "Wąsosze", "Wąsoskie Holendry",
        "Wygoda", "Smolarnia", "Trajbudy"]),
    "pia": dict(weekday=4, places=[
        "Głębockie Pierwsze", "Głębockie Drugie", "Witalisów", "Półwiosek Lubstowski",
        "Tokary", "Różopole", "Kolebki", "Kolebki-Frąsin", "Kolebki-Ługi", "Ignacewo",
        "Pogorzele", "Smolniki", "Smolniki Polskie", "Wierzelin", "Leśnictwo",
        "Piotrkowice", "Pogoń Gosławicka", "Pogoń Lubstowska", "Pogoń-Leśniczówka",
        "Bylew", "Bylew Parcele"]),
}

# (H1: styczeń–czerwiec, H2: lipiec–grudzień)
RAW = {
    "pon": {
        "nies": ("5 12 19 26 2 9 16 23 2 9 16 23 30 7 13 20 27 4 11 18 25 1 8 15 22 29",
                 "6 13 20 27 3 10 17 24 31 7 14 21 28 5 12 19 26 2 9 16 23 30 7 14 21 28"),
        "popiol": ("12 26 9 23 9 23 7 20 18 15", "13 10 7 5 19 2 16 30 14"),
        "papier": ("19 16 2 16 13 27 11 25 8 22", "6 20 3 17 31 14 12 26 9 7"),
        "szklo": ("2 8", "14 7"),
        "bio": ("12 26 9 23 9 23 7 20 4 18 1 15 29", "13 27 10 24 7 21 5 19 2 16 30 14"),
    },
    "wto": {
        "nies": ("7 13 20 27 3 10 17 24 3 10 17 24 31 7 14 21 28 5 12 19 26 2 9 16 23 30",
                 "7 14 21 28 4 11 18 25 1 8 15 22 29 6 13 20 27 3 10 17 24 1 8 15 22 29"),
        "popiol": ("13 27 10 24 10 24 7 21 19 16", "14 11 8 6 20 3 17 1 15"),
        "papier": ("20 17 3 17 14 28 12 26 9 23", "7 21 4 18 1 15 13 27 10 8"),
        "szklo": ("3 9", "15 8"),
        "bio": ("13 27 10 24 10 24 7 21 5 19 2 16 30", "14 28 11 25 8 22 6 20 3 17 1 15"),
    },
    "sro": {
        "nies": ("7 14 21 28 4 11 18 25 4 11 18 25 1 8 15 22 29 6 13 20 27 3 10 17 24",
                 "1 8 15 22 29 5 12 19 26 2 9 16 23 30 7 14 21 28 4 10 18 25 2 9 16 23 30"),
        "popiol": ("14 28 11 25 11 25 8 22 20 17", "15 12 9 7 21 4 18 2 16"),
        "papier": ("21 18 4 18 15 29 13 27 10 24", "8 22 5 19 2 16 14 28 10 9"),
        "szklo": ("4 10", "16 9"),
        "bio": ("14 28 11 25 11 25 8 22 6 20 3 17", "1 15 29 12 26 9 23 7 21 4 18 2 16"),
    },
    "czw": {
        "nies": ("2 8 15 22 29 5 12 19 26 5 12 19 26 2 9 16 23 30 7 14 21 28 5 11 18 25",
                 "2 9 16 23 30 6 13 20 27 3 10 17 24 1 8 15 22 29 5 12 19 26 3 10 17 22 31"),
        "popiol": ("15 29 12 26 12 26 9 23 21 18", "16 13 10 8 22 5 19 3 17"),
        "papier": ("22 19 5 19 16 30 14 28 11 25", "9 23 6 20 3 17 15 29 12 10"),
        "szklo": ("5 11", "17 10"),
        "bio": ("15 29 12 26 12 26 9 23 7 21 5 18", "2 16 30 13 27 10 24 8 22 5 19 3 17"),
    },
    "pia": {
        "nies": ("2 9 16 23 30 6 13 20 27 6 13 20 27 3 10 17 24 30 8 15 22 29 5 12 19 26",
                 "3 10 17 24 31 7 14 21 28 4 11 18 25 2 9 16 23 30 6 13 20 27 4 11 18 23"),
        "popiol": ("16 30 13 27 13 27 10 24 22 19", "17 14 11 9 23 6 20 4 18"),
        "papier": ("23 20 6 20 17 30 15 29 12 26", "10 24 7 21 4 18 16 30 13 11"),
        "szklo": ("6 12", "18 11"),
        "bio": ("16 30 13 27 13 27 10 24 8 22 5 19", "3 17 31 14 28 11 25 9 23 6 20 4 18"),
    },
}

# Szkło jest odbierane raz na kwartał: marzec, czerwiec, wrzesień, grudzień
GLASS_MONTHS = ((3, 6), (9, 12))

# Znane przesunięcia przez święta (data, powód) – nie są błędami
KNOWN_SHIFTS = {
    "pon": {dt.date(2026, 4, 7): "Poniedziałek Wielkanocny"},
    "wto": {dt.date(2026, 1, 7): "Trzech Króli"},
    "sro": {dt.date(2026, 11, 10): "Święto Niepodległości (11.11)"},
    "czw": {dt.date(2026, 1, 2): "Nowy Rok", dt.date(2026, 6, 5): "Boże Ciało",
            dt.date(2026, 12, 22): "Wigilia (24.12)"},
    "pia": {dt.date(2026, 4, 30): "Święto Pracy (1.05)", dt.date(2026, 12, 23): "Boże Narodzenie (25.12)"},
}


def split_months(tokens, first_month):
    """Dzieli ciąg dni na miesiące: nowy miesiąc zaczyna się, gdy liczba maleje."""
    nums = [int(x) for x in tokens.split()]
    months, current = [], [nums[0]]
    for prev, cur in zip(nums, nums[1:]):
        if cur < prev:
            months.append(current)
            current = []
        current.append(cur)
    months.append(current)
    assert len(months) == 6, (tokens, months)
    out = []
    for i, days in enumerate(months):
        for d in days:
            out.append(dt.date(YEAR, first_month + i, d))
    return out


def parse(group, type_id):
    h1, h2 = RAW[group][type_id]
    if type_id == "szklo":
        dates = []
        for tokens, months in zip((h1, h2), GLASS_MONTHS):
            for d, m in zip(tokens.split(), months):
                dates.append(dt.date(YEAR, m, int(d)))
        return dates
    return split_months(h1, 1) + split_months(h2, 7)


def validate(all_dates):
    problems = 0
    for g, per_type in all_dates.items():
        wd = GROUPS[g]["weekday"]
        for t, dates in per_type.items():
            assert dates == sorted(dates), (g, t, "daty nie są posortowane")
            assert len(dates) == len(set(dates)), (g, t, "duplikaty")
            for d in dates:
                if d.weekday() != wd and d not in KNOWN_SHIFTS[g]:
                    problems += 1
                    print(f"UWAGA: {g}/{t} {d} wypada w {DAYS_PL[d.weekday()]}")
    return problems


# ---------- ICS ----------

def esc(text):
    return (text.replace("\\", "\\\\").replace(";", "\\;")
                .replace(",", "\\,").replace("\n", "\\n"))


def fold(line):
    """Składanie linii do 75 bajtów (RFC 5545), bez rozcinania znaków UTF-8."""
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return [line]
    parts, buf, size, limit = [], "", 0, 75
    for ch in line:
        n = len(ch.encode("utf-8"))
        if size + n > limit:
            parts.append(buf)
            buf, size, limit = " " + ch, 1 + n, 75
        else:
            buf += ch
            size += n
    parts.append(buf)
    return parts


def build_ics(group, mask, all_dates):
    g = GROUPS[group]
    chosen = [t for t in TYPES if mask & t[1]]
    by_date = {}
    for t in chosen:
        for d in all_dates[group][t[0]]:
            by_date.setdefault(d, []).append(t)

    places = ", ".join(g["places"])
    day_name = DAYS_PL[g["weekday"]]
    cal_name = f"Odpady – Ślesin ({day_name})"
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0",
        "PRODID:-//Harmonogram odpadow Slesin 2026//PL",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        f"X-WR-CALNAME:{esc(cal_name)}",
        "X-WR-CALDESC:" + esc("Terminy wywozu odpadów komunalnych w 2026 r. Sprawdź oficjalny harmonogram urzędu."),
    ]
    for d in sorted(by_date):
        types_here = by_date[d]
        summary = "🗑️ Wywóz odpadów: " + ", ".join(t[3] for t in types_here)
        desc = "\n".join(t[4] for t in types_here) + f"\n\nMiejscowości: {places}"
        if d in KNOWN_SHIFTS[group]:
            desc += f"\n\nTermin przesunięty ze względu na święto: {KNOWN_SHIFTS[group][d]}."
        nxt = d + dt.timedelta(days=1)
        key = "".join(t[0][:2] for t in types_here)
        lines += [
            "BEGIN:VEVENT",
            f"UID:{group}-{d:%Y%m%d}-{key}@odpady-slesin-{YEAR}",
            f"DTSTAMP:{YEAR}0101T000000Z",
            f"DTSTART;VALUE=DATE:{d:%Y%m%d}",
            f"DTEND;VALUE=DATE:{nxt:%Y%m%d}",
            f"SUMMARY:{esc(summary)}",
            f"DESCRIPTION:{esc(desc)}",
            "TRANSP:TRANSPARENT",
            "BEGIN:VALARM", "ACTION:DISPLAY",
            "DESCRIPTION:" + esc("Jutro wywóz odpadów – wystaw pojemniki"),
            "TRIGGER:-PT6H",  # 18:00 w dniu poprzednim
            "END:VALARM",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    out = []
    for line in lines:
        out.extend(fold(line))
    return "\r\n".join(out) + "\r\n"


def main():
    all_dates = {g: {t[0]: parse(g, t[0]) for t in TYPES} for g in GROUPS}
    problems = validate(all_dates)
    print("Niezgodności dnia tygodnia:", problems)

    ics_dir = os.path.join(HERE, "ics")
    if os.path.isdir(ics_dir):
        shutil.rmtree(ics_dir)
    os.makedirs(ics_dir)
    count = 0
    for g in GROUPS:
        for mask in range(1, FULL_MASK + 1):
            with open(os.path.join(ics_dir, f"{g}-{mask}.ics"), "w", encoding="utf-8", newline="") as f:
                f.write(build_ics(g, mask, all_dates))
            count += 1
    print("Zapisano plików .ics:", count)

    data = {
        "year": YEAR,
        "types": [dict(id=t[0], bit=t[1], name=t[2], color=t[5]) for t in TYPES],
        "groups": [
            dict(id=g, day=DAYS_PL[v["weekday"]], dayAcc=DAYS_ACC[v["weekday"]],
                 places=v["places"],
                 dates={t: [d.isoformat() for d in ds] for t, ds in all_dates[g].items()})
            for g, v in GROUPS.items()
        ],
    }
    with open(os.path.join(HERE, "data.js"), "w", encoding="utf-8") as f:
        f.write("// Plik generowany przez generate.py – nie edytuj ręcznie.\n")
        f.write("window.WASTE_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
    print("Zapisano data.js")


if __name__ == "__main__":
    main()
