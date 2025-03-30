import requests
from bs4 import BeautifulSoup
import random
import mysql.connector
import re
from datetime import datetime
import time


db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="tracker@2024",
    database="mobilepricetracker",
    port="3307"
)
db_cursor = db_connection.cursor()

proxies = [
    {'http': '103.187.111.81'},
    {'http': '20.235.159.154'},
    {'http': '182.78.42.112'},
    {'http': '103.186.254.218'},
    {'http': '103.186.254.218'},
    {'http': '20.235.159.154'},
    {'http': '13.234.24.116'},
    {'http': '3.108.115.48'},
    {'http': '65.1.40.47'},
    {'http': '13.234.24.116'}
]

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.58",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 OPR/85.0.4344.41",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 OPR/85.0.4344.41",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
]



def get_price(soup):
    pr = soup.find('div', class_='Nx9bqj CxhGGd')
    if pr:
        price_text = re.sub(r'[^\d.]', '', pr.text.strip())
        print(price_text)
        return price_text
    return None

def get_deliverytime(soup):
    de = soup.find('span', class_='Y8v7Fl')
    if de:
        delivery_text = de.text.strip()
        print(delivery_text)
        return convert_to_days_from_today(delivery_text)
    return None



def convert_to_days_from_today(delivery_text):
    date_pattern = re.compile(r'(\d{1,2}) (\w+), (\w+)')
    match = date_pattern.search(delivery_text)
    if match:
        day = int(match.group(1))
        month = match.group(2)
        
        year = datetime.now().year

        delivery_date_str = f"{day} {month} {year}"
        delivery_date = datetime.strptime(delivery_date_str, "%d %b %Y") 

        today = datetime.now()
        delta = delivery_date - today

        if delta.days < 0:
            delivery_date = datetime.strptime(f"{day} {month} {year + 1}", "%d %b %Y")
            delta = delivery_date - today

        return f"{delta.days} days"
    return None

def fetch_urls():
    db_cursor.execute("SELECT redirect_link FROM Mobiles WHERE platform_name = 'Flipkart'")
    return db_cursor.fetchall()

def update_data(redirect_link, new_price, new_delivery_time):
    try:
        db_cursor.execute("SELECT price, delivery_time FROM Mobiles WHERE redirect_link = %s", (redirect_link,))
        result = db_cursor.fetchone()
        if result:
            old_price, old_delivery_time = result
            if old_price != new_price or old_delivery_time != new_delivery_time:
                db_cursor.execute("UPDATE Mobiles SET price = %s, delivery_time = %s WHERE redirect_link = %s",
                                  (new_price, new_delivery_time, redirect_link))
                db_connection.commit()
                print(f"Data updated for {redirect_link}")
            else:
                print(f"No changes for {redirect_link}")
    except mysql.connector.Error as e:
        print(f"Error: {e}")

def scrape_data():
    urls = fetch_urls()
    for (url,) in urls:
        while True:
            user_agent = random.choice(user_agents)
            proxy = random.choice(proxies)
            headers = {'User-Agent': user_agent}
            response = requests.get(url, headers=headers, proxies=proxy)
            time.sleep(2)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                new_price = get_price(soup)
                new_delivery_time = get_deliverytime(soup)
                if new_price and new_delivery_time:
                    update_data(url, new_price, new_delivery_time)
                break
            elif response.status_code == 500:
                print("500 Service Unavailable - Retrying...")
                time.sleep(2)
            else:
                response.raise_for_status()

if __name__ == "__main__":
    scrape_data()
