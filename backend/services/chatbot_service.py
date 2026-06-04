"""Chatbot: intent routing to AI tools + general assistant replies."""
import json
import re

import ai_engine

CHATBOT_SYSTEM = (
    "أنت مساعد CMS-AI لإدارة المحتوى بالعربية. ساعد المستخدم في الكتابة، "
    "التلخيص، SEO، والمقالات. كن موجزاً وعملياً. إذا طُلب تنفيذ أمر، "
    "اشرح النتيجة بوضوح."
)

HELP_TEXT = """أوامر المساعد الذكي:

• **توليد مقال:** «اكتب مقالاً عن [الموضوع]»
• **تلخيص:** «لخص: [النص]»
• **عناوين:** «اقترح عناوين لـ [الموضوع أو النص]»
• **SEO:** «حسّن SEO: [النص]»
• **كلمات مفتاحية:** «استخرج كلمات مفتاحية: [النص]»
• **تصحيح:** «صحح: [النص]»
• **حزمة عربية:** «حزمة محتوى عن [الموضوع]»
• **صوت:** «اقرأ: [نص قصير]» أو زر 🔊 بجانب الرد

يمكنك أيضاً طرح أسئلة عامة عن إدارة المحتوى."""

INTENT_PATTERNS: list[tuple[str, str]] = [
    (r"(?:حزمة|باقة)\s+(?:محتوى|عربي)", "arabic_package"),
    (r"(?:اكتب|أنشئ|ولّد|توليد|انشئ)\s+(?:مقال|محتوى)", "generate"),
    (r"(?:لخص|تلخيص|اختصر)", "summarize"),
    (r"(?:اقترح|أعطني|اعطني)\s+(?:عناوين|عنوان)", "titles"),
    (r"(?:seo|سيو|تحسين\s+seo|تحسين\s+السيو)", "seo"),
    (r"(?:كلمات\s+مفتاحية|استخرج\s+كلمات)", "keywords"),
    (r"(?:صحح|تصحيح|تدقيق)", "grammar"),
    (r"(?:اقرأ|نطق|تحويل\s+لصوت|صوت)", "tts"),
    (r"(?:مساعدة|مساعده|help|الأوامر|الاوامر)\s*$", "help"),
]


def detect_intent(message: str) -> tuple[str, str]:
    """Return (intent, payload_text)."""
    text = message.strip()
    lower = text.lower()

    for pattern, intent in INTENT_PATTERNS:
        if re.search(pattern, lower, re.IGNORECASE):
            payload = _extract_payload(text, intent)
            return intent, payload

    if len(text) > 120 and not text.endswith("?"):
        return "summarize", text

    return "chat", text


def _extract_payload(message: str, intent: str) -> str:
    """Strip command prefix and optional colon."""
    m = message.strip()
    for sep in (":", "：", "-", "–"):
        if sep in m:
            parts = m.split(sep, 1)
            if len(parts) == 2 and len(parts[1].strip()) > 3:
                return parts[1].strip()

    patterns_remove = {
        "generate": r"^(?:اكتب|أنشئ|انشئ|ولّد|ولد|توليد)\s+(?:مقال(?:اً|ا)?|محتوى)\s+(?:عن\s+)?",
        "summarize": r"^(?:لخص|تلخيص|اختصر)\s*",
        "titles": r"^(?:اقترح|أعطني|اعطني)\s+(?:عناوين|عنوان)\s+(?:لـ|ل)?\s*",
        "seo": r"^(?:حسّن|حسن)\s*(?:SEO|سيو)\s*:?\s*|^(?:seo|سيو)\s*:?\s*",
        "keywords": r"^(?:استخرج\s+)?كلمات\s+مفتاحية\s*:?\s*",
        "grammar": r"^(?:صحح|تصحيح|تدقيق)\s*:?\s*",
        "arabic_package": r"^(?:حزمة|باقة)\s+(?:محتوى|عربي)\s+(?:عن\s+)?",
        "tts": r"^(?:اقرأ|نطق|تحويل\s+لصوت|صوت)\s*:?\s*",
    }
    if intent in patterns_remove:
        m = re.sub(patterns_remove[intent], "", m, flags=re.IGNORECASE).strip()
    if intent == "arabic_package":
        m = re.sub(r"^(?:حزمة|باقة)\s+(?:محتوى|عربي)\s+(?:عن\s+)?", "", m, flags=re.IGNORECASE).strip()
    return m or message


