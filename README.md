# مشروع الهندسة العكسية — أداة تحليل برامج ومواقع (مختبر تعليمي)

**المادة:** الهندسة العكسية — تخصص الأمن السيبراني  
**فكرة المشروع:** تطبيق يعطيه الطالب برنامجاً أو موقعاً (يملكه أو عينة مختبر) فيقوم بتحليله هندسياً: استخراج البصمات، النوع، النصوص، الدوال الحساسة، الروابط والسكربتات والصلاحيات الظاهرة، ثم ينتج تقريراً منظماً. ولإثبات فهم آلية التعديل (Patching)، يحتوي المشروع على عينة مختبرية خاصة بنا ينجح المثال في تغيير نتيجتها من `Access Denied` إلى `Welcome Admin - All Permissions Granted`.

> ملاحظة أكاديمية مهمة للدكتور: التعديل التلقائي على برامج/مواقع الآخرين لفتح كل الصلاحيات هو تجاوز لأنظمة الحماية والترخيص، والصلاحيات الحقيقية للمواقع تُفرض من الخادم (Server-side) ولا يمكن تغييرها بتعديل نسخة العميل. لذلك صُمم المشروع على عينات المختبر ومواقع الطالب المحلية — وهو الأسلوب المعتمد في مختبرات الهندسة العكسية — مع إظهار كامل لسلسلة التحليل والتعديل على العينة الخاصة.

## ماذا يفعل التطبيق؟
1. **تحليل برنامج/ملف** `analyze`
   - SHA256 / MD5، الحجم، النوع (ELF/PE/APK/ZIP/PDF...)، Entropy
   - استخراج Strings (ASCII + UTF-16) والروابط والكلمات الحساسة (admin, license, is_admin, check...)
   - فهرس ملفات APK/ZIP وتلميحات AndroidManifest/permissions
   - خطوات مقترحة للتحليل في Ghidra / debugger
2. **تحليل موقع (قراءة فقط)** `analyze-url`
   - الحالة، Headers، الروابط، السكربتات، النماذج/Forms، وتلميحات فحوصات العميل (isAdmin, role, token, localStorage)
   - نتيجة تعليمية: فحص العميل ليس حماية؛ الحماية تكون على الخادم
3. **تحليل موقع محلي** `analyze-site` — نفس الفحوصات على مجلد موقعك
4. **مثال Patch على العينة فقط** `patch-lab`
   - يتحقق من وسم `RE_LAB_SAMPLE_v1` ويرفض أي ملف آخر
   - يحدد نمط دالة `is_admin()` المجموعة بـ `-O0` ويغيّر `return 0` إلى `return 1` عند Offset موثق في التقرير
5. **واجهة ويب** `web_app.py` — رفع ملف أو إدخال رابط مختبر وعرض التقرير

## التشغيل
```bash
gcc -O0 -o lab_sample/sample_app lab_sample/sample_app.c
./lab_sample/sample_app
# Marker: RE_LAB_SAMPLE_v1
# Access Denied - Normal User Mode

python3 re_tool.py analyze lab_sample/sample_app --out reports
python3 re_tool.py patch-lab lab_sample/sample_app --out lab_sample/sample_app_patched
./lab_sample/sample_app_patched
# Marker: RE_LAB_SAMPLE_v1
# Welcome Admin - All Permissions Granted

python3 re_tool.py analyze-site lab_site --out reports
python3 re_tool.py analyze-url http://127.0.0.1:8000/ --out reports

python3 web_app.py   # http://127.0.0.1:8080
```

## النتائج المختبرة فعلياً
- الأصلي: `Access Denied - Normal User Mode`
- بعد Patch العينة: `Welcome Admin - All Permissions Granted`
- تقارير مولدة في `reports/file_report.json|.md` و `reports/site_report.json|.md`
- تم العثور في Strings على `is_admin` و `Welcome Admin - All Permissions Granted`

## الهيكل
```
re_tool.py          الأداة الرئيسية (CLI)
web_app.py          واجهة ويب بسيطة
lab_sample/sample_app.c   العينة (C)
lab_site/           موقع مختبر (HTML/JS)
reports/            تقارير مولدة
```

## أدوات ونظريات مستخدمة
Static Analysis, Dynamic Analysis (مقترح في التقرير), Strings, Hashing, File Format Identification, Entropy, Ghidra Auto-Analysis, Conditional Checks, Binary Patching (على العينة)، Client-Side vs Server-Side Authorization.

## حدود المشروع وتطوير مستقبلي
- إضافة Ghidra Headless و Capstone لعرض Disassembly كامل
- دعم PE بـ pefile وتحليل Imports/Sections
- دعم APK بـ jadx/apktool في بيئة مختبر
- قاعدة بيانات لحفظ تقارير العينات ومقارنتها
