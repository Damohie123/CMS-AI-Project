from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from auth_utils import can_edit_article, role_required
from models import Article, ArticleView, db

articles_bp = Blueprint("articles", __name__)


@articles_bp.route("", methods=["GET"])
@jwt_required()
def list_articles():
    status = request.args.get("status")
    category_id = request.args.get("category_id", type=int)
    q = Article.query
    if status:
        q = q.filter_by(status=status)
    if category_id:
        q = q.filter_by(category_id=category_id)
    articles = q.order_by(Article.updated_at.desc()).all()
    return jsonify([a.to_dict(include_content=False) for a in articles])


@articles_bp.route("/<int:article_id>", methods=["GET"])
@jwt_required(optional=True)
def get_article(article_id):
    article = Article.query.get_or_404(article_id)
    track = request.args.get("track_view", "0") == "1"
    if track:
        article.view_count = (article.view_count or 0) + 1
        db.session.add(
            ArticleView(
                article_id=article.id,
                user_agent=(request.headers.get("User-Agent") or "")[:255],
            )
        )
        db.session.commit()
    return jsonify(article.to_dict())


@articles_bp.route("", methods=["POST"])
@jwt_required()
@role_required("admin", "editor", "writer")
def create_article(current_user):
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    if not title or not content:
        return jsonify({"error": "العنوان والمحتوى مطلوبان"}), 400

    article = Article(
        title=title,
        content=content,
        summary=data.get("summary"),
        status=data.get("status", "draft"),
        seo_title=data.get("seo_title"),
        seo_description=data.get("seo_description"),
        keywords=data.get("keywords"),
        author_id=current_user.id,
        category_id=data.get("category_id"),
    )
    db.session.add(article)
    db.session.commit()
    return jsonify(article.to_dict()), 201


@articles_bp.route("/<int:article_id>", methods=["PUT"])
@jwt_required()
@role_required("admin", "editor", "writer")
def update_article(article_id, current_user):
    article = Article.query.get_or_404(article_id)
    if not can_edit_article(current_user, article):
        return jsonify({"error": "لا يمكنك تعديل هذا المقال"}), 403

    data = request.get_json() or {}
    for field in (
        "title", "content", "summary", "status",
        "seo_title", "seo_description", "keywords", "category_id",
    ):
        if field in data:
            setattr(article, field, data[field])
    db.session.commit()
    return jsonify(article.to_dict())


@articles_bp.route("/<int:article_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin", "editor")
def delete_article(article_id, current_user):
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    return jsonify({"message": "تم الحذف"})
