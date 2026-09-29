# Compress PDF v3 — Design

Status: **approved** (2026-09-29)

## Goal

A small, dependable GNOME/KDE app that shrinks PDFs so they fit upload limits on
portals. It should never crash, never make a file bigger, never overwrite
anything silently, and always say what went wrong.

Non-goals for v3.0: editing PDFs, merging/splitting, OCR, password removal,
the "make it smaller than N MB" mode (planned for v3.1).

## Decisions

| Topic | Decision |
|---|---|
| Language / toolkit | Python 3.11+, PyGObject, GTK 4.14+, libadwaita 1.5+ |
| Compression engine | Ghostscript, run as a separate process (`gs`) |
| App ID | `com.itsfoss.CompressPDF` |
| Name | Compress PDF |
| Distribution | Flatpak (GNOME 49 runtime, Ghostscript bundled) and a native `.deb` (`Architecture: all`). AppImage dropped. |
| Save location | Asked every time via the system file dialog (portal) |
| Branding | It's FOSS credit, website and links in the About dialog only |
| License | GPL-3.0-or-later (code), CC-BY-SA-4.0 (icon and screenshots) |
| Old code | Tagged `legacy-v2`, replaced on master |

### License reasoning

- GTK, libadwaita, PyGObject: LGPL-2.1-or-later. Fine with any license.
- Ghostscript: AGPL-3.0. We only run it as a separate program and never link to
  it, so its license does not extend to our code. When bundled in the Flatpak,
  the manifest builds it from its official source tarball, which meets the
  source-offer requirement.
- GPL-3.0-or-later keeps the existing license, is the norm for GNOME apps, is
  compatible with AGPL-3.0 (GPLv3 section 13), and Flathub accepts it.
- Every source file gets an `SPDX-License-Identifier` header. The `LICENSE` file
  becomes the unmodified GPL-3.0 text.

## User experience

One window, no modal pop-ups for normal flow.

```
┌ Compress PDF ───────────────────────────── [≡] ┐
│                                                  │
│   1. Empty state (AdwStatusPage)                 │
│      "Drop PDF files here"                       │
│      [ Select Files… ]                           │
│                                                  │
│   2. Files added                                 │
│      ┌ Files ─────────────────────────────────┐  │
│      │ report.pdf        6.1 MB           [×] │  │
│      │ scan.pdf          1.0 MB           [×] │  │
│      │ [+ Add more]                           │  │
│      └────────────────────────────────────────┘  │
│      ┌ Compression ───────────────────────────┐  │
│      │ ○ High quality    for printing         │  │
│      │ ● Balanced        good for email       │  │
│      │ ○ Small           for upload portals   │  │
│      │ ○ Smallest        lowest image quality │  │
│      └────────────────────────────────────────┘  │
│                              [ Compress ]        │
│                                                  │
│   3. Compressing: per-row progress bar,          │
│      "Page 12 of 47", [Cancel]                   │
│                                                  │
│   4. Done: per row                               │
│      report.pdf   6.1 MB → 1.1 MB  −82%  [Open]  │
│      scan.pdf     Already optimised, not saved   │
│      Toast: "2 files compressed" [Show in folder]│
└──────────────────────────────────────────────────┘
```

Flow details:

- **Adding files:** Select Files button (multi-select, PDF filter), drag and
  drop anywhere in the window, or "Open With → Compress PDF" from Files/Dolphin
  (the `.desktop` file declares `application/pdf`). Duplicates are ignored.
- **Save location:** after pressing Compress:
  - one file → save dialog pre-filled with `<name>-compressed.pdf`; the dialog
    itself asks before overwriting;
  - several files → folder dialog; each output is `<name>-compressed.pdf`, and
    if that exists, `<name>-compressed-2.pdf` and so on. Nothing is overwritten.
- **Never bigger:** each file is compressed to a temporary file first. If the
  result is not at least 5% smaller than the original, nothing is written and
  the row says "Already optimised". Otherwise it is copied to the destination.
- **To Compress / Done:** only files in "To Compress" are ever compressed.
  When a run ends, processed files (compressed, already optimised or failed)
  move to a "Done" section with their result and an Open button; cancelled
  or unstarted files stay queued. Adding a finished file again moves it back
  to "To Compress", so redoing a file is always an explicit choice. "Clear"
  empties the Done section.
- **Cancel:** stops Ghostscript, deletes temp files, and keeps finished files.
- **Settings remembered (GSettings):** last level and window size.
- **Errors, shown in the file's row with a plain explanation:**
  password-protected, not a PDF / damaged, disk full / no permission,
  Ghostscript missing (`.deb` only).
