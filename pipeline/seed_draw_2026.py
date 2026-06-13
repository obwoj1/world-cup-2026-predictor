"""Authoritative FIFA World Cup 2026 final-draw seed data.

The final draw was held in Washington, DC on 2025-12-05, placing all 48 teams into
12 groups of four. Group composition below is cross-checked against ESPN and FIFA
group previews (see data/sources/SOURCES.md).

Each row: (group, name, fifa_code, elo_code, confederation)
  * fifa_code  — FIFA 3-letter code (used as the team id throughout the app)
  * elo_code   — eloratings.net 2-letter code (used to look up the Elo rating)
"""
from __future__ import annotations

# group, name, fifa_code, elo_code, confederation
TEAMS_2026 = [
    ("A", "Mexico", "MEX", "MX", "CONCACAF"),
    ("A", "South Africa", "RSA", "ZA", "CAF"),
    ("A", "South Korea", "KOR", "KR", "AFC"),
    ("A", "Czechia", "CZE", "CZ", "UEFA"),

    ("B", "Canada", "CAN", "CA", "CONCACAF"),
    ("B", "Bosnia and Herzegovina", "BIH", "BA", "UEFA"),
    ("B", "Qatar", "QAT", "QA", "AFC"),
    ("B", "Switzerland", "SUI", "CH", "UEFA"),

    ("C", "Brazil", "BRA", "BR", "CONMEBOL"),
    ("C", "Morocco", "MAR", "MA", "CAF"),
    ("C", "Haiti", "HAI", "HT", "CONCACAF"),
    ("C", "Scotland", "SCO", "SQ", "UEFA"),

    ("D", "United States", "USA", "US", "CONCACAF"),
    ("D", "Paraguay", "PAR", "PY", "CONMEBOL"),
    ("D", "Australia", "AUS", "AU", "AFC"),
    ("D", "Türkiye", "TUR", "TR", "UEFA"),

    ("E", "Germany", "GER", "DE", "UEFA"),
    ("E", "Curaçao", "CUW", "CW", "CONCACAF"),
    ("E", "Ivory Coast", "CIV", "CI", "CAF"),
    ("E", "Ecuador", "ECU", "EC", "CONMEBOL"),

    ("F", "Netherlands", "NED", "NL", "UEFA"),
    ("F", "Japan", "JPN", "JP", "AFC"),
    ("F", "Sweden", "SWE", "SE", "UEFA"),
    ("F", "Tunisia", "TUN", "TN", "CAF"),

    ("G", "Belgium", "BEL", "BE", "UEFA"),
    ("G", "Egypt", "EGY", "EG", "CAF"),
    ("G", "Iran", "IRN", "IR", "AFC"),
    ("G", "New Zealand", "NZL", "NZ", "OFC"),

    ("H", "Spain", "ESP", "ES", "UEFA"),
    ("H", "Cape Verde", "CPV", "CV", "CAF"),
    ("H", "Saudi Arabia", "KSA", "SA", "AFC"),
    ("H", "Uruguay", "URU", "UY", "CONMEBOL"),

    ("I", "France", "FRA", "FR", "UEFA"),
    ("I", "Senegal", "SEN", "SN", "CAF"),
    ("I", "Iraq", "IRQ", "IQ", "AFC"),
    ("I", "Norway", "NOR", "NO", "UEFA"),

    ("J", "Argentina", "ARG", "AR", "CONMEBOL"),
    ("J", "Algeria", "ALG", "DZ", "CAF"),
    ("J", "Austria", "AUT", "AT", "UEFA"),
    ("J", "Jordan", "JOR", "JO", "AFC"),

    ("K", "Portugal", "POR", "PT", "UEFA"),
    ("K", "DR Congo", "COD", "CD", "CAF"),
    ("K", "Uzbekistan", "UZB", "UZ", "AFC"),
    ("K", "Colombia", "COL", "CO", "CONMEBOL"),

    ("L", "England", "ENG", "EN", "UEFA"),
    ("L", "Croatia", "CRO", "HR", "UEFA"),
    ("L", "Ghana", "GHA", "GH", "CAF"),
    ("L", "Panama", "PAN", "PA", "CONCACAF"),
]

GROUPS = sorted({row[0] for row in TEAMS_2026})
