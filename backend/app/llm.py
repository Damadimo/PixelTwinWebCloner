import os
import json
import asyncio
from typing import Dict, Optional
from dotenv import load_dotenv

import anthropic                # pip install anthropic
from openai import AsyncOpenAI                  # pip install openai
from google import genai  # pip install google-generativeai
from bs4 import BeautifulSoup   # pip install beautifulsoup4
import traceback
from .scraper import scrape_site

# Load API keys from environment (python-dotenv can automatically load from .env)

load_dotenv(override=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY").strip()
GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY")


def choose_model() -> Dict[str, str]:
    """
    Return a dict like {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}.
    Fall back to OpenAI GPT-4 if no other keys are present.
    """
    if ANTHROPIC_API_KEY:
        return {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}
    elif GEMINI_API_KEY:
        return {"provider": "google", "model": "gemini-2.0-flash"}
    elif OPENAI_API_KEY:
        return {"provider": "openai", "model": "gpt-4.1"}
    else:
        raise RuntimeError("No LLM credentials found; set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY")


async def generate_clone_html(
    scraped_html: str,
    scraped_css_list: Optional[list] = None,
    metadata: Optional[dict] = None
) -> str:
    """
    Given the scraped HTML (with CSS inlined) and optional CSS files,
    call the chosen LLM to produce a static HTML clone. Return the clone as a string.
    """
    config = choose_model()
    provider = config["provider"]
    model_name = config["model"]

    if not scraped_html.strip():
        raise ValueError("Empty HTML; nothing to clone")

    # 1) Assemble the combined context
    parts = [scraped_html]
    if scraped_css_list:
        for css in scraped_css_list:
            parts.append("/* External CSS: */")
            parts.append(css)
    full_context = "\n\n".join(parts)
    primary_font = metadata.get("fonts") or "sans-serif"

    # 2) Extract metadata values (with sensible defaults)
    page_title   = metadata.get("title") if metadata and metadata.get("title") else "Untitled Page"
    theme_color  = metadata.get("theme_color") or "#ffffff"
    charset      = metadata.get("charset") or "utf-8"

    parts.append(f"\n/* The page's title is '{page_title}', its primary theme color is {theme_color}, it uses the {primary_font} font family, and its charset is {charset}. */\n")

    # 2) Build the prompt
    instruction = (
        "You are tasked with creating a PIXEL-PERFECT visual clone. The result must be VISUALLY IDENTICAL to the original webpage.\n\n"
        
        "## ABSOLUTE VISUAL REPLICATION REQUIREMENTS:\n"
        "1. **EXACT COLORS** - Use every hex code, RGB value, and color from the original CSS\n"
        "2. **PRESERVE ALL BACKGROUNDS** - Gradients, images, patterns must be IDENTICAL\n"
        "3. **KEEP ALL IMAGES** - Every image, logo, icon with original src URLs\n"
        "4. **MAINTAIN EXACT FONTS** - Font families, sizes, weights exactly as original\n"
        "5. **PRESERVE LAYOUT** - Spacing, positioning, dimensions exactly as original\n"
        "6. **COPY ALL STYLING** - Shadows, borders, effects, transitions (but remove animations)\n\n"
        
        "## CRITICAL VISUAL ELEMENTS TO PRESERVE:\n"
        "- **Background gradients and colors** - Copy gradient CSS exactly\n"
        "- **Background images** - Preserve all background-image URLs\n"
        "- **Brand colors** - Maintain exact brand color palette\n"
        "- **Typography styling** - Font weights, sizes, letter-spacing\n"
        "- **Visual effects** - Box-shadows, text-shadows, borders\n"
        "- **Layout structure** - Grid systems, flexbox, positioning\n"
        "- **Image assets** - All logos, icons, decorative images\n\n"
        
        "## CSS CONSOLIDATION REQUIREMENTS:\n"
        "1. **Include ALL provided CSS** - Every single CSS rule must be included\n"
        "2. **Preserve CSS variables** - All custom properties and their values\n"
        "3. **Maintain media queries** - Responsive breakpoints and rules\n"
        "4. **Keep vendor prefixes** - All -webkit-, -moz-, -ms- prefixes\n"
        "5. **Preserve @imports and @font-face** - External fonts and resources\n"
        "6. **Copy gradient syntax exactly** - Linear, radial gradients with exact values\n\n"
        
        "## HTML STRUCTURE PRESERVATION:\n"
        "- Use the EXACT same HTML structure from the scraped content\n"
        "- Keep all class names, IDs, and data attributes\n"
        "- Preserve all img src URLs exactly as provided\n"
        "- Maintain all semantic elements (nav, main, header, section)\n"
        "- Keep all text content exactly as it appears\n"
        "- Preserve form elements with their styling\n\n"
        
        "## BACKGROUND AND IMAGE HANDLING:\n"
        "- **Background gradients**: Copy CSS gradient syntax exactly\n"
        "- **Background images**: Preserve all background-image URLs\n"
        "- **IMG tags**: Keep all src attributes unchanged\n"
        "- **SVG elements**: Preserve inline SVGs completely\n"
        "- **Icon fonts**: Maintain icon font classes and CSS\n"
        "- **Decorative elements**: Keep all visual flourishes and effects\n\n"
        
        "## COLOR PRESERVATION:\n"
        "- Extract and use EVERY color from the original CSS\n"
        "- Preserve hex codes, RGB, RGBA, HSL values exactly\n"
        "- Maintain CSS custom properties (--color-name: value)\n"
        "- Keep gradient color stops and positions exact\n"
        "- Preserve opacity and transparency values\n\n"
        
        "## LAYOUT AND SPACING:\n"
        "- Copy margins, padding, gaps exactly\n"
        "- Preserve flexbox and grid properties\n"
        "- Maintain positioning (absolute, relative, fixed)\n"
        "- Keep z-index values for layering\n"
        "- Preserve viewport units (vw, vh, vmin, vmax)\n\n"
        
        "## JAVASCRIPT REMOVAL (WHILE PRESERVING VISUALS):\n"
        "- Remove <script> tags but keep all visual elements\n"
        "- Remove event handlers but preserve CSS classes\n"
        "- Show the loaded/active state of dynamic elements\n"
        "- Keep data attributes that affect styling\n"
        "- Preserve CSS classes added by JavaScript\n\n"
        
        "## QUALITY CONTROL CHECKLIST:\n"
        "✅ Background colors/gradients match original exactly\n"
        "✅ All images display with original sources\n"
        "✅ Font families and sizes match perfectly\n"
        "✅ Spacing and layout proportions identical\n"
        "✅ Visual effects (shadows, borders) preserved\n"
        "✅ Brand colors and visual identity intact\n"
        "✅ No visual elements missing or changed\n\n"
        
        "## FAILURE CONDITIONS (NEVER DO THESE):\n"
        "❌ NEVER use generic colors instead of original colors\n"
        "❌ NEVER remove background gradients or images\n"
        "❌ NEVER change font families or styling\n"
        "❌ NEVER alter spacing or layout structure\n"
        "❌ NEVER remove or modify image sources\n"
        "❌ NEVER simplify or strip away visual effects\n\n"
        
        "## OUTPUT REQUIREMENTS:\n"
        "Return ONLY the complete HTML document starting with <!DOCTYPE html>\n"
        "Include ALL CSS in a single <style> block in the <head>\n"
        "The result must be visually indistinguishable from the original\n\n"
        
        "Create a pixel-perfect visual clone that preserves every color, gradient, image, and visual effect:"
    )

    try:
        # 3) Call the appropriate LLM API
        if provider == "anthropic":
            clone_html = await _call_anthropic_api(model_name, instruction, full_context)
        elif provider == "openai":
            clone_html = await _call_openai_api(model_name, instruction, full_context)
        elif provider == "google":
            clone_html = await _call_gemini_api(model_name, instruction, full_context)
        else:
            raise RuntimeError(f"Unsupported provider: {provider}")

        # 4) Post-process: simple tag validation / sanitization
        clone_html = _sanitize_and_validate_html(clone_html)

        return clone_html

    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f"Failed to generate clone with {provider}") from e



