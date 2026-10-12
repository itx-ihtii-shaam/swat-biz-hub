"""SwatBiz Hub - Local Business Directory with Subscription & Expiry System."""
from datetime import datetime, timedelta
import os
import base64
from flask import Flask, abort, redirect, render_template, request, url_for

SITE_NAME = 'SwatBiz Hub'

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(basedir, 'templates'),
    static_folder=os.path.join(basedir, 'static'),
)
app.secret_key = 'swat_biz_hub_secret_key'

BUSINESSES = {
    '1': {
        'id': '1',
        'category': 'hospitals',
        'name': 'Saidu Group of Teaching Hospital',
        'address': 'Saidu Sharif, Mingora, Swat',
        'phones': ['+92 946 9240123'],
        'image': 'https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=800&q=80',
        'doctors': [
            {
                'name': 'Dr. Ahmad Khan', 
                'specialty': 'Cardiologist', 
                'appointment_timing': '9 AM - 2 PM', 
                'clinic_timing': 'Mon - Sat (8 AM - 4 PM)',
                'clinic': 'Room 12, OPD Block'
            },
        ],
        'items': [],
        'joined_date': datetime.now() - timedelta(days=10),
        'last_paid_date': datetime.now(),
        'status': 'trial',
    },
    '3': {
        'id': '3',
        'category': 'pharmacies',
        'name': 'Shifa Medical & Pharmacy',
        'address': 'Green Chowk, Mingora, Swat',
        'phones': ['+92 946 7123456'],
        'image': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80',
        'doctors': [],
        'items': [
            {
                'name': 'Panadol Extra Tablets',
                'price': '50',
                'offer': 'Available',
                'image': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=500&q=80'
            },
            {
                'name': 'Augmentin Syrup',
                'price': '650',
                'offer': 'In Stock',
                'image': 'https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&w=500&q=80'
            }
        ],
        'joined_date': datetime.now() - timedelta(days=5),
        'last_paid_date': datetime.now(),
        'status': 'trial',
    },
    '5': {
        'id': '5',
        'category': 'property',
        'name': 'Swat Valley Real Estate',
        'address': 'Main Makanbagh, Mingora, Swat',
        'phones': ['+92 300 9876543'],
        'image': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=800&q=80',
        'doctors': [],
        'items': [
            {
                'name': '5 Marla Brand New House',
                'price': '12500000',
                'offer': 'Ready to Move',
                'image': 'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=500&q=80'
            }
        ],
        'joined_date': datetime.now() - timedelta(days=2),
        'last_paid_date': datetime.now(),
        'status': 'trial',
    }
}

CATEGORIES = {
    'hospitals': {'title': 'Hospitals & Healthcare', 'icon': '🏥'},
    'pharmacies': {'title': 'Pharmacies & Medical Stores', 'icon': '💊'},
    'restaurants': {'title': 'Restaurants & Cafes', 'icon': '🍽️'},
    'supermarts': {'title': 'Supermarts & Grocery', 'icon': '🛒'},
    'property': {'title': 'Property Dealers', 'icon': '🏠'},
    'hotels': {'title': 'Hotels & Guest Houses', 'icon': '🏨'},
    'education': {'title': 'Educational Institutes', 'icon': '🎓'}
}


def check_and_update_subscriptions():
    now = datetime.now()
    for b_id, biz in list(BUSINESSES.items()):
        if biz['status'] == 'deleted':
            continue
        if biz['status'] == 'trial' and (now - biz['joined_date']).days > 30:
            biz['status'] = 'locked'


@app.before_request
def before_request_func():
    check_and_update_subscriptions()


@app.route('/')
def home():
    return render_template('index.html', categories=CATEGORIES, site_name=SITE_NAME, businesses=BUSINESSES)


@app.route('/category/<cat_slug>')
def category_page(cat_slug):
    if cat_slug not in CATEGORIES:
        abort(404)
    
    search_query = request.args.get('q', '').lower().strip()
    
    cat_businesses = []
    for b in BUSINESSES.values():
        if b['category'] == cat_slug and b['status'] != 'deleted':
            if search_query:
                # Check if search matches business name or any item/medicine/property name
                matched = search_query in b['name'].lower()
                matched_items = [item for item in b.get('items', []) if search_query in item['name'].lower()]
                matched_doctors = [doc for doc in b.get('doctors', []) if search_query in doc['name'].lower() or search_query in doc['specialty'].lower()]
                
                if matched or matched_items or matched_doctors:
                    cat_businesses.append(b)
            else:
                cat_businesses.append(b)

    return render_template(
        'category.html',
        category=CATEGORIES[cat_slug],
        businesses=cat_businesses,
        site_name=SITE_NAME,
        search_query=search_query,
        cat_slug=cat_slug
    )


@app.route('/business/<b_id>')
def business_detail(b_id):
    biz = BUSINESSES.get(b_id)
    if not biz or biz['status'] == 'deleted':
        abort(404)
    if biz['status'] == 'locked':
        return render_template('locked.html', business=biz, site_name=SITE_NAME)
    return render_template('detail.html', business=biz, site_name=SITE_NAME)


@app.route('/register', methods=['GET', 'POST'])
def register_business():
    # registration logic remains same as previous update
    return render_template('register.html', categories=CATEGORIES, site_name=SITE_NAME)


@app.route('/admin')
def admin_panel():
    return render_template('admin.html', businesses=BUSINESSES, categories=CATEGORIES, site_name=SITE_NAME)


handler = app

if __name__ == '__main__':
    app.run(debug=True)
