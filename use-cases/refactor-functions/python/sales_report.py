from datetime import datetime


def _validate_inputs(sales_data, report_type, output_format, date_range):
    if not sales_data or not isinstance(sales_data, list):
        raise ValueError("Sales data must be a non-empty list")

    if report_type not in ['summary', 'detailed', 'forecast']:
        raise ValueError("Report type must be 'summary', 'detailed', or 'forecast'")

    if output_format not in ['pdf', 'excel', 'html', 'json']:
        raise ValueError("Output format must be 'pdf', 'excel', 'html', or 'json'")

    if date_range:
        if 'start' not in date_range or 'end' not in date_range:
            raise ValueError("Date range must include 'start' and 'end' dates")

        start_date = datetime.strptime(date_range['start'], '%Y-%m-%d')
        end_date = datetime.strptime(date_range['end'], '%Y-%m-%d')

        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")


def _apply_date_range_filter(sales_data, date_range):
    if not date_range:
        return sales_data

    start_date = datetime.strptime(date_range['start'], '%Y-%m-%d')
    end_date = datetime.strptime(date_range['end'], '%Y-%m-%d')

    filtered_data = []
    for sale in sales_data:
        sale_date = datetime.strptime(sale['date'], '%Y-%m-%d')
        if start_date <= sale_date <= end_date:
            filtered_data.append(sale)

    return filtered_data


def _apply_filters(sales_data, filters):
    if not filters:
        return sales_data

    for key, value in filters.items():
        if isinstance(value, list):
            sales_data = [sale for sale in sales_data if sale.get(key) in value]
        else:
            sales_data = [sale for sale in sales_data if sale.get(key) == value]

    return sales_data


def _handle_empty_data(sales_data, report_type, output_format):
    if sales_data:
        return None

    print("Warning: No data matches the specified criteria")
    if output_format == 'json':
        return {"message": "No data matches the specified criteria", "data": []}

    return _generate_empty_report(report_type, output_format)


def _calculate_basic_metrics(sales_data):
    total_sales = sum(sale['amount'] for sale in sales_data)
    avg_sale = total_sales / len(sales_data)
    max_sale = max(sales_data, key=lambda x: x['amount'])
    min_sale = min(sales_data, key=lambda x: x['amount'])

    return total_sales, avg_sale, max_sale, min_sale


def _group_sales_data(sales_data, grouping):
    if not grouping:
        return {}

    grouped_data = {}
    for sale in sales_data:
        key = sale.get(grouping, 'Unknown')
        if key not in grouped_data:
            grouped_data[key] = {
                'count': 0,
                'total': 0,
                'items': []
            }

        grouped_data[key]['count'] += 1
        grouped_data[key]['total'] += sale['amount']
        grouped_data[key]['items'].append(sale)

    for key in grouped_data:
        grouped_data[key]['average'] = grouped_data[key]['total'] / grouped_data[key]['count']

    return grouped_data


def _build_base_report(report_type, date_range, filters, total_sales, avg_sale, max_sale, min_sale, transaction_count):
    return {
        'report_type': report_type,
        'date_generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date_range': date_range,
        'filters': filters,
        'summary': {
            'total_sales': total_sales,
            'transaction_count': transaction_count,
            'average_sale': avg_sale,
            'max_sale': {
                'amount': max_sale['amount'],
                'date': max_sale['date'],
                'details': max_sale
            },
            'min_sale': {
                'amount': min_sale['amount'],
                'date': min_sale['date'],
                'details': min_sale
            }
        }
    }


def _add_grouping_to_report(report_data, grouping, grouped_data, total_sales):
    if not grouping:
        return

    report_data['grouping'] = {
        'by': grouping,
        'groups': {}
    }

    for key, data in grouped_data.items():
        report_data['grouping']['groups'][key] = {
            'count': data['count'],
            'total': data['total'],
            'average': data['average'],
            'percentage': (data['total'] / total_sales) * 100
        }


def _add_detailed_transactions(report_data, sales_data):
    report_data['transactions'] = []

    for sale in sales_data:
        transaction = {k: v for k, v in sale.items()}

        if 'tax' in sale and 'amount' in sale:
            transaction['pre_tax'] = sale['amount'] - sale['tax']

        if 'cost' in sale and 'amount' in sale:
            transaction['profit'] = sale['amount'] - sale['cost']
            transaction['margin'] = (transaction['profit'] / sale['amount']) * 100

        report_data['transactions'].append(transaction)


