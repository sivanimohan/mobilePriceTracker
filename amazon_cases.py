import requests
from bs4 import BeautifulSoup
import time
import random
import mysql.connector
import re
from datetime import datetime

db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="tracker@2024",
    database="mobilepricetracker",
    port="3307"
    
)
db_cursor = db_connection.cursor()

baseurl = "https://www.amazon.in/"

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




def get_title(soup):
        br = soup.find('span', class_='a-size-large product-title-word-break')
        if br:
            return br.text.strip()
        return None    


def get_rating(soup):
    rg = soup.find('span', class_='a-icon-alt')
    if rg:
        return rg.text.strip()
    return None

def get_price(soup):
    pr = soup.find('span', class_='a-price-whole')
    if pr:
        return pr.text.strip()
    return None


def get_deliverytime(soup):
    de = soup.find('span', attrs={'data-csa-c-delivery-time': True})
    if de:
        delivery_text = de.text.strip()

        delivery_text = re.sub(r'\bFREE\s*delivery\b', '', delivery_text, flags=re.IGNORECASE).strip()
        delivery_text = re.sub(r'\bDetails\b', '', delivery_text, flags=re.IGNORECASE).strip()
        delivery_text = re.sub(r'on orders dispatched by Amazon.*?\.', '', delivery_text, flags=re.IGNORECASE).strip()

        print(delivery_text)
        return convert_to_days_from_today(delivery_text)
    return None

def convert_to_days_from_today(delivery_text):
  
    date_pattern = re.compile(r'\b(\w+), (\d{1,2}) (\w+)\b')
    match = date_pattern.search(delivery_text)
    if match:
        day = int(match.group(2))
        month = match.group(3)
        year = datetime.now().year
        
        try:
            delivery_date = datetime.strptime(f"{day} {month} {year}", "%d %B %Y")
        except ValueError:
            return None
        
        today = datetime.now()
        delta = (delivery_date - today).days
        
        if delta < 0:
            delivery_date = datetime.strptime(f"{day} {month} {year + 1}", "%d %B %Y")
            delta = (delivery_date - today).days
        
        return f"{delta} days"
    return None


def get_image_url(soup):
    image_url_div = soup.find('div', id='imgTagWrapperId', class_='imgTagWrapper')
    if image_url_div:
        image_url = image_url_div.find('img')
        if image_url:
            return image_url.get('src')
    return None


def insert_data(title, redirect_link, platform_id, platform_name, price, rating, delivery_time, image_url):
    try:
  
        db_cursor.execute("SELECT redirect_link FROM Cases WHERE redirect_link = %s", (redirect_link,))
        existing_link = db_cursor.fetchone()

        if not existing_link:
            sql = "INSERT INTO Cases (title, redirect_link, platform_id, platform_name, price, rating, delivery_time, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (title, redirect_link, platform_id, platform_name, price, rating, delivery_time, image_url)
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
                  productlist = soup.find_all('h2', class_='a-size-mini a-spacing-none a-color-base s-line-clamp-4')
                  for item in productlist:
                    for link in item.find_all('a', class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal', href=True):
                        if (link not in productlinks):
                            productlink = baseurl + link['href']
                            productlinks.append(productlink)
                            print(productlink)
                            scrape_mobile_data(productlink)
                            v.append(url)   
            elif r.status_code == 503:
                print("503 Service Unavailable - Retrying...")
                time.sleep(2)  
            else:
                r.raise_for_status()

def scrape_mobile_data(productlink):
    while True:
        user_agent = random.choice(user_agents)
        proxy = random.choice(proxies)
        headers = {'User-Agent': user_agent}
        response = requests.get(productlink, headers=headers, proxies=proxy)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            title = get_title(soup)
            rating = get_rating(soup)
            price = get_price(soup)
            delivery_time = get_deliverytime(soup)
            image_url = get_image_url(soup)

            if all([title, rating,price, delivery_time, image_url]):
                print("Title:", title)
                print("Rating:", rating)
                print("Price:", price)
                print("Delivery Time:", delivery_time)
                print("Image URL:", image_url)
                truncated_url = productlink[:255 - 3] + '...'
                insert_data(title, truncated_url, 1, "Amazon", price, rating, delivery_time, image_url)
                break
            else:
                continue
        else:
            response.raise_for_status()

    

def main():
    
    num_pages = random.randint(1, 21)
    
    for _ in range(num_pages):
        i = random.randint(1, num_pages)
        if i == 1:
            url = "https://www.amazon.in/s?rh=n%3A21529679031%2Cp_72%3A4-&content-id=amzn1.sym.601891be-591c-4695-b226-dfc2707ab366&pd_rd_r=a273aed9-5831-432f-ae78-5b39cc839d1c&pd_rd_w=EpiYr&pd_rd_wg=5RY7Z&pf_rd_p=601891be-591c-4695-b226-dfc2707ab366&pf_rd_r=AKX1HDX1HEGC88CTJ4X1&ref=Oct_d_otopr_S"
        else:
            url = f"https://www.amazon.in/s?i=electronics&rh=n%3A21529679031%2Cp_72%3A1318476031&page={i}&content-id=amzn1.sym.601891be-591c-4695-b226-dfc2707ab366&pd_rd_r=a273aed9-5831-432f-ae78-5b39cc839d1c&pd_rd_w=EpiYr&pd_rd_wg=5RY7Z&pf_rd_p=601891be-591c-4695-b226-dfc2707ab366&pf_rd_r=AKX1HDX1HEGC88CTJ4X1&qid=1716480446&ref=sr_pg_{i}"
        print(url)
        print(i)
        mobiles(url)


if __name__ == "__main__":
    main()


