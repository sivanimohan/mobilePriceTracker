from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="tracker@2024",
    database="mobilepricetracker",
    port="3307"
)

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_colours = []
    selected_conditions = []
    selected_materials = []
    selected_ratings = []
    search_query = ''
    selected_sortby = ''
    selected_prices = []
    selected_delivery_times=[]

    if request.method == 'POST':
        selected_colours = request.form.getlist('colour')
        selected_conditions = request.form.getlist('condition')
        selected_materials = request.form.getlist('material')
        selected_ratings = request.form.getlist('rating')
        search_query = request.form.get('search_query')
        selected_sortby = request.form.get('sortBy')
        selected_prices = request.form.getlist('price')
        selected_delivery_times = request.form.getlist('delivery')

        cursor = conn.cursor()

        sql_query = "SELECT * FROM Cases WHERE 1"
        conditions = []
        params = []

        if search_query:
            conditions.append("title LIKE %s")
            params.append('%' + search_query + '%')

        if selected_colours:
            colour_conditions = ["title LIKE %s" for _ in selected_colours]
            conditions.append("(" + " OR ".join(colour_conditions) + ")")
            params.extend(['%' + colour + '%' for colour in selected_colours])

        if selected_conditions:
            condition_conditions = ["new_refurbished = %s" for _ in selected_conditions]
            conditions.append("(" + " OR ".join(condition_conditions) + ")")
            params.extend(selected_conditions)

        if selected_materials:
            material_conditions = ["title LIKE %s" for _ in selected_materials]
            conditions.append("(" + " OR ".join(material_conditions) + ")")
            params.extend(['%' + material + '%' for material in selected_materials])

        if selected_ratings:
            rating_conditions = []
            for rating_value in selected_ratings:
                if rating_value == '4':
                    rating_conditions.append("CAST(SUBSTRING_INDEX(rating, ' ', 1) AS DECIMAL(5,1)) >= 4.0")
                elif rating_value == '3':
                    rating_conditions.append("CAST(SUBSTRING_INDEX(rating, ' ', 1) AS DECIMAL(5,1)) >= 3.0")
                elif rating_value == '2':
                    rating_conditions.append("CAST(SUBSTRING_INDEX(rating, ' ', 1) AS DECIMAL(5,1)) >= 2.0")
                elif rating_value == '1':
                    rating_conditions.append("CAST(SUBSTRING_INDEX(rating, ' ', 1) AS DECIMAL(5,1)) >= 1.0")
            if rating_conditions:
                conditions.append("(" + " OR ".join(rating_conditions) + ")")

        if selected_prices:
            price_conditions = []
            for price_range in selected_prices:
                if price_range == 'below200':
                    price_conditions.append("price < 200")
                elif price_range == '200to500':
                    price_conditions.append("price BETWEEN 200 AND 500")
                elif price_range == 'above500':
                    price_conditions.append("price > 500")
            if price_conditions:
                conditions.append("(" + " OR ".join(price_conditions) + ")")

        if selected_delivery_times:
            delivery_conditions = []
            for delivery_time in selected_delivery_times:
                if delivery_time == 'within3days':
                    delivery_conditions.append("delivery_time <= 3")
                elif delivery_time == '3to7days':
                    delivery_conditions.append("delivery_time BETWEEN 3 AND 7")
                elif delivery_time == 'morethan7days':
                    delivery_conditions.append("delivery_time > 7")
            if delivery_conditions:
                conditions.append("(" + " OR ".join(delivery_conditions) + ")")

        if conditions:
            sql_query += " AND " + " AND ".join(conditions)

        if selected_sortby == 'HighToLowPrice':
            sql_query += " ORDER BY price DESC"
        elif selected_sortby == 'LowToHighPrice':
            sql_query += " ORDER BY price ASC"
        elif selected_sortby == 'HighToLowRating':
            sql_query += " ORDER BY CAST(SUBSTRING_INDEX(rating, ' ', 1) AS DECIMAL(5,2)) DESC"
        elif selected_sortby == 'LowToHighRating':
            sql_query += " ORDER BY CAST(SUBSTRING_INDEX(rating, ' ', 1) AS DECIMAL(5,2)) ASC"
        elif selected_sortby == 'deliverytime':
            sql_query += " ORDER BY delivery_time ASC"

        cursor.execute(sql_query, params)
        cases_data = cursor.fetchall()
        cursor.close()

        return render_template('case3.html', cases_data=cases_data,
                               search_query=search_query, selected_colours=selected_colours,
                               selected_conditions=selected_conditions, selected_materials=selected_materials,
                               selected_ratings=selected_ratings, selected_sortby=selected_sortby,
                               selected_delivery_times=selected_delivery_times, selected_prices=selected_prices)
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Cases")
        cases_data = cursor.fetchall()
        cursor.close()

        return render_template('case3.html', cases_data=cases_data,
                               search_query=search_query, selected_colours=selected_colours,
                               selected_conditions=selected_conditions, selected_materials=selected_materials,
                               selected_ratings=selected_ratings, selected_sortby=selected_sortby,
                               selected_delivery_times=selected_delivery_times, selected_prices=selected_prices)

if __name__ == '__main__':
    app.run(debug=True, port=5002)

