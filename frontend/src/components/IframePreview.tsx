"use client"

import { forwardRef } from "react"

interface IframePreviewProps {
  html: string
  onDownload: () => void
}

const IframePreview = forwardRef<HTMLIFrameElement, IframePreviewProps>(({ html, onDownload }, ref) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Cloned Website Preview</h2>
        <button onClick={onDownload} className="btn btnPrimary flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
          Download HTML
        </button>
      </div>
      <div className="w-full border rounded-md overflow-hidden bg-white dark:bg-gray-800 dark:border-gray-700">
        <iframe
          ref={ref}
          srcDoc={html}
          className="w-full h-[600px] border-0"
          sandbox="allow-same-origin"
          title="Cloned Website Preview"
        />
      </div>
    </div>
  )
})

IframePreview.displayName = "IframePreview"

export default IframePreview
