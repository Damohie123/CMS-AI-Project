import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'

export default function ArticleEditor() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isNew = !id || id === 'new'

  const [form, setForm] = useState({
    title: '',
    content: '',
    summary: '',
    status: 'draft',
    seo_title: '',
    seo_description: '',
    keywords: '',
    category_id: '',
  })
  const [categories, setCategories] = useState([])
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  const [ttsLoading, setTtsLoading] = useState(false)

  useEffect(() => {
    api.categories().then(setCategories).catch(() => {})
    if (!isNew) {
      api.article(id).then((a) => {
        setForm({
          title: a.title,
          content: a.content,
          summary: a.summary || '',
          status: a.status,
          seo_title: a.seo_title || '',
          seo_description: a.seo_description || '',
          keywords: a.keywords || '',
          category_id: a.category_id || '',
        })
      }).catch((e) => setError(e.message))
    }
  }, [id, isNew])

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const save = async () => {
    setError('')
    setMsg('')
    const body = {
      ...form,
      category_id: form.category_id ? Number(form.category_id) : null,
    }
    try {
      if (isNew) {
        const created = await api.createArticle(body)
        navigate(`/articles/${created.id}`)
      } else {
        await api.updateArticle(id, body)
        setMsg('تم الحفظ')
      }
    } catch (e) {
      setError(e.message)
    }
  }

  const runAi = async (action) => {
    setAiLoading(true)
    setError('')
    try {
      if (action === 'summarize') {
        const r = await api.ai.summarize(form.content)
        set('summary', r.summary)
      } else if (action === 'titles') {
        const r = await api.ai.titles(form.content || form.title)
        if (r.titles?.[0]) set('title', r.titles[0])
      } else if (action === 'seo') {
        const r = await api.ai.seo(form.title, form.content)
        set('seo_title', r.meta_title || form.title)
        set('seo_description', r.meta_description || '')
        set('keywords', (r.keywords || []).join(', '))
      } else if (action === 'keywords') {
        const r = await api.ai.keywords(form.content)
        set('keywords', (r.keywords || []).join(', '))
      } else if (action === 'grammar') {
        const r = await api.ai.grammar(form.content)
        set('content', r.corrected)
      } else if (action === 'duplicate') {
        const r = await api.ai.duplicateCheck(form.content, isNew ? null : Number(id))
        if (r.is_duplicate) setError('تحذير: محتوى مشابه لمقالات موجودة')
        else setMsg('لا يوجد تكرار واضح')
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setAiLoading(false)
    }
  }

  return (
    <>
      <header className="page-header">
        <h1>{isNew ? 'مقال جديد' : 'تعديل المقال'}</h1>
      </header>
      {error && <div className="error-msg">{error}</div>}
      {msg && <div className="success-msg">{msg}</div>}

      <div className="card" style={{ marginBottom: '1rem' }}>
        <p style={{ color: 'var(--muted)', marginBottom: '0.75rem' }}>أدوات AI سريعة:</p>
        <div className="actions">
          <button
            type="button"
            className="btn-ghost"
            disabled={ttsLoading || !form.content.trim()}
            onClick={async () => {
              setTtsLoading(true)
              try {
                const audio = await api.tts(form.summary || form.content.slice(0, 500))
                const el = new Audio(`data:audio/mp3;base64,${audio.audio_base64}`)
                await el.play()
              } catch (e) {
                setError(e.message)
              } finally {
                setTtsLoading(false)
              }
            }}
          >
            {ttsLoading ? 'جاري التشغيل...' : '🔊 استماع'}
          </button>
          {['summarize', 'titles', 'seo', 'keywords', 'grammar', 'duplicate'].map((a) => (
            <button key={a} type="button" className="btn-ghost" disabled={aiLoading} onClick={() => runAi(a)}>
              {aiLabel(a)}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="form-group">
          <label>العنوان</label>
          <input value={form.title} onChange={(e) => set('title', e.target.value)} />
        </div>
        <div className="form-group">
          <label>المحتوى</label>
          <textarea value={form.content} onChange={(e) => set('content', e.target.value)} rows={12} />
        </div>
        <div className="form-group">
          <label>ملخص</label>
          <textarea value={form.summary} onChange={(e) => set('summary', e.target.value)} rows={3} />
        </div>
        <div className="grid-2">
          <div className="form-group">
            <label>الحالة</label>
            <select value={form.status} onChange={(e) => set('status', e.target.value)}>
              <option value="draft">مسودة</option>
              <option value="published">منشور</option>
            </select>
          </div>
          <div className="form-group">
            <label>التصنيف</label>
            <select value={form.category_id} onChange={(e) => set('category_id', e.target.value)}>
              <option value="">—</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name_ar || c.name}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="form-group">
          <label>عنوان SEO</label>
          <input value={form.seo_title} onChange={(e) => set('seo_title', e.target.value)} />
        </div>
        <div className="form-group">
          <label>وصف SEO</label>
          <input value={form.seo_description} onChange={(e) => set('seo_description', e.target.value)} />
        </div>
        <div className="form-group">
          <label>كلمات مفتاحية</label>
          <input value={form.keywords} onChange={(e) => set('keywords', e.target.value)} />
        </div>
        <div className="actions">
          <button type="button" className="btn-primary" onClick={save}>حفظ</button>
          <button type="button" className="btn-ghost" onClick={() => navigate('/articles')}>إلغاء</button>
        </div>
      </div>
    </>
  )
}

function aiLabel(a) {
  const m = {
    summarize: 'تلخيص',
    titles: 'اقتراح عنوان',
    seo: 'تحسين SEO',
    keywords: 'كلمات مفتاحية',
    grammar: 'تصحيح لغوي',
    duplicate: 'كشف التكرار',
  }
  return m[a] || a
}
