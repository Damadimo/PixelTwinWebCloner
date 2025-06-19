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
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="url-input" className="block text-sm font-medium mb-2">
            Website URL to Clone
          </label>
          <div className="flex gap-3">
            <input
              id="url-input"
              type="url"
              className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-lavender focus:border-lavender dark:bg-gray-700 dark:text-white"
              placeholder="https://example.com"
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
                  Cloning...
                </>
              ) : (
                "Clone Website"
              )}
            </button>
          </div>
        </div>

        {/* Demo URLs */}
        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">Try these demo websites:</p>
          <div className="flex flex-wrap gap-2">
            {demoUrls.map((demoUrl) => (
              <button
                key={demoUrl}
                type="button"
                className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
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
