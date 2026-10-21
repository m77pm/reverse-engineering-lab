#!/usr/bin/env python3
"""واجهة ويب بسيطة (stdlib فقط) - شغّل: python3 web_app.py  ثم افتح http://127.0.0.1:8080"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi, json, os, tempfile
from pathlib import Path
from re_tool import analyze_file, analyze_url

HTML = """<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><title>RE Lab</title>
<h1>أداة الهندسة العكسية - مختبر تعليمي</h1>
<p>للاستخدام على عينات/مواقع تملكها أو مقدمة من الدكتور فقط.</p>
<form method="post" enctype="multipart/form-data">ملف للتحليل: <input type="file" name="f"><button>حلّل الملف</button></form>
<hr><form method="post">رابط موقع مختبر: <input name="url" size="50" placeholder="http://127.0.0.1:8000/"><button formaction="/url">حلّل الرابط</button></form>
<pre>{out}</pre></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send(HTML.format(out=""))
    def send(self, body):
        b=body.encode(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        if self.path=="/url":
            length=int(self.headers.get("Content-Length",0)); data=self.rfile.read(length).decode()
            from urllib.parse import parse_qs; url=parse_qs(data).get("url",[""])[0]
            try: out=json.dumps(analyze_url(url),ensure_ascii=False,indent=2)
            except Exception as e: out=str(e)
            return self.send(HTML.format(out=out))
        form=cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={"REQUEST_METHOD":"POST"})
        item=form["f"]
        if item.file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=item.filename) as t: t.write(item.file.read()); name=t.name
            out=json.dumps(analyze_file(Path(name)),ensure_ascii=False,indent=2)
        else: out="اختر ملف"
        self.send(HTML.format(out=out))
    def log_message(self,*a): pass

if __name__=="__main__":
    print("http://127.0.0.1:8080"); HTTPServer(("127.0.0.1",8080),H).serve_forever()
