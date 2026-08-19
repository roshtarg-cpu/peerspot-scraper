"""
PeerSpot Reviews Scraper
Scrapes B2B software reviews, ratings, and user testimonials from PeerSpot.com
"""
import asyncio
import httpx
from apify import Actor
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime, timezone


async def fetch_page(url: str, client: httpx.AsyncClient, retries=3):
    """Fetch page with retries"""
    for attempt in range(retries):
        try:
            response = await client.get(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
                timeout=30.0,
                follow_redirects=True
            )
            
            if response.status_code == 200 and len(response.text) > 500:
                return response.text
            
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)
                
        except Exception as e:
            Actor.log.warning(f'Fetch error (attempt {attempt + 1}/{retries}): {e}')
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)
    
    return None


def extract_json_ld(html: str):
    """Extract JSON-LD structured data"""
    soup = BeautifulSoup(html, 'lxml')
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
    data_list = []
    for script in json_ld_scripts:
        try:
            data = json.loads(script.string)
            data_list.append(data)
        except:
            pass
    
    return data_list


def parse_product_page(html: str, url: str):
    """Parse product review page"""
    soup = BeautifulSoup(html, 'lxml')
    reviews = []
    
    # Extract product name
    product_name = None
    h1 = soup.find('h1')
    if h1:
        product_name = h1.get_text(strip=True).replace(' Reviews', '').replace(' Review', '')
    
    # Try JSON-LD first
    json_ld_data = extract_json_ld(html)
    for data in json_ld_data:
        if data.get('@type') == 'Product':
            product_name = data.get('name', product_name)
    
    # Find review elements
    review_cards = soup.find_all('div', class_=lambda x: x and ('review' in x.lower() or 'card' in x.lower()))
    
    if not review_cards:
        # Try alternative selectors
        review_cards = soup.find_all(['article', 'div'], attrs={'data-testid': lambda x: x and 'review' in x.lower()})
    
    # Parse reviews from HTML structure
    for card in review_cards:
        try:
            review_data = {
                'productName': product_name,
                'sourceUrl': url,
                'scrapedAt': datetime.now(timezone.utc).isoformat(),
            }
            
            # Extract review text
            review_text_elem = card.find(['p', 'div'], class_=lambda x: x and 'content' in str(x).lower())
            if review_text_elem:
                review_data['reviewText'] = review_text_elem.get_text(strip=True)
            
            # Extract rating
            rating_elem = card.find(['span', 'div'], class_=lambda x: x and 'star' in str(x).lower())
            if rating_elem:
                # Count filled stars
                filled_stars = len(rating_elem.find_all('i', class_=lambda x: x and 'fa-star' in str(x) and 'far' not in str(x)))
                if filled_stars > 0:
                    review_data['rating'] = filled_stars
            
            # Extract reviewer name
            author_elem = card.find(['div', 'span', 'a'], class_=lambda x: x and ('author' in str(x).lower() or 'name' in str(x).lower()))
            if author_elem:
                review_data['reviewerName'] = author_elem.get_text(strip=True)
            
            # Extract reviewer title/company
            title_elem = card.find(['div', 'span'], class_=lambda x: x and 'info' in str(x).lower())
            if title_elem:
                review_data['reviewerTitle'] = title_elem.get_text(strip=True)
            
            # Extract date
            date_elem = card.find(['span', 'div', 'time'], class_=lambda x: x and 'date' in str(x).lower())
            if date_elem:
                review_data['reviewDate'] = date_elem.get_text(strip=True)
            
            # Only add if we got meaningful data
            if review_data.get('reviewText') or review_data.get('rating'):
                reviews.append(review_data)
                
        except Exception as e:
            Actor.log.debug(f'Error parsing review card: {e}')
            continue
    
    return reviews


async def scrape_search_page(search_query: str, max_results: int, client: httpx.AsyncClient):
    """Scrape search results for products"""
    Actor.log.info(f'Searching for: {search_query}')
    
    # Use PeerSpot search
    search_url = f'https://www.peerspot.com/search?search={search_query.replace(" ", "+")}'
    html = await fetch_page(search_url, client)
    
    if not html:
        Actor.log.warning('Failed to fetch search page')
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    product_links = []
    
    # Find product links
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Look for product review pages
        if '/products/' in href and '-reviews' in href:
            full_url = urljoin('https://www.peerspot.com', href)
            if full_url not in product_links:
                product_links.append(full_url)
    
    Actor.log.info(f'Found {len(product_links)} product pages')
    return product_links[:10]  # Limit to top 10 products


async def scrape_category_page(category_url: str, client: httpx.AsyncClient):
    """Scrape category page for products"""
    Actor.log.info(f'Scraping category: {category_url}')
    
    html = await fetch_page(category_url, client)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    product_links = []
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/products/' in href and '-reviews' in href:
            full_url = urljoin('https://www.peerspot.com', href)
            if full_url not in product_links:
                product_links.append(full_url)
    
    return product_links


async def main():
    async with Actor:
        Actor.log.info('PeerSpot Scraper starting...')
        
        # Get input
        actor_input = await Actor.get_input() or {}
        search_query = actor_input.get('searchQuery', '')
        category_url = actor_input.get('categoryUrl', '')
        product_urls = actor_input.get('productUrls', [])
        max_results = actor_input.get('maxResults', 100)
        
        Actor.log.info(f'Input: search={search_query}, category={category_url}, products={len(product_urls)}, max={max_results}')
        
        results_count = 0
        
        async with httpx.AsyncClient() as client:
            urls_to_scrape = list(product_urls)  # Start with provided URLs
            
            # If search query provided, get product URLs from search
            if search_query:
                search_products = await scrape_search_page(search_query, max_results, client)
                urls_to_scrape.extend(search_products)
            
            # If category URL provided, get products from category
            if category_url:
                category_products = await scrape_category_page(category_url, client)
                urls_to_scrape.extend(category_products)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_urls = []
            for url in urls_to_scrape:
                if url not in seen:
                    seen.add(url)
                    unique_urls.append(url)
            
            Actor.log.info(f'Scraping {len(unique_urls)} product pages')
            
            # Scrape each product page
            for idx, product_url in enumerate(unique_urls):
                if results_count >= max_results:
                    Actor.log.info(f'Reached max results ({max_results})')
                    break
                
                Actor.log.info(f'[{idx + 1}/{len(unique_urls)}] Scraping: {product_url}')
                
                html = await fetch_page(product_url, client)
                if not html:
                    Actor.log.warning(f'Failed to fetch: {product_url}')
                    continue
                
                reviews = parse_product_page(html, product_url)
                Actor.log.info(f'  Found {len(reviews)} reviews')
                
                # Push results immediately
                for review in reviews:
                    if results_count >= max_results:
                        break
                    
                    await Actor.push_data(review)
                    results_count += 1
                    
                    if results_count % 10 == 0:
                        Actor.log.info(f'Progress: {results_count} reviews scraped')
                
                # Rate limiting
                await asyncio.sleep(1.5)
        
        Actor.log.info(f'✅ Scraping complete! Total reviews: {results_count}')
