#!/usr/bin/python3
import requests
import sqlite3

# Function to create the database and table if they don't exist
def create_database():
    conn = sqlite3.connect('hacker_news.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY,
            title TEXT,
            url TEXT,
            time INTEGER
        )
    ''')

    conn.commit()
    conn.close()

# Function to update news data in the SQLite database
def update_news():
    # First, create the database and table
    create_database()

    # Fetch and insert new news data from the Hacker News API (example code)
    api_url = "https://hacker-news.firebaseio.com/v0/newstories.json?print=pretty"
    response = requests.get(api_url)

    if response.status_code == 200:
        news_ids = response.json()[:10]
    else:
        print("Failed to fetch news from Hacker News API.")
        return  # Stop if fetching data failed

    # Connect to the SQLite database
    conn = sqlite3.connect('hacker_news.db')
    cursor = conn.cursor()

    # Fetch details for each news item and insert it into the database
    for news_id in news_ids:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{news_id}.json?print=pretty"
        item_response = requests.get(item_url)
        if item_response.status_code == 200:
            news_item = item_response.json()
            title = news_item.get('title', '')  # Get the title (empty string if 'title' is not found)
            url = news_item.get('url', '')  # Get the URL (empty string if 'url' is not found)
            creation_time = news_item.get('time', 0)  # Get the creation time (0 if 'time' is not found)

            # Check for duplicates based on title
            cursor.execute('SELECT id FROM news WHERE title = ?', (title,))
            existing = cursor.fetchone()

            # Insert data into the database if title, url, time, and no duplicate exists
            if title and url and creation_time and not existing:
                cursor.execute('INSERT INTO news (title, url, time) VALUES (?, ?, ?)', (title, url, creation_time))
        else:
            print(f"Failed to fetch news from Hacker News API for ID: {news_id}")

    # Commit changes and close the database connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    update_news()
