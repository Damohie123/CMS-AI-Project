import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import Category, User, db
from routes import register_blueprints

# تحميل متغيرات البيئة
load_dotenv(Path(__file__).parent / ".env")

def create_app():
    app = Flask('name')
    app.config.from_object(Config)

    # التعديل هنا: نتحقق أننا لسنا على Vercel قبل إنشاء المجلدات
    if not os.environ.get("VERCEL"):
        Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
        Path(app.config["TTS_FOLDER"]).mkdir(parents=True, exist_ok=True)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    JWTManager(app)
    register_blueprints(app)

    @app.route("/api/health")
    def health():
        return {"status": "ok", "service": "CMS-AI"}

    with app.app_context():
        # ملاحظة: إذا كانت قاعدة بياناتك SQLite، فقد تواجه خطأ هنا أيضاً في Vercel
        db.create_all()
        _seed_defaults()

    return app

def _seed_defaults():
    # هذا الجزء يعمل فقط إذا كانت قاعدة البيانات تسمح بالكتابة
    try:
        if not Category.query.first():
            defaults = [
                ("Technology", "تقنية", "tech"),
                ("Business", "أعمال", "business"),
                ("Education", "تعليم", "education"),
            ]
            for name, name_ar, slug in defaults:
                db.session.add(Category(name=name, name_ar=name_ar, slug=slug))
            db.session.commit()

        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", email="admin@cms.local", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
    except Exception as e:
        print(f"Error seeding database: {e}")

# تعريف app للمستوى العلوي كما يحتاج Vercel
app = create_app()

if name == "main":
    app.run(debug=True, port=5000)
    
