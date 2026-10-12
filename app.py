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
            }
        ],
        'joined_date': datetime.now() - timedelta(days=5),
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


@app.route('/')
def home():
    return render_template('index.html', categories=CATEGORIES, site_name=SITE_NAME)


@app.route('/category/<cat_slug>')
def category_page(cat_slug):
    if cat_slug not in CATEGORIES:
        abort(404)
    
    search_query = request.args.get('q', '').lower().strip()
    cat_businesses = []
    for b in BUSINESSES.values():
        if b.get('category') == cat_slug and b.get('status') != 'deleted':
            if search_query:
                matched = search_query in b.get('name', '').lower()
                matched_items = [item for item in b.get('items', []) if search_query in item.get('name', '').lower()]
                matched_doctors = [doc for doc in b.get('doctors', []) if search_query in doc.get('name', '').lower()]
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
    return render_template('detail.html', business=biz, site_name=SITE_NAME)


@app.route('/register', methods=['GET', 'POST'])
def register_business():
    if request.method == 'POST':
        b_id = str(len(BUSINESSES) + 1)
        name = request.form.get('name')
        category = request.form.get('category')
        address = request.form.get('address')
        phone_inputs = request.form.getlist('phone[]')
        phones = [p.strip() for p in phone_inputs if p.strip()] or ['+92 946 0000000']
        
        image_url = request.form.get('image_url')
        image = image_url.strip() if image_url and image_url.strip() else 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80'

        BUSINESSES[b_id] = {
            'id': b_id,
            'category': category,
            'name': name,
            'address': address,
            'phones': phones,
            'image': image,
            'doctors': [],
            'items': [],
            'joined_date': datetime.now(),
            'last_paid_date': datetime.now(),
            'status': 'trial'
        }
        return redirect(url_for('home'))

    return render_template('register.html', categories=CATEGORIES, site_name=SITE_NAME)


@app.route('/admin')
def admin_panel():
    return render_template('admin.html', businesses=BUSINESSES, categories=CATEGORIES, site_name=SITE_NAME)


handler = app

if __name__ == '__main__':
    app.run(debug=True)
