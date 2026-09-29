# Compress PDF v3 — Test Checklist

Work through the sections that apply to your setup and tick each box. If
something fails, note the section number (for example **5.3**) and use the
report template at the end.

Sections marked **(.deb)**, **(Flatpak)** or **(KDE)** only apply there.

## 0. Your setup

| | |
|---|---|
| Distro and version | |
| Desktop (GNOME, KDE, Cinnamon…) and version | |
| Wayland or X11 | |
| How installed (source, .deb, Flatpak) | |
| Compress PDF version (About dialog) | |

To see error messages, start the app from a terminal:

- source or .deb: `compress-pdf`
- Flatpak: `flatpak run com.itsfoss.CompressPDF`

### Test files to prepare

Keep them in a folder of their own, for example `~/pdf-test/`.

- [ ] A scanned document or phone scan (a few MB)
- [ ] A large PDF with many pages (20+ pages, 20 MB or more)
- [ ] A text-only PDF (exported from a word processor)
- [ ] A PDF with spaces, accents or symbols in its name, e.g. `Résumé 100% (final).pdf`
- [ ] A password-protected PDF:
      `qpdf --encrypt secret secret 256 -- input.pdf locked.pdf`, or without qpdf:
      `gs -q -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOwnerPassword=owner -sUserPassword=secret -sOutputFile=locked.pdf input.pdf`
- [ ] A damaged PDF: `head -c 50000 input.pdf > damaged.pdf`
- [ ] A fake PDF: `echo hello > fake.pdf`

## 1. Install and launch

- [ ] 1.1 The app appears in the app grid or menu as **Compress PDF** with the new icon
- [ ] 1.2 It starts without errors in the terminal
- [ ] 1.3 The icon shows in the dock/taskbar while running
- [ ] 1.4 Menu → **About Compress PDF** shows version 3.0.0, It's FOSS, and working links
- [ ] 1.5 The window follows the system's dark and light style, and switches live when you change it
- [ ] 1.6 The window follows the system accent colour (needs libadwaita 1.6+, e.g. GNOME 47+ or the Flatpak; on Ubuntu 24.04 it stays blue)

## 2. Adding files

- [ ] 2.1 **Select Files…** opens your desktop's own file dialog (GNOME or KDE style)
- [ ] 2.2 The dialog shows only PDFs by default, and multiple files can be selected
- [ ] 2.3 Dragging one or more PDFs from the file manager onto the window shows the "Drop to Add Files" overlay, and the files are added
- [ ] 2.4 Right-click a PDF in the file manager → **Open With → Compress PDF** adds it, both when the app is closed and when it is already open
- [ ] 2.5 **Ctrl+O** opens the file dialog
- [ ] 2.6 The **+** button in the header bar opens the file dialog
- [ ] 2.7 Adding the fake PDF shows "“fake.pdf” is not a PDF file", and it is not added
- [ ] 2.8 Adding the same file twice does not list it twice
- [ ] 2.9 The **×** button removes a file from the list
- [ ] 2.10 The "To Compress" heading shows the right count and total size

## 3. Compression levels

- [ ] 3.1 Four levels are shown; **Balanced** is selected on first start
- [ ] 3.2 The chosen level is remembered after closing and reopening the app
- [ ] 3.3 The levels can't be changed while compressing

## 4. Compressing one file

- [ ] 4.1 **Compress** opens a save dialog with the name `<name>-compressed.pdf`
- [ ] 4.2 The dialog opens in the original file's folder (may not apply in Flatpak)
- [ ] 4.3 Choosing an existing file name asks before replacing it
- [ ] 4.4 The row shows progress, then "old size → new size (N% smaller)"
- [ ] 4.5 A message appears: "1 file compressed, … saved", with **Show in Folder**
- [ ] 4.6 **Show in Folder** opens the file manager at the saved file
- [ ] 4.7 **Open** on the row opens the compressed PDF in your PDF viewer
- [ ] 4.8 The original file is unchanged

## 5. Compressing several files

- [ ] 5.1 With 2+ files, **Compress** asks for a folder ("Save Here")
- [ ] 5.2 Each file is saved as `<name>-compressed.pdf` in that folder
- [ ] 5.3 Compressing the same files into the same folder again creates `-compressed-2.pdf` and so on; nothing is overwritten
- [ ] 5.4 Two files with the same name from different folders get different output names
- [ ] 5.5 Files are compressed one after another, each with its own progress

## 6. "To Compress" and "Done"

- [ ] 6.1 After compressing, finished files move to **Done**, and "To Compress" shows "Add PDF Files…"
- [ ] 6.2 **Compress** is greyed out when nothing is waiting
- [ ] 6.3 Adding a new file and pressing **Compress** processes only the new file, not the finished ones
- [ ] 6.4 Adding a finished file again moves it back to "To Compress"
- [ ] 6.5 **Clear** empties the Done section
- [ ] 6.6 **Open** still works on files in Done

