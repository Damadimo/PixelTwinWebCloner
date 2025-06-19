# scraper.py
import asyncio
import logging
import random
import re
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

# ───────────────────────────────────────────────────────────────────────────────
# CONSTANTS AND CONFIGURATION
# ───────────────────────────────────────────────────────────────────────────────

# A small pool of common User-Agent strings to rotate through for stealth in static fetch.
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:102.0) "
    "Gecko/20100101 Firefox/102.0",
    # Safari on iPhone
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 "
    "Safari/537.36 Edg/114.0.1823.43",
    # Chrome on Android
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Build/TQ3A.230605.006) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.61 Mobile Safari/537.36",
]

# Default timeout (in seconds) for HTTP requests and Playwright navigation.
REQUEST_TIMEOUT = 10
PLAYWRIGHT_TIMEOUT = 30000  # milliseconds

# Minimal delay between requests to mimic human browsing
MIN_DELAY = 0.5  # seconds
MAX_DELAY = 1.5  # seconds

# Logging setup
logger = logging.getLogger("scraper")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s — %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)



def _random_user_agent() -> str:
    """
    Return a random User-Agent from our small pool.
    Helps circumvent very basic bot-detection rules.
    """
    return random.choice(USER_AGENTS)


def _fetch_static_html(url: str) -> Optional[str]:
    """
    Try a simple HTTP GET + BeautifulSoup approach to fetch the page's raw HTML.
    Returns the HTML string if status is 200 and content looks non-empty;
    otherwise returns None to signal fallback to headless approach.
    """
    headers = {
        "User-Agent": _random_user_agent(),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }

    try:
        logger.info(f"Attempting static fetch for {url}")
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()  # Raises an HTTPError for 4xx/5xx
        raw_html = resp.text

        # Parse the HTML
        soup = BeautifulSoup(raw_html, "html.parser")
        
        # Ensure we have a proper HTML structure
        if not soup.find('html'):
            logger.warning("No HTML tag found; falling back to headless.")
            return None
            
        # Get the body content
        body = soup.find('body')
        if not body:
            logger.warning("No body tag found; falling back to headless.")
            return None

        # More lenient content check - just ensure there's some content
        text = body.get_text(strip=True)
        if len(text) < 10:  # Reduced from 20 to be more lenient
            logger.warning("Very little text content found; falling back to headless.")
            return None

        # If we got here, we have valid content
        logger.info("Successfully fetched static HTML content")
        return raw_html

    except Exception as e:
        logger.warning(f"Static fetch failed ({e}); will try headless. URL: {url}")
        return None


def _inline_css_and_collect(html: str, base_url: str) -> (str, List[str]):
    """
    Given raw HTML and a base_url, find all <link rel="stylesheet"> tags,
    fetch each stylesheet's content, then inline them by replacing the tag
    with a <style> block. Returns a tuple (inlined_html, css_contents_list).

    Enhanced to preserve CSS variables, media queries, and modern CSS features.
    """
    soup = BeautifulSoup(html, "html.parser")
    css_texts: List[str] = []

    # Extract any existing CSS variables from style tags first
    existing_styles = []
    for style_tag in soup.find_all("style"):
        style_content = style_tag.get_text() or ""
        if style_content.strip():
            existing_styles.append(style_content)
            css_texts.append(style_content)

    # Process all stylesheets
    link_tags = soup.find_all("link", {"rel": "stylesheet"})
    for link in link_tags:
        href = link.get("href")
        if not href:
            continue
        full_url = urljoin(base_url, href)
        try:
            logger.info(f"Fetching CSS: {full_url}")
            css_resp = requests.get(full_url, headers={"User-Agent": _random_user_agent()}, timeout=REQUEST_TIMEOUT)
            css_resp.raise_for_status()
            css_content = css_resp.text
            
            # Enhanced CSS processing to preserve modern features
            processed_css = _process_modern_css(css_content, base_url)
            css_texts.append(processed_css)

            # Replace <link> tag with <style> containing the processed CSS
            style_tag = soup.new_tag("style")
            style_tag.string = processed_css
            link.replace_with(style_tag)

            # Pause briefly between requests to be polite
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

        except Exception as e:
            logger.warning(f"Failed to fetch CSS at {full_url}: {e}")
            continue

    # Return the modified HTML (with inlined CSS) and the list of raw CSS
    return str(soup), css_texts


