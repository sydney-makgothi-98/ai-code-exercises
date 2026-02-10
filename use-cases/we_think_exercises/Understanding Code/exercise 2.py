def validate_order(order, inventory, customer_data):
    item_id = order['item_id']
    quantity = order['quantity']
    customer_id = order['customer_id']

    if item_id not in inventory:
        return False, {'order_id': order['order_id'], 'error': 'Item not in inventory'}

    if inventory[item_id]['quantity'] < quantity:
        return False, {'order_id': order['order_id'], 'error': 'Insufficient quantity'}

    if customer_id not in customer_data:
        return False, {'order_id': order['order_id'], 'error': 'Customer not found'}

    return True, None


def calculate_base_price(item, quantity):
    return item['price'] * quantity


def apply_premium_discount(price, customer):
    if customer['premium']:
        return price * 0.9
    return price


def calculate_shipping(price, customer):
    if customer['location'] == 'domestic':
        if price < 50:
            return 5.99
        return 0
    return 15.99


def calculate_tax(price):
    return price * 0.08


def update_inventory(item, quantity):
    item['quantity'] -= quantity


def build_order_result(order, item_id, quantity, customer_id, price, shipping, tax, final_price):
    return {
        'order_id': order['order_id'],
        'item_id': item_id,
        'quantity': quantity,
        'customer_id': customer_id,
        'price': price,
        'shipping': shipping,
        'tax': tax,
        'final_price': final_price
    }


def process_order(order, inventory, customer_data):
    item_id = order['item_id']
    quantity = order['quantity']
    customer_id = order['customer_id']

    item = inventory[item_id]
    customer = customer_data[customer_id]

    price = calculate_base_price(item, quantity)
    price = apply_premium_discount(price, customer)
    update_inventory(item, quantity)

    shipping = calculate_shipping(price, customer)
    tax = calculate_tax(price)
    final_price = price + shipping + tax

    result = build_order_result(
        order, item_id, quantity, customer_id, price, shipping, tax, final_price
    )

    return result, final_price


def process_orders(orders, inventory, customer_data):
    results = []
    total_revenue = 0
    error_orders = []

    for order in orders:
        is_valid, error = validate_order(order, inventory, customer_data)
        if not is_valid:
            error_orders.append(error)
            continue

        result, final_price = process_order(order, inventory, customer_data)
        results.append(result)
        total_revenue += final_price

    return {
        'processed_orders': results,
        'error_orders': error_orders,
        'total_revenue': total_revenue
    }