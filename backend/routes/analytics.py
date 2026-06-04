from datetime import datetime, timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from auth_utils import role_required
from models import Article, ArticleView, db

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/overview", methods=["GET"])
@jwt_required()
@role_required("admin", "editor")
def overview(current_user):
    total_articles = Article.query.count()
    published = Article.query.filter_by(status="published").count()
    total_views = db.session.query(func.coalesce(func.sum(Article.view_count), 0)).scalar()

    top = (
        Article.query.order_by(Article.view_count.desc())
        .limit(10)
        .all()
    )

    since = datetime.utcnow() - timedelta(days=30)
    views_by_day = (
        db.session.query(
            func.date(ArticleView.viewed_at).label("day"),
            func.count(ArticleView.id).label("count"),
        )
        .filter(ArticleView.viewed_at >= since)
        .group_by(func.date(ArticleView.viewed_at))
        .order_by(func.date(ArticleView.viewed_at))
        .all()
    )

    return jsonify({
        "total_articles": total_articles,
        "published_articles": published,
        "draft_articles": total_articles - published,
        "total_views": int(total_views or 0),
        "top_articles": [
            {
                "id": a.id,
                "title": a.title,
                "view_count": a.view_count,
                "status": a.status,
            }
            for a in top
        ],
        "views_by_day": [
            {"day": str(row.day), "count": row.count}
            for row in views_by_day
        ],
    })
