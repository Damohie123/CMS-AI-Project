import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Articles from './pages/Articles'
import ArticleEditor from './pages/ArticleEditor'
import AIStudio from './pages/AIStudio'
import Chat from './pages/Chat'
import Media from './pages/Media'
import Analytics from './pages/Analytics'

function PrivateRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <p style={{ padding: '2rem', color: 'var(--muted)' }}>جاري التحميل...</p>
  if (!user) return <Navigate to="/login" replace />
  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="articles" element={<Articles />} />
        <Route path="articles/new" element={<ArticleEditor />} />
        <Route path="articles/:id" element={<ArticleEditor />} />
        <Route path="chat" element={<Chat />} />
        <Route path="ai" element={<AIStudio />} />
        <Route path="media" element={<Media />} />
        <Route path="analytics" element={<Analytics />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  )
}
