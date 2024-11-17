from flask import Flask, jsonify, request, session
from flask_cors import CORS  # Import CORS
from helper import execute_query
import secrets, sqlite3

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#home page of the website
@app.route('/')
def homepage():
    return (
        '<center><b><h1>Welcome to DesigNest!</h1></b></center>'
        '<b><h2>Use: /signup</h2></b><br><br>'
        '<b><h2>Use: /login</h2></b><br><br>'
        '<b><h3>Use: /user/< int:id ></h3></b><br><br>'
        '<b><h4>Use: /product-collection</h4></b><br><br>'
        '<b><h4>Use: /product-clothing</h4></b><br><br>'
        '<b><h5>Use: /view-cart</h5></b>'
    )

#Signup page
@app.route('/signup', methods=['POST'])
def signup_user():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        location = data.get('location')
        state = data.get('state')

        if not all([name, email, password, location, state]):
            return jsonify({'error': 'Missing required fields'}), 400

        query = f"INSERT INTO customer_table (name, email, password, location, state) VALUES ('{name}', '{email}', '{password}', '{location}', '{state}')"
        execute_query(query)
        return jsonify({'message': 'User signed up successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    # Fetch user data from the database
    query = f"SELECT * FROM customer_table WHERE email = '{email}' AND password = '{password}'"
    user = execute_query(query)
    if user:
        session['user_id'] = user[0]['customer_id']  # Store user ID in session
        return jsonify({'message': 'User logged in successfully', 'user': user[0]})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

#user profile
@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = execute_query(f"SELECT * FROM customer_table WHERE customer_id = {id}")
    if user:
        return jsonify(user)
    else:
        return jsonify({'message: No matching user found'})
    
# Fetch user profile
# Profile API
@app.route('/profile', methods=['GET'])
def profile():
    if 'user_id' in session:  # Check if the user is logged in
        user_id = session['user_id']
        query = "SELECT * FROM customer_table WHERE customer_id = ?"
        user = execute_query(query, (user_id,))
        if user:
            return jsonify(user[0])  # Return user details
        else:
            return jsonify({'message': 'No matching user found'}), 404
    else:
        return jsonify({'message': 'User not logged in'}), 401

#product details from collection table
@app.route('/product-collection', methods=['GET'])
def product_collection():
    product = execute_query("SELECT * FROM collection_table")
    return jsonify(product)

#product details
@app.route('/product-clothes', methods=['GET'])
def product_clothing():
    product = execute_query("SELECT * FROM  clothing_item_table")
    return jsonify(product)

#view cart
@app.route('/view-cart/<int:id>', methods=['GET'])
def view_cart(id):
    # Fetch the cart details for the customer
    cart_query = "SELECT * FROM cart_table WHERE customer_id = {}".format(id)
    cart = execute_query(cart_query)
    
    if cart:
        return jsonify(cart)
    else:
        return '<h1 style= "font-size: 56px;">No customer found</h1>' , 404

#add_product
@app.route('/add-product', methods=['POST'])
def add_product():
    try:
        data = request.json
        product_name = data.get('product_name')
        description = data.get('description')
        price = data.get('price')
        category = data.get('category')
        image = data.get('image')  # Assuming image is sent as a base64 string or URL

        if not all([product_name, description, price, category]):
            return jsonify({'error': 'Missing required fields'}), 400

        query = '''
            INSERT INTO products_added (product_name, description, price, category, image)
            VALUES (?, ?, ?, ?, ?)
        '''
        execute_query(query, (product_name, description, price, category, image))
        return jsonify({'message': 'Product added successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug = False)