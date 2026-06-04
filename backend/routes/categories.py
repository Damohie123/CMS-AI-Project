import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from auth_utils import role_required
from models import Category, db

categories_bp = Blueprint("categories", __name__)


def _slugify(name: str) -> str:
    s = re.sub(r"[^\w\u0600-\u06FF\-]+", "-", name.strip().lower())
    return re.sub(r"-+", "-", s).strip("-") or "category"


@categories_bp.route("", methods=["GET"])
@jwt_required()
def list_categories():
    return jsonify([c.to_dict() for c in Category.query.all()])


@categories_bp.route("", methods=["POST"])
@jwt_required()
@role_required("admin", "editor")
def create_category(current_user):
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "اسم التصنيف مطلوب"}), 400
    slug = data.get("slug") or _slugify(name)
    if Category.query.filter_by(slug=slug).first():
        return jsonify({"error": "المعرّف مستخدم"}), 409
    cat = Category(name=name, name_ar=data.get("name_ar"), slug=slug)
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201
