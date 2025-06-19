# Website Visual Cloner

## Project Overview
This project is a full-stack application that allows users to visually clone any public website as a static HTML snapshot. The goal is to create a pixel-perfect, visually indistinguishable static copy of the original site, including all colors, gradients, fonts, images, and layout. The app is designed to work generically for any website, including modern JavaScript-heavy sites.

## Architecture
- **Frontend:** Built with Next.js (React), provides a simple UI for entering a website URL, viewing the clone, and downloading the static HTML. The frontend communicates with the backend via REST API.
- **Backend:** FastAPI (Python) service that handles scraping, CSS extraction, and LLM-powered HTML generation. It uses Playwright for dynamic rendering and BeautifulSoup for HTML parsing. The backend ensures all original styling, images, and layout are preserved.
- **Scraper:** Uses Playwright to render the page, extract computed styles, gradients, and all CSS. Inlines all CSS and makes URLs absolute for static use.
- **LLM Integration:** The backend uses an LLM (Anthropic, OpenAI, or Gemini) to generate a static HTML clone, with strict instructions to preserve all visual details. Multiple validation and fallback layers ensure the output is never blank and always visually faithful.

## How to Run (Windows)
1. **Clone the repository** and open the project folder in your terminal.
2. **Backend setup:**
   - Navigate to the `backend` folder: `cd backend`
   - Create a virtual environment and activate it:
     - `python -m venv .venv`
     - `.venv\Scripts\activate`
   - Install dependencies: `uv pip install --requirements requirements.txt`
   - Install Playwright browsers: `playwright install`
   - Set your LLM API keys in a `.env` file (see `.env.example` if provided)
   - Start the backend server:
     - `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
3. **Frontend setup:**
   - Open a new terminal and navigate to the `frontend` folder: `cd frontend`
   - Install dependencies: `npm install`
   - Start the development server: `npm run dev`
   - The app will be available at `http://localhost:3000`

## How it Works
- Enter a website URL and click "Clone Website".
- The backend scrapes the site, inlines all CSS, and extracts all visual styles.
- The LLM receives strict instructions to generate a static HTML clone that is visually identical to the original.
- The frontend displays the result in an iframe and allows you to download the HTML.
- Multiple validation and fallback layers ensure the output is always substantial and visually faithful, even for complex sites.

## Troubleshooting
- If the clone appears blank or missing styles, check the backend logs for errors.
- Ensure your LLM API keys are set correctly in the backend environment.
- Some sites with advanced anti-bot measures may not be fully cloneable.
- For best results, use the latest version of Chrome and keep Playwright up to date.

## Credits
- Frontend: Next.js, React
- Backend: FastAPI, Playwright, BeautifulSoup
- LLM: Anthropic Claude, OpenAI GPT-4, or Google Gemini (configurable)
- Created by Adam and contributors.
