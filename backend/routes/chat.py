from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import ChatMessage, ChatSession, db
from services import chatbot_service

chat_bp = Blueprint("chat", __name__)


def _session_for_user(session_id: int, user_id: int) -> ChatSession | None:
    return ChatSession.query.filter_by(id=session_id, user_id=user_id).first()


@chat_bp.route("/help", methods=["GET"])
@jwt_required()
def help_commands():
    return jsonify({
        "commands": chatbot_service.HELP_TEXT,
        "intents": [
            "generate", "summarize", "titles", "seo",
            "keywords", "grammar", "arabic_package", "tts", "help",
        ],
    })


@chat_bp.route("/sessions", methods=["GET"])
@jwt_required()
def list_sessions():
    user_id = int(get_jwt_identity())
    sessions = (
        ChatSession.query.filter_by(user_id=user_id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    return jsonify([s.to_dict() for s in sessions])


@chat_bp.route("/sessions", methods=["POST"])
@jwt_required()
def create_session():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    title = (data.get("title") or "محادثة جديدة").strip()[:200]
    session = ChatSession(user_id=user_id, title=title)
    db.session.add(session)
    welcome = ChatMessage(
        session=session,
        role="assistant",
        content=(
            "مرحباً! أنا مساعد CMS-AI. اكتب **مساعدة** لعرض الأوامر، "
            "أو جرّب: «اكتب مقالاً عن التسويق الرقمي»."
        ),
        intent="welcome",
    )
    db.session.add(welcome)
    db.session.commit()
    return jsonify(session.to_dict(include_messages=True)), 201


@chat_bp.route("/sessions/<int:session_id>", methods=["GET"])
@jwt_required()
def get_session(session_id):
    user_id = int(get_jwt_identity())
    session = _session_for_user(session_id, user_id)
    if not session:
        return jsonify({"error": "المحادثة غير موجودة"}), 404
    return jsonify(session.to_dict(include_messages=True))


@chat_bp.route("/sessions/<int:session_id>", methods=["DELETE"])
@jwt_required()
def delete_session(session_id):
    user_id = int(get_jwt_identity())
    session = _session_for_user(session_id, user_id)
    if not session:
        return jsonify({"error": "المحادثة غير موجودة"}), 404
    db.session.delete(session)
    db.session.commit()
    return jsonify({"message": "تم الحذف"})


@chat_bp.route("/sessions/<int:session_id>/messages", methods=["POST"])
@jwt_required()
def send_message(session_id):
    user_id = int(get_jwt_identity())
    session = _session_for_user(session_id, user_id)
    if not session:
        return jsonify({"error": "المحادثة غير موجودة"}), 404

    data = request.get_json() or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "الرسالة فارغة"}), 400

    history = [
        {"role": m.role, "content": m.content}
        for m in session.messages[-10:]
    ]

    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=message,
    )
    db.session.add(user_msg)

    result = chatbot_service.process_message(message, context=history)
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=result["reply"],
        intent=result["intent"],
        extra_data=chatbot_service.serialize_data(result.get("data")),
    )
    db.session.add(assistant_msg)

    if session.title == "محادثة جديدة" and len(message) > 3:
        session.title = message[:60] + ("…" if len(message) > 60 else "")
    session.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "user_message": user_msg.to_dict(),
        "assistant_message": assistant_msg.to_dict(),
        "intent": result["intent"],
        "can_speak": result.get("can_speak", False),
        "speak_text": result.get("speak_text"),
    })
