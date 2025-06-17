import { useEffect, useState } from 'react'
import { useAuth } from './Auth'

interface Summary {
  id: string
  title: string
  created_at: string
  summary_pdf_url: string
}

export function SummaryHistory() {
  const { session } = useAuth()
  const [summaries, setSummaries] = useState<Summary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSummaries = async () => {
      try {
        const response = await fetch('http://localhost:8000/summaries')
        
        if (!response.ok) {
          throw new Error('Failed to fetch summaries')
        }

        const data = await response.json()
        setSummaries(data.summaries)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch summaries')
      } finally {
        setLoading(false)
      }
    }

    fetchSummaries()
  }, [])

  const handleDelete = async (summaryId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/summaries/${summaryId}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Failed to delete summary')
      }

      setSummaries(summaries.filter(summary => summary.id !== summaryId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete summary')
    }
  }

  if (!session) return null
  if (loading) return <div className="app-main-content">Loading...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div className="app-main-content summary-history">
      <h2>Your Summaries</h2>
      {summaries.length === 0 ? (
        <p>No summaries yet. Upload a CIM to get started!</p>
      ) : (
        <div className="summaries-grid">
          {summaries.map((summary) => (
            <div key={summary.id} className="summary-card">
              <h3>{summary.title}</h3>
              <p>Created: {new Date(summary.created_at).toLocaleDateString()}</p>
              <div className="summary-actions">
                <a
                  href={summary.summary_pdf_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="view-button"
                >
                  View Summary
                </a>
                <button
                  onClick={() => handleDelete(summary.id)}
                  className="delete-button"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
} 