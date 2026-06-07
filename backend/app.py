import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db, Category, User
from routes import register_blueprints

# 1. تهيئة البيئة
load_dotenv(Path(__file__).parent / ".env")

# 2. إنشاء التطبيق (هنا يتم تعريف app)
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 3. تسجيل الإضافات
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    JWTManager(app)
    
    # 4. تسجيل المسارات (وهنا نستخدم app بعد أن تم تعريفها)
    register_blueprints(app)

    @app.route("/")
    def home():
        return "مرحباً بك في موقع CMS-AI"

    @app.route("/api/health")
    def health():
        return {"status": "ok", "service": "CMS-AI"}

    return app

# 5. تعريف app للمستوى العلوي (هذا ما يحتاجه Vercel)
app = create_app()

# 6. تشغيل قاعدة البيانات (داخل سياق التطبيق)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
