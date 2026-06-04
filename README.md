# نظام إدارة المحتوى بالذكاء الاصطناعي | CMS-AI

نظام ذكي لإدارة المحتوى يدعم العربية: إنشاء المقالات، التصنيف، SEO، التلخيص، التحليلات، وصلاحيات المستخدمين.

## المكونات

| المكون | التقنية |
|--------|---------|
| الواجهة | React + Vite (RTL عربي) |
| الخادم | Python Flask + JWT |
| قاعدة البيانات | SQLite (قابل للتحويل إلى MySQL) |
| الذكاء الاصطناعي | OpenAI API + معالجة محلية احتياطية |

## الميزات المنفذة

- **المستخدمون:** تسجيل دخول، أدوار (مدير / محرر / كاتب)
- **المحتوى:** CRUD مقالات، تصنيفات، رفع وسائط
- **AI:** توليد مقالات، تلخيص، عناوين، كلمات مفتاحية، SEO عربي، تصحيح لغوي، كشف تكرار
- **مولد المحتوى العربي:** مقدمة، خاتمة، هاشتاقات، SEO في طلب واحد
- **التحليلات:** مشاهدات، رسوم Chart.js، أكثر المقالات قراءة
- **المساعد الذكي (Chatbot):** محادثات محفوظة في SQLite، توجيه أوامر عربية لأدوات AI
- **نص إلى صوت (TTS):** OpenAI TTS أو gTTS (عربي) عبر `POST /api/ai/tts`

## التشغيل السريع

### 1. الخادم (Backend)

```powershell
cd backend
py -3 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

> على Windows إذا لم يعمل `python`، استخدم `py -3` بدلاً منه.

الخادم يعمل على: `http://127.0.0.1:5000`

### 2. الواجهة (Frontend)

```bash
cd frontend
npm install
npm run dev
```

الواجهة: `http://127.0.0.1:5173`

### حساب افتراضي

- المستخدم: `admin`
- كلمة المرور: `admin123`

## تفعيل OpenAI (اختياري)

في `backend/.env`:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

بدون المفتاح يعمل النظام بوضع محلي (قوالب عربية + استخراج كلمات مفتاحية).

## هيكل المشروع

```
CMS-AI/
├── backend/
│   ├── app.py
│   ├── ai_engine.py
│   ├── models.py
│   └── routes/
├── frontend/
│   └── src/
└── README.md
```

## API رئيسية

| Method | Path | الوصف |
|--------|------|--------|
| POST | `/api/auth/login` | تسجيل الدخول |
| GET | `/api/articles` | قائمة المقالات |
| POST | `/api/ai/arabic-package` | مولد المحتوى العربي |
| POST | `/api/ai/generate` | توليد مقال |
| POST | `/api/ai/tts` | نص → صوت (MP3) |
| POST | `/api/chat/sessions/{id}/messages` | المساعد الذكي |
| GET | `/api/analytics/overview` | إحصائيات |

## توسعات مقترحة (للمشروع الأكاديمي)

- تحسين صوت عربي (أصوات edge-tts إضافية)
- توصية محتوى (تشابه المقالات)
- MySQL: `DATABASE_URL=mysql+pymysql://user:pass@localhost/cms_ai`

## الترخيص

مشروع تعليمي — حر الاستخدام والتعديل.
