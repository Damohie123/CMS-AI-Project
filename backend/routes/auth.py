from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from models import ROLES, User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    role = data.get("role", "writer")

    if not username or not email or not password:
        return jsonify({"error": "جميع الحقول مطلوبة"}), 400
    if role not in ROLES:
        role = "writer"
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "اسم المستخدم مستخدم"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "البريد مستخدم"}), 409

    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "تم التسجيل", "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "بيانات الدخول غير صحيحة"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()})


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "غير موجود"}), 404
    return jsonify(user.to_dict())
