"""SwatBiz Hub - Local Business Directory with Subscription & Expiry System."""
from datetime import datetime, timedelta
import os
import base64
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

# Mock Database with Expanded Categories
BUSINESSES = {
    '1': {
        'id': '1',
        'category': 'hospitals',
        'name': 'Saidu Group of Teaching Hospital',
        'address': 'Saidu Sharif, Mingora, Swat',
        'phones': ['+92 946 9240123', '+92 300 1234567'],
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
    '2': {
        'id': '2',
        'category': 'restaurants',
        'name': 'Rock City Restaurant & Hotel',
        'address': 'By-pass Road, Mingora, Swat',
        'phones': ['+92 946 7112233'],
        'image': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80',
        'doctors': [],
        'items': [
            {
                'name': 'Special Chicken Karahi',
                'price': '2200',
                'offer': '10% OFF',
                'image': 'https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=500&q=80'
            }
        ],
        'joined_date': datetime.now() - timedelta(days=45),
        'last_paid_date': datetime.now() - timedelta(days=40),
        'status': 'active',
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
                'name': 'First Aid Emergency Kit',
                'price': '1500',
                'offer': 'Free Delivery',
                'image': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=500&q=80'
            }
        ],
        'joined_date': datetime.now() - timedelta(days=5),
        'last_paid_date': datetime.now(),
        'status': 'trial',
    },
    '4': {
        'id': '4',
        'category': 'supermarts',
        'name': 'Swat Grand Supermart',
        'address': 'Station Chowk, Mingora, Swat',
        'phones': ['+92 946 8889999'],
        'image': 'https://images.unsplash.com/photo-1578916171728-46686eac8d58?auto=format&fit=crop&w=800&q=80',
        'doctors': [],
        'items': [
            {
                'name': 'Cooking Oil (5 Litre)',
                'price': '2800',
                'offer': 'Sale',
                'image': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=500&q=80'
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

        if biz['status'] == 'trial':
            if (now - biz['joined_date']).days > 30:
                biz['status'] = 'locked'
            continue

        days_since_payment = (now - biz['last_paid_date']).days
        if days_since_payment > 150:
            biz['status'] = 'deleted'
        elif days_since_payment > 30:
            biz['status'] = 'locked'


def process_image_input(request_obj, file_key='image_file', url_key='image_url'):
    file = request_obj.files.get(file_key)
    if file and file.filename != '':
        file_bytes = file.read()
        encoded = base64.b64encode(file_bytes).decode('utf-8')
        mime_type = file.mimetype or 'image/jpeg'
        return f"data:{mime_type};base64,{encoded}"
    
    image_url = request_obj.form.get(url_key)
    if image_url and image_url.strip():
        return image_url.strip()
        
    return 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80'


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


@app.route('/register', methods=['GET', 'POST'])
def register_business():
    if request.method == 'POST':
        b_id = str(len(BUSINESSES) + 1)
        name = request.form.get('name')
        category = request.form.get('category')
        address = request.form.get('address')
        
        phone_inputs = request.form.getlist('phone[]')
        phones = [p.strip() for p in phone_inputs if p.strip()]
        if not phones:
            phones = ['+92 946 0000000']

        image = process_image_input(request, 'image_file', 'image_url')
        
        doctors = []
        items = []

        if category == 'hospitals':
            doc_names = request.form.getlist('doc_name[]')
            doc_specs = request.form.getlist('doc_spec[]')
            doc_app_times = request.form.getlist('doc_app_time[]')
            doc_clinic_times = request.form.getlist('doc_clinic_time[]')
            doc_clinics = request.form.getlist('doc_clinic[]')

            for i in range(len(doc_names)):
                if doc_names[i].strip():
                    doctors.append({
                        'name': doc_names[i].strip(),
                        'specialty': doc_specs[i].strip() if i < len(doc_specs) else 'Specialist',
                        'appointment_timing': doc_app_times[i].strip() if i < len(doc_app_times) else '9 AM - 2 PM',
                        'clinic_timing': doc_clinic_times[i].strip() if i < len(doc_clinic_times) else 'Mon - Sat (9 AM - 5 PM)',
                        'clinic': doc_clinics[i].strip() if i < len(doc_clinics) else 'Main OPD'
                    })
        else:
            item_names = request.form.getlist('item_name[]')
            item_prices = request.form.getlist('item_price[]')
            item_offers = request.form.getlist('item_offer[]')
            item_files = request.files.getlist('item_file[]')

            for i in range(len(item_names)):
                if item_names[i].strip():
                    item_img = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=500&q=80'
                    if i < len(item_files) and item_files[i].filename != '':
                        f = item_files[i]
                        fb = f.read()
                        enc = base64.b64encode(fb).decode('utf-8')
                        m = f.mimetype or 'image/jpeg'
                        item_img = f"data:{m};base64,{enc}"

                    items.append({
                        'name': item_names[i].strip(),
                        'price': item_prices[i].strip() if i < len(item_prices) else '0',
                        'offer': item_offers[i].strip() if i < len(item_offers) else '',
                        'image': item_img
                    })

        BUSINESSES[b_id] = {
            'id': b_id,
            'category': category,
            'name': name,
            'address': address,
            'phones': phones,
            'phone': phones[0],
            'image': image,
            'doctors': doctors,
            'items': items,
            'joined_date': datetime.now(),
            'last_paid_date': datetime.now(),
            'status': 'trial'
        }
        return redirect(url_for('business_detail', b_id=b_id))

    return render_template('register.html', categories=CATEGORIES, site_name=SITE_NAME)


@app.route('/admin')
def admin_panel():
    return render_template(
        'admin.html', businesses=BUSINESSES, categories=CATEGORIES, site_name=SITE_NAME
    )


handler = app

if __name__ == '__main__':
    app.run(debug=True)
