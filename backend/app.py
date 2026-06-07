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

# في بداية ملف app.py، داخل create_app:
def create_app():
    from flask import Blueprint

# تعريف الـ Blueprint
main_bp = Blueprint('main', name)

@main_bp.route('/')
def index():
    return {"message": "Server is running successfully!"}
def create_app():
    app = Flask(name)
    # ... بقية الإعدادات ...
    
    # تأكد من وجود هذا السطر
    from routes import main_bp 
    app.register_blueprint(main_bp)
    
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
    
