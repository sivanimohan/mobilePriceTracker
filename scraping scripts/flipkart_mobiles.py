
import requests
from bs4 import BeautifulSoup
import time
import random
import mysql.connector


db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="tracker@2024",
    database="mobilepricetracker",
    port="3307"
    
)
db_cursor = db_connection.cursor()
baseurl = "https://www.flipkart.com"

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
    # Mozilla Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
    # Google Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    # Apple Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0.2 Safari/605.1.15",
    # Microsoft Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.58",
    # Opera
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 OPR/85.0.4344.41",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 OPR/85.0.4344.41",
    # Internet Explorer
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    # Add more user agents as needed
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
        return pr.text.strip()
    return None
def get_deliverytime(soup):
    de = soup.find('span', class_='Y8v7Fl')
    if de:
        return de.text.strip()
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
        else:
            response.raise_for_status()
            continue

    

def main():
    num_pages = random.randint(1, 412)
    
    for _ in range(num_pages):
        i = random.randint(1, num_pages)
        if i == 1:
            url = "https://www.flipkart.com/search?q=mobile+phones&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off"
        else:
            url = f"https://www.flipkart.com/search?q=mobile+phones&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off&page={i}"
        print(url)
        print(i)
        mobiles(url)


if __name__ == "__main__":
    main()