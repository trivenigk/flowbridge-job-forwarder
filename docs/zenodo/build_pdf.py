"""Convert PAPER.md to publication-quality PDF.

Renders with academic paper styling:
- Cover page with title, author, ORCID, date
- Justified body text
- Proper section hierarchy
- Styled tables, code blocks, abstract
- Page numbers + running header
"""
import base64
import re
import markdown
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

ROOT = Path(__file__).parent.parent
md_path = ROOT / "PAPER.md"
out_dir = ROOT / "zenodo"
html_path = out_dir / "_paper_render.html"
out_pdf = out_dir / "FlowBridge_PAPER.pdf"

raw_md = md_path.read_text(encoding="utf-8")

# Strip the leading title block (we replace it with cover page)
md_text = re.sub(
    r'^# .*?\n\n\*\*Author:\*\*.*?\n\*\*Date:\*\*.*?\n\*\*Status:\*\*.*?\n\n---\n\n',
    '',
    raw_md,
    count=1,
    flags=re.DOTALL,
)

body = markdown.markdown(
    md_text,
    extensions=["extra", "toc", "tables", "fenced_code", "sane_lists"]
)

# Extract abstract (first paragraph after Abstract heading)
abstract_match = re.search(r'<h2[^>]*>Abstract</h2>\s*<p>(.*?)</p>', body, re.DOTALL)
abstract_html = abstract_match.group(1) if abstract_match else ""

# Build cover page + body
today = datetime.now().strftime("%B %Y")

