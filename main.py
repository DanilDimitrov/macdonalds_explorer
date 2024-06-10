from flask import Flask, jsonify
import json
from parser import update_products

app = Flask(__name__)

with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


@app.route('/all_products', methods=['GET'])
def all_products():
    return jsonify(data)


@app.route('/products/<string:product_name>', methods=['GET'])
def get_product(product_name):
    try:
        for product in list(data):
            if product['name'] == product_name:
                return jsonify(product)
        return jsonify({'error': 'Product not found'}), 404
    except:
        return jsonify({'error': 'Product not found'}), 404


@app.route('/products/<string:product_name>/<string:product_field>', methods=['GET'])
def get_product_field(product_name, product_field):
    try:
        for product in data:
            if product['name'] == product_name:
                if product_field in product:
                    return jsonify({product_field: product[product_field]})
                else:
                    return jsonify({'error': 'Field not found'}), 404
        return jsonify({'error': "Product not found"}), 404
    except:
        return jsonify({'error': 'Product not found'}), 404


if __name__ == "__main__":
    update_products()
    app.run()