## 7. Progress, Cancel and closing

Use the large PDF.

- [ ] 7.1 The row shows "Page N of M" and a moving progress bar
- [ ] 7.2 The window stays responsive while compressing (you can scroll and open the menu)
- [ ] 7.3 **Cancel** stops within about a second, and a "Compression cancelled" message appears
- [ ] 7.4 Files finished before the cancel keep their result; the cancelled file stays in "To Compress"
- [ ] 7.5 No half-written output file is left behind
- [ ] 7.6 Closing the window while compressing asks "Stop Compressing?"
- [ ] 7.7 **Keep Compressing** continues; **Stop and Close** closes the app within a second or two
- [ ] 7.8 If compressing finishes while that question is open, the question disappears
- [ ] 7.9 After closing, no `gs` process is left running (`pgrep -a gs`)

## 8. Difficult files

- [ ] 8.1 Password-protected PDF → "This PDF is password protected." (no file saved)
- [ ] 8.2 Damaged PDF → either compressed with "Damaged file repaired", or a clear error
- [ ] 8.3 Text-only PDF → "Already optimised, not saved" with a green tick, and no file written
- [ ] 8.4 A file with spaces, accents or `%` in the name compresses and saves correctly
- [ ] 8.5 A PDF on a USB stick (`/media/…`) compresses
- [ ] 8.6 A PDF on a network share opened from the file manager (SMB/SFTP) compresses
- [ ] 8.7 Saving into a folder you can't write to shows an error, not a crash
- [ ] 8.8 A very large PDF (100+ MB) compresses without freezing the window

## 9. Output quality

Compress the scanned document at each level and open the results.

- [ ] 9.1 **High Quality:** looks the same as the original
- [ ] 9.2 **Balanced:** looks the same on screen; small print readable
- [ ] 9.3 **Small:** slightly softer; small print still readable
- [ ] 9.4 **Smallest:** visibly softer, but text is still readable
- [ ] 9.5 Each level gives a smaller file than the one above it (or "Already optimised")
- [ ] 9.6 Pages keep their orientation (landscape stays landscape)
- [ ] 9.7 Links and selectable text in text PDFs still work after compression

## 10. Window and accessibility

- [ ] 10.1 Resizing the window very narrow (about phone width) keeps everything usable, with no cut-off buttons
- [ ] 10.2 Maximising and restoring works, and the window size is remembered after reopening
- [ ] 10.3 Everything can be reached with **Tab**, and activated with **Enter**/**Space**
- [ ] 10.4 **Ctrl+Enter** starts compressing, **Ctrl+W** closes the window, **Ctrl+Q** quits
- [ ] 10.5 Looks right with display scaling at 125%, 150% and 200%
- [ ] 10.6 Optional: with the Orca screen reader, buttons and file rows are read out sensibly

## 11. (.deb) Native package

- [ ] 11.1 `sudo apt install ./compress-pdf_3.0.0_all.deb` pulls in Ghostscript and GTK/libadwaita automatically
- [ ] 11.2 The package is small (under 100 KB)
- [ ] 11.3 `sudo apt remove compress-pdf` removes the app cleanly
- [ ] 11.4 **Ubuntu 25.10+ only:** Cancel is still quick (7.3), and network-share files still work (8.6). Ubuntu restricts Ghostscript with AppArmor there, and the app works around it

## 12. (Flatpak)

- [ ] 12.1 `flatpak install ./compress-pdf.flatpak` installs, and the app runs
- [ ] 12.2 Files from anywhere can be added through the dialog and by drag and drop, even though the app has no file-system permission
- [ ] 12.3 Saving works to any folder you pick, including USB sticks
- [ ] 12.4 "Show in Folder" and "Open" work from inside the sandbox
- [ ] 12.5 Ghostscript does not need to be installed on the system

## 13. (KDE)

- [ ] 13.1 The file and save dialogs are KDE's own (Dolphin style)
- [ ] 13.2 Dragging from Dolphin works
- [ ] 13.3 "Open With" from Dolphin works
- [ ] 13.4 The app looks tidy under Breeze (light and dark)
- [ ] 13.5 "Show in Folder" opens Dolphin

## Reporting a problem

Open an issue at <https://github.com/itsfoss/compress-pdf/issues> with:

```
Checklist item: (e.g. 7.3)
Distro / desktop / Wayland or X11:
Installed from: source / .deb / Flatpak
What I did:
What I expected:
What happened:
Terminal output (run the app from a terminal, see section 0):
```

Please don't attach private PDFs. If a file is needed to reproduce the
problem, try to find a public one that shows the same issue.
