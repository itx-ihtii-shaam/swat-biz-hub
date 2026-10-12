"""SwatBiz Hub - Clean Two-Module Categorized Admin Dashboard."""
from datetime import datetime, timedelta
import os
import base64
from flask import Flask, abort, redirect, render_template_string, request, url_for, session

SITE_NAME = 'SwatBiz Hub'
ADMIN_PASSWORD = 'admin123'

app = Flask(__name__)
app.secret_key = 'swat_biz_hub_secret_key'

BUSINESSES = {
    '1': {
        'id': '1',
        'category': 'hospitals',
        'name': 'Saidu Group of Teaching Hospital',
        'address': 'Saidu Sharif, Mingora, Swat',
        'phones': ['+92 946 9240123'],
        'image': 'https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=800&q=80',
        'doctors': [],
        'items': [],
        'joined_date': datetime.now() - timedelta(days=25),
        'expiry_date': datetime.now() + timedelta(days=3), # Expiry Alert
        'status': 'approved',
        'payment_method': 'Bank Transfer',
        'payment_ref': 'TXN-984210',
        'payment_status': 'paid'
    },
    '2': {
        'id': '2',
        'category': 'restaurants',
        'name': 'Khyber Shinwari Restaurant',
        'address': 'Fizagat, Swat',
        'phones': ['+92 946 881122'],
        'image': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80',
        'doctors': [],
        'items': [],
        'joined_date': datetime.now() - timedelta(days=1),
        'expiry_date': datetime.now() + timedelta(days=30),
        'status': 'pending', # Pending Business
        'payment_method': 'EasyPaisa',
        'payment_ref': 'TID-9920182',
        'payment_status': 'unpaid' # Pending Payment
    },
    '3': {
        'id': '3',
        'category': 'pharmacies',
        'name': 'Shifa Medical & Pharmacy',
        'address': 'Green Chowk, Mingora, Swat',
        'phones': ['+92 946 7123456'],
        'image': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80',
        'doctors': [],
        'items': [],
        'joined_date': datetime.now() - timedelta(days=5),
        'expiry_date': datetime.now() + timedelta(days=25),
        'status': 'approved',
        'payment_method': 'EasyPaisa',
        'payment_ref': 'TID-7782194',
        'payment_status': 'paid'
    },
    '4': {
        'id': '4',
        'category': 'education',
        'sub_category': 'school_college',
        'name': 'Swat Public School & College',
        'address': 'Circular Road, Mingora, Swat',
        'phones': ['+92 946 7112233'],
        'image': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80',
        'joined_date': datetime.now() - timedelta(days=2),
        'expiry_date': datetime.now() + timedelta(days=2), # Expiry Alert
        'status': 'approved',
        'payment_method': 'Bank Transfer',
        'payment_ref': 'Meezan Bank - 001283',
        'payment_status': 'paid'
    }
}

CATEGORIES = {
    'hospitals': {'title': 'Hospitals & Healthcare', 'icon': '🏥', 'search_hint': 'Search name or location...'},
    'pharmacies': {'title': 'Pharmacies & Medical Stores', 'icon': '💊', 'search_hint': 'Search medicine or store...'},
    'restaurants': {'title': 'Restaurants & Cafes', 'icon': '🍽️', 'search_hint': 'Search restaurant...'},
    'supermarts': {'title': 'Supermarts & Grocery', 'icon': '🛒', 'search_hint': 'Search store or item...'},
    'property': {'title': 'Property Dealers', 'icon': '🏠', 'search_hint': 'Search plot or house...'},
    'hotels': {'title': 'Hotels & Guest Houses', 'icon': '🏨', 'search_hint': 'Search hotel...'},
    'education': {'title': 'Educational Institutes', 'icon': '🎓', 'search_hint': 'Search school or college...'}
}

