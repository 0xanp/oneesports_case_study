import streamlit as st
from web_scraper import scrape_one_esports
from collections import Counter, defaultdict
import pandas as pd
import time
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime, timedelta

start = time.time()

@st.cache_data
def scraper():
    all_country_data = {}
    for country, url in urls.items():
        with st.spinner(f'Fetching data from {country} website...'):
            all_country_data[country] = scrape_one_esports(url)
    return all_country_data

def convert_to_dataframe(all_country_data):
    data = []
    for country, articles in all_country_data.items():
        for article in articles:
            data.append({
                'country': country,
                'author': article['author'],
                'category': article['category'],
                'title': article['title'],
                'date_published': pd.to_datetime(article['date_published'], unit='s')
            })
    return pd.DataFrame(data)

# Set the page config to wide mode for better visualization layout
st.set_page_config(layout="wide")

# URLs for different country-specific versions of the site
urls = {
    "Global": "https://www.oneesports.gg/",
    "Vietnam": "https://www.oneesports.vn/",
    "Indonesia": "https://www.oneesports.id/",
    "Philipines": "https://www.oneesports.ph/",
    "Thailand": "https://www.oneesports.co.th/"
}

# Streamlit UI
st.title("ONE Esports Content Analysis Dashboard")

# Load the master data
all_country_data = scraper()
end = time.time()

st.write(end - start) # time in seconds
data = convert_to_dataframe(all_country_data)
data = data.drop_duplicates(subset=['title'])
data = data[data['date_published']>(datetime.now() - timedelta(days=60))]
st.write(data)
st.write(data.describe(include='all'))
# Comparative Analysis Across Countries
st.header("Comparative Analysis Across Countries")
# Article Count by Category Across Countries
st.subheader("Article Count by Category Across Countries")
category_data = {}
for country, articles in all_country_data.items():
    category_counts = Counter([article['category'] for article in articles])
    category_data[country] = category_counts
st.bar_chart(category_data)

# Article Count by Author Across Countries
st.subheader("Article Count by Author Across Countries")
author_data = {}
for country, articles in all_country_data.items():
    author_counts = Counter([article['author'] for article in articles])
    author_data[country] = author_counts
st.bar_chart(author_data)

# Convert 'date_published' to just date for easier grouping and set it as the index after sorting
data['date'] = pd.to_datetime(data['date_published']).dt.date
data.sort_values('date', inplace=True)
data.set_index('date', inplace=True)

# Function to plot line chart for articles over time by country
st.header("Articles Over Time by Country")
country_time_data = data.groupby(['country', data.index]).size().unstack(level=0, fill_value=0)
st.line_chart(country_time_data)

# Identify the top 10 authors by the number of articles
top_authors = data['author'].value_counts().head(10).index.tolist()

# Filter the data to include only the top 10 authors
top_authors_data = data[data['author'].isin(top_authors)]

# Line Chart for Articles Over Time by Author
st.header("Articles Over Time by Top 10 Authors")
author_time_data = top_authors_data.groupby(['author', 'date']).size().unstack(level=0, fill_value=0)
st.line_chart(author_time_data)


# Individual Country Analysis
st.header("Individual Country Analysis")
selected_country = st.selectbox("Select a Country for Detailed Analysis", list(urls.keys()))

# Show details for the selected country
if selected_country:
    st.subheader(f"Analysis for {selected_country}")

    # Fetch and display data
    news_data = all_country_data[selected_country]

    # Articles count by author, categorized by the categories they wrote in
    st.subheader("Article Count by Category")
    author_category_counts = defaultdict(Counter)
    for article in news_data:
        author_category_counts[article['author']][article['category']] += 1
    author_category_chart_data = {author: author_category_counts[author] for author in sorted(author_category_counts)}
    st.bar_chart(author_category_chart_data)

    # Articles count by category, broken down by authors
    st.subheader("Article Count by Author")
    category_author_counts = defaultdict(Counter)
    for article in news_data:
        category_author_counts[article['category']][article['author']] += 1
    category_author_chart_data = {category: category_author_counts[category] for category in sorted(category_author_counts)}
    st.bar_chart(category_author_chart_data)

    # Article distribution by country
    filtered_data = data[data['country'] == selected_country]
    st.header("Article Distribution by Country")
    country_count = filtered_data['country'].value_counts()
    st.bar_chart(country_count)

    # Articles over time
    st.header("Articles Over Time")
    articles_over_time = filtered_data.groupby(['country', filtered_data.index]).size().unstack(level=0, fill_value=0)
    st.line_chart(articles_over_time)

    # Top authors
    st.header("Top Authors")
    top_authors = filtered_data['author'].value_counts().head(10)
    st.bar_chart(top_authors)

    # Word Cloud
    st.header("Word Cloud from Article Titles")
    text = ' '.join(filtered_data['title'].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color ='white').generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot(plt)
