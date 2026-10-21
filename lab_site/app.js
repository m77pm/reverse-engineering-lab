// موقع مختبر تعليمي: هذا فحص من جهة العميل فقط وليس حماية حقيقية
let isAdmin = false; // الطالب يحلل هذا المتغير ويناقش لماذا لا يكفي للحماية
if (isAdmin) { document.getElementById('msg').textContent = 'Welcome Admin - All Permissions'; }