def process_message(message: str, context: list[dict] | None = None) -> dict:
    """
    Process user message; returns assistant reply + metadata for API/DB.
    context: [{"role":"user"|"assistant","content":"..."}]
    """
    intent, payload = detect_intent(message)

    if intent == "help":
        return _pack("help", HELP_TEXT, None)

    if intent == "generate":
        if len(payload) < 3:
            return _pack("generate", "حدّد موضوع المقال، مثال: اكتب مقالاً عن الذكاء الاصطناعي", None)
        data = ai_engine.generate_article(payload)
        reply = _format_generate(data, payload)
        return _pack("generate", reply, data)

    if intent == "summarize":
        if len(payload) < 20:
            return _pack("summarize", "أرسل نصاً أطول للتلخيص (بعد «لخص:»).", None)
        data = ai_engine.summarize_text(payload)
        reply = f"**ملخص:**\n\n{data.get('summary', '')}\n\n_المصدر: {data.get('source', 'ai')}_"
        return _pack("summarize", reply, data)

    if intent == "titles":
        if len(payload) < 3:
            return _pack("titles", "أدخل موضوعاً أو نصاً لاقتراح العناوين.", None)
        data = ai_engine.suggest_titles(payload)
        lines = "\n".join(f"{i}. {t}" for i, t in enumerate(data.get("titles", []), 1))
        return _pack("titles", f"**عناوين مقترحة:**\n\n{lines}", data)

    if intent == "seo":
        if len(payload) < 20:
            return _pack("seo", "أرسل محتوى أطول لتحليل SEO.", None)
        data = ai_engine.seo_suggestions("", payload)
        tips = data.get("suggestions")
        if isinstance(tips, list):
            tips_txt = "\n".join(f"• {t}" for t in tips)
        else:
            tips_txt = str(tips or "")
        kw = ", ".join(data.get("keywords", [])[:10])
        reply = (
            f"**Meta Title:** {data.get('meta_title', '')}\n\n"
            f"**Meta Description:** {data.get('meta_description', '')}\n\n"
            f"**كلمات مفتاحية:** {kw}\n\n**نصائح:**\n{tips_txt}"
        )
        return _pack("seo", reply, data)

    if intent == "keywords":
        if len(payload) < 10:
            return _pack("keywords", "أرسل نصاً لاستخراج الكلمات المفتاحية.", None)
        data = ai_engine.extract_keywords(payload)
        kw = ", ".join(data.get("keywords", []))
        return _pack("keywords", f"**الكلمات المفتاحية:** {kw}", data)

    if intent == "grammar":
        if len(payload) < 5:
            return _pack("grammar", "أرسل النص المراد تصحيحه.", None)
        data = ai_engine.grammar_check(payload)
        issues = data.get("issues") or []
        issues_txt = "\n".join(f"• {i['message']}" for i in issues) if issues else "لا مشاكل شكلية"
        reply = f"**النص المصحح:**\n\n{data.get('corrected', '')}\n\n**ملاحظات:** {issues_txt}"
        return _pack("grammar", reply, data)

    if intent == "arabic_package":
        if len(payload) < 3:
            return _pack("arabic_package", "حدّد الموضوع: حزمة محتوى عن [الموضوع]", None)
        data = ai_engine.arabic_content_package(payload)
        reply = _format_arabic_package(data)
        return _pack("arabic_package", reply, data)

    if intent == "tts":
        if len(payload) < 2:
            return _pack("tts", "اكتب نصاً للقراءة: اقرأ: [النص]", {"text": ""})
        return _pack(
            "tts",
            f"اضغط زر 🔊 لسماع النص ({len(payload)} حرفاً).",
            {"text": payload[:4096]},
        )

    return _pack("chat", _general_chat(message, context), None)


def _general_chat(message: str, context: list[dict] | None) -> str:
    history = ""
    if context:
        recent = context[-6:]
        history = "\n".join(
            f"{m['role']}: {m['content'][:200]}" for m in recent
        )
    user = message
    if history:
        user = f"سياق المحادثة:\n{history}\n\nسؤال المستخدم: {message}"

    reply = ai_engine.chat_with_context(CHATBOT_SYSTEM, user)
    if reply:
        return reply
    return (
        "أنا مساعد CMS-AI. يمكنني توليد المقالات، التلخيص، SEO، وغيرها. "
        "اكتب «مساعدة» لعرض الأوامر، أو «اكتب مقالاً عن [موضوعك]»."
    )


def _format_generate(data: dict, topic: str) -> str:
    if data.get("content") and data.get("source") == "openai":
        return f"**مقال عن «{topic}»:**\n\n{data['content']}"
    parts = [
        f"**{data.get('title', topic)}**",
        data.get("introduction") and f"\n_المقدمة:_\n{data['introduction']}",
        data.get("body") and f"\n{data['body']}",
        data.get("conclusion") and f"\n_الخاتمة:_\n{data['conclusion']}",
    ]
    if data.get("hashtags"):
        parts.append("\n**هاشتاقات:** " + " ".join(data["hashtags"]))
    if data.get("keywords"):
        parts.append("**كلمات:** " + ", ".join(data["keywords"]))
    return "\n".join(p for p in parts if p)


def _format_arabic_package(data: dict) -> str:
    a = data.get("article") or {}
    lines = [_format_generate(a, data.get("topic", ""))]
    if data.get("title_suggestions"):
        lines.append(
            "\n**عناوين بديلة:**\n"
            + "\n".join(f"• {t}" for t in data["title_suggestions"][:5])
        )
    seo = data.get("seo") or {}
    if seo.get("meta_description"):
        lines.append(f"\n**SEO:** {seo.get('meta_title')} — {seo.get('meta_description')}")
    return "\n".join(lines)


def _pack(intent: str, reply: str, data) -> dict:
    return {
        "intent": intent,
        "reply": reply,
        "data": data,
        "can_speak": intent in ("tts", "summarize", "generate", "chat", "grammar", "arabic_package"),
        "speak_text": _speak_text_for(intent, reply, data),
    }


def _speak_text_for(intent: str, reply: str, data) -> str | None:
    if intent == "tts" and isinstance(data, dict):
        return (data.get("text") or "")[:4096] or None
    if intent == "summarize" and isinstance(data, dict):
        return data.get("summary")
    if intent == "generate" and isinstance(data, dict):
        return data.get("content") or data.get("body")
    if intent == "grammar" and isinstance(data, dict):
        return data.get("corrected")
    if intent == "chat":
        return re.sub(r"\*+", "", reply)[:500]
    return None


def serialize_data(data) -> str | None:
    if data is None:
        return None
    try:
        return json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError):
        return json.dumps({"raw": str(data)}, ensure_ascii=False)
