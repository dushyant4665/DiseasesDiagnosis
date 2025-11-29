'use client'

import { useState } from 'react'

export default function Home() {
  const [symptoms, setSymptoms] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const diagnose = async () => {
    if (!symptoms.trim()) {
      setError('Please enter your symptoms')
      return
    }

    setLoading(true)
    setError('')
    setResults([])

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms: symptoms.trim() })
      })

      const data = await response.json()

      if (data.error) {
        setError(data.error)
      } else if (data.predictions && data.predictions.length > 0) {
        setResults(data.predictions)
      } else {
        setError('No matching diseases found. Please try different symptoms.')
      }
    } catch (err) {
      setError('Failed to connect to diagnosis service. Make sure Python server is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            AI Disease Diagnosis
          </h1>
          <p className="text-slate-400 text-lg">
            Enter your symptoms and let AI predict possible diseases
          </p>
        </div>

        <div className="card">
          <label className="block text-lg font-semibold mb-3 text-blue-300">
            Enter Your Symptoms
          </label>
          
          <textarea
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && diagnose()}
            // placeholder="Type your symptoms... e.g. fever and cough, chest pain, pain in neck..."
          />

          <div className="mt-6 flex justify-center">
            <button 
              onClick={diagnose} 
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Analyzing...' : 'Diagnose'}
            </button>
          </div>

          {loading && (
            <div className="flex justify-center mt-8">
              <div className="spinner"></div>
            </div>
          )}

          {error && (
            <div className="mt-6 p-4 bg-red-900/20 border border-red-500/50 rounded-lg text-red-300">
              {error}
            </div>
          )}
        </div>

        {results.length > 0 && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold mb-6 text-blue-300">
              Diagnosis Results
            </h2>
            
            {results.map((result, index) => (
              <div key={index} className="result-card">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-xl font-bold text-white">
                    {result.disease}
                  </h3>
                  <span className="text-2xl font-bold text-blue-400">
                    {Math.round(result.confidence * 100)}%
                  </span>
                </div>

                <div className="confidence-bar">
                  <div 
                    className="confidence-fill"
                    style={{ width: `${result.confidence * 100}%` }}
                  ></div>
                </div>

                {result.matched_symptoms && (
                  <div className="mt-4">
                    <p className="text-sm text-slate-400 mb-2">Matched Symptoms:</p>
                    <div className="flex flex-wrap gap-2">
                      {result.matched_symptoms.map((symptom, i) => (
                        <span 
                          key={i}
                          className="px-3 py-1 bg-blue-900/30 text-blue-300 rounded-full text-sm"
                        >
                          {symptom}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {result.recommendation && (
                  <div className="mt-4 p-3 bg-slate-800/50 rounded-lg">
                    <p className="text-sm text-slate-300">
                      <span className="font-semibold text-blue-400">Recommendation: </span>
                      {result.recommendation}
                    </p>
                  </div>
                )}
              </div>
            ))}

            <div className="mt-6 p-4 bg-yellow-900/20 border border-yellow-500/30 rounded-lg">
              <p className="text-sm text-yellow-200">
                ⚠️ <strong>Disclaimer:</strong> This is an AI-powered tool for educational purposes. 
                Always consult a healthcare professional for accurate medical diagnosis.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}



