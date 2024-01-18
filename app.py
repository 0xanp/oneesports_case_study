import streamlit as st
from web_scraper import scrape_one_esports
from collections import Counter, defaultdict

@st.cache_data
def scraper():
    all_country_data = {}
    for country, url in urls.items():
        with st.spinner(f'Fetching data from {country} website...'):
            all_country_data[country] = scrape_one_esports(url)
    return all_country_data

# Helper function to sort categories
def sort_categories(data):
    # Sort by total articles count and then by number of countries
    return sorted(data, key=lambda x: (sum(data[x].values()), len(data[x])), reverse=True)


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

# Comparative Analysis Across Countries
st.header("Comparative Analysis Across Countries")
all_country_data = scraper()

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

