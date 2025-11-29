import './globals.css'

export const metadata = {
  title: 'AI Disease Diagnosis',
  description: 'AI-powered symptom checker and disease predictor',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}