- **Adaptive:** usable at narrow widths (AdwBreakpoint), keyboard navigable,
  labels for screen readers.

## Compression levels

Downsampling by dpi alone is not enough. Benchmarks on real files
(Ghostscript 10.06):

| Sample | Size | 300 dpi | 150 dpi | 100 dpi | 72 dpi |
|---|---|---|---|---|---|
| Phone scan, 1 page | 913 KB | −42% | −71% | −85% | −92% |
| 7-page scan, 200 ppi JPEG | 5.9 MB | 0% | −57% | −82% | −88% |
| Office scanner, 1 page, 300 ppi | 1.0 MB | 0% | −90% | −94% | −96% |
| 47-page JPEG 2000 photos on large pages | 43 MB | −49% | −49% | −49% | −49% |

The last file already sits at 72 ppi because its pages are oversized, so dpi
changes nothing. Ghostscript also copies JPEG and JPEG 2000 images through
unchanged by default. Turning copy-through off and controlling JPEG quality
fixes it (first 3 pages: 3.0 MB → 2.4 / 1.4 / 0.9 MB at quality factor
0.4 / 0.76 / 1.3).

So each level sets both image resolution and JPEG quality:

| Level | Colour/grey dpi | Mono dpi | JPEG QFactor | Passthrough |
|---|---|---|---|---|
| High quality | 200 | 600 | 0.4 | off |
| Balanced (default) | 150 | 300 | 0.76 | off |
| Small | 100 | 200 | 1.0 | off |
| Smallest | 72 | 150 | 1.3 | off |

Common flags: `-dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite
-dCompatibilityLevel=1.5 -dDetectDuplicateImages=true
-dDownsample*Images=true -d*ImageDownsampleThreshold=1.0`, fonts subset and
embedded. The numbers are starting points. They will be tuned against the test
set with a benchmark script, which stays in the repo; the sample files do not.

Validated in stage 2 (`tools/bench.py`, plus a synthetic 300 dpi scan with
7 pt and 9 pt text rendered at each level): High Quality and Balanced look the
same as the original, Small softens slightly with 7 pt text still readable,
Smallest blurs 7 pt text and bands photos but stays legible.

Also passed to Ghostscript: `-dAutoRotatePages=/None` (keep scanned pages the
way they were), `-dPassThroughJPEGImages=false -dPassThroughJPXImages=false`.

Safety rules found while testing Ghostscript 10.06:

- A password-protected PDF makes Ghostscript **exit 0** and write an empty
  PDF. Success is therefore "exit 0 **and** at least one page processed
  **and** a non-empty output", never the exit code alone.
- A non-PDF file is run as a PostScript program. The app checks for a
  `%PDF-` header in the first 1 KiB and never hands anything else to
  Ghostscript.
- `%` in the output name is a page-number template; it is escaped.

### Ubuntu's AppArmor profile for Ghostscript (native `.deb` only)

Ubuntu 25.10+ ships `/etc/apparmor.d/gs` in enforce mode. The Flatpak is not
affected (its gs lives in `/app/bin`). Two consequences, both handled:

- **No process may signal gs**, not even its parent: `kill` returns EACCES,
  so `Gio.Subprocess.force_exit()` silently does nothing. Cancel therefore
  also closes our end of gs's stdout; gs dies of SIGPIPE when it reports its
  next page (measured 0.36 s instead of 17 s on a 47-page file).
- **gs may only open `*.pdf` (and a few other extensions) under `$HOME`,
  `/tmp`, `/mnt` and `/media`.** Files on network shares
  (`/run/user/UID/gvfs/…`), in `/dev/shm`, or without a `.pdf` extension fail
  with `undefinedfilename`. When that happens and the app itself can read the
  file, it copies it into its cache folder and retries once.

Both are covered by tests (`test_cancel_is_prompt`,
`test_reads_files_gs_is_not_allowed_to`).

Progress comes from Ghostscript's own output: it prints
`Processing pages 1 through N.` then `Page n` for each page. No extra pass is
needed to count pages.

## Architecture

