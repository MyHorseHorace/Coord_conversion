"""
Convertisseur de coordonnées géodésiques — Québec / Global (NAD83 / WGS84)
===========================================================================
Systèmes supportés :
  • DMS  — Degrés, Minutes, Secondes          (NAD83)
  • DD   — Degrés Décimaux                    (NAD83)
  • MTM  — Transverse Mercator Modifiée        (NAD83, zones 2–12, Québec)
  • UTM  — Universal Transverse Mercator       (WGS84, zones 17–20 Nord, Québec)

Modes d'utilisation :
  1. Saisie interactive (menu console)
  2. Traitement par lot depuis un fichier CSV
       Format CSV attendu — séparateur virgule ou point-virgule, en-tête optionnel :

       DMS  →  sondage, longitude, latitude
                 ex : S-01, 73°34'08.000"W, 45°30'15.000"N

       DD   →  sondage, longitude, latitude
                 ex : S-01, -73.568889, 45.504167

       MTM  →  sondage, zone, easting, northing
                 ex : S-01, 8, 299590.123, 5040010.820

       UTM  →  sondage, zone, hemisphere, easting, northing
                 ex : S-01, 18, N, 611982.456, 5039496.123

Notes :
  - MTM utilise le datum NAD83 (EPSG:4617).
  - UTM utilise le datum WGS84 (EPSG:4326).
  - Pour le Québec, NAD83 ≈ WGS84 à mieux que 1 m ; les conversions
    inter-systèmes sont faites via pyproj qui gère le changement de datum.

Usage :
    python convertisseur_coords.py

Dépendances :
    pip install pyproj tabulate
"""

import csv
import os
import re
from pyproj import Transformer
from tabulate import tabulate

# ── Zones MTM — NAD83 (EPSG:32182–32192) ────────────────────────────────────

MTM_ZONES = {
    2:  {"epsg": 32182, "meridian": 55.5, "lon_min": 54.0, "lon_max": 57.0},
    3:  {"epsg": 32183, "meridian": 58.5, "lon_min": 57.0, "lon_max": 60.0},
    4:  {"epsg": 32184, "meridian": 61.5, "lon_min": 60.0, "lon_max": 63.0},
    5:  {"epsg": 32185, "meridian": 64.5, "lon_min": 63.0, "lon_max": 66.0},
    6:  {"epsg": 32186, "meridian": 67.5, "lon_min": 66.0, "lon_max": 69.0},
    7:  {"epsg": 32187, "meridian": 70.5, "lon_min": 69.0, "lon_max": 72.0},
    8:  {"epsg": 32188, "meridian": 73.5, "lon_min": 72.0, "lon_max": 75.0},
    9:  {"epsg": 32189, "meridian": 76.5, "lon_min": 75.0, "lon_max": 78.0},
   10:  {"epsg": 32190, "meridian": 79.5, "lon_min": 78.0, "lon_max": 81.0},
   11:  {"epsg": 32191, "meridian": 82.5, "lon_min": 81.0, "lon_max": 84.0},
   12:  {"epsg": 32192, "meridian": 85.5, "lon_min": 84.0, "lon_max": 87.0},
}

# ── Zones UTM Nord — WGS84 (EPSG:326xx) ─────────────────────────────────────
# Québec est couvert par les zones 17 à 21.

def _utm_epsg(zone: int, hemisphere: str = "N") -> int:
    """Retourne le code EPSG WGS84 UTM pour une zone et hémisphère donnés."""
    if hemisphere.upper() == "N":
        return 32600 + zone   # ex. zone 18N → EPSG:32618
    else:
        return 32700 + zone   # ex. zone 18S → EPSG:32718


def get_utm_zone(lon_dd: float) -> int:
    """Calcule le numéro de zone UTM à partir de la longitude (degrés décimaux)."""
    return int((lon_dd + 180) / 6) + 1