def _process_modern_css(css_content: str, base_url: str) -> str:
    """
    Process CSS to preserve modern features while making URLs absolute.
    """
    # 1. Make relative URLs in CSS absolute
    def make_url_absolute(match):
        url = match.group(1).strip('\'"')
        if url.startswith(('http://', 'https://', '//', 'data:')):
            return match.group(0)  # Already absolute or data URL
        absolute_url = urljoin(base_url, url)
        quote_char = '"' if '"' in match.group(0) else "'"
        return f"url({quote_char}{absolute_url}{quote_char})"
    
    # Process url() references
    css_content = re.sub(r'url\([\'"]?([^\'")]+)[\'"]?\)', make_url_absolute, css_content)
    
    # 2. Preserve CSS features that are important for visual fidelity
    # Ensure we don't accidentally remove important CSS constructs
    
    # 3. Add high-priority markers for critical visual styles
    if 'gradient' in css_content.lower():
        css_content = '/* Contains gradients - preserve exactly */\n' + css_content
    
    if 'background-image' in css_content.lower():
        css_content = '/* Contains background images - preserve exactly */\n' + css_content
        
    if '@keyframes' in css_content.lower():
        css_content = '/* Contains animations - may be removed for static version */\n' + css_content
    
    return css_content


def _extract_image_urls(html: str, base_url: str) -> List[str]:
    """
    Scan the inlined or original HTML for <img> tags and CSS background images.
    Returns a list of absolute URLs to all discovered images.
    We only collect URLs here; we do not download them. The clone can hot-link.
    """
    soup = BeautifulSoup(html, "html.parser")
    image_urls: List[str] = []

    # 1) <img> tags
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        full_src = urljoin(base_url, src)
        image_urls.append(full_src)

    # 2) Inline CSS background-image in style attributes
    for tag in soup.find_all(style=True):
        style = tag.get("style")
        # look for background-image: url(...)
        matches = re.findall(r"background(?:-image)?:\s*url\(([^)]+)\)", style, re.IGNORECASE)
        for m in matches:
            # strip quotes if any
            m_clean = m.strip('"\' ')
            full_img = urljoin(base_url, m_clean)
            image_urls.append(full_img)

    # 3) <style> tags with CSS background-image declarations
    for style_tag in soup.find_all("style"):
        css_text = style_tag.get_text() or ""
        matches = re.findall(r"background(?:-image)?:\s*url\(([^)]+)\)", css_text, re.IGNORECASE)
        for m in matches:
            m_clean = m.strip('"\' ')
            full_img = urljoin(base_url, m_clean)
            image_urls.append(full_img)

    # Deduplicate and return
    return list(dict.fromkeys(image_urls))


