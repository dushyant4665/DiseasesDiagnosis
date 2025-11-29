export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { symptoms } = req.body

  if (!symptoms || !symptoms.trim()) {
    return res.status(400).json({ error: 'Symptoms cannot be empty' })
  }

  try {
    const modelUrl = process.env.MODEL_URL || 'http://localhost:8000'
    
    const response = await fetch(`${modelUrl}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symptoms })
    })

    if (!response.ok) {
      throw new Error('Model service error')
    }

    const data = await response.json()
    res.status(200).json(data)
  } catch (error) {
    // Add more context to the error returned so the client can see which URL failed
    const causeMessage = error && error.cause ? String(error.cause) : error.message || String(error)
    console.error('Model API error when calling', modelUrl, causeMessage)
    res.status(500).json({ error: `Failed to get predictions from ${modelUrl}. Cause: ${causeMessage}` })
  }
}