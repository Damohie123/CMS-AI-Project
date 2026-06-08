import sys
import os
from flask import Flask

# 1. ضبط المسار (لضمان رؤية المجلدات الفرعية)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes import register_blueprints
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # تهيئة الإضافات
    db.init_app(app)
    register_blueprints(app)
    
    @app.route("/")
    def home():
        return {"message": "AI Engine is running"}
        
    return app

# 2. هذا السطر هو ما يبحث عنه Vercel
# يجب أن يكون المتغير المسمى "app" موجوداً في المستوى الأعلى للملف
app = create_app()

if __name__ == "__main__":
    app.run()
