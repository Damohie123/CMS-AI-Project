from .ai import ai_bp
from routes.analytics import analytics_bp
from routes.chat import chat_bp
from routes.articles import articles_bp
from routes.auth import auth_bp
from routes.categories import categories_bp
from routes.media import media_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(articles_bp, url_prefix='/api/articles')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(media_bp, url_prefix='/api/media')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