SUB_CATEGORIES = {
    'education': [
        {'slug': 'all', 'title': 'All Institutes', 'icon': '🎓'},
        {'slug': 'schools', 'title': 'Schools', 'icon': '🏫'},
        {'slug': 'colleges', 'title': 'Colleges', 'icon': '🏛️'}
    ]
}

INDEX_BASE_HEAD = '''
<!DOCTYPE html>
<html lang="en" id="html-root" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - ''' + SITE_NAME + '''</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config = { darkMode: 'class' }</script>
</head>
<body class="bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 min-h-screen">
    <header class="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white shadow-xl">
        <div class="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
            <a href="/" class="text-2xl font-extrabold tracking-tight">🏙️ ''' + SITE_NAME + '''</a>
            <div class="flex items-center space-x-3">
                <a href="/register" class="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-xl text-sm font-bold shadow-lg transition">＋ Register Business</a>
                <button onclick="document.getElementById('html-root').classList.toggle('dark')" class="bg-white/10 hover:bg-white/25 px-3.5 py-2 rounded-xl text-sm font-medium transition">🌓</button>
            </div>
        </div>
    </header>
'''

BASE_HEAD = '''
<!DOCTYPE html>
<html lang="en" id="html-root" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - ''' + SITE_NAME + '''</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config = { darkMode: 'class' }</script>
</head>
<body class="bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 min-h-screen">
    <header class="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white shadow-xl">
        <div class="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
            <a href="/" class="text-xl font-bold hover:underline">← Back to Home</a>
            <div class="flex items-center space-x-3">
                <a href="/register" class="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-xl text-sm font-bold shadow-lg transition">＋ Register Business</a>
                <button onclick="document.getElementById('html-root').classList.toggle('dark')" class="bg-white/10 hover:bg-white/25 px-3.5 py-2 rounded-xl text-sm font-medium transition">🌓</button>
            </div>
        </div>
    </header>
'''

FOOTER = '''
    <footer class="text-center py-8 text-sm text-gray-500 border-t border-gray-200 dark:border-gray-800 mt-20">
        <p>&copy; 2026 ''' + SITE_NAME + '''. All rights reserved.</p>
    </footer>
</body>
</html>
'''

INDEX_TEMPLATE = INDEX_BASE_HEAD + '''
    <section class="py-16 px-4 text-center bg-gradient-to-b from-blue-950/20 to-transparent">
        <div class="max-w-3xl mx-auto space-y-4">
            <h2 class="text-4xl md:text-5xl font-black tracking-tight">Discover Swat & Mingora Businesses</h2>
            <p class="text-gray-500 dark:text-gray-400 text-lg">Find top hospitals, pharmacies, restaurants, supermarts, hotels, and educational institutes instantly.</p>
        </div>
    </section>
    <main class="max-w-7xl mx-auto px-4 pb-20">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {% for slug, cat in categories.items() %}
            <a href="/category/{{ slug }}" class="bg-white dark:bg-gray-900 p-8 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-sm hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1.5 flex items-center space-x-5 group">
                <span class="text-5xl p-4 bg-gray-50 dark:bg-gray-800 rounded-2xl group-hover:scale-110 transition-transform">{{ cat.icon }}</span>
                <div>
                    <h3 class="text-xl font-bold group-hover:text-blue-500 transition-colors">{{ cat.title }}</h3>
                    <p class="text-sm text-gray-400 mt-1">Browse listings & items →</p>
                </div>
            </a>
            {% endfor %}
        </div>
    </main>
''' + FOOTER

@app.route('/')
def home():
    return render_template_string(INDEX_TEMPLATE, categories=CATEGORIES, title="Home")

@app.route('/category/<cat_slug>')
def category_page(cat_slug):
    if cat_slug not in CATEGORIES:
        abort(404)
    cat_businesses = [b for b in BUSINESSES.values() if b.get('category') == cat_slug and b.get('status') == 'approved']
    return render_template_string(BASE_HEAD + f'''
    <main class="max-w-7xl mx-auto px-4 py-12">
        <h2 class="text-3xl font-bold mb-6">{CATEGORIES[cat_slug]['title']}</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            {% for biz in businesses %}
            <div class="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-800">
                <h3 class="font-bold text-lg">{{ biz.name }}</h3>
                <p class="text-sm text-gray-400">📍 {{ biz.address }}</p>
            </div>
            {% endfor %}
        </div>
    </main>
    ''' + FOOTER, businesses=cat_businesses, title=CATEGORIES[cat_slug]['title'])