async def _call_anthropic_api(model_name: str, instruction: str, context: str) -> str:
    
    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    
    try:
        message = await client.messages.create(
            model=model_name,
            max_tokens=4096,  # Adjust based on expected output length
            temperature=0.2,
            system="You are a helpful assistant for generating HTML clones.",
            messages=[
                {
                    "role": "user",
                    "content": instruction
                },
                {
                    "role": "user",
                    "content": context
                },
            ]
        )
        return message.content[0].text.strip()
    except Exception as e:
        raise RuntimeError(f"Anthropic API error: {str(e)}")


async def _call_openai_api(model_name: str, instruction: str, context: str) -> str:


    client = AsyncOpenAI(api_key = OPENAI_API_KEY)
    
    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for generating HTML clones."},
                {"role": "user", "content": f"{instruction}\n\n{context}"}
            ],
            temperature=0.2,
            max_tokens=160000  # Adjust based on expected output length
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}")


async def _call_gemini_api(model_name: str, instruction: str, context: str) -> str:
    """Call Google Gemini API."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    try:
        response = client.models.generate_content(
            model=model_name,
            config=genai.types.GenerateContentConfig(
                system_instruction=instruction),
            contents=[context]
        )
        return response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {str(e)}")


def _sanitize_and_validate_html(html_str: str) -> str:
    """
    Basic post-processing of the LLM output. At minimum:
    - Ensure there's a <!DOCTYPE html> and <html>…</html> root.
    - Remove any <script> tags that may have slipped through.
    - Optionally, run an HTML formatter or linter to catch unclosed tags.
    """
    try:
        soup = BeautifulSoup(html_str, "html.parser")

        # 1) Remove any script tags in case the model inserted them anyway
        for script in soup.find_all("script"):
            script.decompose()

        # 2) Remove any potentially harmful attributes
        dangerous_attrs = ['onload', 'onclick', 'onerror', 'onmouseover']
        for tag in soup.find_all():
            for attr in dangerous_attrs:
                if tag.has_attr(attr):
                    del tag[attr]

        # 3) Ensure a DOCTYPE (naïve check)
        html_content = str(soup)
        if not html_content.lstrip().lower().startswith("<!doctype html>"):
            # Prepend a DOCTYPE
            html_content = "<!DOCTYPE html>\n" + html_content

        return html_content

    except Exception as e:
        # If BeautifulSoup fails, return original with basic script removal
        import re
        html_str = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html_str, flags=re.IGNORECASE)
        
        if not html_str.lstrip().lower().startswith("<!doctype html>"):
            html_str = "<!DOCTYPE html>\n" + html_str
            
        return html_str


# Synchronous wrapper for backward compatibility
def generate_clone_html_sync(
    scraped_html: str,
    scraped_css_list: Optional[list] = None,
    metadata: Optional[dict] = None
) -> str:
    """Synchronous wrapper for generate_clone_html."""
    return asyncio.run(generate_clone_html(scraped_html, scraped_css_list, metadata))