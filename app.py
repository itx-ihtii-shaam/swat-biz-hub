"""SwatBiz Hub - Local Business Directory with Subscription & Expiry System."""
from datetime import datetime, timedelta
import os
from flask import Flask, abort, redirect, render_template, request, url_for

SITE_NAME = 'SwatBiz Hub'

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'swat_biz_hub_secret_key'

# Mock Database (In production, replace this with SQLite, PostgreSQL or MongoDB)
# Status options: 'active', 'trial', 'locked', 'deleted'
BUSINESSES = {
    '1': {
        'id': '1',
        'category': 'hospitals',
        'name': 'Saidu Group of Teaching Hospital',
        'address': 'Saidu Sharif, Mingora, Swat',
        'phone': '+92 946 9240123',
        'doctors': [
            {'name': 'Dr. Ahmad Khan', 'specialty': 'Cardiologist', 'timing': '9 AM - 2 PM'},
            {
                'name': 'Dr. Fatima Ali',
                'specialty': 'Pediatrician',
                'timing': '10 AM - 4 PM',
            },
        ],
        'joined_date': datetime.now() - timedelta(days=10),  # Trial period
        'last_paid_date': datetime.now(),
        'status': 'trial',
    },
    '2': {
        'id': '2',
        'category': 'restaurants',
        'name': 'Rock City Restaurant & Hotel',
        'address': 'By-pass Road, Mingora, Swat',
        'phone': '+92 946 7112233',
        'doctors': [],  # Not applicable for restaurants
        'joined_date': datetime.now() - timedelta(days=45),
        'last_paid_date': datetime.now() - timedelta(days=40),  # Active paid
        'status': 'active',
    },
}

CATEGORIES = {
    'hospitals': {'title': 'Hospitals & Healthcare', 'icon': '🏥'},
    'restaurants': {'title': 'Restaurants & Cafes', 'icon': '🍽️'},
    'property': {'title': 'Property Dealers', 'icon': '🏠'},
}


def check_and_update_subscriptions():
    """Logic to check expiry:

    - If unpaid for > 30 days: Status becomes 'locked' (Details won't open).
    - If unpaid for > 150 days (5 months): Status becomes 'deleted' (Auto-delete).
    """
    now = datetime.now()
    for b_id, biz in list(BUSINESSES.items()):
        if biz['status'] == 'deleted':
            continue

        # Check trial expiry (e.g. 30 days trial)
        if biz['status'] == 'trial':
            if (now - biz['joined_date']).days > 30:
                biz['status'] = 'locked'
            continue

        # Check paid subscription expiry
        days_since_payment = (now - biz['last_paid_date']).days
        if days_since_payment > 150:  (~5 months)
            biz['status'] = 'deleted'
        elif days_since_payment > 30:  (1 month crossed)
            biz['status'] = 'locked'


@app.before_request
def before_request_func():
    check_and_update_subscriptions()


@app.route('/')
def home():
    return render_template(
        'index.html', categories=CATEGORIES, site_name=SITE_NAME
    )


@app.route('/category/<cat_slug>')
def category_page(cat_slug):
    if cat_slug not in CATEGORIES:
        abort(404)

    # Sirf wo business dikhayein jo deleted na hon
    cat_businesses = [
        b
        for b in BUSINESSES.values()
        if b['category'] == cat_slug and b['status'] != 'deleted'
    ]
    return render_template(
        'category.html',
        category=CATEGORIES[cat_slug],
        businesses=cat_businesses,
        site_name=SITE_NAME,
    )


@app.route('/business/<b_id>')
def business_detail(b_id):
    biz = BUSINESSES.get(b_id)
    if not biz or biz['status'] == 'deleted':
        abort(404)

    # Agar 1 mahina payment na ki ho aur status 'locked' ho toh detail open nahi hogi
    if biz['status'] == 'locked':
        return render_template('locked.html', business=biz, site_name=SITE_NAME)

    return render_template('detail.html', business=biz, site_name=SITE_NAME)


@app.route('/admin')
def admin_panel():
    """Admin panel to view subscription statuses and manually manage payments."""
    return render_template(
        'admin.html', businesses=BUSINESSES, site_name=SITE_NAME
    )


if __name__ == '__main__':
    app.run(debug=True)
