#!/usr/bin/env python3
"""تشغيل كامل من الهاتف بضغطة واحدة:
   python3 run_on_phone.py
ينفذ: تشغيل الأصلي -> تحليل -> Patch -> تشغيل المعدّل -> تحليل الموقع -> تقارير
لا يحتاج gcc ولا لابتوب، Python فقط (Termux أو Pydroid 3)."""
import subprocess, sys
from pathlib import Path
root = Path(__file__).parent
def run(cmd): print("\n$ "+" ".join(cmd)); r=subprocess.run(cmd, cwd=root, text=True, capture_output=True); print(r.stdout); print(r.stderr, file=sys.stderr); return r
# 1) إنشاء access.dat الأصلي 0x00
(root/"phone_sample"/"access.dat").write_bytes(b"\x00")
print("=== 1) Original sample ==="); run([sys.executable, "phone_sample/sample_app.py"])
print("=== 2) Analyze sample ==="); run([sys.executable, "re_tool.py", "analyze", "phone_sample/sample_app.py", "--out", "reports"])
print("=== 3) Patch (lab sample only) ==="); run([sys.executable, "phone_sample/patch_phone.py"])
print("=== 4) Patched sample ==="); run([sys.executable, "patched_sample/sample_app.py"])
print("=== 5) Analyze lab site ==="); run([sys.executable, "re_tool.py", "analyze-site", "lab_site", "--out", "reports"])
print("\nDONE - خلصت كل الخطوات. التقارير في مجلد reports/")
print("قبل التعديل: Access Denied  |  بعد التعديل: Welcome Admin - All Permissions Granted")
