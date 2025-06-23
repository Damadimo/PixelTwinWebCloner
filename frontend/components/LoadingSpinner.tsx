interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg"
  className?: string
}

export default function LoadingSpinner({ size = "md", className = "" }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
  }

  return (
    <div className={`${sizeClasses[size]} ${className} pixel-art`}>
      <div className="w-full h-full animate-spin">
        <div className="w-full h-full relative">
          <div className="absolute inset-0 border-2 border-current border-t-transparent"></div>
          <div className="absolute inset-1 border border-current border-t-transparent animate-spin" style={{animationDirection: 'reverse', animationDuration: '0.75s'}}></div>
        </div>
      </div>
    </div>
  )
}
