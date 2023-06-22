import argparse
import os
import json
import csv
from datetime import datetime, timedelta


class Customer(object):
    def __init__(self, customer_id, loyalty_score):
        self.customer_id = customer_id
        self.loyalty_score = loyalty_score


def get_params() -> dict:
    parser = argparse.ArgumentParser(description='DataTest')
    parser.add_argument('--customers_location', required=False, default="./input_data/starter/customers.csv")
    parser.add_argument('--products_location', required=False, default="./input_data/starter/products.csv")
    parser.add_argument('--transactions_location', required=False, default="./input_data/starter/transactions/")
    parser.add_argument('--output_location', required=False, default="./output_data/outputs/")
    return vars(parser.parse_args())


def load_customers(file_path: str):
    customers = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        for row in csv_reader:
            if len(row) >= 2:  # Check if row has at least 2 columns
                customer_id = row[0]
                loyalty_score = int(row[1])
                customers.append(Customer(customer_id, loyalty_score))
    return customers



def load_products(file_path: str):
    products = {}
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        for row in csv_reader:
            if len(row) >= 3:  # Check if row has at least 3 columns
                product_id = row[0]
                product_description = row[1]
                product_category = row[2]
                if product_category not in products:
                    products[product_category] = {}
                products[product_category][product_description] = product_id
    return products



def process_transactions(transactions_location: str, customers, products):
    purchase_count = {}
    for day_directory in os.listdir(transactions_location):
        day_directory_path = os.path.join(transactions_location, day_directory)
        if os.path.isdir(day_directory_path):
            for filename in os.listdir(day_directory_path):
                file_path = os.path.join(day_directory_path, filename)
                with open(file_path, 'r') as file:
                    for line in file:
                        transaction = json.loads(line)
                        customer_id = transaction['customer_id']
                        basket = transaction['basket']
                        for item in basket:
                            product_id = item['product_id']
                            # print('product',products)
                            # print('product_id',product_id)
                            product_category = get_product_category(products, product_id)
                            purchase_count_key = (customer_id, product_id, product_category)
                            if purchase_count_key not in purchase_count:
                                purchase_count[purchase_count_key] = 0
                            purchase_count[purchase_count_key] += 1
    return purchase_count


def get_product_category(product_data: dict,product_id: str) -> str:
    for category, products in product_data.items():
        if product_id in products.values():
            return category
    return None


def generate_output(customers, purchase_count):
    output = []
    for customer in customers:
        customer_id = customer.customer_id
        loyalty_score = customer.loyalty_score
        for (customer_id_key, product_id, product_category), count in purchase_count.items():
            if customer_id == customer_id_key:
                output.append({
                    'customer_id': customer_id,
                    'loyalty_score': loyalty_score,
                    'product_id': product_id,
                    'product_category': product_category,
                    'purchase_count': count
                })
    return output


def main():
    params = get_params()
    customers = load_customers(params['customers_location'])
    products = load_products(params['products_location'])
    purchase_count = process_transactions(params['transactions_location'], customers, products)
    output = generate_output(customers, purchase_count)
    output_location = params['output_location']
    os.makedirs(output_location, exist_ok=True)
    output_file = os.path.join(output_location, 'output.json')
    with open(output_file, 'w') as file:
        json.dump(output, file)


if __name__ == "__main__":
    main()
