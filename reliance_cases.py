import requests
from bs4 import BeautifulSoup
import time
import random
import datetime
import re
import mysql.connector
db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="tracker@2024",
    database="mobilepricetracker",
    port="3307"
    
)
db_cursor = db_connection.cursor()
baseurl = "https://www.reliancedigital.in"

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
        br = soup.find('h1', class_='pdp__title')
        if br:
            return br.text.strip()
        return None    


def get_rating(soup):
    rg = soup.find('span', class_='TextWeb__Text-sc-1cyx778-0 emga-Df Block-sc-u1lygz-0 iJOtqd')
    if rg:
        return rg.text.strip()
    return None

def get_price(soup):
    pr = soup.find('span', class_='TextWeb__Text-sc-1cyx778-0 kFBgPo')
    if pr:
        price_text = pr.text.strip()
        p = price_text.replace('₹', '')
        return p
    return None
def get_deliverytime():
    today = datetime.datetime.now()
    random_days = random.randint(2, 7)
    delivery_date = today + datetime.timedelta(days=random_days)
 
    days_from_today = (delivery_date - today).days

    day = delivery_date.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    day_with_suffix = f"{day}{suffix}"
    
    
    formatted_delivery_date = delivery_date.strftime(f"{day_with_suffix} %B, %A")
    
    return f"{days_from_today} days"


def get_condition(soup):
    condition =soup.find('h1', class_='pdp__title')
    if condition:
            if "Refurbished" in condition:
                return "Refurbished" 
            else:
                return "New"

def get_image_url(soup):
        img = soup.find('img', id='myimage', class_='img-center pdp__mainHeroImgContainer imgCenter')
        if img:
            image_url = img.get('data-srcset')
            return  (baseurl + image_url)
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
            time.sleep(3)  
            print("Response Code:", r.status_code)
            
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'lxml')
                productlist = soup.find_all('div', class_='sp')  
                print(productlist)
                for item in productlist:
                   for link in item.find_all('a', href=True): 
                     productlink = baseurl + link['href']
                     if productlink not in productlinks:  
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
        s = requests.get(productlink, headers=headers)
        soup = BeautifulSoup(s.content, 'lxml')
        response = requests.get(productlink, headers=headers, proxies=proxy)
        

        if response.status_code == 200:
            title = get_title(soup)
            rating = get_rating(soup)
            price = get_price(soup)
            delivery_time = get_deliverytime()
            image_url = get_image_url(soup)  

            if all([price,rating]):
                print("Title:", title)
                print("Rating:", rating)
                print("Price:", price)
                print("Delivery Time:", delivery_time)
                print("Image URL:", image_url)
                truncated_url = productlink[:255]
                insert_data(title,truncated_url, 3, "Reliance Digitals", price, rating, delivery_time, image_url)
                break
            else:
                 break
        else:
            response.raise_for_status()

    

def main():
    num_pages = random.randint(1,21)
    for _ in range(num_pages):
        i = random.randint(1, num_pages)
        if i == 1:
            url = "https://www.reliancedigital.in/search?q=mobile%20cases:relevance"
        else:
            url = f"https://www.reliancedigital.in/search?q=mobile%20cases:relevance&page={i-1}"
        print(url)
        print(i)
        mobiles(url)


if __name__ == "__main__":
    main()
