"""SwatBiz Hub - Local Business Directory with Subscription & Expiry System."""
from datetime import datetime, timedelta
import os
from flask import Flask, abort, redirect, render_template, request, url_for

SITE_NAME = 'SwatBiz Hub'

# Absolute path fix for Vercel serverless environment
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(basedir, 'templates'),
    static_folder=os.path.join(basedir, 'static'),
)
app.secret_key = 'swat_biz_hub_secret_key'

# Mock Database
BUSINESSES = {
    '1': {
        'id': '1',
        'category': 'hospitals',
        'name': 'Saidu Group of Teaching Hospital',
        'address': 'Saidu Sharif, Mingora, Swat',
        'phone': '+92 946 9240123',
        'doctors': [
            {'name': 'Dr. Ahmad Khan', 'specialty': 'Cardiologist', 'timing': '9 AM - 2 PM'},
            {'name': 'Dr. Fatima Ali', 'specialty': 'Pediatrician', 'timing': '10 AM - 4 PM'},
        ],
        'joined_date': datetime.now() - timedelta(days=10),
        'last_paid_date': datetime.now(),
        'status': 'trial',
    },
    '2': {
        'id': '2',
        'category': 'restaurants',
        'name': 'Rock City Restaurant & Hotel',
        'address': 'By-pass Road, Mingora, Swat',
        'phone': '+92 946 7112233',
        'doctors': [],
        'joined_date': datetime.now() - timedelta(days=45),
        'last_paid_date': datetime.now() - timedelta(days=40),
        'status': 'active',
    },
}

CATEGORIES = {
    'hospitals': {'title': 'Hospitals & Healthcare', 'icon': '🏥'},
    'restaurants': {'title': 'Restaurants & Cafes', 'icon': '🍽️'},
    'property': {'title': 'Property Dealers', 'icon': '🏠'},
}


def check_and_update_subscriptions():
    now = datetime.now()
    for b_id, biz in list(BUSINESSES.items()):
        if biz['status'] == 'deleted':
            continue

        if biz['status'] == 'trial':
            if (now - biz['joined_date']).days > 30:
                biz['status'] = 'locked'
            continue

        days_since_payment = (now - biz['last_paid_date']).days
        if days_since_payment > 150:
            biz['status'] = 'deleted'
        elif days_since_payment > 30:
            biz['status'] = 'locked'


@app.before_request
def before_request_func():
    check_and_update_subscriptions()


@app.route('/')
def home():
    return render_template('index.html', categories=CATEGORIES, site_name=SITE_NAME)


@app.route('/category/<cat_slug>')
def category_page(cat_slug):
    if cat_slug not in CATEGORIES:
        abort(404)
    cat_businesses = [
        b for b in BUSINESSES.values() 
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
    if biz['status'] == 'locked':
        return render_template('locked.html', business=biz, site_name=SITE_NAME)
    return render_template('detail.html', business=biz, site_name=SITE_NAME)


@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        b_id = str(len(BUSINESSES) + 1)
        name = request.form.get('name')
        category = request.form.get('category')
        address = request.form.get('address')
        phone = request.form.get('phone')
        
        doc_input = request.form.get('doctors', '')
        doctors = []
        if doc_input and category == 'hospitals':
            for line in doc_input.split('\n'):
                parts = line.split(':')
                if len(parts) >= 2:
                    doctors.append({
                        'name': parts[0].strip(),
                        'specialty': parts[1].strip(),
                        'timing': '9 AM - 5 PM'
                    })

        BUSINESSES[b_id] = {
            'id': b_id,
            'category': category,
            'name': name,
            'address': address,
            'phone': phone,
            'doctors': doctors,
            'joined_date': datetime.now(),
            'last_paid_date': datetime.now(),
            'status': 'trial'
        }
        return redirect(url_for('admin_panel'))

    return render_template(
        'admin.html', businesses=BUSINESSES, categories=CATEGORIES, site_name=SITE_NAME
    )


handler = app

if __name__ == '__main__':
    app.run(debug=True)
