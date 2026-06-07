
# داخل ملف backend/app.py
import sys
import os

# إضافة المجلد الحالي للمسار لضمان رؤية المجلدات الفرعية
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from routes import register_blueprints # هذا السطر يجب أن يعمل الآن

app = Flask(__name__)
register_blueprints(app)

from pathlib import Path

from dotenv import load_dotenv

from flask import Flask

from flask_cors import CORS

from flask_jwt_extended import JWTManager

from config import Config

from models import Category, User, db

# داخل backend/app.py
@app.route('/test-route')
def test_route():
    return "نظام التوجيه يعمل!"

from backend.routes import register_blueprints

# داخل backend/routes/__init__.py

from flask import Flask

from routes.ai import  ai_bp #

app = Flask(__name__)

app.register_blueprint(ai_bp, url_prefix='/ai') 



# 4. أخيراً: تعريف المسارات الأخرى (مثل الصفحة الرئيسية)

@app.route('/')

def home():

    return "مرحباً بك في موقع CMS-AI"



if __name__ == "__main__":

    app.run()



# إضافة url_prefix تجعل المسارات تبدأ بـ /ai مثل /ai/generate

from flask import Flask, Blueprint  # أضفنا Blueprint هنا

from flask_cors import CORS

from flask_jwt_extended import JWTManager

# ... باقي الاستيرادات

# تحميل متغيرات البيئة

load_dotenv(Path(__file__).parent / ".env")



# في بداية ملف app.py، داخل create_app:

def create_app():

    from flask import Blueprint



# تعريف الـ Blueprint

ai_bp = Blueprint('ai_bp',__name__)



@ai_bp.route('/')

def index():

    return {"message": "Server is running successfully!"}

def create_app():

    app = Flask(__name__)

    # ... بقية الإعدادات ...

    

    # تأكد من وجود هذا السطر

    from routes import ai_bp 

    app.register_blueprint(ai_bp)

    

    return app

    

    app = Flask(__name__) # صححت "name" إلى name

    

    # تحميل إعدادات قاعدة البيانات من متغير البيئة

    # تأكد أن Config الخاص بك يستخدم هذا أيضاً

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

    app.config.from_object(Config)

    

    # ... بقية الكود



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



if __name__ == "__main__":

    app.run(debug=True, port=5000)
