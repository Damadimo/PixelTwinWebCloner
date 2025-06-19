"use client"

import ReactCompareImage from "react-compare-image"

interface DiffSliderProps {
  originalImage: string
  cloneImage: string
}

export default function DiffSlider({ originalImage, cloneImage }: DiffSliderProps) {
  return (
    <div className="w-full border rounded-md overflow-hidden bg-white dark:bg-gray-800 dark:border-gray-700">
      <ReactCompareImage
        leftImage={originalImage}
        rightImage={cloneImage}
        leftImageLabel="Original"
        rightImageLabel="Clone"
        sliderLineWidth={2}
        sliderLineColor="#8b5cf6"
        handleSize={40}
        handle={
          <div className="w-10 h-10 bg-lavender rounded-full flex items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
            </svg>
          </div>
        }
      />
    </div>
  )
}
