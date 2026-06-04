import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const { user } = useAuth()
  const [articles, setArticles] = useState([])
  const [stats, setStats] = useState(null)

  useEffect(() => {
    api.articles().then(setArticles).catch(() => {})
    if (user?.role === 'admin' || user?.role === 'editor') {
      api.analytics().then(setStats).catch(() => {})
    }
  }, [user])

  const recent = articles.slice(0, 5)

  return (
    <>
      <header className="page-header">
        <h1>مرحباً، {user?.username}</h1>
        <p>لوحة تحكم نظام إدارة المحتوى بالذكاء الاصطناعي</p>
      </header>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="value">{stats.total_articles}</div>
            <div className="label">إجمالي المقالات</div>
          </div>
          <div className="stat-card">
            <div className="value">{stats.published_articles}</div>
            <div className="label">منشور</div>
          </div>
          <div className="stat-card">
            <div className="value">{stats.total_views}</div>
            <div className="label">مشاهدات</div>
          </div>
        </div>
      )}

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2>آخر المقالات</h2>
          <Link to="/articles/new" className="btn-primary" style={{ padding: '0.5rem 1rem', borderRadius: 'var(--radius)' }}>
            مقال جديد
          </Link>
        </div>
        {recent.length === 0 ? (
          <p style={{ color: 'var(--muted)' }}>لا توجد مقالات بعد. أنشئ مقالاً أو استخدم مولد المحتوى العربي.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>العنوان</th>
                  <th>الحالة</th>
                  <th>المشاهدات</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((a) => (
                  <tr key={a.id}>
                    <td><Link to={`/articles/${a.id}`}>{a.title}</Link></td>
                    <td><span className={`badge badge-${a.status}`}>{a.status}</span></td>
                    <td>{a.view_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="grid-2" style={{ marginTop: '1.5rem' }}>
        <Link to="/chat" className="card" style={{ display: 'block' }}>
          <h3>💬 المساعد الذكي</h3>
          <p style={{ color: 'var(--muted)', marginTop: '0.5rem' }}>Chatbot مع توليد، تلخيص، وصوت</p>
        </Link>
        <Link to="/ai" className="card" style={{ display: 'block' }}>
          <h3>🤖 أدوات الذكاء الاصطناعي</h3>
          <p style={{ color: 'var(--muted)', marginTop: '0.5rem' }}>توليد، تلخيص، SEO، ومولد المحتوى العربي</p>
        </Link>
        <Link to="/articles/new" className="card" style={{ display: 'block' }}>
          <h3>✍️ كتابة مقال</h3>
          <p style={{ color: 'var(--muted)', marginTop: '0.5rem' }}>إضافة وتعديل المحتوى مع اقتراحات AI</p>
        </Link>
      </div>
    </>
  )
}
