import { useEffect, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'
import { Bar, Line, Doughnut } from 'react-chartjs-2'
import { api } from '../api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
)

export default function Analytics() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.analytics().then(setData).catch((e) => setError(e.message))
  }, [])

  if (error) return <div className="error-msg">{error}</div>
  if (!data) return <p style={{ color: 'var(--muted)' }}>جاري التحميل...</p>

  const viewsChart = {
    labels: data.views_by_day.map((d) => d.day),
    datasets: [{
      label: 'مشاهدات يومية',
      data: data.views_by_day.map((d) => d.count),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.2)',
      tension: 0.3,
    }],
  }

  const topChart = {
    labels: data.top_articles.slice(0, 5).map((a) => a.title.slice(0, 30)),
    datasets: [{
      label: 'مشاهدات',
      data: data.top_articles.slice(0, 5).map((a) => a.view_count),
      backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'],
    }],
  }

  const statusChart = {
    labels: ['منشور', 'مسودة'],
    datasets: [{
      data: [data.published_articles, data.draft_articles],
      backgroundColor: ['#10b981', '#6b7280'],
    }],
  }

  return (
    <>
      <header className="page-header">
        <h1>التحليلات</h1>
        <p>تقارير المشاهدات وتفاعل المحتوى</p>
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="value">{data.total_articles}</div>
          <div className="label">مقالات</div>
        </div>
        <div className="stat-card">
          <div className="value">{data.total_views}</div>
          <div className="label">مشاهدات</div>
        </div>
        <div className="stat-card">
          <div className="value">{data.published_articles}</div>
          <div className="label">منشور</div>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>المشاهدات (30 يوم)</h3>
          <Line data={viewsChart} options={{ responsive: true, plugins: { legend: { display: false } } }} />
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>حالة المحتوى</h3>
          <Doughnut data={statusChart} />
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>أكثر المقالات مشاهدة</h3>
        <Bar data={topChart} options={{ indexAxis: 'y', responsive: true, plugins: { legend: { display: false } } }} />
      </div>
    </>
  )
}
