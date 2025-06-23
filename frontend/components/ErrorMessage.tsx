"use client"

interface ErrorMessageProps {
  message: string
  onDismiss: () => void
}

export default function ErrorMessage({ message, onDismiss }: ErrorMessageProps) {
  return (
    <div className="bg-red-900/40 border-2 border-red-300 p-4" style={{ borderRadius: 0 }}>
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className="w-5 h-5 mr-3 pixel-art">
            <div className="w-full h-full border-2 border-red-300 bg-red-300"></div>
          </div>
          <p className="text-red-100 pixel-text font-medium">&gt; ERROR: {message}</p>
        </div>
        <button onClick={onDismiss} className="text-red-300 hover:text-red-100 pixel-text">
          <div className="w-5 h-5 pixel-art">
            <div className="w-full h-full relative">
              <div className="absolute inset-0 border border-current"></div>
              <div className="absolute inset-1 border border-current transform rotate-45"></div>
            </div>
          </div>
        </button>
      </div>
    </div>
  )
}
