import os
from flask import Flask
from routes import register_blueprints
from models import db
from config import Config

def create_app():
    # 1. إنشاء التطبيق هنا فقط
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 2. تهيئة الإضافات
    db.init_app(app)
    
    # 3. تسجيل المسارات
    register_blueprints(app)
    
    @app.route("/")
    def home():
        return "مرحباً بك في موقع CMS-AI"
        
    return app

# 4. هذا المتغير هو ما تبحث عنه Vercel
app = create_app()

if __name__ == "__main__":
    app.run()
