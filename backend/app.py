import sys
import os
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# ضبط المسار ليتمكن بايثون من رؤية المجلدات الفرعية في Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# الاستيرادات الخاصة بك
from config import Config
from models import db, Category, User
from routes import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # إعدادات المجلدات لـ Vercel (نظام الملفات هناك للقراءة فقط)
    if not os.environ.get("VERCEL"):
        Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
        Path(app.config["TTS_FOLDER"]).mkdir(parents=True, exist_ok=True)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    JWTManager(app)
    
    # تسجيل الـ Blueprints
    register_blueprints(app)

    @app.route("/")
    def home():
        return {"message": "AI Engine is running"}

    @app.route("/api/health")
    def health():
        return {"status": "ok", "service": "CMS-AI"}

    return app

# تعريف app للـ Vercel Runtime
app = create_app()

if __name__ == "__ai_bp__":
    app.run()
