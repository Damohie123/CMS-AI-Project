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

def _seed_defaults():
    """دالة لإنشاء بيانات افتراضية إذا كانت قاعدة البيانات فارغة"""
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

def create_app():
    app = Flask(__name__)
    
    # تحميل الإعدادات
    app.config.from_object(Config)
    
    # الإضافات
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    JWTManager(app)
    
    # تسجيل المسارات (Blueprints)
    register_blueprints(app)

    @app.route("/")
    def home():
        return "مرحباً بك في موقع CMS-AI"

    @app.route("/api/health")
    def health():
        return {"status": "ok", "service": "CMS-AI"}

    with app.app_context():
        # ملاحظة: تأكد أن قاعدة البيانات في Vercel تدعم الكتابة (مثل PostgreSQL)
        db.create_all()
        _seed_defaults()

    return app

# تعريف app المطلوب بواسطة Vercel
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
