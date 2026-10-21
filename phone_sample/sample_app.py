#!/usr/bin/env python3
# RE_LAB_SAMPLE_v1 - phone edition, pure Python, no compiler needed
# البرنامج يقرأ بايت الصلاحية من access.dat : 0x00 = مستخدم عادي, 0x01 = Admin
import os, sys
MARKER = "RE_LAB_SAMPLE_v1"
here = os.path.dirname(os.path.abspath(__file__))
try:
    flag = open(os.path.join(here, "access.dat"), "rb").read()[0]
except Exception:
    flag = 0
print(f"Marker: {MARKER}")
if flag == 1:
    print("Welcome Admin - All Permissions Granted")
else:
    print("Access Denied - Normal User Mode")
