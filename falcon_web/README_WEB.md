# Falcon Web

منصة Falcon المبنية باستخدام Django، وتعمل بجانب بوت Telegram دون حذفه.

## تشغيل محلي

```bash
cd falcon_web
python -m pip install -r requirements-web.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## PythonAnywhere

1. اسحب فرع `django-web` من GitHub.
2. أنشئ virtualenv وثبت `requirements-web.txt`.
3. أضف Web App يدويًا واختر Python.
4. اجعل مسار المشروع `/home/USERNAME/Falcon/falcon_web`.
5. عدّل WSGI ليضيف مسار المشروع ثم يستورد `falcon_web.wsgi.application`.
6. اضبط متغيرات البيئة المذكورة في `.env.example` دون رفع القيم السرية إلى GitHub.
7. نفذ `python manage.py check` ثم `python manage.py migrate` بعد أخذ نسخة احتياطية.
8. أعد تحميل Web App.

## مهم

الإعداد الافتراضي يستخدم SQLite للتطوير فقط. قبل ربط قاعدة MySQL الحالية يجب مراجعة مخطط جداول البوت وعمل نسخة احتياطية. لا تنفذ migrations على قاعدة الإنتاج قبل هذه المراجعة.