# ── Conversions DMS ↔ DD ─────────────────────────────────────────────────────

def dms_to_dd(d: float, m: float, s: float, hemi: str) -> float:
    """DMS → degrés décimaux. hemi : N / S / E / O / W"""
    hemi = hemi.upper().strip()
    if hemi not in ("N", "S", "E", "O", "W"):
        raise ValueError(f"Direction invalide : '{hemi}'. Utiliser N, S, E, O ou W.")
    dd = abs(d) + m / 60.0 + s / 3600.0
    return -dd if hemi in ("S", "O", "W") else dd


def dd_to_dms(dd: float, axis: str = "lat") -> tuple:
    """Degrés décimaux → (degrés, minutes, secondes, direction). axis : 'lat' ou 'lon'"""
    hemi = ("N" if dd >= 0 else "S") if axis == "lat" else ("E" if dd >= 0 else "O")
    val = abs(dd)
    d = int(val)
    m_f = (val - d) * 60
    m = int(m_f)
    s = round((m_f - m) * 60, 6)
    if s >= 60.0:
        s, m = 0.0, m + 1
    if m >= 60:
        m, d = 0, d + 1
    return d, m, s, hemi


# ── Conversions DD ↔ MTM ─────────────────────────────────────────────────────

def get_mtm_zone(lon_dd: float) -> int:
    """Détecte automatiquement la zone MTM selon la longitude."""
    lon_abs = abs(lon_dd)
    for zone, p in MTM_ZONES.items():
        if p["lon_min"] <= lon_abs < p["lon_max"]:
            return zone
    raise ValueError(
        f"Longitude {lon_abs:.4f}° O hors couverture MTM (54°–87° O).\n"
        "  Vérifiez votre coordonnée ou entrez les coordonnées en UTM."
    )


def dd_to_mtm(lat_dd: float, lon_dd: float, zone: int = None) -> dict:
    """DD (NAD83) → MTM. Zone auto-détectée si non fournie."""
    if zone is None:
        zone = get_mtm_zone(lon_dd)
    if zone not in MTM_ZONES:
        raise ValueError(f"Zone MTM-{zone} inconnue. Valides : {list(MTM_ZONES)}")
    p = MTM_ZONES[zone]
    t = Transformer.from_crs("EPSG:4617", f"EPSG:{p['epsg']}", always_xy=True)
    e, n = t.transform(lon_dd, lat_dd)
    return {"mtm_easting": e, "mtm_northing": n,
            "mtm_zone": zone, "mtm_epsg": p["epsg"], "mtm_meridian": p["meridian"]}


def mtm_to_dd(easting: float, northing: float, zone: int) -> tuple:
    """MTM (NAD83) → (lat_dd, lon_dd)."""
    if zone not in MTM_ZONES:
        raise ValueError(f"Zone MTM-{zone} inconnue. Valides : {list(MTM_ZONES)}")
    p = MTM_ZONES[zone]
    t = Transformer.from_crs(f"EPSG:{p['epsg']}", "EPSG:4617", always_xy=True)
    lon_dd, lat_dd = t.transform(easting, northing)
    return lat_dd, lon_dd


# ── Conversions DD ↔ UTM ─────────────────────────────────────────────────────

def dd_to_utm(lat_dd: float, lon_dd: float, zone: int = None,
              hemisphere: str = "N") -> dict:
    """DD (WGS84) → UTM. Zone auto-détectée si non fournie."""
    if zone is None:
        zone = get_utm_zone(lon_dd)
    epsg = _utm_epsg(zone, hemisphere)
    t = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    e, n = t.transform(lon_dd, lat_dd)
    meridian = -183 + zone * 6  # méridien central UTM
    return {"utm_easting": e, "utm_northing": n,
            "utm_zone": zone, "utm_hemisphere": hemisphere.upper(),
            "utm_epsg": epsg, "utm_meridian": abs(meridian)}


