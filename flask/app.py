import pymysql
from flask import Flask
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import jsonify
from flask import flash, request
from flask import Flask, render_template
import requests

app = Flask(__name__)
CORS(app)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'testdb'
app.config['MYSQL_DATABASE_HOST'] = 'db'
mysql.init_app(app)

@app.route('/prices')
def prices():
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM prices ORDER BY price ASC")
		pricesRows = cursor.fetchall()
		response = jsonify(pricesRows)
		response.status_code = 200
		return response
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()


@app.route('/news')
def get_news():
    # Remplacez par l'URL réelle de votre API d'actualités
    api_url = 'https://newsapi.org/v2/everything?q=iphone&from=2024-01-03&to=2024-01-03&sortBy=popularity&apiKey=3005e89b1f17469da9339a6c21139b10'
    response = requests.get(api_url)
    
    if response.status_code == 200:
        news_items = response.json().get('articles')
    else:
        news_items = []

    # Rendre une page HTML avec les articles récupérés
    return render_template('forecast.html', articles=news_items)

@app.route('/states')
def states():
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT distinct etat FROM prices")
		pricesRows = cursor.fetchall()
		response = jsonify(pricesRows)
		response.status_code = 200
		return response
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()







@app.route('/categories')
def categories():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Utilisez une sous-requête avec ROW_NUMBER pour limiter à 3 éléments par 'etat'
        query = """
        SELECT id, title, price, image_url, product_url, seller, etat FROM (
            SELECT id, title, price, image_url, product_url, seller, etat,
            ROW_NUMBER() OVER (PARTITION BY etat ORDER BY price ASC) as rn
            FROM prices
        ) AS rows_filtered WHERE rn <= 3
        ORDER BY etat ASC, price ASC;
        """
        
        cursor.execute(query)
        pricesRows = cursor.fetchall()

        groupedData = {}
        for row in pricesRows:
            etat = row['etat']
            if etat not in groupedData:
                groupedData[etat] = []
            if len(groupedData[etat]) < 3:  
                groupedData[etat].append({
                    "id": row['id'],
                    "title": row['title'],
                    "price": row['price'],
                    "image_url": row['image_url'],
                    "product_url": row['product_url'],
                    "seller": row['seller']
                })

        response = jsonify(groupedData)
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
    finally:
        if cursor: 
            cursor.close()
        if conn:
            conn.close()





@app.route('/')
def index():
    return render_template('index.html')


@app.route('/categorie')
def categorie():
    return render_template('categorie.html')

@app.route('/news')
def actus():
    return render_template('forecast.html')


@app.route('/prices/<title>')
def pricesIsin(title):
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM prices WHERE title=%s ORDER BY datafrom DESC LIMIT 5", title)
		pricesRows = cursor.fetchall()
		response = jsonify(pricesRows)
		response.status_code = 200
		return response
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()



def update_database_logic():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Vérifiez si la colonne 'etat' existe déjà
        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE table_schema = 'testdb' AND table_name = 'prices' AND column_name = 'etat';
        """)
        if cursor.fetchone()[0] == 0:
            # Si la colonne 'etat' n'existe pas, l'ajouter
            cursor.execute("ALTER TABLE prices ADD COLUMN etat VARCHAR(255);")
        
        # Définir les prix minimum et maximum pour 'Certideal'
        cursor.execute("SELECT MIN(price) FROM prices WHERE seller = 'Certideal';")
        min_price = cursor.fetchone()[0]
        cursor.execute("SELECT MAX(price) FROM prices WHERE seller = 'Certideal';")
        max_price = cursor.fetchone()[0]
        
        # Mise à jour de la colonne 'etat' en fonction des prix
        cursor.execute("""
            UPDATE prices
            SET etat = CASE
                WHEN price <= %s THEN 'Correct'
                WHEN price >= %s THEN 'Parfait'
                ELSE 'Très bon état'
            END
            WHERE seller = 'Certideal';
        """, (min_price, max_price))
        
        # Mise à jour des lignes où 'etat' est NULL à 'premium'
        cursor.execute("UPDATE prices SET etat = 'Premium' WHERE etat IS NULL;")

        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback() # Rollback en cas d'erreur
        print(str(e))
    finally:
        cursor.close()
        conn.close()





@app.before_first_request
def startup():
    update_database_logic()

@app.route('/update-prices', methods=['POST'])
def update_prices():
    update_database_logic()
    return jsonify(success=True)




@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    response = jsonify(message)
    response.status_code = 404
    return response
		
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

    
