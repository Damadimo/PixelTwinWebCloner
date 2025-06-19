"use client"

import { useState, type FormEvent } from "react"

interface UrlFormProps {
  onSubmit: (url: string) => Promise<void>
  isLoading: boolean
}

export default function UrlForm({ onSubmit, isLoading }: UrlFormProps) {
  const [inputUrl, setInputUrl] = useState("")

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!inputUrl.trim()) return

    let formattedUrl = inputUrl.trim()
    if (!/^https?:\/\//i.test(formattedUrl)) {
      formattedUrl = `https://${formattedUrl}`
    }

    await onSubmit(formattedUrl)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <label htmlFor="url-input" className="block font-medium">
          Enter website URL to clone
        </label>
        <div className="flex gap-2">
          <input
            id="url-input"
            type="url"
            className="flex-1 p-3 border rounded-md focus:ring-2 focus:ring-lavender focus:border-lavender dark:bg-gray-800 dark:border-gray-700"
            placeholder="https://example.com"
            value={inputUrl}
            onChange={(e) => setInputUrl(e.target.value)}
            disabled={isLoading}
            required
          />
          <button
            type="submit"
            className="btn btnPrimary"
            disabled={isLoading || !inputUrl.trim()}
            aria-busy={isLoading}
          >
            {isLoading ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Cloning...
              </>
            ) : (
              "Clone"
            )}
          </button>
        </div>
      </div>
    </form>
  )
}
