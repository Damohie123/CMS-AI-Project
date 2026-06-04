import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Media() {
  const [files, setFiles] = useState([])
  const [error, setError] = useState('')

  const load = () => api.media().then(setFiles).catch((e) => setError(e.message))

  useEffect(() => { load() }, [])

  const onUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setError('')
    try {
      await api.upload(file)
      load()
    } catch (err) {
      setError(err.message)
    }
    e.target.value = ''
  }

  return (
    <>
      <header className="page-header">
        <h1>الوسائط</h1>
        <p>رفع الصور والملفات</p>
      </header>
      {error && <div className="error-msg">{error}</div>}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <label className="btn-primary" style={{ display: 'inline-block', cursor: 'pointer' }}>
          رفع ملف
          <input type="file" hidden accept="image/*,.pdf,.doc,.docx" onChange={onUpload} />
        </label>
      </div>
      <div className="card table-wrap">
        <table>
          <thead>
            <tr>
              <th>الاسم</th>
              <th>النوع</th>
              <th>الحجم</th>
              <th>رابط</th>
            </tr>
          </thead>
          <tbody>
            {files.map((f) => (
              <tr key={f.id}>
                <td>{f.original_name}</td>
                <td>{f.mime_type}</td>
                <td>{(f.size / 1024).toFixed(1)} KB</td>
                <td><a href={f.url} target="_blank" rel="noreferrer">فتح</a></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
