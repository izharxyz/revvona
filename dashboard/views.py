import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.utils import timezone

from checkout.models import Order, OrderItem
from products.models import Category, Product


def get_last_6_months_labels(now):
    return [(now - timedelta(days=30 * i)).strftime('%B') for i in range(6)][::-1]


def calculate_revenues(now):
    revenues = []
    for i in range(6):
        start_date = (now - timedelta(days=30 * (i + 1)))
        end_date = (now - timedelta(days=30 * i))
        revenue = Order.objects.filter(
            status='delivered',
            updated_at__range=[start_date, end_date]
        ).aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0
        revenues.append(revenue)
    return revenues


def get_last_30_days_labels(now):
    return [(now - timedelta(days=i)).strftime('%b %d') for i in range(30)][::-1]


def calculate_last_30_days_sales(now):
    sales = []
    for i in range(30):
        day_start = now - timedelta(days=i + 1)
        day_end = now - timedelta(days=i)
        sales_count = Order.objects.filter(
            status='delivered',
            updated_at__range=[day_start, day_end]
        ).count()
        sales.append(sales_count)
    return sales[::-1]


def calculate_order_status_counts(now):
    confirmed_orders = []
    delivered_orders = []
    cancelled_orders = []

    for i in range(30):
        day_start = now - timedelta(days=i + 1)
        day_end = now - timedelta(days=i)

        confirmed_count = Order.objects.filter(
            status='confirmed',
            updated_at__range=[day_start, day_end]
        ).count()
        delivered_count = Order.objects.filter(
            status='delivered',
            updated_at__range=[day_start, day_end]
        ).count()
        cancelled_count = Order.objects.filter(
            status='cancelled',
            updated_at__range=[day_start, day_end]
        ).count()

        confirmed_orders.append(confirmed_count)
        delivered_orders.append(delivered_count)
        cancelled_orders.append(cancelled_count)

    return confirmed_orders[::-1], delivered_orders[::-1], cancelled_orders[::-1]


def populate_random_data(revenues, last_30_days_sales, confirmed_orders, delivered_orders, cancelled_orders):
    if all(revenue == 0 for revenue in revenues):
        revenues = [random.randint(1000, 5000) for _ in range(6)]
    if all(sales == 0 for sales in last_30_days_sales):
        last_30_days_sales = [random.randint(40, 100) for _ in range(30)]
    if all(order == 0 for order in confirmed_orders) and all(order == 0 for order in delivered_orders) and all(order == 0 for order in cancelled_orders):
        confirmed_orders = [random.randint(17, 20) for _ in range(30)]
        delivered_orders = [random.randint(17, 20) for _ in range(30)]
        cancelled_orders = [random.randint(0, 4) for _ in range(30)]
    return revenues, last_30_days_sales, confirmed_orders, delivered_orders, cancelled_orders


def get_top_products_data(now):
    last_7_days = now - timedelta(days=7)
    previous_week = now - timedelta(days=14)

    top_products_last_7_days = (
        OrderItem.objects.filter(
            order__status='delivered',
            order__updated_at__gte=last_7_days
        )
        .values(product_name=F('product__name'))
        .annotate(sales_price=Sum(F('product__price') * F('quantity'), output_field=DecimalField()))
        .order_by('-sales_price')[:3]
    )

    top_products_previous_week = (
        OrderItem.objects.filter(
            order__status='delivered',
            order__updated_at__range=[previous_week, last_7_days]
        )
        .values(product_name=F('product__name'))
        .annotate(sales_price=Sum(F('product__price') * F('quantity'), output_field=DecimalField()))
    )

    previous_week_sales = {item['product_name']: item['sales_price']
                           for item in top_products_previous_week}

    products_data = []
    for product in top_products_last_7_days:
        last_week_sales = previous_week_sales.get(product['product_name'], 0)
        increment = 0
        if last_week_sales > 0:
            increment = ((product['sales_price'] -
                         last_week_sales) / last_week_sales) * 100
        products_data.append({
            'product_name': product['product_name'],
            'sales_price': product['sales_price'],
            'increment': round(increment, 2)
        })

    while len(products_data) < 3:
        products_data.append({
            'product_name': f"Unknown Product {chr(65 + len(products_data))}",
            'sales_price': 10000,
            'increment': 0.0
        })

    return products_data


def get_new_customers(now):
    last_7_days = now - timedelta(days=7)
    previous_7_days = now - timedelta(days=14)

    current_customers = User.objects.filter(
        date_joined__gte=last_7_days,
        is_staff=False  # Exclude staff users
    ).count()

    previous_customers = User.objects.filter(
        date_joined__range=[previous_7_days, last_7_days],
        is_staff=False  # Exclude staff users
    ).count()

    increment = calculate_increment(current_customers, previous_customers)

    return {
        'name': 'Customers',
        'value': current_customers,
        'increment': round(increment, 2),
        # Total customers excluding staff
        'total_value': User.objects.filter(is_staff=False).count()
    }


def get_new_products(now):
    last_7_days = now - timedelta(days=7)
    previous_7_days = now - timedelta(days=14)

    current_products = Product.objects.filter(
        created_at__gte=last_7_days).count()
    previous_products = Product.objects.filter(
        created_at__range=[previous_7_days, last_7_days]).count()

    increment = calculate_increment(current_products, previous_products)

    return {
        'name': 'Products',
        'value': current_products,
        'increment': round(increment, 2),
        'total_value': Product.objects.count()  # Total products
    }


def get_new_categories(now):
    last_7_days = now - timedelta(days=7)
    previous_7_days = now - timedelta(days=14)

    current_categories = Category.objects.filter(
        created_at__gte=last_7_days).count()
    previous_categories = Category.objects.filter(
        created_at__range=[previous_7_days, last_7_days]).count()

    increment = calculate_increment(current_categories, previous_categories)

    return {
        'name': 'Categories',
        'value': current_categories,
        'increment': round(increment, 2),
        'total_value': Category.objects.count()  # Total categories
    }


def calculate_increment(current_count, previous_count):
    if previous_count == 0:
        return 100.0 if current_count > 0 else 0.0  # Handle division by zero
    return ((current_count - previous_count) / previous_count) * 100


def dashboard_callback(request, context):
    now = timezone.now()

    last_6_months_labels = get_last_6_months_labels(now)
    revenues = calculate_revenues(now)
    last_30_days = get_last_30_days_labels(now)
    last_30_days_sales = calculate_last_30_days_sales(now)
    confirmed_orders, delivered_orders, cancelled_orders = calculate_order_status_counts(
        now)

    # Check for empty data and populate with random values
    revenues, last_30_days_sales, confirmed_orders, delivered_orders, cancelled_orders = populate_random_data(
        revenues, last_30_days_sales, confirmed_orders, delivered_orders, cancelled_orders
    )

    top_products = get_top_products_data(now)

    card_items = [
        get_new_customers(now),
        get_new_products(now),
        get_new_categories(now)
    ]

    # Update context
    context.update(
        {
            'last_6_months_labels': last_6_months_labels,
            'revenues': revenues,
            'last_30_days': last_30_days,
            'last_30_days_sales': last_30_days_sales,
            'confirmed_orders': confirmed_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'top_products': top_products,
            'card_items': card_items
        }
    )

    return context