def utm_to_dd(easting: float, northing: float, zone: int,
              hemisphere: str = "N") -> tuple:
    """UTM (WGS84) → (lat_dd, lon_dd)."""
    epsg = _utm_epsg(zone, hemisphere)
    t = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
    lon_dd, lat_dd = t.transform(easting, northing)
    return lat_dd, lon_dd


# ── Calcul centralisé de tous les systèmes ───────────────────────────────────

def all_from_dd(lat_dd: float, lon_dd: float,
                mtm_zone: int = None, utm_zone: int = None,
                utm_hemi: str = "N") -> dict:
    """
    Calcule DMS, MTM et UTM à partir de degrés décimaux (NAD83 ≈ WGS84).
    Retourne un dict unifié avec toutes les représentations.
    """
    lat_dms = dd_to_dms(lat_dd, "lat")
    lon_dms = dd_to_dms(lon_dd, "lon")

    # MTM — peut échouer si hors couverture
    try:
        mtm = dd_to_mtm(lat_dd, lon_dd, mtm_zone)
        mtm_ok = True
    except ValueError as e:
        mtm = {"mtm_error": str(e)}
        mtm_ok = False

    # UTM — détection automatique si zone non fournie
    if utm_zone is None:
        utm_zone = get_utm_zone(lon_dd)
    utm = dd_to_utm(lat_dd, lon_dd, utm_zone, utm_hemi)

    return {
        "lat_dd": lat_dd, "lon_dd": lon_dd,
        "lat_dms": lat_dms, "lon_dms": lon_dms,
        "mtm_ok": mtm_ok,
        **mtm,
        **utm,
    }


# ── Affichage ────────────────────────────────────────────────────────────────

W = 54  # largeur intérieure de la boîte

def _box(title: str, lines: list):
    print("\n┌" + "─" * W + "┐")
    print(f"│  {title:<{W-2}}│")
    print("├" + "─" * W + "┤")
    for line in lines:
        if line == "---":
            print("│  " + "·" * (W - 2) + "  │")
        else:
            print(f"│  {line:<{W-2}}│")
    print("└" + "─" * W + "┘")


def print_all(r: dict):
    ld, lm, ls, lh = r["lat_dms"]
    od, om, os_, oh = r["lon_dms"]

    lines = [
        "── Degrés, Minutes, Secondes (DMS) ────────────────",
        f"  Latitude  :  {ld:3d}° {lm:02d}' {ls:06.3f}\"  {lh}",
        f"  Longitude :  {od:3d}° {om:02d}' {os_:06.3f}\"  {oh}",
        "",
        "── Degrés Décimaux (DD) ────────────────────────────",
        f"  Latitude  :  {r['lat_dd']:>16.8f} °",
        f"  Longitude :  {r['lon_dd']:>16.8f} °",
        "",
    ]

    if r["mtm_ok"]:
        lines += [
            "── MTM  (NAD83) ────────────────────────────────────",
            f"  Zone      :  MTM-{r['mtm_zone']}  (EPSG:{r['mtm_epsg']})",
            f"  Méridien  :  {r['mtm_meridian']}° O",
            f"  Est       :  {r['mtm_easting']:>16.3f} m",
            f"  Nord      :  {r['mtm_northing']:>16.3f} m",
            "",
        ]
    else:
        lines += [
            "── MTM  (NAD83) ────────────────────────────────────",
            f"  ⚠  {r.get('mtm_error','Hors couverture MTM')[:48]}",
            "",
        ]

    lines += [
        "── UTM  (WGS84) ────────────────────────────────────",
        f"  Zone      :  {r['utm_zone']}{r['utm_hemisphere']}  (EPSG:{r['utm_epsg']})",
        f"  Méridien  :  {r['utm_meridian']}° O",
        f"  Est       :  {r['utm_easting']:>16.3f} m",
        f"  Nord      :  {r['utm_northing']:>16.3f} m",
    ]

    _box("Résultats de la conversion", lines)


