"""AI Engine: text generation, summarization, SEO, keywords — OpenAI with local fallback."""
import re
from collections import Counter

from flask import current_app

ARABIC_PROMPT_PREFIX = (
    "أنت مساعد محتوى عربي محترف. اكتب بالعربية الفصحى الواضحة. "
    "راعِ SEO والجمهور العربي."
)


def _openai_client():
    api_key = current_app.config.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    try:
        from openai import OpenAI

        return OpenAI(api_key=api_key)
    except Exception:
        return None


def chat_with_context(system: str, user: str, max_tokens: int = 800) -> str | None:
    """General assistant turn for chatbot."""
    return _chat(system, user, max_tokens=max_tokens)


def _chat(system: str, user: str, max_tokens: int = 1200) -> str | None:
    client = _openai_client()
    if not client:
        return None
    try:
        resp = client.chat.completions.create(
            model=current_app.config.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception:
        return None


def _extract_keywords_local(text: str, limit: int = 10) -> list[str]:
    arabic_words = re.findall(r"[\u0600-\u06FF]{3,}", text)
    latin_words = re.findall(r"[a-zA-Z]{4,}", text.lower())
    stop = {
        "في", "من", "على", "إلى", "أن", "هذا", "هذه", "التي", "الذي",
        "كان", "ما", "عن", "مع", "بين", "the", "and", "for", "that",
    }
    words = [w for w in arabic_words + latin_words if w not in stop]
    counts = Counter(words)
    return [w for w, _ in counts.most_common(limit)]


def _summarize_local(text: str, max_sentences: int = 3) -> str:
    sentences = re.split(r"[.!?؟。\n]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    if not sentences:
        return text[:300] + ("..." if len(text) > 300 else "")
    return ". ".join(sentences[:max_sentences]) + "."


def generate_article(topic: str, tone: str = "informative", length: str = "medium") -> dict:
    system = f"{ARABIC_PROMPT_PREFIX} أنشئ مقالاً منظمًا بمقدمة وعناوين فرعية وخاتمة."
    user = (
        f"الموضوع: {topic}\nالأسلوب: {tone}\nالطول: {length}\n"
        "أرجع: عنواناً، مقدمة، 3 فقرات، خاتمة، 5 كلمات مفتاحية، 5 هاشتاقات."
    )
    ai_text = _chat(system, user, max_tokens=2000)
    if ai_text:
        return {"source": "openai", "content": ai_text, "topic": topic}

    intro = f"في هذا المقال نستعرض موضوع «{topic}» بأسلوب {tone}."
    body = (
        f"يشهد مجال {topic} تطوراً ملحوظاً يستدعي من المؤسسات والصناع "
        "مواكبة أفضل الممارسات وتوظيف التقنيات الحديثة.\n\n"
        "من أهم المحاور: التخطيط، الجودة، وقياس الأثر على الجمهور المستهدف.\n\n"
        "يُنصح بمراجعة المحتوى دورياً وتحديثه وفق بيانات التفاعل والتحليلات."
    )
    conclusion = "ختاماً، الاستثمار في محتوى عربي أصيل يعزز الحضور الرقمي ويبني الثقة."
    keywords = _extract_keywords_local(topic + " " + body)
    hashtags = [f"#{k[:15]}" for k in keywords[:5]] or ["#محتوى", "#ذكاء_اصطناعي"]

    return {
        "source": "local",
        "topic": topic,
        "title": f"دليل شامل: {topic}",
        "introduction": intro,
        "body": body,
        "conclusion": conclusion,
        "keywords": keywords,
        "hashtags": hashtags,
        "content": f"{intro}\n\n{body}\n\n{conclusion}",
    }


def summarize_text(text: str, max_length: int = 200) -> dict:
    system = "لخّص النص التالي بالعربية في فقرة أو فقرتين دون فقد المعنى الأساسي."
    summary = _chat(system, text[:6000], max_tokens=400)
    if summary:
        return {"source": "openai", "summary": summary}
    local = _summarize_local(text)
    if len(local) > max_length:
        local = local[:max_length] + "..."
    return {"source": "local", "summary": local}


def suggest_titles(text_or_topic: str, count: int = 5) -> dict:
    system = "اقترح عناوين جذابة بالعربية لمحتوى ويب. أرجع قائمة مرقمة فقط."
    user = f"المحتوى أو الموضوع:\n{text_or_topic[:3000]}\nعدد العناوين: {count}"
    ai = _chat(system, user, max_tokens=300)
    if ai:
        titles = [
            re.sub(r"^\d+[\.\)\-]\s*", "", line).strip()
            for line in ai.split("\n")
            if line.strip()
        ]
        return {"source": "openai", "titles": titles[:count]}

    base = text_or_topic.strip()[:60] or "محتوى جديد"
    templates = [
        f"كل ما تحتاج معرفته عن {base}",
        f"{base}: دليل عملي للمبتدئين",
        f"كيف تستفيد من {base} في عملك؟",
        f"أهم 7 نقاط حول {base}",
        f"{base} — رؤية 2026",
    ]
    return {"source": "local", "titles": templates[:count]}


def seo_suggestions(title: str, content: str) -> dict:
    system = (
        f"{ARABIC_PROMPT_PREFIX} حلّل SEO بالعربية: meta title، meta description، "
        "كلمات مفتاحية، نصائح تحسين."
    )
    user = f"العنوان: {title}\n\nالمحتوى:\n{content[:4000]}"
    ai = _chat(system, user, max_tokens=600)
    keywords = _extract_keywords_local(title + " " + content)
    if ai:
        return {
            "source": "openai",
            "suggestions": ai,
            "keywords": keywords,
            "meta_title": title[:60],
            "meta_description": _summarize_local(content, 1)[:160],
        }
    return {
        "source": "local",
        "keywords": keywords,
        "meta_title": (title or "مقال")[:60],
        "meta_description": _summarize_local(content, 1)[:160],
        "suggestions": [
            "استخدم العنوان في أول 100 كلمة",
            "أضف عناوين فرعية H2/H3 بالعربية",
            "ضمّن الكلمات المفتاحية بشكل طبيعي",
            "حسّن وصف meta لأقل من 160 حرفاً",
            "أضف روابط داخلية لمقالات ذات صلة",
        ],
    }


def extract_keywords(text: str, limit: int = 15) -> dict:
    keywords = _extract_keywords_local(text, limit)
    return {"keywords": keywords, "count": len(keywords)}


def grammar_check(text: str) -> dict:
    """Basic checks; full grammar via OpenAI when configured."""
    issues = []
    if "  " in text:
        issues.append({"type": "spacing", "message": "مسافات مزدوجة"})
    if re.search(r"[.!?]{2,}", text):
        issues.append({"type": "punctuation", "message": "علامات ترقيم متكررة"})
    ai = _chat(
        "صحّح الأخطاء اللغوية في النص العربي وأعد النص المصحح فقط.",
        text[:3000],
        max_tokens=1500,
    )
    if ai:
        return {"source": "openai", "corrected": ai, "issues": issues}
    return {
        "source": "local",
        "corrected": text,
        "issues": issues,
        "note": "أضف OPENAI_API_KEY لتحسين التصحيح اللغوي",
    }


def arabic_content_package(topic: str) -> dict:
    """مولد محتوى عربي ذكي: مقدمة، خاتمة، هاشتاقات، SEO."""
    article = generate_article(topic)
    seo = seo_suggestions(
        article.get("title") or topic,
        article.get("content") or article.get("body", ""),
    )
    titles = suggest_titles(topic)
    return {
        "topic": topic,
        "article": article,
        "seo": seo,
        "title_suggestions": titles.get("titles", []),
    }


def detect_duplicate(content: str, existing_snippets: list[str], threshold: float = 0.35) -> dict:
    """Simple word-overlap duplicate detection."""
    def tokenize(t):
        return set(re.findall(r"[\u0600-\u06FF]+|[a-zA-Z]+", t.lower()))

    new_tokens = tokenize(content)
    if not new_tokens:
        return {"is_duplicate": False, "matches": []}

    matches = []
    for i, snippet in enumerate(existing_snippets):
        old = tokenize(snippet)
        if not old:
            continue
        overlap = len(new_tokens & old) / max(len(new_tokens | old), 1)
        if overlap >= threshold:
            matches.append({"index": i, "similarity": round(overlap, 2)})

    return {
        "is_duplicate": len(matches) > 0,
        "matches": sorted(matches, key=lambda x: -x["similarity"])[:5],
    }