def _build_forecast_section(sales_data):
    monthly_sales = {}

    for sale in sales_data:
        sale_date = datetime.strptime(sale['date'], '%Y-%m-%d')
        month_key = f"{sale_date.year}-{sale_date.month:02d}"

        if month_key not in monthly_sales:
            monthly_sales[month_key] = 0

        monthly_sales[month_key] += sale['amount']

    sorted_months = sorted(monthly_sales.keys())
    growth_rates = []

    for i in range(1, len(sorted_months)):
        prev_month = sorted_months[i-1]
        curr_month = sorted_months[i]

        prev_amount = monthly_sales[prev_month]
        curr_amount = monthly_sales[curr_month]

        if prev_amount > 0:
            growth_rate = ((curr_amount - prev_amount) / prev_amount) * 100
            growth_rates.append(growth_rate)

    avg_growth_rate = sum(growth_rates) / len(growth_rates) if growth_rates else 0

    forecast = {}

    if sorted_months:
        last_month = sorted_months[-1]
        last_amount = monthly_sales[last_month]

        year, month = map(int, last_month.split('-'))

        for i in range(1, 4):
            month += 1
            if month > 12:
                month = 1
                year += 1

            forecast_month = f"{year}-{month:02d}"
            forecast_amount = last_amount * (1 + (avg_growth_rate / 100))

            forecast[forecast_month] = forecast_amount
            last_amount = forecast_amount

    return {
        'monthly_sales': monthly_sales,
        'growth_rates': {sorted_months[i]: growth_rates[i-1] for i in range(1, len(sorted_months))},
        'average_growth_rate': avg_growth_rate,
        'projected_sales': forecast
    }


def _build_charts_section(sales_data, grouping, grouped_data):
    charts_data = {}

    time_chart = {'labels': [], 'data': []}
    date_sales = {}

    for sale in sales_data:
        if sale['date'] not in date_sales:
            date_sales[sale['date']] = 0
        date_sales[sale['date']] += sale['amount']

    for date in sorted(date_sales.keys()):
        time_chart['labels'].append(date)
        time_chart['data'].append(date_sales[date])

    charts_data['sales_over_time'] = time_chart

    if grouping:
        pie_chart = {'labels': [], 'data': []}

        for key, data in grouped_data.items():
            pie_chart['labels'].append(key)
            pie_chart['data'].append(data['total'])

        charts_data['sales_by_' + grouping] = pie_chart

    return charts_data


def _generate_output(report_data, output_format, include_charts):
    if output_format == 'json':
        return report_data
    elif output_format == 'html':
        return _generate_html_report(report_data, include_charts)
    elif output_format == 'excel':
        return _generate_excel_report(report_data, include_charts)
    elif output_format == 'pdf':
        return _generate_pdf_report(report_data, include_charts)


def generate_sales_report(sales_data, report_type='summary', date_range=None,
                         filters=None, grouping=None, include_charts=False,
                         output_format='pdf'):
    """
    Generate a comprehensive sales report based on provided data and parameters.

    Parameters:
    - sales_data: List of sales transactions
    - report_type: 'summary', 'detailed', or 'forecast'
    - date_range: Dict with 'start' and 'end' dates
    - filters: Dict of filters to apply
    - grouping: How to group data ('product', 'category', 'customer', 'region')
    - include_charts: Whether to include charts/visualizations
    - output_format: 'pdf', 'excel', 'html', or 'json'

    Returns:
    - Report data or file path depending on output_format
    """
    _validate_inputs(sales_data, report_type, output_format, date_range)

    sales_data = _apply_date_range_filter(sales_data, date_range)
    sales_data = _apply_filters(sales_data, filters)

    empty_response = _handle_empty_data(sales_data, report_type, output_format)
    if empty_response is not None:
        return empty_response

    total_sales, avg_sale, max_sale, min_sale = _calculate_basic_metrics(sales_data)

    grouped_data = _group_sales_data(sales_data, grouping)

    report_data = _build_base_report(
        report_type,
        date_range,
        filters,
        total_sales,
        avg_sale,
        max_sale,
        min_sale,
        len(sales_data)
    )

    _add_grouping_to_report(report_data, grouping, grouped_data, total_sales)

    if report_type == 'detailed':
        _add_detailed_transactions(report_data, sales_data)

    if report_type == 'forecast':
        report_data['forecast'] = _build_forecast_section(sales_data)

    if include_charts:
        report_data['charts'] = _build_charts_section(sales_data, grouping, grouped_data)

    return _generate_output(report_data, output_format, include_charts)

# Helper functions (not implemented here)
def _generate_empty_report(report_type, output_format):
    # Generate an empty report file
    pass

def _generate_html_report(report_data, include_charts):
    # Generate HTML report
    pass

def _generate_excel_report(report_data, include_charts):
    # Generate Excel report
    pass

def _generate_pdf_report(report_data, include_charts):
    # Generate PDF report
    pass