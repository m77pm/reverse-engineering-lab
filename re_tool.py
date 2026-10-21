#!/usr/bin/env python3
"""
Reverse Engineering Lab Tool - مشروع تعليمي لمادة الهندسة العكسية
Scope (النطاق الأكاديمي):
  - تحليل ملفات/عينات يملكها الطالب أو مقدمة من المختبر/الدكتور
  - تحليل مواقع يملكها الطالب أو مواقع مختبر محلية
  - مثال الـ patch يعمل فقط على العينة المختبرية الخاصة بالمشروع
    (يتحقق من وسم RE_LAB_SAMPLE_v1 داخل الملف ويرفض غيرها)

Features:
  analyze      : hashes, file type, entropy, strings, indicators, ZIP/APK listing
  analyze-url  : headers, links, scripts, forms, endpoints (read-only fetch)
  analyze-site : تحليل مجلد موقع محلي
  patch-lab    : patch تعليمي على lab_sample فقط (is_admin: 0 -> 1)
  make-report  : يتم إنشاء تقرير JSON + Markdown تلقائيا مع كل تحليل
"""
import argparse, hashlib, html.parser, json, math, os, re, sys, urllib.request, urllib.error, zipfile
from pathlib import Path
from collections import Counter

LAB_MARKER = b"RE_LAB_SAMPLE_v1"

def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    c = Counter(data); n = len(data)
    return round(-sum((v/n) * math.log2(v/n) for v in c.values()), 3)

def extract_strings(data: bytes, min_len=4):
    ascii_s = re.findall(rb"[ -~]{%d,}" % min_len, data)
    utf16 = re.findall(rb"(?:[ -~]\x00){%d,}" % min_len, data)
    out = [s.decode("ascii", "ignore") for s in ascii_s]
    out += [s.decode("utf-16le", "ignore") for s in utf16]
    return sorted(set(out))

def detect_type(data: bytes, name: str):
    if data.startswith(b"\x7fELF"): return "ELF (Linux executable/library)"
    if data.startswith(b"MZ"): return "PE (Windows executable)"
    if data.startswith(b"PK\x03\x04"):
        return "ZIP/APK/JAR archive" if name.lower().endswith((".apk",".jar")) else "ZIP archive"
    if data.startswith(b"\x89PNG"): return "PNG image"
    if data.startswith(b"%PDF"): return "PDF"
    if b"<html" in data[:2048].lower(): return "HTML"
    return "Unknown / raw binary"

KEYWORDS = ["admin","password","passwd","license","serial","token","login","auth",
            "permission","root","debug","api_key","secret","is_admin","check","verify"]

def analyze_file(path: Path):
    data = path.read_bytes()
    strings = extract_strings(data)
    report = {
        "file": str(path), "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "md5": hashlib.md5(data).hexdigest(),
        "type": detect_type(data, path.name),
        "entropy": entropy(data),
        "is_lab_sample": LAB_MARKER in data,
        "strings_count": len(strings),
        "strings_sample": strings[:300],
        "urls_found": sorted(set(re.findall(r"https?://[^\s\"'<>]+", "\n".join(strings)))),
        "keyword_hits": {k: [s for s in strings if k.lower() in s.lower()][:20] for k in KEYWORDS if any(k.lower() in s.lower() for s in strings)},
    }
    # ZIP / APK internals
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            report["archive_entries"] = z.namelist()[:500]
            for entry in z.namelist():
                if entry.endswith("AndroidManifest.xml") or entry.lower().endswith("permissions.txt"):
                    try:
                        txt = z.read(entry)[:20000]
                        report.setdefault("manifest_hints", []).append(txt.decode("utf-8","ignore")[:4000])
                    except Exception:
                        pass
    # Disassembly hint (optional tools)
    report["next_steps"] = [
        "Open in Ghidra: File > Import, then Analyze > Auto Analysis",
        "Look for keyword_hits functions (e.g. is_admin / check / verify)",
        "Set a breakpoint on the comparison, observe registers/flags (dynamic analysis)",
        "Document the offset of any conditional jump before discussing patching theory",
    ]
    return report

class LinkParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.scripts=[]; self.forms=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag=="a" and "href" in d: self.links.append(d["href"])
        if tag=="script" and "src" in d: self.scripts.append(d["src"])
        if tag=="form": self.forms.append({"action": d.get("action",""), "method": d.get("method","GET")})

