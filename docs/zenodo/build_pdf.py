"""Convert PAPER.md to PDF using Chrome headless print-to-PDF."""
import base64
import json
import markdown
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

md_text = md_path.read_text(encoding="utf-8")
body = markdown.markdown(md_text, extensions=["extra", "toc", "tables", "fenced_code"])

html_doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>FlowBridge Paper</title>
<style>
  @page {{ size: A4; margin: 1in; }}
  body {{
    font-family: "Times New Roman", Times, serif;
    font-size: 11pt; line-height: 1.5; color: #1a1a1a;
    max-width: 800px; margin: 0 auto;
  }}
  h1 {{ font-size: 22pt; }}
  h2 {{ font-size: 16pt; margin-top: 1.5em; }}
  h3 {{ font-size: 13pt; }}
  h4 {{ font-size: 11.5pt; }}
  p {{ margin: 0.5em 0; }}
  ul, ol {{ margin: 0.5em 0; padding-left: 1.5em; }}
  code {{ font-family: "Courier New", monospace; background: #f4f4f4;
         padding: 1px 4px; border-radius: 3px; font-size: 10pt; }}
  pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px;
        overflow-x: auto; font-size: 9pt; white-space: pre-wrap; }}
  pre code {{ background: none; padding: 0; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 10pt; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; vertical-align: top; }}
  th {{ background: #f0f0f0; font-weight: bold; }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 1.5em 0; }}
  blockquote {{ margin: 1em 0; padding-left: 1em; border-left: 3px solid #ccc; color: #555; }}
</style></head><body>
{body}
</body></html>"""

html_path.write_text(html_doc, encoding="utf-8")

# Chrome headless print to PDF
opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--disable-gpu")
opts.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
driver.get(f"file:///{html_path.as_posix()}")

result = driver.execute_cdp_cmd("Page.printToPDF", {
    "format": "A4",
    "marginTop": 1, "marginBottom": 1, "marginLeft": 1, "marginRight": 1,
    "printBackground": True,
    "displayHeaderFooter": True,
    "footerTemplate": '<div style="font-size:8pt;width:100%;text-align:center;color:#888;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
    "headerTemplate": '<div></div>',
})

out_pdf.write_bytes(base64.b64decode(result["data"]))
driver.quit()
html_path.unlink()  # cleanup intermediate

print(f"PDF written: {out_pdf}")
print(f"Size: {out_pdf.stat().st_size // 1024} KB")
