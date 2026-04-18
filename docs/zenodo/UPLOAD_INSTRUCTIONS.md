# Zenodo Upload Instructions

Free DOI in 2 minutes. No approval needed.

---

## Step 1: Convert PAPER.md to PDF

### Option A: Pandoc (best quality)
```bash
cd docs
pandoc PAPER.md -o PAPER.pdf --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -V mainfont="Times New Roman" \
  --toc --toc-depth=2
```

### Option B: VS Code
1. Install "Markdown PDF" extension
2. Open PAPER.md
3. Right-click → Markdown PDF: Export (pdf)

### Option C: Online (no install)
1. Go to https://www.markdowntopdf.com/
2. Upload PAPER.md
3. Download PDF

---

## Step 2: Upload to Zenodo

1. Go to https://zenodo.org
2. Log in (use ORCID: 0009-0009-7797-2397)
3. Click **+ Upload** → **New Upload**
4. Drag the PDF file
5. Fill in metadata using `zenodo_metadata.json` as reference:

| Field | Value |
|-------|-------|
| Upload type | Publication |
| Publication type | Preprint |
| Publication date | 2026-04-17 |
| Title | (copy from metadata.json) |
| Authors | Ganta, Triveni Gopala Krishna |
| Affiliation | Independent Researcher |
| ORCID | 0009-0009-7797-2397 |
| Description | (copy HTML from metadata.json) |
| Keywords | (copy from metadata.json — comma-separated) |
| License | MIT |
| Access | Open |
| Language | English |
| Related identifier | https://github.com/trivenigk/flowbridge-job-forwarder |
| Relation | is supplement to |

6. Click **Save**
7. Click **Publish** — DOI assigned instantly

---

## Step 3: Update Repo with DOI

After Zenodo gives you DOI like `10.5281/zenodo.XXXXXXX`:

1. Update `README.md` citation block:
```
Ganta, T. (2026). FlowBridge: A Zero-Cost Generalized Framework...
Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX
```

2. Update LinkedIn articles in `docs/linkedin/FB0*` — replace `[DOI link]` placeholder

3. Add Zenodo badge to README:
```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

---

## Step 4: After Zenodo, also submit to:

| Platform | Cost | Time | Notes |
|----------|------|------|-------|
| **arXiv** | Free | Days (needs endorsement first) | Best academic visibility |
| **SSRN** | Free | 1-3 days review | Business/social sciences angle |
| **OpenReview** | Free | Self-publish | ML community |
| **HAL** | Free | Same day | EU repository |

You already have Zenodo + ORCID + SSRN setup per memory. Reuse same metadata.
