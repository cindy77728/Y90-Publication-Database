# Y90 Publication Database — GitHub Pages Weekly PubMed Update

Upload all files/folders in this package to your GitHub Pages repository.

Files included:
- `index.html` — your publication database webpage, patched to load `publications.json`
- `publications.json` — stores papers added by the weekly PubMed automation
- `.github/workflows/weekly-pubmed-update.yml` — scheduled GitHub Actions workflow
- `scripts/update_pubmed.py` — PubMed search/update script

How it works:
1. GitHub Actions runs every Monday at 09:00 Taiwan time.
2. It searches PubMed for recent Y-90 / radioembolization publications.
3. New records are added to `publications.json` with Review Status = `AI Draft`.
4. Your webpage loads `publications.json` when opened and merges new records into the database.

Important:
- Auto-added papers still need human review.
- GitHub Pages may need Actions permission: Settings → Actions → General → Workflow permissions → Read and write permissions.
- You can manually run the update: Actions → Weekly PubMed Update → Run workflow.


Update in this version:
- Library category strip now supports parent-to-subcategory drill-down. Click a parent category such as Metastases to reveal mCRC, Breast cancer, Lung cancer, etc.
- Manage Categories still supports easy click-to-edit subcategory chips.


Latest patch: removed the visible "Reset all subcategories" button and fixed the search icon / placeholder overlap in the search bar.


Latest patch v4.6.7: Force-flattens all legacy subcategory tags in publication records on page load, so Library and Manage Categories stay consistent. Add subcategories manually again after upload.

Latest patch v4.6.8:
- Parent-only category mode is enabled.
- Old tags such as "Dosimetry / Dose Response" will display as "Dosimetry" in the Library.
- The app also cleans localStorage category paths after loading.
- If old data still appears, clear site data for the GitHub Pages site once.

Latest patch v5.2 — category persistence fix:
- Local category edits are no longer overwritten by `publications.json` every time the page refreshes.
- Export JSON now downloads a GitHub-ready file named `publications.json`.
- To publish your browser edits to GitHub, click Export JSON, then upload that downloaded `publications.json` to GitHub and replace the existing `publications.json` file.
- The page compares local edits with the exported timestamp, so manual category edits should stay after refresh.