def _extract_metadata(html: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    meta_theme = soup.find("meta", attrs={"name": "theme-color"})

    # Try to find a <meta charset="…"> or <meta http-equiv="Content-Type" content="charset=…">
    meta_charset = soup.find("meta", attrs={"charset": True})
    if meta_charset is None:
        meta_charset = soup.find("meta", attrs={"http-equiv": "Content-Type"})

    # Ensure not None
    if meta_charset is None:
        charset_value = None
    else:
        # If it had a `charset` attribute, use that, otherwise look at `content`
        charset_value = meta_charset.get("charset") or meta_charset.get("content")

    # Extract additional visual metadata
    body = soup.find("body")
    html_tag = soup.find("html")
    
    # Try to detect if this is a dark theme website
    is_dark_theme = False
    if body:
        body_classes = body.get("class", [])
        if isinstance(body_classes, list):
            body_classes = " ".join(body_classes)
        is_dark_theme = any(keyword in body_classes.lower() for keyword in ['dark', 'night', 'black'])
    
    # Look for viewport settings
    viewport_meta = soup.find("meta", attrs={"name": "viewport"})
    viewport_content = viewport_meta.get("content") if viewport_meta else None
    
    # Try to extract brand/logo images
    logo_candidates = []
    logo_selectors = ['img[alt*="logo"]', 'img[src*="logo"]', '.logo img', '#logo img', 'svg[class*="logo"]']
    for selector in logo_selectors:
        try:
            elements = soup.select(selector)
            for elem in elements[:3]:  # Limit to 3 candidates
                if elem.name == 'img' and elem.get('src'):
                    logo_candidates.append(elem.get('src'))
                elif elem.name == 'svg':
                    logo_candidates.append('inline-svg')
        except:
            continue

    return {
        "title": (title_tag.get_text(strip=True) if title_tag else None),
        "theme_color": (meta_theme.get("content") if meta_theme else None),
        "charset": charset_value,
        "is_dark_theme": is_dark_theme,
        "viewport": viewport_content,
        "logo_candidates": logo_candidates[:3],  # Top 3 logo candidates
        "has_navigation": bool(soup.find(['nav', 'header', '[role="navigation"]'])),
        "main_sections": len(soup.find_all(['main', 'section', 'article'])),
    }



# ───────────────────────────────────────────────────────────────────────────────
# FALLBACK: HEADLESS BROWSER FETCH (PLAYWRIGHT)
# ───────────────────────────────────────────────────────────────────────────────

class PlaywrightScraper:
    """
    Encapsulates a long-running Playwright Browser instance in stealth mode.
    We create one global browser at module import time to reuse across calls,
    avoiding the overhead of launching a new browser for every request.
    """

    _browser: Optional[Browser] = None
    _context: Optional[BrowserContext] = None
    _lock = asyncio.Lock()  # ensure one-time startup

    @classmethod
    async def _initialize(cls):
        """
        Lazily initialize the Playwright browser in stealth-like configuration.
        """
        if cls._browser is None:
            async with cls._lock:
                if cls._browser is None:
                    logger.info("Starting Playwright browser (headless Chrome)...")
                    playwright = await async_playwright().start()

                    # Launch a headless Chromium in stealth mode via simple flags.
                    # For a truly robust stealth, you could integrate a specialized stealth plugin.
                    cls._browser = await playwright.chromium.launch(
                        headless=True,
                        args=[
                            "--disable-blink-features=AutomationControlled",
                            "--no-sandbox",
                            "--disable-setuid-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-gpu",
                        ],
                    )
                    cls._context = await cls._browser.new_context(
                        user_agent=_random_user_agent(),
                        viewport={"width": 1280, "height": 800},
                    )
                    # You can add more context-wide stealth configs here if needed.

    @classmethod
    async def fetch_with_playwright(cls, url: str) -> Optional[str]:
        """
        Uses Playwright to navigate to the target URL, waits for network idle,
        then returns the fully-rendered HTML. Retries once if it fails the first time.
        """
        await cls._initialize()
        assert cls._browser is not None and cls._context is not None

        page: Optional[Page] = None
        try:
            page = await cls._context.new_page()
            
            # Set up request interception to handle authentication
            await page.route("**/*", lambda route: route.continue_())
            
            # Set up better headers
            await page.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Upgrade-Insecure-Requests": "1",
            })
            
            logger.info(f"[Playwright] Navigating to {url}")
            
            # Navigate with longer timeout and wait for both network and DOM
            await page.goto(
                url,
                timeout=PLAYWRIGHT_TIMEOUT,
                wait_until=["networkidle", "domcontentloaded", "load"]
            )
            
            # Wait longer for initial content
            await asyncio.sleep(3)

            # Scroll to bottom to trigger lazy-loaded content
            await page.evaluate(
                """
                () => {
                  return new Promise((resolve) => {
                    let totalHeight = 0;
                    const distance = 100;
                    const timer = setInterval(() => {
                      window.scrollBy(0, distance);
                      totalHeight += distance;
                      if (totalHeight >= document.body.scrollHeight) {
                        clearInterval(timer);
                        resolve(true);
                      }
                    }, 100);
                  });
                }
                """
            )

            # Wait longer after scroll for any lazy content to load
            await asyncio.sleep(3)

            # Wait for any content to appear
            try:
                await page.wait_for_selector(
                    "body > *",  # Any direct child of body
                    timeout=15000
                )
            except Exception:
                logger.warning("No content found in body, but continuing anyway")

            # Capture any dynamically injected <style> blocks
            fresh_styles = await page.evaluate("""
                Array.from(document.querySelectorAll('style'))
                     .map(s => s.outerHTML)
                     .join('\\n')
            """)

            # Capture any dynamically injected <link> tags
            fresh_links = await page.evaluate("""
                Array.from(document.querySelectorAll('link[rel="stylesheet"]'))
                     .map(l => l.outerHTML)
                     .join('\\n')
            """)

            # Capture ALL computed styles, not just CSS variables
            complete_styling = await page.evaluate("""
                const getAllStyles = () => {
                    const styles = {};
                    const sheets = document.styleSheets;
                    
                    // 1. Extract CSS Variables (Custom Properties)
                    const root = document.documentElement;
                    const rootStyles = getComputedStyle(root);
                    const cssVars = {};
                    
                    for (let i = 0; i < rootStyles.length; i++) {
                        const prop = rootStyles[i];
                        if (prop.startsWith('--')) {
                            cssVars[prop] = rootStyles.getPropertyValue(prop);
                        }
                    }
                    
                    // 2. Extract body and HTML background styles
                    const bodyStyles = getComputedStyle(document.body);
                    const htmlStyles = getComputedStyle(document.documentElement);
                    
                    const backgroundCSS = [];
                    
                    // HTML background
                    if (htmlStyles.background && htmlStyles.background !== 'rgba(0, 0, 0, 0)') {
                        backgroundCSS.push(`html { background: ${htmlStyles.background}; }`);
                    }
                    if (htmlStyles.backgroundColor && htmlStyles.backgroundColor !== 'rgba(0, 0, 0, 0)') {
                        backgroundCSS.push(`html { background-color: ${htmlStyles.backgroundColor}; }`);
                    }
                    if (htmlStyles.backgroundImage && htmlStyles.backgroundImage !== 'none') {
                        backgroundCSS.push(`html { background-image: ${htmlStyles.backgroundImage}; }`);
                    }
                    
                    // Body background  
                    if (bodyStyles.background && bodyStyles.background !== 'rgba(0, 0, 0, 0)') {
                        backgroundCSS.push(`body { background: ${bodyStyles.background}; }`);
                    }
                    if (bodyStyles.backgroundColor && bodyStyles.backgroundColor !== 'rgba(0, 0, 0, 0)') {
                        backgroundCSS.push(`body { background-color: ${bodyStyles.backgroundColor}; }`);
                    }
                    if (bodyStyles.backgroundImage && bodyStyles.backgroundImage !== 'none') {
                        backgroundCSS.push(`body { background-image: ${bodyStyles.backgroundImage}; }`);
                    }
                    
                    // 3. Find elements with background gradients/images
                    const elementsWithBackgrounds = document.querySelectorAll('*');
                    const gradientCSS = [];
                    
                    elementsWithBackgrounds.forEach((elem, index) => {
                        if (index > 100) return; // Limit to prevent excessive processing
                        
                        const computedStyle = getComputedStyle(elem);
                        const bgImage = computedStyle.backgroundImage;
                        const background = computedStyle.background;
                        
                        if (bgImage && bgImage !== 'none' && (bgImage.includes('gradient') || bgImage.includes('url'))) {
                            let selector = elem.tagName.toLowerCase();
                            if (elem.id) selector += `#${elem.id}`;
                            if (elem.className) {
                                const classes = elem.className.split(' ').filter(c => c.trim());
                                if (classes.length > 0) selector += `.${classes[0]}`;
                            }
                            gradientCSS.push(`${selector} { background-image: ${bgImage}; }`);
                        }
                        
                        if (background && background !== 'rgba(0, 0, 0, 0)' && background.includes('gradient')) {
                            let selector = elem.tagName.toLowerCase();
                            if (elem.id) selector += `#${elem.id}`;
                            if (elem.className) {
                                const classes = elem.className.split(' ').filter(c => c.trim());
                                if (classes.length > 0) selector += `.${classes[0]}`;
                            }
                            gradientCSS.push(`${selector} { background: ${background}; }`);
                        }
                    });
                    
                    // 4. Combine all styles
                    let result = '';
                    
                    // CSS Variables first
                    if (Object.keys(cssVars).length > 0) {
                        result += ':root {\\n' + Object.entries(cssVars).map(([key, value]) => `  ${key}: ${value};`).join('\\n') + '\\n}\\n\\n';
                    }
                    
                    // Background styles
                    if (backgroundCSS.length > 0) {
                        result += '/* Background Styles */\\n' + backgroundCSS.join('\\n') + '\\n\\n';
                    }
                    
                    // Gradient/image styles
                    if (gradientCSS.length > 0) {
                        result += '/* Gradient and Image Backgrounds */\\n' + gradientCSS.join('\\n') + '\\n\\n';
                    }
                    
                    return result;
                };
                
                return getAllStyles();
            """)

            # Get the final content
            content = await page.content()
            
            # Combine all styles and content with complete styling first
            style_components = []
            if complete_styling and complete_styling.strip():
                style_components.append(complete_styling)
            if fresh_links and fresh_links.strip():
                style_components.append(fresh_links)
            if fresh_styles and fresh_styles.strip():
                style_components.append(fresh_styles)
            
            combined_styles = '\n'.join(style_components)
            
            content = f"<style>\n{combined_styles}\n</style>\n{content}"
            
            return content

        except Exception as e:
            logger.warning(f"Playwright fetch failed on first attempt ({e}); retrying once...")
            try:
                if page:
                    await page.close()
                
                page = await cls._context.new_page()
                await page.goto(
                    url,
                    timeout=PLAYWRIGHT_TIMEOUT,
                    wait_until=["networkidle", "domcontentloaded", "load"]
                )
                await asyncio.sleep(3)
                content = await page.content()
                return content
            except Exception as e2:
                logger.error(f"Playwright fetch failed on second attempt ({e2}); aborting.")
                return None
        finally:
            if page:
                await page.close()

    @classmethod
    async def close(cls):
        """
        Gracefully shut down the Playwright browser (only if your application lifecycle
        calls for it – e.g. FastAPI shutdown event).
        """
        if cls._context:
            await cls._context.close()
        if cls._browser:
            await cls._browser.close()


