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
    <main className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <header className="text-center mb-12">
        <div className="flex items-center justify-center gap-3 mb-6">
          {/* Purple 4-leaf clover logo */}
          <div className="w-12 h-12 relative">
            <svg viewBox="0 0 100 100" className="w-full h-full">
              {/* Top leaf */}
              <ellipse cx="50" cy="30" rx="15" ry="20" fill="#8b5cf6" transform="rotate(0 50 30)" />
              {/* Right leaf */}
              <ellipse cx="70" cy="50" rx="15" ry="20" fill="#8b5cf6" transform="rotate(90 70 50)" />
              {/* Bottom leaf */}
              <ellipse cx="50" cy="70" rx="15" ry="20" fill="#8b5cf6" transform="rotate(180 50 70)" />
              {/* Left leaf */}
              <ellipse cx="30" cy="50" rx="15" ry="20" fill="#8b5cf6" transform="rotate(270 30 50)" />
              {/* Center circle */}
              <circle cx="50" cy="50" r="8" fill="#7c3aed" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-lavender to-purple-700 bg-clip-text text-transparent">
            Orchid AI Website Cloner
          </h1>
        </div>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Enter any website URL and watch our AI recreate it with pixel-perfect precision
        </p>
      </header>

      {/* Main Content */}
      <div className="space-y-8">
        <CloneForm onSubmit={handleClone} isLoading={isLoading} />

        {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

        {cloneResult && <CloneResult result={cloneResult} originalUrl={originalUrl} onReset={handleReset} />}
      </div>

      {/* Footer */}
      <footer className="text-center mt-16 pt-8 border-t border-gray-200 dark:border-gray-700">
        <p className="text-gray-500 dark:text-gray-400">Powered by Next.js, FastAPI, and AI</p>
      </footer>
    </main>
  )
}