# ── Saisie console ────────────────────────────────────────────────────────────

def _ask(prompt: str, typ=str, validator=None):
    while True:
        try:
            val = typ(input(f"  {prompt} : ").strip())
            if validator and not validator(val):
                raise ValueError
            return val
        except (ValueError, TypeError):
            print("  ⚠  Valeur invalide, veuillez réessayer.")


def _ask_hemi(prompt: str, choices: tuple) -> str:
    s = "/".join(choices)
    while True:
        v = input(f"  {prompt} ({s}) : ").strip().upper()
        if v in choices:
            return v
        print(f"  ⚠  Entrez l'une des options : {s}")


def input_dms() -> dict:
    print("\n  ── Latitude ──")
    lat_d = _ask("Degrés   (ex: 45)",   int,   lambda x: 0 <= x <= 90)
    lat_m = _ask("Minutes  (ex: 30)",   int,   lambda x: 0 <= x < 60)
    lat_s = _ask("Secondes (ex: 0.0)",  float, lambda x: 0 <= x < 60)
    lat_h = _ask_hemi("Hémisphère", ("N", "S"))
    print("  ── Longitude ──")
    lon_d = _ask("Degrés   (ex: 73)",   int,   lambda x: 0 <= x <= 180)
    lon_m = _ask("Minutes  (ex: 34)",   int,   lambda x: 0 <= x < 60)
    lon_s = _ask("Secondes (ex: 0.0)",  float, lambda x: 0 <= x < 60)
    lon_h = _ask_hemi("Hémisphère", ("E", "W"))
    lat_dd = dms_to_dd(lat_d, lat_m, lat_s, lat_h)
    lon_dd = dms_to_dd(lon_d, lon_m, lon_s, lon_h)
    return all_from_dd(lat_dd, lon_dd)


def input_dd() -> dict:
    print("\n  Latitude : positive = Nord, négative = Sud.")
    print("  Longitude : négative = Ouest  (ex: -73.567).")
    lat_dd = _ask("Latitude  DD", float, lambda x: -90  <= x <= 90)
    lon_dd = _ask("Longitude DD", float, lambda x: -180 <= x <= 180)
    return all_from_dd(lat_dd, lon_dd)


def input_mtm() -> dict:
    zones_str = ", ".join(str(z) for z in MTM_ZONES)
    print(f"\n  Zones disponibles : {zones_str}")
    zone     = _ask("Zone MTM",  int,   lambda x: x in MTM_ZONES)
    easting  = _ask("Est  (m)  (ex: 299590)",  float)
    northing = _ask("Nord (m)  (ex: 5040011)", float)
    lat_dd, lon_dd = mtm_to_dd(easting, northing, zone)
    r = all_from_dd(lat_dd, lon_dd, mtm_zone=zone)
    # Conserver les MTM saisis tels quels (évite arrondi aller-retour)
    r["mtm_easting"]  = easting
    r["mtm_northing"] = northing
    return r


def input_utm() -> dict:
    print("\n  Zones UTM couvrant le Québec : 17, 18, 19, 20, 21.")
    print("  Hémisphère Nord (N) dans la quasi-totalité des cas.")
    zone  = _ask("Zone UTM  (ex: 18)",  int,   lambda x: 1 <= x <= 60)
    hemi  = _ask_hemi("Hémisphère", ("N", "S"))
    east  = _ask("Est  (m)  (ex: 607000)", float)
    north = _ask("Nord (m)  (ex: 5040000)", float)
    lat_dd, lon_dd = utm_to_dd(east, north, zone, hemi)
    r = all_from_dd(lat_dd, lon_dd, utm_zone=zone, utm_hemi=hemi)
    # Conserver les UTM saisis tels quels
    r["utm_easting"]  = east
    r["utm_northing"] = north
    return r