@app.route('/register', methods=['GET', 'POST'])
def register_business():
    if request.method == 'POST':
        b_id = str(len(BUSINESSES) + 1)
        BUSINESSES[b_id] = {
            'id': b_id,
            'category': request.form.get('category'),
            'name': request.form.get('name'),
            'address': request.form.get('address'),
            'phones': [request.form.get('phone', '')],
            'status': 'pending',
            'payment_method': request.form.get('payment_method', 'Cash'),
            'payment_ref': request.form.get('payment_ref', 'N/A'),
            'payment_status': 'unpaid',
            'expiry_date': datetime.now() + timedelta(days=30)
        }
        return redirect('/')
    return render_template_string(BASE_HEAD + '''
    <main class="max-w-2xl mx-auto px-4 py-12">
        <h2 class="text-3xl font-bold text-center mb-6">Register Business</h2>
        <form method="POST" class="space-y-4">
            <input type="text" name="name" required placeholder="Business Name" class="w-full p-3 rounded-xl bg-gray-800 border border-gray-700">
            <select name="category" class="w-full p-3 rounded-xl bg-gray-800 border border-gray-700">
                {% for slug, cat in categories.items() %}
                <option value="{{ slug }}">{{ cat.title }}</option>
                {% endfor %}
            </select>
            <input type="text" name="address" required placeholder="Address" class="w-full p-3 rounded-xl bg-gray-800 border border-gray-700">
            <input type="text" name="phone" required placeholder="Phone Number" class="w-full p-3 rounded-xl bg-gray-800 border border-gray-700">
            <select name="payment_method" class="w-full p-3 rounded-xl bg-gray-800 border border-gray-700">
                <option value="EasyPaisa">EasyPaisa</option>
                <option value="JazzCash">JazzCash</option>
                <option value="Bank Transfer">Bank Transfer</option>
            </select>
            <input type="text" name="payment_ref" placeholder="TID / Ref Number" class="w-full p-3 rounded-xl bg-gray-800 border border-gray-700">
            <button type="submit" class="w-full bg-blue-600 py-3 rounded-xl font-bold">Submit</button>
        </form>
    </main>
    ''' + FOOTER, categories=CATEGORIES, title="Register")

