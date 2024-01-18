import requests
from bs4 import BeautifulSoup

def scrape_one_esports(base_url, max_pages=10):
    news_data = []

    for page in range(1, max_pages + 1):
        url = f"{base_url}page/{page}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.find_all('article')
        for article in articles:
            headline = article.find('h2')
            category = article.find('a', class_='category')  # Adjust class as per the website
            author = article.find('a', class_='author')  # Adjust class as per the website
            print(headline, category, author)
            if headline and category and author:
                title = headline.get_text().strip()
                category_text = category.get_text().strip()
                author_name = author.get_text().strip()

                news_data.append({
                    'title': title, 
                    'category': category_text,
                    'author': author_name
                })

    return news_data
