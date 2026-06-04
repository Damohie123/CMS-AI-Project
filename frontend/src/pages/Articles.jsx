import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'

export default function Articles() {
  const { user } = useAuth()
  const [articles, setArticles] = useState([])
  const [error, setError] = useState('')

  const load = () => api.articles().then(setArticles).catch((e) => setError(e.message))

  useEffect(() => { load() }, [])

  const canDelete = user?.role === 'admin' || user?.role === 'editor'

  const handleDelete = async (id) => {
    if (!confirm('حذف هذا المقال؟')) return
    try {
      await api.deleteArticle(id)
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <>
      <header className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1>المقالات</h1>
          <p>إدارة المحتوى والتصنيفات</p>
        </div>
        <Link to="/articles/new" className="btn-primary" style={{ padding: '0.55rem 1.2rem' }}>+ مقال جديد</Link>
      </header>
      {error && <div className="error-msg">{error}</div>}
      <div className="card table-wrap">
        <table>
          <thead>
            <tr>
              <th>العنوان</th>
              <th>الكاتب</th>
              <th>الحالة</th>
              <th>المشاهدات</th>
              <th>إجراءات</th>
            </tr>
          </thead>
          <tbody>
            {articles.map((a) => (
              <tr key={a.id}>
                <td>{a.title}</td>
                <td>{a.author}</td>
                <td><span className={`badge badge-${a.status}`}>{a.status}</span></td>
                <td>{a.view_count}</td>
                <td className="actions">
                  <Link to={`/articles/${a.id}`} className="btn-ghost" style={{ padding: '0.35rem 0.75rem' }}>تعديل</Link>
                  {canDelete && (
                    <button type="button" className="btn-danger" style={{ padding: '0.35rem 0.75rem' }} onClick={() => handleDelete(a.id)}>
                      حذف
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {articles.length === 0 && <p style={{ padding: '1rem', color: 'var(--muted)' }}>لا مقالات</p>}
      </div>
    </>
  )
}
