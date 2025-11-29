import { NextResponse } from 'next/server'

export async function POST(request) {
  try {
    const body = await request.json()
    const { symptoms } = body

    if (!symptoms || !symptoms.trim()) {
      return NextResponse.json(
        { error: 'Symptoms are required' },
        { status: 400 }
      )
    }

    const pythonUrl = process.env.PYTHON_API_URL || 'http://localhost:8000'

    const response = await fetch(`${pythonUrl}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symptoms })
    })

    if (!response.ok) {
      throw new Error('Python API error')
    }

    const data = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    // Log the error with the python URL and any nested cause for easier debugging
    console.error('Prediction error when calling Python API at', pythonUrl, error)
    const causeMessage = error && error.cause ? String(error.cause) : error.message || String(error)
    return NextResponse.json(
      { error: `Failed to get predictions from ${pythonUrl}. Cause: ${causeMessage}` },
      { status: 500 }
    )
  }
}
