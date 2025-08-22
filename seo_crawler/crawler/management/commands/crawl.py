import re, requests, nltk, asyncio
from urllib.parse import urljoin, urlparse
from collections import deque
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from crawler.models import Domain, Page, Insight
from playwright.async_api import async_playwright
from asgiref.sync import sync_to_async
from urllib.robotparser import RobotFileParser

nltk.download("stopwords", quiet=True)
stopwords = set(nltk.corpus.stopwords.words("english"))

class Command(BaseCommand):
    help = "Crawl a domain and extract SEO insights"

    def add_arguments(self, parser):
        parser.add_argument("domain", type=str)
        parser.add_argument("--max-pages", type=int, default=50, help="Limit number of pages")

    def handle(self, *args, **options):
        domain_name = options["domain"]
        max_pages = options["max_pages"]

        asyncio.run(self.crawl_domain(domain_name, max_pages))

    async def crawl_domain(self, domain_name, max_pages):
        # Create or get Domain row
        domain_obj, _ = await sync_to_async(Domain.objects.get_or_create)(domain_name=domain_name)

        visited = set()
        queue = deque()

        # ROBOTS.TXT 
        rp = RobotFileParser()
        robots_url = f"https://{domain_name}/robots.txt"
        try:
            rp.set_url(robots_url)
            rp.read()
            self.stdout.write(self.style.SUCCESS(f"Robots.txt loaded from {robots_url}"))
        except Exception:
            self.stdout.write(self.style.WARNING("No valid robots.txt found, crawling all URLs"))
            rp = None

        # SITEMAP.XML 
        sitemap_url = f"https://{domain_name}/sitemap.xml"
        try:
            resp = requests.get(sitemap_url, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "xml")
                urls = [loc.text for loc in soup.find_all("loc")]
                if urls:
                    queue.extend(urls)
                    self.stdout.write(self.style.SUCCESS(f"Seeded {len(urls)} URLs from sitemap.xml"))
            else:
                queue.append(f"https://{domain_name}/")
        except Exception:
            queue.append(f"https://{domain_name}/")

        # PLAYWRIGHT with Chromium/Chrome
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            count = 0
            while queue and count < max_pages:
                url = queue.popleft()
                if url in visited:
                    continue
                visited.add(url)

                # Respect robots.txt
                if rp and not rp.can_fetch("*", url):
                    self.stdout.write(self.style.WARNING(f"Skipping {url} (disallowed by robots.txt)"))
                    continue

                try:
                    page = await context.new_page()
                    await page.goto(url, timeout=15000)
                    html = await page.content()
                    await page.close()

                    soup = BeautifulSoup(html, "html.parser")

                    # Extract SEO data
                    title = soup.title.string if soup.title else None
                    meta_description = None
                    meta_tag = soup.find("meta", attrs={"name": "description"})
                    if meta_tag and "content" in meta_tag.attrs:
                        meta_description = meta_tag["content"]

                    h1 = [h.get_text(strip=True) for h in soup.find_all("h1")]
                    h2 = [h.get_text(strip=True) for h in soup.find_all("h2")]
                    h3 = [h.get_text(strip=True) for h in soup.find_all("h3")]
                    p_count = len(soup.find_all("p"))
                    image_count = len(soup.find_all("img"))

                    links = soup.find_all("a", href=True)
                    internal_links, external_links = 0, 0
                    for link in links:
                        href = link["href"]
                        if href.startswith("http"):
                            if urlparse(href).netloc == domain_name:
                                internal_links += 1
                                if href not in visited:
                                    queue.append(href)
                            else:
                                external_links += 1
                        else:
                            new_url = urljoin(url, href)
                            internal_links += 1
                            if new_url not in visited:
                                queue.append(new_url)

                    # Keyword extraction
                    text = soup.get_text(" ", strip=True)
                    words = [w.lower() for w in re.findall(r"\w+", text) if w.lower() not in stopwords]
                    total_words = len(words)
                    freq = {}
                    for w in words:
                        freq[w] = freq.get(w, 0) + 1
                    keywords = [
                        {"keyword": k, "density": (v/total_words)*100}
                        for k, v in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
                    ]

                    # Save to DataBase
                    page_obj = await sync_to_async(Page.objects.create)(
                        domain=domain_obj, url=url, status_code=200
                    )

                    await sync_to_async(Insight.objects.create)(
                        page=page_obj,
                        title=title,
                        meta_description=meta_description,
                        h1=h1,
                        h2=h2,
                        h3=h3,
                        p_count=p_count,
                        image_count=image_count,
                        internal_links=internal_links,
                        external_links=external_links,
                        keywords=keywords,
                    )

                    count += 1
                    self.stdout.write(self.style.SUCCESS(f"Crawled ({count}): {url}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed {url}: {e}"))
                    continue

            await browser.close()