html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>FlowBridge Paper</title>
<style>
  @page {{
    size: A4;
    margin: 1in 0.9in 1in 0.9in;
    @bottom-center {{
      content: counter(page) " of " counter(pages);
      font-family: "Times New Roman", serif;
      font-size: 9pt;
      color: #666;
    }}
    @top-center {{
      content: "FlowBridge: A Zero-Cost Email-to-Messaging Framework";
      font-family: "Times New Roman", serif;
      font-size: 9pt;
      color: #888;
      font-style: italic;
    }}
  }}
  @page:first {{
    @top-center {{ content: ""; }}
    @bottom-center {{ content: ""; }}
  }}

  * {{ box-sizing: border-box; }}

  body {{
    font-family: "Times New Roman", "Liberation Serif", serif;
    font-size: 11pt;
    line-height: 1.55;
    color: #1a1a1a;
    text-align: justify;
    hyphens: auto;
  }}

  /* Cover page */
  .cover {{
    page-break-after: always;
    text-align: center;
    padding-top: 1.5in;
  }}
  .cover .label {{
    font-size: 10pt;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 1in;
  }}
  .cover h1 {{
    font-size: 24pt;
    line-height: 1.25;
    margin: 0 0 0.6in 0;
    font-weight: bold;
    text-align: center;
    color: #0a0a0a;
  }}
  .cover .author {{
    font-size: 14pt;
    margin-bottom: 0.1in;
    color: #1a1a1a;
  }}
  .cover .affil {{
    font-size: 11pt;
    color: #555;
    font-style: italic;
    margin-bottom: 0.05in;
  }}
  .cover .orcid {{
    font-size: 10pt;
    color: #777;
    margin-bottom: 0.6in;
    font-family: monospace;
  }}
  .cover .date {{
    font-size: 11pt;
    color: #666;
    margin-bottom: 1.8in;
  }}
  .cover .repo {{
    font-size: 9.5pt;
    color: #555;
    margin-top: 1in;
    border-top: 1px solid #ddd;
    padding-top: 12pt;
  }}
  .cover .repo a {{ color: #0a4a9a; text-decoration: none; }}

  /* Abstract block */
  .abstract-box {{
    margin: 0 0.4in 0.4in 0.4in;
    padding: 16pt 22pt;
    background: #f7f7f8;
    border-left: 3px solid #888;
    font-size: 10.5pt;
    line-height: 1.55;
    text-align: justify;
  }}
  .abstract-box .label {{
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-size: 9pt;
    color: #555;
    margin-bottom: 8pt;
    display: block;
  }}

  /* Headings */
  h1 {{
    font-size: 18pt;
    margin-top: 0;
    margin-bottom: 0.4em;
    color: #0a0a0a;
    font-weight: bold;
    page-break-before: avoid;
    page-break-after: avoid;
  }}
  h2 {{
    font-size: 14pt;
    margin-top: 1.4em;
    margin-bottom: 0.5em;
    color: #0a0a0a;
    font-weight: bold;
    page-break-after: avoid;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 4pt;
  }}
  h3 {{
    font-size: 12pt;
    margin-top: 1.1em;
    margin-bottom: 0.4em;
    color: #1a1a1a;
    font-weight: bold;
    page-break-after: avoid;
  }}
  h4 {{
    font-size: 11pt;
    margin-top: 0.9em;
    margin-bottom: 0.3em;
    color: #2a2a2a;
    font-weight: bold;
    font-style: italic;
    page-break-after: avoid;
  }}

  p {{ margin: 0 0 0.55em 0; orphans: 3; widows: 3; }}

  /* Lists */
  ul, ol {{ margin: 0.4em 0 0.7em 0; padding-left: 1.6em; }}
  li {{ margin: 0.2em 0; }}

  /* Inline code */
  code {{
    font-family: "Consolas", "Liberation Mono", monospace;
    background: #f4f4f6;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 9.5pt;
    color: #0a3a6a;
  }}

  /* Code blocks */
  pre {{
    background: #f7f7f9;
    border: 1px solid #e4e4e8;
    border-left: 3px solid #4a6a9a;
    padding: 10pt 14pt;
    margin: 10pt 0;
    border-radius: 4px;
    font-size: 9pt;
    line-height: 1.45;
    white-space: pre-wrap;
    page-break-inside: avoid;
  }}
  pre code {{
    background: none;
    padding: 0;
    color: #1a1a1a;
    font-size: 9pt;
  }}

  /* Tables */
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 10pt 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
  }}
  th {{
    background: #2a2a2a;
    color: #fff;
    font-weight: bold;
    text-align: left;
    padding: 6pt 9pt;
    border: 1px solid #2a2a2a;
  }}
  td {{
    border: 1px solid #d0d0d0;
    padding: 5pt 9pt;
    vertical-align: top;
  }}
  tr:nth-child(even) td {{ background: #fafafa; }}

  /* Quotes */
  blockquote {{
    margin: 1em 0.4in;
    padding: 6pt 14pt;
    border-left: 3px solid #888;
    color: #444;
    font-style: italic;
    background: #f8f8f9;
  }}

  /* Horizontal rules */
  hr {{
    border: none;
    border-top: 1px solid #ddd;
    margin: 1.5em 0;
  }}

  /* Strong/em */
  strong {{ font-weight: bold; color: #0a0a0a; }}
  em {{ font-style: italic; }}

  /* Links */
  a {{ color: #0a4a9a; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  /* Hide first abstract h2 + p (we render in box above) */
  .body-content > h2:first-of-type + p {{ display: none; }}
  .body-content > h2:first-of-type {{ display: none; }}
</style>
</head>
<body>

<!-- COVER PAGE -->
<section class="cover">
  <div class="label">Preprint · Open Access</div>
  <h1>FlowBridge: A Zero-Cost Generalized Framework for Cross-Platform Email-to-Messaging Automation Using Browser Automation in Containerized Virtual Display Environments</h1>
  <div class="author"><strong>Triveni Gopala Krishna Ganta</strong></div>
  <div class="affil">Independent Researcher</div>
  <div class="orcid">ORCID: 0009-0009-7797-2397</div>
  <div class="date">{today}</div>
  <div class="repo">
    Source code: <a href="https://github.com/trivenigk/flowbridge-job-forwarder">github.com/trivenigk/flowbridge-job-forwarder</a><br>
    License: MIT
  </div>
</section>

<!-- ABSTRACT BLOCK -->
<div class="abstract-box">
  <span class="label">Abstract</span>
  {abstract_html}
</div>

<!-- BODY -->
<div class="body-content">
{body}
</div>

</body></html>"""

html_path.write_text(html_doc, encoding="utf-8")

# Render with Chrome
opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--disable-gpu")
opts.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
driver.get(f"file:///{html_path.as_posix()}")

result = driver.execute_cdp_cmd("Page.printToPDF", {
    "format": "A4",
    "marginTop": 0.9, "marginBottom": 0.9, "marginLeft": 0.85, "marginRight": 0.85,
    "printBackground": True,
    "displayHeaderFooter": False,  # using @page CSS for header/footer
    "preferCSSPageSize": True,
})

out_pdf.write_bytes(base64.b64decode(result["data"]))
driver.quit()
html_path.unlink()

print(f"PDF written: {out_pdf}")
print(f"Size: {out_pdf.stat().st_size // 1024} KB")
