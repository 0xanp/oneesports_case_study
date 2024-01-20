import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_one_esports(base_url, max_pages=150):
    news_data = []

    for page in range(0, max_pages + 1):
        url = f"{base_url}page/{page}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

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
                    'date_published' : date_published
                })

    return news_data
