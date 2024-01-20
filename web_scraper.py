import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

def fetch_page_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_page_content(html, cutoff_date):
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

            try:
                # Assuming date_published is a Unix timestamp
                date_published_dt = datetime.fromtimestamp(int(date_published))
            except ValueError:
                print(f"Unexpected date format: {date_published}")
                continue

            if date_published_dt < cutoff_date:
                return news_data, False  # Return False to indicate cutoff

            news_data.append({
                'title': title,
                'category': category_text,
                'author': author_name,
                'date_published': date_published_dt.strftime("%Y-%m-%d")  # Formatting the date
            })

    return news_data, True  # Return True to indicate continuation

def scrape_one_esports(base_url, cutoff_date):
    all_news_data = []
    page = 1
    continue_scraping = True

    with ThreadPoolExecutor(max_workers=20) as executor:
        while continue_scraping:
            future_to_content = {executor.submit(fetch_page_content, f"{base_url}page/{page}/"): page}
            for future in as_completed(future_to_content):
                data = future.result()
                if data:
                    news_data, continue_scraping = parse_page_content(data, cutoff_date)
                    all_news_data.extend(news_data)
                if not continue_scraping:
                    break
            page += 1

    return all_news_data
