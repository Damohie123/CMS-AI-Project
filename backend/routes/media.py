import uuid
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from auth_utils import role_required
from models import Media, db

media_bp = Blueprint("media", __name__)

ALLOWED = {"png", "jpg", "jpeg", "gif", "webp", "pdf", "doc", "docx"}


def _allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED


@media_bp.route("", methods=["GET"])
@jwt_required()
def list_media():
    return jsonify([m.to_dict() for m in Media.query.order_by(Media.created_at.desc()).all()])


@media_bp.route("/upload", methods=["POST"])
@jwt_required()
@role_required("admin", "editor", "writer")
def upload(current_user):
    if "file" not in request.files:
        return jsonify({"error": "لم يُرفع ملف"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "اسم ملف غير صالح"}), 400
    if not _allowed(f.filename):
        return jsonify({"error": "نوع ملف غير مدعوم"}), 400

    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = f.filename.rsplit(".", 1)[1].lower()
    stored = f"{uuid.uuid4().hex}.{ext}"
    path = upload_dir / stored
    f.save(path)

    media = Media(
        filename=stored,
        original_name=secure_filename(f.filename),
        mime_type=f.mimetype,
        size=path.stat().st_size,
        uploaded_by=current_user.id,
    )
    db.session.add(media)
    db.session.commit()
    return jsonify(media.to_dict()), 201


@media_bp.route("/files/<filename>", methods=["GET"])
def serve_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
