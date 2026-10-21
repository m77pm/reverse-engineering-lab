#!/usr/bin/env python3
"""Patch تعليمي للنسخة الهاتفية - يعمل فقط على عينة المشروع.
ينسخ phone_sample إلى patched_sample ويقلب بايت access.dat من 0x00 إلى 0x01
وهذا يوضح فكرة الـ Binary Patching: تحديد الـ Offset وتغيير قيمة بايت واحد."""
import shutil, sys
from pathlib import Path
src = Path(__file__).parent
dst = src.parent / "patched_sample"
if "RE_LAB_SAMPLE_v1" not in (src / "sample_app.py").read_text():
    print("Refused: not lab sample"); sys.exit(2)
if dst.exists(): shutil.rmtree(dst)
shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
data = bytearray((dst / "access.dat").read_bytes())
print(f"Before: access.dat[0] = 0x{data[0]:02x} at offset 0x0")
data[0] = 1
(dst / "access.dat").write_bytes(data)
print(f"After : access.dat[0] = 0x{data[0]:02x}")
print(f"Patched copy created: {dst}")
