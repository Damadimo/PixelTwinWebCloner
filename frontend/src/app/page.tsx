"use client"

import { useState, useRef, useEffect } from "react"
import UrlForm from "@/components/UrlForm"
import IframePreview from "@/components/IframePreview"
import DiffSlider from "@/components/DiffSlider"
import Toast from "@/components/Toast"
import { cloneWebsite, getScreenshot, refineClone } from "@/lib/api"
import { saveAs } from "file-saver"
import html2canvas from "html2canvas"

export default function Home() {
  const [url, setUrl] = useState("")
  const [clonedHtml, setClonedHtml] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [originalScreenshot, setOriginalScreenshot] = useState<string | null>(null)
  const [cloneScreenshot, setCloneScreenshot] = useState<string | null>(null)
  const [refinePrompt, setRefinePrompt] = useState("")
  const [isRefining, setIsRefining] = useState(false)
  const iframeRef = useRef<HTMLIFrameElement>(null)

  const handleClone = async (inputUrl: string) => {
    setUrl(inputUrl)
    setIsLoading(true)
    setError(null)
    setClonedHtml(null)
    setOriginalScreenshot(null)
    setCloneScreenshot(null)

    try {
      const { html } = await cloneWebsite(inputUrl)
      setClonedHtml(html)

      // Get screenshot of original website
      const screenshot = await getScreenshot(inputUrl)
      setOriginalScreenshot(screenshot)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to clone website")
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefine = async () => {
    if (!clonedHtml || !refinePrompt.trim()) return

    setIsRefining(true)
    setError(null)

    try {
      const { html } = await refineClone(clonedHtml, refinePrompt)
      setClonedHtml(html)
      setRefinePrompt("")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to refine clone")
    } finally {
      setIsRefining(false)
    }
  }

  const handleDownload = () => {
    if (!clonedHtml) return

    const blob = new Blob([clonedHtml], { type: "text/html" })
    const filename = `${url.replace(/^https?:\/\//, "").replace(/[^\w]/g, "-")}-clone.html`
    saveAs(blob, filename)
  }

  const captureCloneScreenshot = async () => {
    if (!iframeRef.current || !iframeRef.current.contentDocument?.body) return

    try {
      const canvas = await html2canvas(iframeRef.current.contentDocument.body)
      const dataUrl = canvas.toDataURL("image/png")
      setCloneScreenshot(dataUrl)
    } catch (err) {
      console.error("Failed to capture clone screenshot:", err)
    }
  }

  // Capture clone screenshot when iframe loads
  useEffect(() => {
    if (clonedHtml && iframeRef.current) {
      const iframe = iframeRef.current
      const handleLoad = () => {
        captureCloneScreenshot()
      }

      iframe.addEventListener("load", handleLoad)
      return () => {
        iframe.removeEventListener("load", handleLoad)
      }
    }
  }, [clonedHtml])

  return (
    <main className="container mx-auto px-4 py-8 max-w-[900px]">
      <header className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 relative">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-8 flex flex-wrap">
                <div className="w-3.5 h-3.5 bg-lavender rounded-full m-0.5"></div>
                <div className="w-3.5 h-3.5 bg-lavender rounded-full m-0.5"></div>
                <div className="w-3.5 h-3.5 bg-lavender rounded-full m-0.5"></div>
                <div className="w-3.5 h-3.5 bg-lavender rounded-full m-0.5"></div>
              </div>
            </div>
          </div>
          <h1 className="text-2xl font-bold">Orchid AI Website Cloner</h1>
        </div>
      </header>

      <UrlForm onSubmit={handleClone} isLoading={isLoading} />

      {error && <Toast message={error} type="error" onClose={() => setError(null)} />}

      {clonedHtml && (
        <div className="mt-8 space-y-6">
          <IframePreview html={clonedHtml} ref={iframeRef} onDownload={handleDownload} />

          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Refine Clone</h2>
            <div className="flex gap-2">
              <textarea
                className="w-full p-3 border rounded-md dark:bg-gray-800 dark:border-gray-700"
                placeholder="e.g. Make it dark mode"
                value={refinePrompt}
                onChange={(e) => setRefinePrompt(e.target.value)}
                rows={2}
                disabled={isRefining}
              />
              <button
                className="btn btnPrimary whitespace-nowrap self-start"
                onClick={handleRefine}
                disabled={isRefining || !refinePrompt.trim()}
              >
                {isRefining ? (
                  <>
                    <svg
                      className="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Refining...
                  </>
                ) : (
                  "Refine"
                )}
              </button>
            </div>
          </div>

          {originalScreenshot && cloneScreenshot && (
            <div className="mt-8 space-y-4">
              <h2 className="text-xl font-semibold">Before / After Comparison</h2>
              <DiffSlider originalImage={originalScreenshot} cloneImage={cloneScreenshot} />
            </div>
          )}
        </div>
      )}
    </main>
  )
}
