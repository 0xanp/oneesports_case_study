import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_page_content(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_page_content(html):
    news_data = []
    soup = BeautifulSoup(html, 'html.parser')

    articles = soup.find_all('article')
    for article in articles:
        headline = article.find('h2')
        category = article.find('a', class_='category')
        author = article.find('a', class_='author')
        date = article.find('span', class_='date')

        if headline and category and author and date:
            title = headline.get_text().strip()
            category_text = category.get_text().strip()
            author_name = author.get_text().strip()
            date_published = date.get('data-publish-time').strip()
            news_data.append({
                'title': title,
                'category': category_text,
                'author': author_name,
                'date_published': date_published
            })

    return news_data

def scrape_one_esports(base_url, max_pages=150):
    all_news_data = []
    urls = [f"{base_url}page/{page}/" for page in range(1, max_pages + 1)]

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(fetch_page_content, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            data = future.result()
            if data:
                all_news_data.extend(parse_page_content(data))

    return all_news_data
