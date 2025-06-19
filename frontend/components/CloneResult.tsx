"use client"

import { useState, useEffect } from "react"
import type { CloneResponse } from "../lib/types"
import { downloadFile, formatFilename, extractHtmlContent, isValidHtml } from "../lib/utils"

interface CloneResultProps {
  result: CloneResponse
  originalUrl: string
  onReset: () => void
}

export default function CloneResult({ result, originalUrl, onReset }: CloneResultProps) {
  const [processedHtml, setProcessedHtml] = useState<string>("")
  const [htmlError, setHtmlError] = useState<string | null>(null)

  useEffect(() => {
    // Process the HTML content when component mounts or result changes
    try {
      console.log("Processing HTML content:", {
        originalLength: result.clone_html?.length || 0,
        originalPreview: result.clone_html?.substring(0, 200) || "No content"
      });
      
      const extractedHtml = extractHtmlContent(result.clone_html)
      
      console.log("After extraction:", {
        extractedLength: extractedHtml.length,
        extractedPreview: extractedHtml.substring(0, 200)
      });

      if (!isValidHtml(extractedHtml)) {
        setHtmlError("The cloned content doesn't appear to be valid HTML")
        setProcessedHtml(`
          <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5;">
              <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2 style="color: #e53e3e; margin-top: 0;">⚠️ HTML Processing Error</h2>
                <p>The cloned content doesn't appear to be valid HTML. Raw content:</p>
                <pre style="background: #f7fafc; padding: 10px; border-radius: 4px; overflow: auto; white-space: pre-wrap; max-height: 300px;">${extractedHtml.substring(0, 1000)}${extractedHtml.length > 1000 ? "..." : ""}</pre>
                <div style="margin-top: 20px;">
                  <strong>Debug Info:</strong>
                  <ul>
                    <li>Original length: ${result.clone_html?.length || 0}</li>
                    <li>Extracted length: ${extractedHtml.length}</li>
                    <li>Starts with: ${extractedHtml.substring(0, 50)}...</li>
                  </ul>
                </div>
                <div style="background: #fff3cd; padding: 15px; border-radius: 4px; margin-top: 15px; border-left: 4px solid #ffc107;">
                  <h3 style="margin-top: 0; color: #856404;">💡 Troubleshooting Tips</h3>
                  <p>This usually indicates the AI had difficulty processing this specific website. Try:</p>
                  <ul>
                    <li>Trying a different website with more static content</li>
                    <li>Checking if the website requires authentication</li>
                    <li>Downloading the HTML file to see the actual content</li>
                  </ul>
                </div>
              </div>
            </body>
          </html>
        `)
      } else {
        console.log("HTML validation passed, setting processed HTML");
        setProcessedHtml(extractedHtml)
        setHtmlError(null)
      }
    } catch (error) {
      console.error("Error processing HTML:", error);
      setHtmlError("Failed to process HTML content")
      setProcessedHtml(`
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #e53e3e;">Error processing HTML content</h2>
            <p>There was an error processing the cloned HTML content: ${error instanceof Error ? error.message : 'Unknown error'}</p>
            <p>Original content length: ${result.clone_html?.length || 0}</p>
            <div style="background: #f8d7da; padding: 15px; border-radius: 4px; margin-top: 15px; border-left: 4px solid #dc3545;">
              <h3 style="margin-top: 0; color: #721c24;">🔧 What you can do:</h3>
              <ul>
                <li>Check the browser console for more details</li>
                <li>Try cloning a different website</li>
                <li>Download the HTML file to inspect it manually</li>
                <li>Report this issue if it persists</li>
              </ul>
            </div>
          </body>
        </html>
      `)
    }
  }, [result.clone_html])

  const handleDownload = () => {
    const filename = formatFilename(originalUrl)
    // Download the processed HTML (cleaned of markdown syntax)
    downloadFile(processedHtml, filename, "text/html")
  }

  const handleViewOriginal = () => {
    window.open(originalUrl, "_blank")
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Clone Complete! 🎉</h2>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Successfully cloned: {originalUrl}</p>
            {htmlError && <p className="text-red-600 dark:text-red-400 mt-1 text-sm">⚠️ {htmlError}</p>}
          </div>
          <div className="flex gap-3">
            <button onClick={handleViewOriginal} className="btn btn-secondary flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
              View Original
            </button>
            <button onClick={handleDownload} className="btn btn-primary flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              Download HTML
            </button>
            <button onClick={onReset} className="btn btn-secondary">
              Clone Another
            </button>
          </div>
        </div>
      </div>

      {/* Preview */}
      <div className="p-6">
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden bg-white">
          <iframe
            srcDoc={processedHtml}
            className="w-full h-[600px] border-0"
            sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-downloads allow-modals"
            title="Cloned Website Preview"
            referrerPolicy="no-referrer"
            loading="lazy"
            onLoad={(e) => {
              console.log("Iframe loaded successfully");
              // Try to access iframe content for debugging
              try {
                const iframe = e.target as HTMLIFrameElement;
                const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
                if (iframeDoc) {
                  const bodyContent = iframeDoc.body?.innerHTML || "";
                  const bodyText = iframeDoc.body?.textContent || "";
                  console.log("Iframe body content length:", bodyContent.length);
                  console.log("Iframe body text length:", bodyText.length);
                  console.log("Iframe body preview:", bodyText.substring(0, 200));
                  
                  // Count meaningful elements
                  const meaningfulElements = iframeDoc.querySelectorAll('p, h1, h2, h3, h4, h5, h6, div, span, img, a, button, nav, main, section, article');
                  const visibleElements = Array.from(meaningfulElements).filter(el => 
                    el.textContent?.trim() || el.tagName.toLowerCase() === 'img'
                  );
                  
                  console.log("Iframe meaningful elements:", meaningfulElements.length);
                  console.log("Iframe visible elements:", visibleElements.length);
                  
                  if (bodyText.length < 50 || visibleElements.length < 5) {
                    console.warn("⚠️ Iframe has very little content!");
                    console.log("Content details:", {
                      textLength: bodyText.length,
                      visibleElements: visibleElements.length,
                      bodyPreview: bodyContent.substring(0, 500)
                    });
                    setHtmlError(`Preview shows minimal content (${bodyText.length} characters, ${visibleElements.length} elements). The AI may have generated a mostly empty page. Check the downloaded file for the actual content.`);
                  } else {
                    console.log("✅ Iframe content looks good:", {
                      textLength: bodyText.length,
                      visibleElements: visibleElements.length
                    });
                  }
                } else {
                  console.log("Could not access iframe content (security restrictions)");
                }
              } catch (error) {
                console.log("Could not inspect iframe content:", error);
              }
            }}
            onError={(e) => {
              console.error("Iframe error:", e);
              setHtmlError("Failed to load preview. The website might have security restrictions.");
            }}
          />
        </div>
      </div>

      {/* Debug Info */}
      <div className="p-6 border-t border-gray-200 dark:border-gray-700">
        <details className="space-y-2">
          <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100">
            🔍 Debug Information
          </summary>
          <div className="mt-2 space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <div>
              <strong>Original content length:</strong> {result.clone_html.length} characters
            </div>
            <div>
              <strong>Processed content length:</strong> {processedHtml.length} characters
            </div>
            <div>
              <strong>Content starts with:</strong>
              <code className="ml-2 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                {result.clone_html.substring(0, 50)}...
              </code>
            </div>
            <div>
              <strong>Images found:</strong> {result.images?.length || 0}
            </div>
            {result.images && result.images.length > 0 && (
              <div>
                <strong>Image URLs:</strong>
                <ul className="mt-1 ml-4 list-disc">
                  {result.images.slice(0, 5).map((img, index) => (
                    <li key={index} className="truncate">
                      {img}
                    </li>
                  ))}
                  {result.images.length > 5 && <li>... and {result.images.length - 5} more</li>}
                </ul>
              </div>
            )}
          </div>
        </details>
      </div>
    </div>
  )
}