```
compress-pdf/
├── meson.build
├── com.itsfoss.CompressPDF.json          Flatpak manifest
├── data/
│   ├── com.itsfoss.CompressPDF.desktop.in
│   ├── com.itsfoss.CompressPDF.metainfo.xml.in
│   ├── com.itsfoss.CompressPDF.gschema.xml
│   └── icons/ (scalable + symbolic SVG)
├── src/compress_pdf/
│   ├── main.py          Adw.Application, actions, "open" handler
│   ├── window.py        window states, drag and drop, file dialogs
│   ├── file_row.py      one row per file (status, progress, result)
│   ├── compressor.py    builds gs args, runs Gio.Subprocess, parses progress
│   ├── batch.py         runs files one by one, saves results without overwriting
│   ├── levels.py        level table above
│   ├── errors.py        gs output → user message
│   └── ui/*.blp         Blueprint UI definitions
├── po/                  gettext translations
├── debian/              native package
├── tests/               pytest; generates its own PDFs at test time
└── tools/bench.py       level tuning against a local folder of PDFs
```

- **No threads.** Ghostscript runs through `Gio.Subprocess` with async stdout
  reads on the GLib main loop, so the UI never blocks and cancel is a
  `force_exit()`.
- Files are compressed **one at a time** in v3.0. Ghostscript is single-threaded
  and this keeps progress readable. Two at a time can come later.
- `compressor.py` does not import GTK, so it can be tested without a display.
- Temp files go to `GLib.get_user_cache_dir()`, which works inside and outside
  the sandbox, and are cleaned up on exit and on cancel.

### libadwaita 1.5 limit

Allowed: `AdwApplicationWindow`, `AdwToolbarView`, `AdwHeaderBar`,
`AdwStatusPage`, `AdwPreferencesGroup`, `AdwActionRow`, `AdwToastOverlay`,
`AdwAboutDialog`, `AdwAlertDialog`, `AdwBreakpoint`, `AdwBanner`.

Not allowed (newer than 1.5): `AdwSpinner` (1.6, use `Gtk.Spinner`),
`AdwToggleGroup` / `AdwWrapBox` (1.7), `AdwBottomSheet` (1.6).

The development machine has libadwaita 1.9, so the app is also run inside the
GNOME 46 Flatpak runtime (libadwaita 1.5) to catch any accidental use of newer
APIs.

## Packaging

**Flatpak**
- Runtime `org.gnome.Platform//49`. Modules: Ghostscript (built from source,
  minimal: no X11 device, no CUPS), then the app.
- `finish-args`: `--socket=wayland`, `--socket=fallback-x11`, `--share=ipc`,
  `--device=dri`. **No filesystem and no network access.** Files come in and go
  out only through the portal, which is possible because the user picks the
  save location every time.
- Expected app size: about 5–10 MB download on top of the shared runtime.

**.deb**
- `Architecture: all`, built with meson + debhelper + dh-python.
- `Depends: python3 (>= 3.11), python3-gi, gir1.2-gtk-4.0, gir1.2-adw-1
  (>= 1.5), ghostscript`.
- Targets Ubuntu 24.04+, Mint 22+, Debian 13+, and derivatives.
- Expected size: under 100 KB.

**Metadata:** AppStream metainfo with screenshots, release notes, and content
rating. Passes `appstreamcli validate` and `desktop-file-validate`.

## App icon

A GNOME-style full-colour icon (128 px SVG, following the GNOME app icon
guidelines: simple shapes, the GNOME palette, a soft base shadow, readable at
32 px). Concept: a white page with a folded corner, squeezed from top and bottom
by two arrow bars in a single accent colour. Plus a monochrome symbolic variant.

## Testing

- Unit tests: argument building, progress parsing, error mapping, output
  naming, the "never bigger" rule. PDFs are generated at test time with
  Ghostscript, so no binary fixtures are committed.
- Local run against the private sample PDFs. They are kept outside the repo and
  never committed.
- Manual check on this machine (Ubuntu 26.04, GNOME), plus the GNOME 46 runtime
  for the libadwaita 1.5 check.
- A `.deb` and a `.flatpak` bundle are handed over for testing on other distros
  and on KDE.

## Milestones

1. Project skeleton: meson, app runs, empty window, About dialog, icon
2. Compressor module and tests, levels tuned with the benchmark
3. Full UI flow: files, levels, save, progress, cancel, results, errors
4. `.deb` package
5. Flatpak manifest with Ghostscript, portal-only file access
6. Metainfo, screenshots, README, translations template
7. Test builds handed over

v3.1: "Smaller than N MB" mode, password prompt for protected PDFs, optional
grayscale conversion, and "shrink oversized pages to A4/Letter". Photos
converted to PDF often sit on huge pages at 72 ppi, so dpi limits cannot
touch them; fitting to A4 made one such sample 4× smaller (1449 KB → 351 KB
for 3 pages at Balanced).