def analyze_url(url: str):
    req = urllib.request.Request(url, headers={"User-Agent":"RE-Lab-Tool/1.0 (educational)"})
    with urllib.request.urlopen(req, timeout=10) as r:
        body = r.read(); headers = dict(r.headers); status = r.status; final = r.geturl()
    text = body.decode("utf-8","ignore")
    p = LinkParser(); p.feed(text)
    inline_js_checks = sorted(set(re.findall(r"(isAdmin|is_admin|role|permission|token|localStorage|sessionStorage)[^\n;]{0,60}", text)))
    return {"url": url, "final_url": final, "status": status, "headers": headers,
            "size_bytes": len(body), "links": sorted(set(p.links)), "scripts": sorted(set(p.scripts)),
            "forms": p.forms, "client_side_check_hints": inline_js_checks[:50],
            "note": "Client-side checks are NOT security. Real authorization must be enforced server-side. This tool only fetches/reads; it does not bypass server authentication."}

def analyze_site(folder: Path):
    files=[]; hints=[]
    for f in folder.rglob("*"):
        if f.is_file():
            rel=str(f.relative_to(folder)); files.append(rel)
            if f.suffix.lower() in (".js",".html",".php",".py"):
                t=f.read_text(errors="ignore")
                for m in re.finditer(r"(isAdmin|is_admin|role\s*=|permission|localStorage|checkAuth)[^\n;]{0,80}", t):
                    hints.append({"file": rel, "hint": m.group(0)[:120]})
    return {"site_folder": str(folder), "files": files, "client_side_check_hints": hints[:100],
            "note": "Use analyze-site on your own/local site copy only."}

def write_report(report, out_dir: Path, name="report"):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir/f"{name}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [f"# Reverse Engineering Lab Report\n", f"```json\n{json.dumps({k:v for k,v in report.items() if k!='strings_sample'}, ensure_ascii=False, indent=2)[:6000]}\n```\n"]
    if "strings_sample" in report:
        md.append("## Strings (sample)\n" + "\n".join(f"- `{s}`" for s in report["strings_sample"][:80]))
    (out_dir/f"{name}.md").write_text("\n".join(md), encoding="utf-8")
    print(f"[+] Report: {out_dir/f'{name}.json'}")
    print(f"[+] Report: {out_dir/f'{name}.md'}")

def patch_lab(src: Path, dst: Path):
    """Educational patch ONLY for our lab sample.
    Pattern at -O0 (x86_64): is_admin() { return 0; }
      55 48 89 e5  b8 00 00 00 00  5d c3
    Patch:                         b8 01 00 00 00
    """
    data = bytearray(src.read_bytes())
    if LAB_MARKER not in data:
        print("[-] Refused: this is not the lab sample (marker RE_LAB_SAMPLE_v1 not found). Patch demo is limited to the project's own sample.", file=sys.stderr); return 2
    pattern = b"\xb8\x00\x00\x00\x00\x5d\xc3"
    idx = data.find(pattern)
    if idx == -1:
        print("[-] Pattern not found. Recompile with: gcc -O0 -o lab_sample/sample_app lab_sample/sample_app.c", file=sys.stderr); return 3
    data[idx+1] = 1
    dst.write_bytes(data); os.chmod(dst, 0o755)
    print(f"[+] Patched lab sample: {src} -> {dst} at offset 0x{idx+1:x} (return 0 -> return 1)")
    print("[+] Run the patched file to see: Welcome Admin")
    return 0

def main():
    ap = argparse.ArgumentParser(description="Reverse Engineering Lab Tool (educational)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a=sub.add_parser("analyze"); a.add_argument("file"); a.add_argument("--out", default="reports")
    u=sub.add_parser("analyze-url"); u.add_argument("url"); u.add_argument("--out", default="reports")
    s=sub.add_parser("analyze-site"); s.add_argument("folder"); s.add_argument("--out", default="reports")
    p=sub.add_parser("patch-lab"); p.add_argument("file"); p.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.cmd=="analyze": write_report(analyze_file(Path(args.file)), Path(args.out), "file_report")
    elif args.cmd=="analyze-url": write_report(analyze_url(args.url), Path(args.out), "url_report")
    elif args.cmd=="analyze-site": write_report(analyze_site(Path(args.folder)), Path(args.out), "site_report")
    elif args.cmd=="patch-lab": sys.exit(patch_lab(Path(args.file), Path(args.out)))

if __name__=="__main__":
    main()
