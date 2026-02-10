# inventory_analysis.py
def find_product_combinations(products, target_price, price_margin=10, progress_step=100):
    """
    Find all pairs of products where the combined price is within
    the target_price ± price_margin range.

    Args:
        products: List of dictionaries with 'id', 'name', and 'price' keys
        target_price: The ideal combined price
        price_margin: Acceptable deviation from the target price

    Returns:
        List of dictionaries with product pairs and their combined price
    """
    results = []

    lower_bound = target_price - price_margin
    upper_bound = target_price + price_margin
    total_products = len(products)

    # For each possible pair of products (only evaluate each pair once)
    for i in range(total_products):
        if progress_step and i % progress_step == 0:
            print(f"Processing product {i + 1} of {total_products}")

        product1 = products[i]
        price1 = product1['price']

        for j in range(i + 1, total_products):
            product2 = products[j]
            combined_price = price1 + product2['price']

            if lower_bound <= combined_price <= upper_bound:
                results.append({
                    'product1': product1,
                    'product2': product2,
                    'combined_price': combined_price,
                    'price_difference': abs(target_price - combined_price)
                })

    # Sort by price difference from target
    results.sort(key=lambda x: x['price_difference'])
    return results

# Example usage
if __name__ == "__main__":
    import time
    import random

    # Generate a large list of products
    print("Generating Product List")
    product_list = []
    for i in range(5000):
        product_list.append({
            'id': i,
            'name': f'Product {i}',
            'price': random.randint(5, 500)
        })

    # Measure execution time
    print(f"Finding product combinations for {len(product_list)} products")
    start_time = time.time()
    combinations = find_product_combinations(product_list, 500, 50)
    end_time = time.time()

    print(f"Found {len(combinations)} product combinations")
    print(f"Execution time: {end_time - start_time:.2f} seconds")