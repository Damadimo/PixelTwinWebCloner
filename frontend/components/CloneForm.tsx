"use client"

import type React from "react"

import { useState } from "react"
import LoadingSpinner from "./LoadingSpinner"

interface CloneFormProps {
  onSubmit: (url: string) => Promise<void>
  isLoading: boolean
}

export default function CloneForm({ onSubmit, isLoading }: CloneFormProps) {
  const [url, setUrl] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return

    let formattedUrl = url.trim()
    if (!/^https?:\/\//i.test(formattedUrl)) {
      formattedUrl = `https://${formattedUrl}`
    }

    await onSubmit(formattedUrl)
  }

  const demoUrls = ["https://stripe.com", "https://vercel.com", "https://github.com", "https://tailwindcss.com"]

  return (
    <div className="pixel-card p-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="url-input" className="block text-sm font-medium mb-3 pixel-text text-pixel-accent font-bold">
            &gt; INPUT_TARGET_URL:
          </label>
          <div className="flex gap-3">
            <input
              id="url-input"
              type="url"
              className="flex-1 px-4 py-3 pixel-border text-pixel-beige-light pixel-text focus:ring-2 focus:ring-pixel-accent focus:border-pixel-accent placeholder:text-pixel-beige-muted"
              style={{ background: 'rgba(45, 62, 82, 0.5)' }}
              placeholder="https://target-site.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isLoading}
              required
            />
            <button
              type="submit"
              className="btn btn-primary px-8 py-3 flex items-center gap-2"
              disabled={isLoading || !url.trim()}
            >
              {isLoading ? (
                <>
                  <LoadingSpinner size="sm" />
                  EXECUTING...
                </>
              ) : (
                "EXECUTE"
              )}
            </button>
          </div>
        </div>

        {/* Demo URLs */}
        <div>
          <p className="text-sm text-pixel-beige-muted mb-3 pixel-text">&gt; DEMO_TARGETS:</p>
          <div className="flex flex-wrap gap-2">
            {demoUrls.map((demoUrl) => (
              <button
                key={demoUrl}
                type="button"
                className="px-3 py-2 text-sm text-pixel-beige pixel-border hover:bg-pixel-beige hover:text-pixel-navy-dark transition-colors pixel-text"
                style={{ background: 'rgba(45, 62, 82, 0.3)' }}
                onClick={() => setUrl(demoUrl)}
                disabled={isLoading}
              >
                {demoUrl.replace("https://", "")}
              </button>
            ))}
          </div>
        </div>
      </form>
    </div>
  )
}
