# Mobile Price Tracker

A robust Python-based system for tracking, storing, and updating mobile phone and mobile case prices from Amazon, Flipkart, and Reliance Digital. Supports automated scraping, database integration, and easy updatability, with extensible support for other platforms.

---

## Features

- **Automated Price Scraping**: Scrapes price, delivery estimates, ratings, images, and product details for mobiles and mobile cases from Amazon, Flipkart, and Reliance Digital.
- **Database Integration**: Stores and updates product information in a MySQL database.
- **Duplicate Handling**: Prevents duplicate entries for the same product link.
- **Proxy & User Agent Rotation**: Helps bypass rate limits and scraping blocks.
- **Update Scripts**: Periodically update prices and delivery info for tracked products.
- **Extensible**: Easily add support for more e-commerce platforms or product categories.
- **Flask Interface**: (See `flask/`) Ready for web dashboard integration.

---

## Getting Started

### Prerequisites

- Python 3.7+
- MySQL server running (default config: host `127.0.0.1`, port `3307`, user `root`, password `tracker@2024`)
- Required Python packages (see below)

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/sivanimohan/mobile-price-tracker.git
   cd mobile-price-tracker
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```
   _Or manually:_
   ```bash
   pip install requests beautifulsoup4 mysql-connector-python
   ```

3. **Set Up Database**

   - Create a MySQL database named `mobilepricetracker`.
   - Create tables `Mobiles` and `Cases` as required by the scripts, with columns matching the insert statements.

4. **Configure Credentials**

   - Update MySQL credentials and port in scripts if your setup is different.

---

## Usage

### 1. Scrape and Insert New Products

- **Amazon:**  
  - Mobiles: `python amazon_mobiles.py`
  - Mobile Cases: `python amazon_cases.py`

- **Flipkart:**  
  - Mobiles: `python flipkart_mobiles.py`
  - Mobile Cases: `python flipkart_cases.py`

- **Reliance Digital:**  
  - Mobiles: `python reliance_mobiles.py`
  - Mobile Cases: `python reliance_cases.py`

### 2. Update Prices and Delivery for Existing Products

- **Amazon:**  
  - Mobiles: `python amazon_mobiles_update.py`
  - Cases: `python amazon_cases_update.py`

- **Flipkart:**  
  - Mobiles: `python flipkart_mobiles_update.py`
  - Cases: `python flipkart_cases_update.py`

- **Reliance Digital:**  
  - Mobiles: `python reliance_mobiles_update.py`
  - Cases: `python reliance_cases_update.py`

### 3. Web Dashboard

- See the `flask/` directory for a Flask-based dashboard (setup separately).

---

## File Structure

```
mobile-price-tracker/
├── amazon_mobiles.py             # Scrape and insert new mobile products from Amazon
├── amazon_cases.py               # Scrape and insert new mobile case products from Amazon
├── amazon_mobiles_update.py      # Update prices/delivery for mobiles (Amazon)
├── amazon_cases_update.py        # Update prices/delivery for cases (Amazon)
├── flipkart_mobiles.py           # Scrape Flipkart mobiles
├── flipkart_cases.py             # Scrape Flipkart cases
├── flipkart_mobiles_update.py    # Update Flipkart mobiles
├── flipkart_cases_update.py      # Update Flipkart cases
├── reliance_mobiles.py           # Scrape Reliance Digital mobiles
├── reliance_cases.py             # Scrape Reliance Digital cases
├── reliance_mobiles_update.py    # Update Reliance Digital mobiles
├── reliance_cases_update.py      # Update Reliance Digital cases
├── flask/                        # Flask web dashboard and static assets
├── requirements.txt              # Python dependencies
└── README.md
```

---

## Configuration

- **Proxies/User Agents:**  
  Edit the `proxies` and `user_agents` lists in the scripts for better robustness.

- **Database:**  
  Ensure your MySQL server is accessible and tables exist as expected.

---

## Notes & Tips

- E-commerce sites often change HTML structure; if scraping breaks, update the relevant selectors in the scripts.
- Respect the terms of service of all e-commerce platforms. Use responsibly and avoid frequent scraping.
- For production deployments, rotate proxies frequently and consider using headless browsers if needed.

---

## License

This project is licensed under the MIT License.

---

_Made with ❤️ for competitive pricing and data automation!_
