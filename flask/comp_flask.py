from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)


try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="tracker@2024",
        database="mobilepricetracker",
        port="3307"
    )
    print("Database connected successfully")
except mysql.connector.Error as err:
    print(f"Database connection error: {err}")
    exit(1)


@app.route('/', methods=['GET'])
def index():
    return render_template('comp.html')


@app.route('/search_mobiles', methods=['POST'])
def search_mobiles():
    data = request.get_json()
    search_query = data.get('search_query', '').lower()

    cursor = conn.cursor(dictionary=True)
    sql_query = "SELECT title, price, rating FROM Mobiles WHERE title LIKE %s"
    params = ['%' + search_query + '%']

    cursor.execute(sql_query, params)
    mobile_data = cursor.fetchall()
    cursor.close()

    mobiles = [{'name': mobile['title'], 'price': mobile['price']} for mobile in mobile_data]

    return jsonify({'mobiles': mobiles})


@app.route('/compare_mobiles', methods=['POST'])
def compare_mobiles():
    data = request.get_json()
    print("Received data:", data)  

    filters = data.get('filters', {})
    print(filters)
    mobiles_to_compare = [data.get('mobile1'), data.get('mobile2')]

    cursor = conn.cursor(dictionary=True)

    
    cursor.execute("SELECT * FROM Mobiles WHERE title IN (%s, %s)", mobiles_to_compare)
    comparison_data = cursor.fetchall()
    print(comparison_data)
    if len(comparison_data) < 2:
        return jsonify({'error': 'One or both mobiles not found in the database.'}), 404

    
    colour = filters.get('colour', [])
    ram = filters.get('ram', [])
    memory = filters.get('memory', [])
    price = filters.get('price', [])
    rating = filters.get('rating', [])
    
    ram_values = ['2GB', '4GB', '6GB', '8GB', '12GB', '16GB']
    memory_values = ['32GB', '64GB', '128GB', '256GB', '512GB']
    max_price = 200000.00
    max_rating = 5.0  
    def extract_ram(title):
        for ram in ram_values:
            if ram in title:
                return ram
        return None

    
    def extract_memory(title):
        for memory in memory_values:
            if memory in title:
                return memory
        return None
    import re
    
    def extract_price(price_value):
        return (float(price_value)) 
    def extract_rating(rating_value):
   
       if isinstance(rating_value, str) and '/' in rating_value:
        
        rating_value = rating_value.split('/')[0]
   
       elif isinstance(rating_value, str):
        
          match = re.match(r'(\d+(\.\d+)?)\s*out of 5 stars', rating_value)
          if match:
            rating_value = match.group(1)

    
       return float(rating_value)


    mobile_scores = []
    for mobile in comparison_data:
        score = 0

        if ram_values:
            mobile_ram = extract_ram(mobile['title'])
            if mobile_ram:
                max_ram = max(ram_values, key=lambda x: int(x.replace('GB', '')))
                converted_ram_score = (int(mobile_ram.replace('GB', '')) / int(max_ram.replace('GB', ''))) * 10
                print(f" RAM score (out of 10): {converted_ram_score}")
                score += converted_ram_score

        
        if memory_values:
            mobile_memory = extract_memory(mobile['title'])
            if mobile_memory:
                max_memory = max(memory_values, key=lambda x: int(x.replace('GB', '')))
                converted_memory_score = (int(mobile_memory.replace('GB', '')) / int(max_memory.replace('GB', ''))) * 10
                print(f"Memory score (out of 10): {converted_memory_score}")
                score += converted_memory_score

        
        if max_price:
            mobile_price = extract_price(mobile['price'])
            converted_price_score = ((mobile_price/max_price)*10)
            reversed_price_score = 10 - converted_price_score
            print(f"Price score (out of 10): {reversed_price_score}")
            score += reversed_price_score

        
        if max_rating:
            mobile_rating = extract_rating(mobile['rating'])
            converted_rating_score = (mobile_rating / max_rating) * 10
            print(f"Rating score (out of 10): {converted_rating_score}")
            score += converted_rating_score

        
        if colour: 
          for c in colour:  
            if c.lower() in mobile['title'].lower(): 
             score += 10 
             break 

        
        if ram:  
               mobile_ram = extract_ram(mobile['title'])
               for r in ram:
                  if r.lower() in mobile_ram.lower() : 
                    score += 10
                    break 


        if memory:  
               mobile_memory = extract_memory(mobile['title'])
               for m in memory:
                  if m.lower() in mobile_memory.lower() :
                    score += 10
                    break 

        
        if price: 
         for selected_range in price:
           mobile_price = float(mobile['price'])
           if selected_range == "below20000" and mobile_price < 20000:
            score += 10  
            break
           elif selected_range == "20000to40000" and 20000 <= mobile_price <= 40000:
            score += 10  
            break
           elif selected_range == "above40000" and mobile_price > 40000:
            score += 10  
            break

        
           if rating:  
              for selected_range in rating:  
                 mobile_rating = float(mobile['rating'])  
                 if selected_range == "4_and_above" and mobile_rating >= 4.0:
                   score += 10  
                   break
                 elif selected_range == "3_and_above" and mobile_rating >= 3.0:
                    score += 10 
                    break


        mobile_scores.append({
            'name': mobile['title'],
            'price': mobile['price'],
            'rating': mobile['rating'],
            'score': score,
            'condition': mobile['new_refurbished'],
            'platform': mobile['platform_name'], 
            'delivery_time': mobile['delivery_time'],  
            'image': mobile['image_url'], 
            'link': mobile['redirect_link'] 
        })

    
    mobile1_data = next((m for m in mobile_scores if m['name'] == data.get('mobile1')), None)
    mobile2_data = next((m for m in mobile_scores if m['name'] == data.get('mobile2')), None)

    
    better_mobile = max([mobile1_data, mobile2_data], key=lambda x: x['score']) if mobile1_data and mobile2_data else None

    return jsonify({
        'mobile1': mobile1_data,
        'mobile2': mobile2_data,
        'better_mobile': better_mobile['name'] if better_mobile else None
    })




if __name__ == '__main__':
    app.run(debug=True, port=5003)
