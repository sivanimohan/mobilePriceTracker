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
        price_text = re.sub(r'[^\d.]', '', pr.text.strip())
        return price_text
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
            condition = get_condition(soup)
            image_url = get_image_url(soup)  

            if all([price]):
                print("Title:", title)
                print("Rating:", rating)
                print("Price:", price)
                print("Delivery Time:", delivery_time)
                print("Condition:", condition)
                print("Image URL:", image_url)
                insert_data(title, productlink, 3, "Reliance Digitals", price, rating, delivery_time, image_url, condition)
                break
            
            else:
                    break
        else:
            response.raise_for_status()

    

def main():
    num_pages = random.randint(1,51)
    for _ in range(num_pages):
        i = random.randint(1, num_pages)
        if i == 1:
            url = "https://www.reliancedigital.in/search?q=mobile%20phone:relevance:availability:Exclude%20out%20of%20Stock&page=0"
        else:
            url = f"https://www.reliancedigital.in/search?q=mobile%20phone:relevance:availability:Exclude%20out%20of%20Stock&page={i-1}"
        print(url)
        print(i)
        mobiles(url)


if __name__ == "__main__":
    main()
