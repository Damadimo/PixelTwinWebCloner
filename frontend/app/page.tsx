"use client"

import { useState } from "react"
import CloneForm from "../components/CloneForm"
import CloneResult from "../components/CloneResult"
import ErrorMessage from "../components/ErrorMessage"
import { cloneWebsite } from "../lib/api"
import type { CloneResponse } from "../lib/types"

export default function Home() {
  const [cloneResult, setCloneResult] = useState<CloneResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [originalUrl, setOriginalUrl] = useState<string>("")

  const handleClone = async (url: string) => {
    setIsLoading(true)
    setError(null)
    setCloneResult(null)
    setOriginalUrl(url)

    try {
      const result = await cloneWebsite(url)
      setCloneResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to clone website")
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setCloneResult(null)
    setError(null)
    setOriginalUrl("")
  }

  return (
    <main className="container mx-auto px-4 py-8 max-w-4xl min-h-screen">
      {/* Header */}
      <header className="text-center mb-12">
        <div className="flex items-center justify-center gap-4 mb-8">
          {/* Pixel art logo */}
          <div className="w-16 h-16 relative pixel-art">
            <div className="w-full h-full border-2 border-pixel-beige bg-pixel-navy" style={{
              background: `
                radial-gradient(circle at 25% 25%, #f4e4bc 2px, transparent 2px),
                radial-gradient(circle at 75% 25%, #f4e4bc 2px, transparent 2px),
                radial-gradient(circle at 25% 75%, #f4e4bc 2px, transparent 2px),
                radial-gradient(circle at 75% 75%, #f4e4bc 2px, transparent 2px),
                #4a6785
              `,
              backgroundSize: '8px 8px'
            }}>
              <div className="absolute inset-2 bg-pixel-navy-dark border-2 border-pixel-beige">
                <div className="w-full h-full flex items-center justify-center">
                  <div className="w-6 h-6 bg-pixel-beige pixel-art"></div>
                </div>
              </div>
            </div>
          </div>
          <h1 className="text-4xl font-bold text-pixel-navy-dark pixel-text tracking-wider" style={{ textShadow: '2px 2px 0px #f4e4bc' }}>
            PIXELTWIN AI
          </h1>
        </div>
        <div className="pixel-card p-6 max-w-2xl mx-auto mb-6">
          <p className="text-lg text-pixel-accent pixel-text text-center font-bold">
            &gt; CLONE_WEBSITE.EXE
          </p>
          <p className="text-sm text-pixel-beige pixel-text text-center mt-2">
            Enter target URL and execute pixel-perfect replication protocol
          </p>
        </div>
      </header>

      {/* Main Content */}
      <div className="space-y-8">
        <CloneForm onSubmit={handleClone} isLoading={isLoading} />

        {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

        {cloneResult && <CloneResult result={cloneResult} originalUrl={originalUrl} onReset={handleReset} />}
      </div>

      {/* Footer */}
      <footer className="text-center mt-16 pt-8 border-t-2 border-pixel-beige">
        <div className="pixel-card p-4 max-w-md mx-auto">
          <p className="text-pixel-beige-muted pixel-text text-sm">
            &gt; SYSTEM.STATUS: <span className="text-pixel-accent font-bold">ONLINE</span><br/>
            &gt; POWERED_BY: NEXT.JS + FASTAPI + AI
          </p>
        </div>
      </footer>
    </main>
  )
}
