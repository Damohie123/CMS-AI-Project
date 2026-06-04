from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from models import User


def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user:
                return jsonify({"error": "المستخدم غير موجود"}), 404
            if user.role != "admin" and user.role not in allowed_roles:
                return jsonify({"error": "صلاحية غير كافية"}), 403
            return fn(*args, **kwargs, current_user=user)

        return wrapper

    return decorator


def admin_or_editor(user):
    return user.role in ("admin", "editor")


def can_edit_article(user, article):
    if user.role == "admin":
        return True
    if user.role == "editor":
        return True
    return user.role == "writer" and article.author_id == user.id
