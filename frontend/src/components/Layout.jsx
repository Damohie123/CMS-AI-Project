import { Link, NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './Layout.css'

const nav = [
  { to: '/', label: 'لوحة التحكم' },
  { to: '/articles', label: 'المقالات' },
  { to: '/chat', label: 'المساعد الذكي' },
  { to: '/ai', label: 'الذكاء الاصطناعي' },
  { to: '/media', label: 'الوسائط' },
  { to: '/analytics', label: 'التحليلات', roles: ['admin', 'editor'] },
]

export default function Layout() {
  const { user, logout } = useAuth()

  const links = nav.filter(
    (n) => !n.roles || n.roles.includes(user?.role) || user?.role === 'admin',
  )

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon">✦</span>
          <div>
            <strong>CMS-AI</strong>
            <small>إدارة محتوى ذكية</small>
          </div>
        </div>
        <nav>
          {links.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span className={`badge badge-${user?.role}`}>{roleLabel(user?.role)}</span>
          <p>{user?.username}</p>
          <button type="button" className="btn-ghost" onClick={logout}>
            تسجيل الخروج
          </button>
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}

function roleLabel(role) {
  const map = { admin: 'مدير', editor: 'محرر', writer: 'كاتب' }
  return map[role] || role
}
