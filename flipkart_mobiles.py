
import requests
from bs4 import BeautifulSoup
import time
import datetime
import random
import mysql.connector
from datetime import datetime
import re


db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="tracker@2024",
    database="mobilepricetracker",
    port="3307"
    
)
db_cursor = db_connection.cursor()
baseurl = "https://www.flipkart.com"

proxies=[
    {'http': '103.133.221.251'},
    {'http': '103.143.169.25'},
    {'http': '117.242.189.115'},
    {'http': '103.137.45.47'},
    {'http': '103.137.218.73'},
    {'http': '122.175.19.164'},
    {'http': '103.68.207.34'},
    {'http': '103.168.164.94'},
    {'http': '103.137.45.202'},
    {'http': '117.250.3.58'},
    {'http': '136.226.230.82'},
    {'http': '136.226.230.82'},
    {'http': '136.226.230.82'},
    {'http': '136.226.230.82'},
    {'http': '136.226.230.82'}
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




def get_title(soup):
        br = soup.find('span', class_='VU-ZEz')
        if br:
            return br.text.strip()
        return None    
            


def get_rating(soup):
    rg = soup.find('div', class_='XQDdHH')
    if rg:
        return rg.text.strip()
    return None

def get_price(soup):
    pr = soup.find('div', class_='Nx9bqj CxhGGd')
    if pr:
        price_text = re.sub(r'[^\d.]', '', pr.text.strip())
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




def get_condition(soup):
    condition = soup.find('span', class_='VU-ZEz')
    if condition:
            if "Refurbished" in condition:
                return "Refurbished" 
            else:
                return "New"

def get_image_url(soup):
    image_url_div = soup.find('div',class_='_4WELSP _6lpKCl')
    if image_url_div:
        image_url = image_url_div.find('img')
        if image_url:
            return image_url.get('src')
    return None

def insert_data(title, redirect_link, platform_id, platform_name, price, rating, delivery_time, image_url, new_refurbished):
    try:
        db_cursor.execute("SELECT redirect_link FROM Mobiles WHERE redirect_link = %s", (redirect_link,))
        existing_link = db_cursor.fetchone()
      
        if not existing_link:
            sql = "INSERT INTO Mobiles (title, redirect_link, platform_id, platform_name, price, rating, delivery_time, image_url, new_refurbished) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (title, redirect_link, platform_id, platform_name, price, rating, delivery_time, image_url, new_refurbished)
            db_cursor.execute(sql, values)
            db_connection.commit()
            print("Data inserted successfully!")
        else:
            print("Duplicate product link found. Skipping insertion.")

    except mysql.connector.Error as e:
        print(f"Error: {e}")

def mobiles(url):
    page = []
    productlink=""
    productlinks=[]
    visited=[]
    v=[]
    while (url not in v):
            user_agent = random.choice(user_agents)
            proxy = random.choice(proxies)
            headers = {'User-Agent': user_agent}
            r = requests.get(url, headers=headers, proxies=proxy)
            time.sleep(2)  
            print("Response Code:", r.status_code)
            
            if r.status_code == 200:
                  soup = BeautifulSoup(r.content, 'lxml')
                  productlist = soup.find_all('div', class_='tUxRFH')
                  for item in productlist:
                    for link in item.find_all('a', class_='CGtC98', href=True):
                        if (link not in productlinks):
                            productlink =baseurl+link['href']
                            productlinks.append(productlink)
                            print(productlink)
                            scrape_mobile_data(productlink)
                            v.append(url)   
            elif r.status_code == 503:
                print("503 Service Unavailable - Retrying...")
                time.sleep(2)
            elif r.status_code == 500:
                print("500 Service Unavailable - Retrying...")
                time.sleep(2)
            elif r.status_code == 429:
                print("429 Service Unavailable - Retrying...")
                time.sleep(2)
            else:
                r.raise_for_status()

def scrape_mobile_data(productlink):
    while True:
        user_agent = random.choice(user_agents)
        proxy = random.choice(proxies)
        headers = {'User-Agent': user_agent}
        s = requests.get(productlink, headers=headers)
        soup = BeautifulSoup(s.content, 'lxml')
        response = requests.get(productlink, headers=headers, proxies=proxy)
        print(response.status_code)

        if response.status_code == 200:
            title = get_title(soup)
            rating = get_rating(soup)
            price = get_price(soup)
            delivery_time = get_deliverytime(soup)
        
            condition = get_condition(soup)
            image_url = get_image_url(soup)  

            if all([title]):
                print("Title:", title)
                print("Rating:", rating)
                print("Price:", price)
                print("Delivery Time:", delivery_time)

                print("Condition:", condition)
                print("Image URL:", image_url)
                insert_data(title, productlink, 2, "Flipkart", price, rating, delivery_time, image_url, condition)
                break
        elif response.status_code == 500:
                print("500 Service Unavailable - Retrying...")
                time.sleep(2)
                continue
        elif response.status_code == 429:
                print("429 Service Unavailable - Retrying...")
                time.sleep(2)
                continue
        else:
            response.raise_for_status()
            continue

    

def main():
    num_pages = random.randint(1, 41)
    
    for _ in range(num_pages):
        i = random.randint(1, num_pages)
        if i == 1:
            url = "https://www.flipkart.com/mobiles/pr?sid=tyy%2C4io&q=mobiles&otracker=categorytree&sort=popularity"
        else:
            url = f"https://www.flipkart.com/mobiles/pr?sid=tyy%2C4io&q=mobiles&otracker=categorytree&sort=popularity&page={i}"
        print(url)
        print(i)
        mobiles(url)


if __name__ == "__main__":
    main()
