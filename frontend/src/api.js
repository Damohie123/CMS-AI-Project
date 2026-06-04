const API = '/api'

function headers() {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

async function request(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: { ...headers(), ...options.headers },
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error || 'حدث خطأ')
  return data
}

export const api = {
  login: (username, password) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  register: (body) =>
    request('/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  me: () => request('/auth/me'),
  articles: (params = '') => request(`/articles${params}`),
  article: (id, track = false) =>
    request(`/articles/${id}${track ? '?track_view=1' : ''}`),
  createArticle: (body) =>
    request('/articles', { method: 'POST', body: JSON.stringify(body) }),
  updateArticle: (id, body) =>
    request(`/articles/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteArticle: (id) =>
    request(`/articles/${id}`, { method: 'DELETE' }),
  categories: () => request('/categories'),
  createCategory: (body) =>
    request('/categories', { method: 'POST', body: JSON.stringify(body) }),
  media: () => request('/media'),
  upload: async (file) => {
    const token = localStorage.getItem('token')
    const fd = new FormData()
    fd.append('file', file)
    const res = await fetch(`${API}/media/upload`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: fd,
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'فشل الرفع')
    return data
  },
  analytics: () => request('/analytics/overview'),
  tts: (text, opts = {}) =>
    request('/ai/tts', {
      method: 'POST',
      body: JSON.stringify({ text, ...opts }),
    }),
  aiTools: () => request('/ai/tools'),
  chat: {
    help: () => request('/chat/help'),
    sessions: () => request('/chat/sessions'),
    createSession: (title) =>
      request('/chat/sessions', {
        method: 'POST',
        body: JSON.stringify({ title }),
      }),
    getSession: (id) => request(`/chat/sessions/${id}`),
    deleteSession: (id) =>
      request(`/chat/sessions/${id}`, { method: 'DELETE' }),
    sendMessage: (id, message) =>
      request(`/chat/sessions/${id}/messages`, {
        method: 'POST',
        body: JSON.stringify({ message }),
      }),
  },
  ai: {
    generate: (body) => request('/ai/generate', { method: 'POST', body: JSON.stringify(body) }),
    summarize: (text) => request('/ai/summarize', { method: 'POST', body: JSON.stringify({ text }) }),
    titles: (text) => request('/ai/titles', { method: 'POST', body: JSON.stringify({ text }) }),
    seo: (title, content) =>
      request('/ai/seo', { method: 'POST', body: JSON.stringify({ title, content }) }),
    keywords: (text) => request('/ai/keywords', { method: 'POST', body: JSON.stringify({ text }) }),
    grammar: (text) => request('/ai/grammar', { method: 'POST', body: JSON.stringify({ text }) }),
    arabicPackage: (topic) =>
      request('/ai/arabic-package', { method: 'POST', body: JSON.stringify({ topic }) }),
    duplicateCheck: (content, exclude_article_id) =>
      request('/ai/duplicate-check', {
        method: 'POST',
        body: JSON.stringify({ content, exclude_article_id }),
      }),
  },
}