# --- CLEAN TWO-MODULE ADMIN HUB ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin')

    if not session.get('admin_logged_in'):
        return render_template_string(BASE_HEAD + '''
        <main class="max-w-md mx-auto px-4 py-20 text-center">
            <div class="bg-gray-900 p-8 rounded-3xl border border-gray-800">
                <h2 class="text-2xl font-bold mb-4">🔒 Admin Login</h2>
                <form method="POST" class="space-y-4">
                    <input type="password" name="password" required placeholder="Password" class="w-full p-3 rounded-xl bg-gray-800 border border-gray-700 text-center">
                    <button type="submit" class="w-full bg-blue-600 py-3 rounded-xl font-bold">Login</button>
                </form>
            </div>
        </main>
        ''' + FOOTER, title="Admin Login")

    module = request.args.get('module') # None (Hub), 'business', 'payment'
    tab = request.args.get('tab', 'pending') # 'pending', 'approved', 'alerts'
    action = request.args.get('action')
    biz_id = request.args.get('id')

    if action == 'logout':
        session.pop('admin_logged_in', None)
        return redirect('/')

    if action and biz_id in BUSINESSES:
        if action == 'approve':
            BUSINESSES[biz_id]['status'] = 'approved'
        elif action == 'approve_pay':
            BUSINESSES[biz_id]['payment_status'] = 'paid'
            BUSINESSES[biz_id]['expiry_date'] = datetime.now() + timedelta(days=30)
        elif action == 'delete':
            BUSINESSES[biz_id]['status'] = 'deleted'
        return redirect(f'/admin?module={module}&tab={tab}')

    now = datetime.now()
    pending_biz = {k: v for k, v in BUSINESSES.items() if v.get('status') == 'pending'}
    approved_biz = {k: v for k, v in BUSINESSES.items() if v.get('status') == 'approved'}
    pending_pay = {k: v for k, v in BUSINESSES.items() if v.get('payment_status') == 'unpaid'}
    paid_pay = {k: v for k, v in BUSINESSES.items() if v.get('payment_status') == 'paid'}
    expiring_alerts = {k: v for k, v in BUSINESSES.items() if (v.get('expiry_date') - now).days <= 5 and v.get('status') != 'deleted'}

    # 1. MAIN CLEAN HUB (2 BIG CARDS LIKE HOME PAGE)
    if not module:
        return render_template_string(BASE_HEAD + '''
        <main class="max-w-5xl mx-auto px-4 py-12">
            <div class="flex justify-between items-center mb-10">
                <h2 class="text-3xl font-extrabold">🛠️ Admin Control Panel</h2>
                <a href="/admin?action=logout" class="bg-red-600/20 text-red-400 px-4 py-2 rounded-xl text-sm font-bold">Logout</a>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <!-- CATEGORY 1: BUSINESS MANAGEMENT MODULE -->
                <a href="/admin?module=business&tab=pending" class="bg-gray-900 p-8 rounded-3xl border border-gray-800 hover:border-blue-500 transition-all shadow-2xl flex flex-col justify-between group">
                    <div>
                        <div class="flex justify-between items-center mb-6">
                            <span class="text-6xl">🏢</span>
                            {% if pending_biz %}
                            <span class="bg-yellow-500/20 text-yellow-400 text-xs px-3 py-1.5 rounded-full font-bold">''' + str(len(pending_biz)) + ''' New Pending</span>
                            {% else %}
                            <span class="bg-green-500/20 text-green-400 text-xs px-3 py-1.5 rounded-full font-bold">All Approved</span>
                            {% endif %}
                        </div>
                        <h3 class="text-2xl font-black group-hover:text-blue-500 transition-colors">1. Business Directory Module</h3>
                        <p class="text-gray-400 text-sm mt-2">Manage new business registration approvals, live directory listings, and deletions.</p>
                    </div>
                    <div class="mt-8 text-blue-500 font-bold text-sm flex justify-between items-center">
                        <span>Open Business Portal →</span>
                        <span class="text-xs text-gray-500">''' + str(len(approved_biz)) + ''' Live Businesses</span>
                    </div>
                </a>

                <!-- CATEGORY 2: PAYMENT & SUBSCRIPTIONS MODULE -->
                <a href="/admin?module=payment&tab=pending" class="bg-gray-900 p-8 rounded-3xl border border-gray-800 hover:border-indigo-500 transition-all shadow-2xl flex flex-col justify-between group">
                    <div>
                        <div class="flex justify-between items-center mb-6">
                            <span class="text-6xl">💳</span>
                            {% if pending_pay or expiring %}
                            <span class="bg-orange-500/20 text-orange-400 text-xs px-3 py-1.5 rounded-full font-bold">Action Needed</span>
                            {% else %}
                            <span class="bg-blue-500/20 text-blue-400 text-xs px-3 py-1.5 rounded-full font-bold">All Verified</span>
                            {% endif %}
                        </div>
                        <h3 class="text-2xl font-black group-hover:text-indigo-500 transition-colors">2. Payment & Subscription Module</h3>
                        <p class="text-gray-400 text-sm mt-2">Verify EasyPaisa/JazzCash TID receipts, payment history, and short-time expiry alerts.</p>
                    </div>
                    <div class="mt-8 text-indigo-500 font-bold text-sm flex justify-between items-center">
                        <span>Open Payment Portal →</span>
                        <span class="text-xs text-red-400 font-bold">''' + str(len(expiring_alerts)) + ''' Expiry Alerts</span>
                    </div>
                </a>
            </div>
        </main>
        ''' + FOOTER, pending_biz=pending_biz, approved_biz=approved_biz, pending_pay=pending_pay, expiring=expiring_alerts, title="Admin Hub")

    # 2. MODULE 1: BUSINESS MANAGEMENT
    elif module == 'business':
        return render_template_string(BASE_HEAD + '''
        <main class="max-w-5xl mx-auto px-4 py-12">
            <div class="flex justify-between items-center mb-8">
                <a href="/admin" class="text-sm font-bold text-blue-500 hover:underline">← Back to Admin Hub</a>
                <h2 class="text-2xl font-extrabold">🏢 Business Directory Module</h2>
            </div>

            <!-- SUB CATEGORY TABS -->
            <div class="flex space-x-3 mb-8">
                <a href="/admin?module=business&tab=pending" class="px-5 py-2.5 rounded-xl text-sm font-bold {% if tab == 'pending' %} bg-blue-600 text-white {% else %} bg-gray-900 text-gray-400 {% endif %}">
                    ⏳ New Pending Approvals (''' + str(len(pending_biz)) + ''')
                </a>
                <a href="/admin?module=business&tab=approved" class="px-5 py-2.5 rounded-xl text-sm font-bold {% if tab == 'approved' %} bg-blue-600 text-white {% else %} bg-gray-900 text-gray-400 {% endif %}">
                    ✅ Approved Live Directory (''' + str(len(approved_biz)) + ''')
                </a>
            </div>

            <!-- DATA LIST -->
            <div class="bg-gray-900 p-6 rounded-3xl border border-gray-800">
                {% if tab == 'pending' %}
                    {% if pending_biz %}
                        <div class="space-y-4">
                            {% for b_id, biz in pending_biz.items() %}
                            <div class="bg-gray-800/60 p-4 rounded-2xl flex justify-between items-center">
                                <div>
                                    <h4 class="font-bold">{{ biz.name }}</h4>
                                    <p class="text-xs text-gray-400">📍 {{ biz.address }} | 📞 {{ biz.phones[0] }}</p>
                                </div>
                                <div class="flex gap-2">
                                    <a href="/admin?module=business&tab=pending&action=approve&id={{ b_id }}" class="bg-green-600 px-4 py-2 rounded-xl text-xs font-bold">Approve</a>
                                    <a href="/admin?module=business&tab=pending&action=delete&id={{ b_id }}" class="bg-red-600/20 text-red-400 px-3 py-2 rounded-xl text-xs font-bold">Delete</a>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    {% else %}
                        <p class="text-gray-500 text-center py-8">No pending business approvals.</p>
                    {% endif %}
                {% elif tab == 'approved' %}
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {% for b_id, biz in approved_biz.items() %}
                        <div class="bg-gray-800/40 p-4 rounded-2xl flex justify-between items-center">
                            <div>
                                <h4 class="font-bold">{{ biz.name }}</h4>
                                <p class="text-xs text-gray-400">📍 {{ biz.address }}</p>
                            </div>
                            <a href="/admin?module=business&tab=approved&action=delete&id={{ b_id }}" class="bg-red-600/20 text-red-400 px-3 py-1.5 rounded-xl text-xs font-bold">Delete</a>
                        </div>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
        </main>
        ''' + FOOTER, title="Business Module")

    # 3. MODULE 2: PAYMENT & SUBSCRIPTIONS
    elif module == 'payment':
        return render_template_string(BASE_HEAD + '''
        <main class="max-w-5xl mx-auto px-4 py-12">
            <div class="flex justify-between items-center mb-8">
                <a href="/admin" class="text-sm font-bold text-indigo-500 hover:underline">← Back to Admin Hub</a>
                <h2 class="text-2xl font-extrabold">💳 Payment & Subscription Module</h2>
            </div>

            <!-- SUB CATEGORY TABS -->
            <div class="flex flex-wrap gap-3 mb-8">
                <a href="/admin?module=payment&tab=pending" class="px-5 py-2.5 rounded-xl text-sm font-bold {% if tab == 'pending' %} bg-indigo-600 text-white {% else %} bg-gray-900 text-gray-400 {% endif %}">
                    ⚠️ New Payment Verification (''' + str(len(pending_pay)) + ''')
                </a>
                <a href="/admin?module=payment&tab=alerts" class="px-5 py-2.5 rounded-xl text-sm font-bold {% if tab == 'alerts' %} bg-red-600 text-white {% else %} bg-gray-900 text-gray-400 {% endif %} animate-pulse">
                    🚨 5-Day Expiry Alerts (''' + str(len(expiring_alerts)) + ''')
                </a>
                <a href="/admin?module=payment&tab=history" class="px-5 py-2.5 rounded-xl text-sm font-bold {% if tab == 'history' %} bg-indigo-600 text-white {% else %} bg-gray-900 text-gray-400 {% endif %}">
                    💳 Verified Payment Record (''' + str(len(paid_pay)) + ''')
                </a>
            </div>

            <div class="bg-gray-900 p-6 rounded-3xl border border-gray-800">
                {% if tab == 'pending' %}
                    {% if pending_pay %}
                        <div class="space-y-4">
                            {% for b_id, biz in pending_pay.items() %}
                            <div class="bg-gray-800/60 p-4 rounded-2xl flex justify-between items-center">
                                <div>
                                    <h4 class="font-bold">{{ biz.name }}</h4>
                                    <p class="text-xs text-blue-400">Method: {{ biz.get('payment_method') }} | Ref/TID: <code>{{ biz.get('payment_ref') }}</code></p>
                                </div>
                                <a href="/admin?module=payment&tab=pending&action=approve_pay&id={{ b_id }}" class="bg-blue-600 px-4 py-2 rounded-xl text-xs font-bold">Confirm Payment</a>
                            </div>
                            {% endfor %}
                        </div>
                    {% else %}
                        <p class="text-gray-500 text-center py-8">No pending payment verifications.</p>
                    {% endif %}
                {% elif tab == 'alerts' %}
                    {% if expiring %}
                        <div class="space-y-4">
                            {% for b_id, biz in expiring.items() %}
                            <div class="bg-red-950/40 border border-red-500/50 p-4 rounded-2xl flex justify-between items-center">
                                <div>
                                    <h4 class="font-bold text-white">{{ biz.name }}</h4>
                                    <p class="text-xs text-red-400 font-bold mt-1">⏳ Expiry Alert: Less than 5 Days Remaining!</p>
                                </div>
                                <a href="/admin?module=payment&tab=alerts&action=approve_pay&id={{ b_id }}" class="bg-red-600 px-4 py-2 rounded-xl text-xs font-bold">Renew (+30 Days)</a>
                            </div>
                            {% endfor %}
                        </div>
                    {% else %}
                        <p class="text-gray-500 text-center py-8">No short-time expiry alerts right now.</p>
                    {% endif %}
                {% elif tab == 'history' %}
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {% for b_id, biz in paid_pay.items() %}
                        <div class="bg-gray-800/40 p-4 rounded-2xl">
                            <h4 class="font-bold">{{ biz.name }}</h4>
                            <p class="text-xs text-gray-400 mt-1">Method: {{ biz.get('payment_method') }} | TID: <code>{{ biz.get('payment_ref') }}</code></p>
                            <span class="text-xs font-bold text-green-400 mt-2 block">✓ Active Subscription</span>
                        </div>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
        </main>
        ''' + FOOTER, expiring=expiring_alerts, title="Payment Module")

handler = app

if __name__ == '__main__':
    app.run(debug=True)
