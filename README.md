# CoordQC — Geodetic Coordinate Converter

A lightweight Progressive Web App (PWA) for converting geodetic coordinates between four systems used in Quebec and globally. Works offline and can be installed on Android and iOS directly from the browser — no app store required.

---

## Purpose

Fieldwork, geotechnical reporting, and GIS work in Quebec routinely involves switching between coordinate systems across different datums and projections. CoordQC centralizes these conversions in a single mobile-friendly tool:

| System | Full Name | Datum | Coverage |
|--------|-----------|-------|----------|
| **DMS** | Degrees, Minutes, Seconds | NAD83 | Global |
| **DD** | Decimal Degrees | NAD83 | Global |
| **MTM** | Modified Transverse Mercator | NAD83 | Quebec (zones 2–12) |
| **UTM** | Universal Transverse Mercator | WGS84 | Global (zones 1–60) |

> **Note on datums:** NAD83 and WGS84 differ by less than 1 metre in Quebec. CoordQC handles the datum transformation automatically via [proj4js](https://proj4js.org/).

---

## How It Works

CoordQC uses **proj4js** — the JavaScript port of the PROJ cartographic projection library — to perform all coordinate transformations client-side. No data is ever sent to a server.

**Zone detection is automatic:** when entering DMS, DD, or UTM coordinates, CoordQC determines the correct MTM zone (2–12) and UTM zone from the longitude. Zone selection is only required when entering MTM or UTM coordinates directly.

**MTM projection parameters (NAD83):**
- Scale factor k₀ = 0.9999
- False easting = 304 800 m
- Zone width = 3°
- EPSG codes: 32182 (zone 2) through 32192 (zone 12)

**UTM projection parameters (WGS84):**
- Scale factor k₀ = 0.9996
- False easting = 500 000 m
- Zone width = 6°
- EPSG codes: 32601–32660 (North), 32701–32760 (South)

---

## Usage

Enter coordinates in any one of the four systems. The app immediately outputs all other representations simultaneously.

### Input systems

**DMS — Degrees, Minutes, Seconds**
```
Latitude  :  45° 30′ 15.000″  N  or  S
Longitude :  73° 34′ 08.000″  W  or  E
```

**DD — Decimal Degrees**
```
Latitude  :   45.504167   (positive = North, negative = South)
Longitude :  −73.568889   (positive = East,  negative = West)
```

**MTM — Modified Transverse Mercator**
```
Zone      :  8            (central meridian: 73.5° W)
Easting   :  299 590 m   (false easting: 304 800 m)
Northing  :  5 040 011 m (from the equator)
```

**UTM — Universal Transverse Mercator**
```
Zone      :  18N          (central meridian: 75° W)
Easting   :  611 982 m   (false easting: 500 000 m)
Northing  :  5 039 496 m (from the equator, northern hemisphere)
```

### Output

Every conversion produces all four systems at once. A **Copy all results** button formats and copies the full output to the clipboard for pasting into reports or GIS software.

If the input coordinates fall outside the MTM coverage area (54°–87° W), a warning is displayed in the MTM result block while DD, DMS, and UTM are still computed normally.

---

## Installation

CoordQC is a PWA — it installs directly from the browser without going through an app store.

### Android (Chrome)

1. Open the app URL in **Chrome**
2. A banner reading **"Install CoordQC"** will appear at the bottom of the screen
3. Tap **Install** and confirm
4. The app icon appears on your home screen and opens full-screen, without the browser UI

The app caches all its resources on first load and works fully **offline** afterwards.

### iOS (Safari)

Apple does not support the automatic install banner. The manual steps are:

1. Open the app URL in **Safari** (Chrome and Firefox do not support PWA installation on iOS)
2. Tap the **Share** button (square with an arrow, at the bottom of the screen)
3. Scroll down and tap **"Add to Home Screen"**
4. Confirm the name and tap **Add**

The app will open full-screen from your home screen and works offline.

### Desktop (Chrome / Edge)

An install icon (⊕) appears in the address bar. Click it to install CoordQC as a desktop app.

---

## Files

| File | Description |
|------|-------------|
| `index.html` | Main application — all UI and conversion logic |
| `manifest.json` | PWA manifest (name, icons, display mode) |
| `sw.js` | Service worker — enables offline use |
| `icon-192.png` | App icon 192×192 px |
| `icon-512.png` | App icon 512×512 px |

---

## Dependencies

- [proj4js](https://cdnjs.cloudflare.com/ajax/libs/proj4js/2.9.0/proj4.js) — loaded from CDN, cached offline after first visit
- [Sora](https://fonts.google.com/specimen/Sora) + [DM Mono](https://fonts.google.com/specimen/DM+Mono) — Google Fonts, cached offline after first visit

No build tools, no frameworks, no package manager. The app is a single HTML file with two companion PWA files.

---

## License

MIT License — free to use, modify, and distribute.