# ───────────────────────────────────────────────────────────────────────────────
# PRIMARY ENTRY POINT
# ───────────────────────────────────────────────────────────────────────────────

async def scrape_site(url: str) -> Dict[str, Optional[object]]:
    """
    Scrape the target webpage at `url`. Returns a dictionary with:
      - "html": The raw (possibly inlined) HTML string,
      - "css": A list of raw CSS strings from <link> tags,
      - "images": A list of all discovered image URLs,
      - "metadata": A small dict of extracted metadata (title, theme_color, charset).

    Workflow:
      1) Try a fast & simple requests+BS4 fetch.
      2) If static fetch fails or seems insufficient, fall back to Playwright.
      3) Inline external CSS into the HTML and collect them.
      4) Extract image URLs.
      5) Extract metadata.
      6) Return everything in a single dict.
    """
    # Normalize URL (ensure it has a scheme)
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url

    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # 1) Attempt fast static fetch
    raw_html = _fetch_static_html(url)

    # 2) If static fetch returned None or obviously incomplete, use Playwright
    if raw_html is None:
        logger.info("Static HTML fetch was insufficient. Using Playwright fallback...")
        raw_html = await PlaywrightScraper.fetch_with_playwright(url)
        if raw_html is None:
            # Both methods failed; return an error‐like dict (could also raise an exception)
            return {
                "html": None,
                "css": [],
                "images": [],
                "metadata": None,
                "error": "Unable to fetch page content via static or headless methods.",
            }

    # 3) Inline CSS and collect CSS content
    inlined_html, css_list = _inline_css_and_collect(raw_html, base_url)

    # 4) Extract image URLs for hot-linking or future download
    img_urls = _extract_image_urls(inlined_html, base_url)

    # 5) Extract simple metadata
    meta = _extract_metadata(inlined_html)

    return {
        "html": inlined_html,
        "css": css_list,
        "images": img_urls,
        "metadata": meta,
        "error": None,
    }


# If you want to test this file stand-alone, you can use the following snippet:
# (Remember to run inside an async event loop, e.g. `python -m asyncio run scraper.py`)
if __name__ == "__main__":
    import sys

    async def main():
        if len(sys.argv) < 2:
            print("Usage: python scraper.py <URL>")
            return
        url_to_scrape = sys.argv[1]
        result = await scrape_site(url_to_scrape)
        if result["error"]:
            print("Error:", result["error"])
        else:
            print("=== Metadata ===")
            print(result["metadata"])
            print("\n=== Number of CSS files fetched ===", len(result["css"]))
            print("=== Number of images found ===", len(result["images"]))
            print("\n=== Sample HTML (first 500 chars) ===")
            print(result["html"][:500] + "...")
    asyncio.run(main())
