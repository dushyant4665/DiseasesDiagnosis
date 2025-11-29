import { useState } from 'react'
import Head from 'next/head'

export default function Home() {
  const [symptoms, setSymptoms] = useState('')
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const predict = async () => {
    if (!symptoms.trim()) {
      setError('Please enter symptoms')
      return
    }

    setLoading(true)
    setError('')
    setPredictions([])

    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms })
      })

      const data = await res.json()

      if (data.error) {
        setError(data.error)
      } else if (data.predictions && data.predictions.length > 0) {
        setPredictions(data.predictions)
      } else {
        setError('No matching diseases found')
      }
    } catch (err) {
      setError('Failed to connect to prediction service')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Head>
        <title>AI Disease Diagnosis</title>
      </Head>

      <div className="container">
        <h1>AI Disease Diagnosis</h1>
        <p className="subtitle">Enter your symptoms separated by commas</p>

        <div className="input-box">
          <input
            type="text"
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && predict()}
            placeholder="e.g., fever, cough, headache"
          />
          <button onClick={predict} disabled={loading}>
            {loading ? 'Analyzing...' : 'Predict Disease'}
          </button>
        </div>

        {error && <div className="error">{error}</div>}

        {predictions.length > 0 && (
          <div className="results">
            <h2>Predictions</h2>
            {predictions.map((p, i) => (
              <div key={i} className="prediction">
                <div className="disease-name">{p.disease}</div>
                <div className="confidence">
                  <span>Confidence: {(p.score * 100).toFixed(0)}%</span>
                  <div className="bar">
                    <div className="fill" style={{ width: `${p.score * 100}%` }}></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  )
}