# ── Menu principal ────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════════════════════════════════════════╗
║         Convertisseur de coordonnées géodésiques — Québec / Global      ║
║              DMS  ↔  DD  ↔  MTM (NAD83)  ↔  UTM (WGS84)               ║
╠═══╦══════════════════════════════════════════════════════════════════════╣
║ 1 ║  DMS — Degrés, Minutes, Secondes                  (datum : NAD83)  ║
║   ║    Latitude  :  45° 30' 15.000"  N   ou  S                        ║
║   ║    Longitude :  73° 34' 08.000"  W   ou  E                        ║
╠═══╬══════════════════════════════════════════════════════════════════════╣
║ 2 ║  DD  — Degrés Décimaux                            (datum : NAD83)  ║
║   ║    Latitude  :   45.504167        (+ = Nord,  – = Sud)            ║
║   ║    Longitude :  –73.568889        (+ = Est,   – = Ouest)          ║
╠═══╬══════════════════════════════════════════════════════════════════════╣
║ 3 ║  MTM — Transverse Mercator Modifiée, zones 2–12   (datum : NAD83)  ║
║   ║    Zone      :  8        (méridien central : 73.5° O)             ║
║   ║    Est       :  299 590  m   (faux-est : 304 800 m, k₀ = 0.9999) ║
║   ║    Nord      :  5 040 011 m  (depuis l'équateur)                  ║
╠═══╬══════════════════════════════════════════════════════════════════════╣
║ 4 ║  UTM — Universal Transverse Mercator, zones 17–21 (datum : WGS84)  ║
║   ║    Zone      :  18N      (méridien central : 75° O)               ║
║   ║    Est       :  611 982  m   (faux-est : 500 000 m, k₀ = 0.9996) ║
║   ║    Nord      :  5 039 496 m  (depuis l'équateur, hémisphère N)    ║
╠═══╩══════════════════════════════════════════════════════════════════════╣
║ 5 ║  CSV — Traitement par lot depuis un fichier                         ║
║   ║    DMS : sondage, longitude, latitude                               ║
║   ║          ex : S-01, 73°34'08.000"W, 45°30'15.000"N                 ║
║   ║    DD  : sondage, longitude, latitude                               ║
║   ║          ex : S-01, -73.568889, 45.504167                          ║
║   ║    MTM : sondage, zone, easting, northing                           ║
║   ║          ex : S-01, 8, 299590.123, 5040010.820                     ║
║   ║    UTM : sondage, zone, hémisphère, easting, northing               ║
║   ║          ex : S-01, 18, N, 611982.456, 5039496.123                 ║
╠═══╩══════════════════════════════════════════════════════════════════════╣
║  0   Quitter                                                            ║
╚══════════════════════════════════════════════════════════════════════════╝"""

HANDLERS = {
    "1": input_dms,
    "2": input_dd,
    "3": input_mtm,
    "4": input_utm,
}


# ── Traitement par lot — CSV ──────────────────────────────────────────────────

def _parse_dms_string(s: str) -> tuple:
    """
    Analyse une chaîne DMS de la forme  73°34'08.000"W  ou  45°30'15"N.
    Retourne (degrés, minutes, secondes, hémisphère).
    Formats acceptés :
      • 73°34'08.000"W
      • 73° 34' 08.000" W
      • 73d34m08.000sW   (variante avec lettres)
    """
    s = s.strip()
    # Remplacer les variantes de symboles
    s = s.replace("°", "°").replace("'", "'").replace("′", "'") \
         .replace('"', '"').replace("″", '"').replace("''", '"')
    # Regex générale : D° M' S" H
    m = re.match(
        r"""(\d+(?:\.\d+)?)\s*[°d]\s*   # degrés
            (\d+(?:\.\d+)?)\s*[\'m]\s*  # minutes
            (\d+(?:\.\d+)?)\s*[\"s]?\s* # secondes (symbole optionnel)
            ([NSEWOnsewо])               # hémisphère""",
        s, re.VERBOSE | re.IGNORECASE
    )
    if not m:
        raise ValueError(f"Format DMS non reconnu : '{s}'\n"
                         "  Exemple attendu : 73°34'08.000\"W")
    d, mn, sc, h = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4).upper()
    if h == "O":
        h = "W"
    return d, mn, sc, h


def _detect_separator(line: str) -> str:
    """Détecte le séparateur CSV (virgule ou point-virgule)."""
    return ";" if line.count(";") >= line.count(",") else ","


def _is_header(fields: list) -> bool:
    """Retourne True si la ligne ressemble à un en-tête (champ non numérique)."""
    for f in fields[1:]:
        try:
            float(f.strip().replace(",", "."))
        except ValueError:
            # Si ce n'est pas un nombre et pas un DMS, c'est un en-tête
            try:
                _parse_dms_string(f.strip())
            except ValueError:
                return True
    return False


def _fmt_dms(lat_dd: float, lon_dd: float) -> tuple:
    """Formate lat et lon en chaînes DMS lisibles."""
    ld, lm, ls, lh = dd_to_dms(lat_dd, "lat")
    od, om, os_, oh = dd_to_dms(lon_dd, "lon")
    # dd_to_dms retourne "O" pour ouest — on utilise "W" par convention
    oh = "W" if oh == "O" else oh
    lat_s = f"{ld}°{lm:02d}'{ls:06.3f}\"{lh}"
    lon_s = f"{od}°{om:02d}'{os_:06.3f}\"{oh}"
    return lat_s, lon_s


def process_csv(filepath: str, sys: str,
                mtm_zone: int = None, utm_zone: int = None,
                utm_hemi: str = "N") -> None:
    """
    Lit un CSV, convertit chaque ligne et affiche un tableau de résultats.
    Exporte aussi le résultat dans un fichier CSV de sortie.

    Paramètres
    ----------
    filepath : chemin du fichier CSV
    sys      : système d'entrée — 'DMS', 'DD', 'MTM' ou 'UTM'
    mtm_zone : zone MTM forcée (MTM en entrée seulement)
    utm_zone : zone UTM forcée (UTM en entrée seulement)
    utm_hemi : hémisphère UTM en entrée ('N' ou 'S')
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Fichier introuvable : '{filepath}'")

    rows_ok   = []   # lignes converties avec succès
    rows_err  = []   # lignes en erreur

    with open(filepath, newline="", encoding="utf-8-sig") as f:
        raw_lines = [l for l in f if l.strip()]

    if not raw_lines:
        raise ValueError("Le fichier CSV est vide.")

    sep = _detect_separator(raw_lines[0])

    # Ignorer l'en-tête si présent
    reader = csv.reader(raw_lines, delimiter=sep)
    all_rows = list(reader)
    start = 1 if _is_header(all_rows[0]) else 0
    data_rows = all_rows[start:]

    if not data_rows:
        raise ValueError("Aucune donnée trouvée après l'en-tête.")

    for i, fields in enumerate(data_rows, start=start + 1):
        fields = [f.strip() for f in fields]
        try:
            sondage = fields[0]

            # ── Parsing selon le système ──────────────────────────────────
            if sys == "DMS":
                # Colonnes : sondage, longitude, latitude
                if len(fields) < 3:
                    raise ValueError("3 colonnes attendues : sondage, longitude, latitude")
                lon_d, lon_m, lon_s, lon_h = _parse_dms_string(fields[1])
                lat_d, lat_m, lat_s, lat_h = _parse_dms_string(fields[2])
                lat_dd = dms_to_dd(lat_d, lat_m, lat_s, lat_h)
                lon_dd = dms_to_dd(lon_d, lon_m, lon_s, lon_h)
                orig_lat = fields[2]
                orig_lon = fields[1]

            elif sys == "DD":
                # Colonnes : sondage, longitude, latitude
                if len(fields) < 3:
                    raise ValueError("3 colonnes attendues : sondage, longitude, latitude")
                lon_dd = float(fields[1])
                lat_dd = float(fields[2])
                orig_lat = f"{lat_dd:.8f} °"
                orig_lon = f"{lon_dd:.8f} °"

            elif sys == "MTM":
                # Colonnes : sondage, zone, easting, northing
                if len(fields) < 4:
                    raise ValueError("4 colonnes attendues : sondage, zone, easting, northing")
                zone_in  = int(fields[1])
                east_in  = float(fields[2])
                north_in = float(fields[3])
                lat_dd, lon_dd = mtm_to_dd(east_in, north_in, zone_in)
                orig_lat = f"{north_in:.3f} m N"
                orig_lon = f"{east_in:.3f} m E  (MTM-{zone_in})"
                mtm_zone = zone_in   # conserver pour l'affichage

            elif sys == "UTM":
                # Colonnes : sondage, zone, hemisphere, easting, northing
                if len(fields) < 5:
                    raise ValueError("5 colonnes attendues : sondage, zone, hémisphère, easting, northing")
                zone_in  = int(fields[1])
                hemi_in  = fields[2].upper()
                east_in  = float(fields[3])
                north_in = float(fields[4])
                lat_dd, lon_dd = utm_to_dd(east_in, north_in, zone_in, hemi_in)
                orig_lat = f"{north_in:.3f} m N"
                orig_lon = f"{east_in:.3f} m E  (UTM-{zone_in}{hemi_in})"
                utm_zone = zone_in
                utm_hemi = hemi_in

            else:
                raise ValueError(f"Système inconnu : '{sys}'")

            # ── Conversion vers tous les systèmes ─────────────────────────
            r = all_from_dd(lat_dd, lon_dd,
                            mtm_zone=mtm_zone if sys in ("DMS","DD","MTM") else None,
                            utm_zone=utm_zone if sys in ("DMS","DD","UTM") else None,
                            utm_hemi=utm_hemi)

            # ── Construction de la ligne de résultat ──────────────────────
            dms_lat, dms_lon = _fmt_dms(lat_dd, lon_dd)

            mtm_e = f"{r['mtm_easting']:>14.3f} m"  if r["mtm_ok"] else "—"
            mtm_n = f"{r['mtm_northing']:>14.3f} m"  if r["mtm_ok"] else "—"
            mtm_z = f"MTM-{r['mtm_zone']}"            if r["mtm_ok"] else "hors zone"

            rows_ok.append({
                "Sondage":     sondage,
                # Système d'origine
                "Orig. Lat.":  orig_lat,
                "Orig. Lon.":  orig_lon,
                # DMS
                "DMS Lat.":    dms_lat,
                "DMS Lon.":    dms_lon,
                # DD
                "DD Lat. (°)": f"{lat_dd:.8f}",
                "DD Lon. (°)": f"{lon_dd:.8f}",
                # MTM
                "MTM Zone":    mtm_z,
                "MTM Est (m)": mtm_e,
                "MTM Nord (m)":mtm_n,
                # UTM
                "UTM Zone":    f"{r['utm_zone']}{r['utm_hemisphere']}",
                "UTM Est (m)": f"{r['utm_easting']:>14.3f} m",
                "UTM Nord (m)":f"{r['utm_northing']:>14.3f} m",
            })

        except Exception as e:
            rows_err.append({"Ligne": i, "Sondage": fields[0] if fields else "?",
                             "Erreur": str(e)})

    # ── Affichage console ─────────────────────────────────────────────────
    print(f"\n  Fichier : {filepath}")
    print(f"  Système d'entrée : {sys}  |  {len(rows_ok)} succès, {len(rows_err)} erreur(s)\n")

    if rows_ok:
        # Afficher en deux blocs pour éviter un tableau trop large en console
        keys_orig = ["Sondage", "Orig. Lat.", "Orig. Lon."]
        keys_dms  = ["Sondage", "DMS Lat.", "DMS Lon."]
        keys_dd   = ["Sondage", "DD Lat. (°)", "DD Lon. (°)"]
        keys_mtm  = ["Sondage", "MTM Zone", "MTM Est (m)", "MTM Nord (m)"]
        keys_utm  = ["Sondage", "UTM Zone", "UTM Est (m)", "UTM Nord (m)"]

        def sub(keys):
            return [{k: row[k] for k in keys} for row in rows_ok]

        # colalign="left" force le traitement comme chaînes → évite la notation scientifique
        def show(title, keys):
            print(f"\n  ── {title} ──")
            print(tabulate(sub(keys), headers="keys", tablefmt="rounded_outline",
                           colalign=("left",) * len(keys)))

        if sys != "DMS":
            show("Coordonnées d'origine", keys_orig)
            show("DMS", keys_dms)
        else:
            show("DMS (origine)", keys_dms)
        if sys != "DD":
            show("Degrés Décimaux", keys_dd)
        if sys != "MTM":
            show("MTM (NAD83)", keys_mtm)
        if sys != "UTM":
            show("UTM (WGS84)", keys_utm)

    if rows_err:
        print("\n  ── Erreurs ──")
        print(tabulate(rows_err, headers="keys", tablefmt="rounded_outline"))

    # ── Export CSV de sortie ──────────────────────────────────────────────
    if rows_ok:
        base, ext = os.path.splitext(filepath)
        out_path  = base + "_converti.csv"
        fieldnames = list(rows_ok[0].keys())
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_ok)
        print(f"\n  ✓ Résultats exportés → {out_path}")


def input_csv() -> None:
    """Dialogue console pour le traitement par lot CSV."""
    print("\n  ── Traitement par lot — CSV ──────────────────────────────")
    print("  Format des colonnes selon le système choisi :")
    print("    DMS : sondage, longitude, latitude")
    print("          ex: S-01, 73°34'08.000\"W, 45°30'15.000\"N")
    print("    DD  : sondage, longitude, latitude")
    print("          ex: S-01, -73.568889, 45.504167")
    print("    MTM : sondage, zone, easting, northing")
    print("          ex: S-01, 8, 299590.123, 5040010.820")
    print("    UTM : sondage, zone, hemisphere, easting, northing")
    print("          ex: S-01, 18, N, 611982.456, 5039496.123")
    print()

    filepath = input("  Chemin du fichier CSV : ").strip().strip('"').strip("'")

    sys_map = {"1": "DMS", "2": "DD", "3": "MTM", "4": "UTM"}
    print("  Système d'entrée :  1=DMS  2=DD  3=MTM  4=UTM")
    while True:
        choix = input("  Choix : ").strip()
        if choix in sys_map:
            sys = sys_map[choix]
            break
        print("  ⚠  Entrez 1, 2, 3 ou 4.")

    # Paramètres supplémentaires pour MTM/UTM
    mtm_zone = utm_zone = None
    utm_hemi = "N"

    try:
        process_csv(filepath, sys, mtm_zone, utm_zone, utm_hemi)
    except (FileNotFoundError, ValueError) as e:
        print(f"\n  ✖ Erreur : {e}")


# ── Menu principal ─────────────────────────────────────────────────────────────

def main():
    while True:
        print(MENU)
        choix = input("  Choix : ").strip()
        if choix == "0":
            print("\n  Au revoir.\n")
            break
        elif choix in HANDLERS:
            try:
                r = HANDLERS[choix]()
                print_all(r)
            except ValueError as e:
                print(f"\n  ✖ Erreur : {e}")
        elif choix == "5":
            input_csv()
        else:
            print("  ⚠  Option invalide.")
        input("\n  Appuyer sur Entrée pour continuer...")


if __name__ == "__main__":
    main()
