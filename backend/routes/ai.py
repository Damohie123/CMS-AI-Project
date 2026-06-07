from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required

import ai_engine
from models import Article
from services import tts_service

main_bp = Blueprint("main", __name__)


@main_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate():
    data = request.get_json() or {}
    topic = (data.get("topic") or "").strip()
    if not topic:
        return jsonify({"error": "الموضوع مطلوب"}), 400
    return jsonify(
        ai_engine.generate_article(
            topic,
            tone=data.get("tone", "informative"),
            length=data.get("length", "medium"),
        )
    )


@main_bp.route("/summarize", methods=["POST"])
@jwt_required()
def summarize():
    data = request.get_json() or {}
    text = data.get("text") or ""
    if not text.strip():
        return jsonify({"error": "النص مطلوب"}), 400
    return jsonify(ai_engine.summarize_text(text))


@main_bp.route("/titles", methods=["POST"])
@jwt_required()
def titles():
    data = request.get_json() or {}
    text = (data.get("text") or data.get("topic") or "").strip()
    if not text:
        return jsonify({"error": "أدخل نصاً أو موضوعاً"}), 400
    return jsonify(ai_engine.suggest_titles(text, count=data.get("count", 5)))


@main_bp.route("/seo", methods=["POST"])
@jwt_required()
def seo():
    data = request.get_json() or {}
    title = data.get("title", "")
    content = data.get("content", "")
    if not content.strip():
        return jsonify({"error": "المحتوى مطلوب"}), 400
    return jsonify(ai_engine.seo_suggestions(title, content))


@main_bp.route("/keywords", methods=["POST"])
@jwt_required()
def keywords():
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"error": "النص مطلوب"}), 400
    return jsonify(ai_engine.extract_keywords(text, limit=data.get("limit", 15)))


@main_bp.route("/grammar", methods=["POST"])
@jwt_required()
def grammar():
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"error": "النص مطلوب"}), 400
    return jsonify(ai_engine.grammar_check(text))


@main_bp.route("/arabic-package", methods=["POST"])
@jwt_required()
def arabic_package():
    data = request.get_json() or {}
    topic = (data.get("topic") or "").strip()
    if not topic:
        return jsonify({"error": "الموضوع مطلوب"}), 400
    return jsonify(ai_engine.arabic_content_package(topic))


@main_bp.route("/tools", methods=["GET"])
@jwt_required()
def list_tools():
    """AI capabilities exposed by the backend."""
    return jsonify({
        "tools": [
            {"id": "generate", "name": "توليد مقال", "endpoint": "POST /api/ai/generate"},
            {"id": "summarize", "name": "تلخيص", "endpoint": "POST /api/ai/summarize"},
            {"id": "titles", "name": "اقتراح عناوين", "endpoint": "POST /api/ai/titles"},
            {"id": "seo", "name": "تحسين SEO", "endpoint": "POST /api/ai/seo"},
            {"id": "keywords", "name": "كلمات مفتاحية", "endpoint": "POST /api/ai/keywords"},
            {"id": "grammar", "name": "تصحيح لغوي", "endpoint": "POST /api/ai/grammar"},
            {"id": "arabic-package", "name": "حزمة محتوى عربي", "endpoint": "POST /api/ai/arabic-package"},
            {"id": "tts", "name": "نص إلى صوت", "endpoint": "POST /api/ai/tts"},
            {"id": "chat", "name": "مساعد ذكي", "endpoint": "POST /api/chat/sessions/{id}/messages"},
        ],
        "openai_configured": bool(current_app.config.get("OPENAI_API_KEY")),
    })


@main_bp.route("/tts", methods=["POST"])
@jwt_required()
def text_to_speech():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "النص مطلوب"}), 400
    try:
        result = tts_service.synthesize(
            text,
            lang=data.get("lang") or current_app.config.get("TTS_DEFAULT_LANG", "ar"),
            voice=data.get("voice") or current_app.config.get("TTS_OPENAI_VOICE", "nova"),
            save_file=data.get("save_file", True),
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503


@main_bp.route("/tts/audio/<filename>", methods=["GET"])
@jwt_required(optional=True)
def serve_tts_audio(filename):
    safe = "".join(c for c in filename if c.isalnum() or c in ".-_")
    if safe != filename or not filename.endswith(".mp3"):
        return jsonify({"error": "ملف غير صالح"}), 400
    return send_from_directory(current_app.config["TTS_FOLDER"], filename)


@main_bp.route("/duplicate-check", methods=["POST"])
@jwt_required()
def duplicate_check():
    data = request.get_json() or {}
    content = data.get("content", "")
    article_id = data.get("exclude_article_id")
    if not content.strip():
        return jsonify({"error": "المحتوى مطلوب"}), 400
    q = Article.query
    if article_id:
        q = q.filter(Article.id != article_id)
    snippets = [a.content for a in q.limit(50).all()]
    return jsonify(ai_engine.detect_duplicate(content, snippets))
