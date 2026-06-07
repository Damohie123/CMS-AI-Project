from flask import Flask
from routes import register_blueprints

def create_app():
    # تعريف التطبيق داخل الدالة
    app = Flask(__name__)
    
    # تسجيل المسارات داخل الدالة بعد تعريف app
    register_blueprints(app)
    
    @app.route("/")
    def home():
        return "مرحباً بك في موقع CMS-AI"
        
    return app

# تعريف app للمستوى العالمي ليراه Vercel
app = create_app()

if __name__ == "__main__":
    app.run()
