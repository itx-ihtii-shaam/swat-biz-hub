"""SwatBiz Hub - Final Application with Dynamic Repeater Fields & Category Dynamic Inputs."""
from datetime import datetime, timedelta
import os
from flask import Flask, abort, redirect, render_template_string, request, url_for, session

SITE_NAME = 'SwatBiz Hub'
ADMIN_PASSWORD = 'admin123'

app = Flask(__name__)
app.secret_key = 'swat_biz_hub_secret_key'

BUSINESSES = {
    '1': {
        'id': '1',
        'category': 'hospitals',
        'subcategory': 'General Hospital',
        'name': 'Saidu Group of Teaching Hospital',
        'address': 'Saidu Sharif, Mingora, Swat',
        'phones': ['+92 946 9240123'],
        'image': 'https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=800&q=80',
        'status': 'approved',
        'payment_method': 'Free Trial',
        'payment_ref': 'TRIAL-FREE',
        'payment_status': 'paid',
        'joining_date': datetime.now() - timedelta(days=10),
        'expiry_date': datetime.now() + timedelta(days=50),
        'special_info': 'Dr. Muhammad Ali (Cardiologist - OPD Block Room 12), Dr. Ayesha Khan (Pediatrician - Children Ward)',
        'tests_dishes': 'MRI, CT Scan, X-Ray, Ultrasound, Emergency Care',
        'client_password': 'client123'
    },
    '2': {
        'id': '2',
        'category': 'restaurants',
        'subcategory': 'Traditional / Shinwari',
        'name': 'Khyber Shinwari Restaurant',
        'address': 'Fizagat, Swat',
        'phones': ['+92 946 881122'],
        'image': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80',
        'status': 'pending',
        'payment_method': 'Free Trial',
        'payment_ref': 'TRIAL-FREE',
        'payment_status': 'paid',
        'joining_date': datetime.now(),
        'expiry_date': datetime.now() + timedelta(days=60),
        'special_info': 'Special Family Cabin Available | Chef Rashid (Master Grill Chef)',
        'tests_dishes': 'Dumba Karahi (Rs. 2400/kg), Shinwari Tikka (Rs. 1800/kg), Mutton Kabab, Green Tea',
        'client_password': 'client123'
    },
    '3': {
        'id': '3',
        'category': 'pharmacies',
        'subcategory': 'Medical Store',
        'name': 'Shifa Medical & Pharmacy',
        'address': 'Green Chowk, Mingora, Swat',
        'phones': ['+92 946 7123456'],
        'image': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80',
        'status': 'approved',
        'payment_method': 'EasyPaisa',
        'payment_ref': 'TID-7782194',
        'payment_status': 'paid',
        'joining_date': datetime.now() - timedelta(days=45),
        'expiry_date': datetime.now() + timedelta(days=15),
        'special_info': 'Available Pharmacist: Dr. Bilal Ahmed (B.Pharm)',
        'tests_dishes': 'Blood Pressure Check, Blood Glucose Testing, First Aid Kit',
        'client_password': 'client123'
    }
}

CATEGORIES = {
    'hospitals': {
        'title': 'Hospitals & Healthcare', 'icon': '🏥', 'search_hint': 'Search name or location...', 'info_title': '👨‍⚕️ Doctors, Clinic & Timings', 'extra_title': '🔬 Available Tests & Services',
        'subcategories': ['General Hospital', 'Dental Clinic', 'Eye Specialist', 'Cardiology Clinic', 'Laboratory & Diagnostics']
    },
    'pharmacies': {
        'title': 'Pharmacies & Medical Stores', 'icon': '💊', 'search_hint': 'Search medicine or store...', 'info_title': '🧑‍⚕️ Qualified Pharmacists & Staff', 'extra_title': '💊 Available Medicines & Items',
        'subcategories': ['Medical Store', 'Homeopathic Store', 'Herbal & Organic', 'Surgical Equipment']
    },
    'restaurants': {
        'title': 'Restaurants & Cafes', 'icon': '🍽️', 'search_hint': 'Search restaurant...', 'info_title': '👨‍🍳 Chefs & Dining Features', 'extra_title': '🍲 Menu, Dishes & Prices',
        'subcategories': ['Traditional / Shinwari', 'Fast Food & Burgers', 'BBQ & Grill', 'Coffee Shop & Cafe', 'Desi Restaurant']
    },
    'supermarts': {
        'title': 'Supermarts & Grocery', 'icon': '🛒', 'search_hint': 'Search store or item...', 'info_title': '🏬 Store Facilities & Staff', 'extra_title': '🛍️ Available Groceries & Products',
        'subcategories': ['General Store', 'Supermarket', 'Vegetables & Fruits', 'Bakery & Sweets']
    },
    'property': {
        'title': 'Property Dealers', 'icon': '🏠', 'search_hint': 'Search plot or house...', 'info_title': '🧑‍💼 Agents & Dealers', 'extra_title': '🏡 Featured Plots & Properties',
        'subcategories': ['Plot & Land Dealer', 'House & Villa Rentals', 'Commercial Plaza', 'Real Estate Agency']
    },
    'hotels': {
        'title': 'Hotels & Guest Houses', 'icon': '🏨', 'search_hint': 'Search hotel...', 'info_title': '🛎️ Management & Reception', 'extra_title': '🛏️ Rooms, Rates & Facilities',
        'subcategories': ['Luxury Hotel', 'Guest House', 'Resort', 'Budget Inn']
    },
    'education': {
        'title': 'Educational Institutes', 'icon': '🎓', 'search_hint': 'Search school or college...', 'info_title': '👨‍🏫 Faculty & Teachers Info', 'extra_title': '📚 Offered Courses & Programs',
        'subcategories': ['School & College', 'University', 'Academy & Tuition', 'Language & Computer Center']
    }
}

HOME_HEAD = '''
<!DOCTYPE html>
<html lang="en" id="html-root" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>''' + SITE_NAME + '''</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏙️</text></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config = { darkMode: 'class' }</script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen transition-colors duration-300">
    <header class="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white shadow-xl">
        <div class="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
            <a href="/" class="text-2xl font-extrabold tracking-tight hover:opacity-85 transition transform hover:scale-105">🏙️ ''' + SITE_NAME + '''</a>
            <div class="flex items-center space-x-3">
                <a href="/register" class="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-xl text-sm font-bold shadow-lg transform hover:-translate-y-0.5 transition-all">＋ Register Business</a>
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
    <title>''' + SITE_NAME + '''</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏙️</text></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config = { darkMode: 'class' }</script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen transition-colors duration-300">
    <header class="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white shadow-xl">
        <div class="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
            <a href="/" class="text-xl font-bold hover:text-blue-400 transition-all transform hover:-translate-x-1 flex items-center gap-2">← Back to Home</a>
            <div class="flex items-center space-x-3">
                <a href="/register" class="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-xl text-sm font-bold shadow-lg transform hover:-translate-y-0.5 transition-all">＋ Register Business</a>
            </div>
        </div>
    </header>
'''

ADMIN_HEAD = '''
<!DOCTYPE html>
<html lang="en" id="html-root" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin - ''' + SITE_NAME + '''</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🛠️</text></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config = { darkMode: 'class' }</script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen transition-colors duration-300">
    <header class="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white shadow-xl">
        <div class="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
            <span class="text-xl font-bold">🛠️ Admin Control Center</span>
            <div class="flex items-center space-x-3">
                <a href="/admin?action=logout" class="bg-red-600/20 text-red-400 hover:bg-red-600 hover:text-white px-4 py-2 rounded-xl text-sm font-bold transition transform hover:scale-105">Logout</a>
            </div>
        </div>
    </header>
'''

ADMIN_SUB_HEAD = '''
<!DOCTYPE html>
<html lang="en" id="html-root" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin - ''' + SITE_NAME + '''</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🛠️</text></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config = { darkMode: 'class' }</script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen transition-colors duration-300">
    <header class="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white shadow-xl">
        <div class="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
            <a href="/admin" class="text-xl font-bold hover:text-indigo-400 transition-all transform hover:-translate-x-1 flex items-center gap-2">← Back to Admin Hub</a>
            <div class="flex items-center space-x-3">
                <a href="/admin?action=logout" class="bg-red-600/20 text-red-400 hover:bg-red-600 hover:text-white px-4 py-2 rounded-xl text-sm font-bold transition transform hover:scale-105">Logout</a>
            </div>
        </div>
    </header>
'''

FOOTER = '''
    <footer class="text-center py-8 text-sm text-gray-500 border-t border-gray-800 mt-20">
        <p>&copy; 2026 ''' + SITE_NAME + '''. All rights reserved.</p>
    </footer>
</body>
</html>
'''

@app.route('/')
def home():
    cards = ""
    for slug, cat in CATEGORIES.items():
        cards += '''
        <a href="/category/''' + slug + '''" class="bg-gray-900 p-8 rounded-3xl border border-gray-800 shadow-sm hover:shadow-2xl hover:border-blue-500 transition-all duration-300 transform hover:-translate-y-1.5 flex items-center space-x-5 group">
            <span class="text-5xl p-4 bg-gray-800 rounded-2xl group-hover:scale-110 transition-transform duration-300">''' + cat["icon"] + '''</span>
            <div>
                <h3 class="text-xl font-bold group-hover:text-blue-500 transition-colors duration-200">''' + cat["title"] + '''</h3>
                <p class="text-sm text-gray-400 mt-1">Browse listings →</p>
            </div>
        </a>
        '''
    
    html = HOME_HEAD + '''
    <section class="py-16 px-4 text-center">
        <h2 class="text-4xl md:text-5xl font-black tracking-tight">Discover Swat & Mingora Businesses</h2>
        <p class="text-gray-400 text-lg mt-2">Find verified local services instantly.</p>
    </section>
    <main class="max-w-7xl mx-auto px-4 pb-20">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            ''' + cards + '''
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/category/<cat_slug>')
def category_page(cat_slug):
    if cat_slug not in CATEGORIES:
        abort(404)
    
    cat = CATEGORIES[cat_slug]
    search_query = request.args.get('q', '').lower().strip()
    
    now = datetime.now()
    all_biz = [b for b in BUSINESSES.values() if b.get('category') == cat_slug and b.get('status') == 'approved' and b.get('expiry_date', now) >= now]
    filtered = []
    for b in all_biz:
        if search_query:
            if search_query in b.get('name', '').lower() or search_query in b.get('address', '').lower() or search_query in b.get('subcategory', '').lower() or search_query in b.get('special_info', '').lower() or search_query in b.get('tests_dishes', '').lower():
                filtered.append(b)
        else:
            filtered.append(b)

    cards = ""
    for b in filtered:
        subcat_badge = '<span class="bg-indigo-600/20 text-indigo-400 text-xs px-2.5 py-1 rounded-md font-semibold">' + b.get('subcategory', 'General') + '</span>' if b.get('subcategory') else ''
        cards += '''
        <a href="/business/''' + b['id'] + '''" class="bg-gray-900 rounded-2xl shadow-sm hover:shadow-2xl hover:border-blue-500 transition-all duration-300 transform hover:-translate-y-1.5 border border-gray-800 overflow-hidden flex flex-col justify-between group">
            <img src="''' + b.get('image', 'https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=800&q=80') + '''" class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-500">
            <div class="p-6">
                <div class="mb-2">''' + subcat_badge + '''</div>
                <h3 class="text-xl font-bold group-hover:text-blue-400 transition-colors">''' + b['name'] + '''</h3>
                <p class="text-sm text-gray-400 mt-1">📍 ''' + b['address'] + '''</p>
                <p class="text-xs text-blue-400 mt-2 font-bold">📞 ''' + b.get('phones', ['N/A'])[0] + '''</p>
                <span class="inline-block mt-4 text-xs font-bold text-blue-500 bg-blue-500/10 px-3 py-1.5 rounded-lg group-hover:bg-blue-600 group-hover:text-white transition">View Details →</span>
            </div>
        </a>
        '''
    if not cards:
        cards = '<div class="col-span-3 text-center py-20 text-gray-500"><p class="text-xl">No active or approved listings found.</p></div>'

    json_list = ""
    for b in all_biz:
        json_list += '{"id": "' + b['id'] + '", "name": "' + b['name'].replace('"', '\\"') + '", "address": "' + b['address'].replace('"', '\\"') + '", "sub": "' + b.get('subcategory', '').replace('"', '\\"') + '", "info": "' + b.get('special_info', '').replace('"', '\\"') + '", "items": "' + b.get('tests_dishes', '').replace('"', '\\"') + '"},'

    html = BASE_HEAD + '''
    <main class="max-w-7xl mx-auto px-4 py-12">
        <div class="mb-8 text-center">
            <span class="text-6xl inline-block animate-bounce">''' + cat['icon'] + '''</span>
            <h2 class="text-4xl font-extrabold mt-4">''' + cat['title'] + '''</h2>
            <div class="mt-6 max-w-xl mx-auto relative">
                <form method="GET" action="/category/''' + cat_slug + '''" class="flex gap-3">
                    <input type="text" id="searchInput" name="q" value="''' + search_query + '''" placeholder="''' + cat['search_hint'] + '''" autocomplete="off" class="w-full px-5 py-3.5 rounded-2xl bg-gray-900 border border-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                    <button type="submit" class="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3.5 rounded-2xl font-semibold transition transform hover:scale-105">Search</button>
                </form>
                <div id="suggestionsBox" class="absolute left-0 right-0 mt-2 bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl hidden z-50 overflow-hidden text-left"></div>
            </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            ''' + cards + '''
        </div>
    </main>
    <script>
        const allListings = [''' + json_list + '''];
        const searchInput = document.getElementById('searchInput');
        const suggestionsBox = document.getElementById('suggestionsBox');

        if(searchInput) {
            searchInput.addEventListener('input', function() {
                const query = this.value.toLowerCase().trim();
                if (!query) {
                    suggestionsBox.classList.add('hidden');
                    suggestionsBox.innerHTML = '';
                    return;
                }
                const matches = allListings.filter(b => 
                    b.name.toLowerCase().includes(query) || b.address.toLowerCase().includes(query) || b.sub.toLowerCase().includes(query) || b.info.toLowerCase().includes(query) || b.items.toLowerCase().includes(query)
                );
                if (matches.length > 0) {
                    let html = '';
                    matches.forEach(match => {
                        html += `<div class="px-5 py-3 hover:bg-gray-800 cursor-pointer border-b border-gray-800 last:border-none transition" onclick="window.location.href='/business/${match.id}'">
                            <div class="text-sm font-bold text-white">''' + cat['icon'] + ` ${match.name} <span class="text-xs text-indigo-400 font-normal">(${match.sub})</span></div>
                            <div class="text-xs text-gray-400">📍 ${match.address}</div>
                        </div>`;
                    });
                    suggestionsBox.innerHTML = html;
                    suggestionsBox.classList.remove('hidden');
                } else {
                    suggestionsBox.classList.add('hidden');
                }
            });
        }

        document.addEventListener('click', function(e) {
            if (searchInput && suggestionsBox && !searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
                suggestionsBox.classList.add('hidden');
            }
        });
    </script>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/business/<b_id>', methods=['GET', 'POST'])
def business_detail(b_id):
    if b_id not in BUSINESSES:
        abort(404)
    b = BUSINESSES[b_id]
    
    is_admin = session.get('admin_logged_in')
    client_auth_key = f'client_auth_{b_id}'
    is_client = session.get(client_auth_key)

    error_msg = ""
    if request.method == 'POST':
        entered_pass = request.form.get('client_password', '')
        if entered_pass == b.get('client_password', 'client123'):
            session[client_auth_key] = True
            is_client = True
        else:
            error_msg = "Incorrect Client Password! Please try again."

    now = datetime.now()
    if (b.get('status') != 'approved' or b.get('expiry_date', now) < now) and not is_admin and not is_client:
        html = BASE_HEAD + '''
        <main class="max-w-xl mx-auto px-4 py-20 text-center">
            <div class="bg-gray-900 border border-gray-800 rounded-3xl p-10 shadow-2xl space-y-4">
                <span class="text-6xl inline-block">🔒</span>
                <h1 class="text-2xl font-bold text-white">Listing Inactive, Expired or Password Protected</h1>
                <p class="text-gray-400 text-sm">Please enter the Client Password to unlock and view this listing.</p>
                
                <form method="POST" class="space-y-3 pt-2">
                    <input type="password" name="client_password" required placeholder="Enter Client Password" class="w-full p-3.5 rounded-xl bg-gray-800 border border-gray-700 text-center focus:ring-2 focus:ring-blue-500 outline-none text-sm">
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold transition text-sm">Unlock Listing</button>
                </form>
                ''' + (f'<p class="text-red-400 text-xs font-semibold">{error_msg}</p>' if error_msg else '') + '''

                <div class="pt-4">
                    <a href="/" class="text-gray-400 hover:text-white text-xs underline">Return to Home</a>
                </div>
            </div>
        </main>
        ''' + FOOTER
        return render_template_string(html)

    cat_meta = CATEGORIES.get(b['category'], {'info_title': 'Special Info', 'extra_title': 'Tests & Dishes'})
    special_info = b.get('special_info', 'Not specified')
    tests_dishes = b.get('tests_dishes', 'Not specified')

    html = BASE_HEAD + '''
    <main class="max-w-4xl mx-auto px-4 py-12">
        <div class="bg-gray-900 border border-gray-800 rounded-3xl overflow-hidden shadow-2xl">
            <img src="''' + b.get('image', 'https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=800&q=80') + '''" class="w-full h-72 object-cover">
            <div class="p-8 space-y-6">
                <div>
                    <div class="flex items-center gap-3 mb-2">
                        <span class="bg-blue-600/20 text-blue-400 text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider">Verified Listing</span>
                        <span class="bg-indigo-600/20 text-indigo-400 text-xs px-3 py-1 rounded-full font-semibold">''' + b.get('subcategory', 'General') + '''</span>
                    </div>
                    <h1 class="text-3xl md:text-4xl font-black mt-3">''' + b['name'] + '''</h1>
                    <p class="text-gray-400 mt-1 text-base">📍 ''' + b['address'] + '''</p>
                    <div class="mt-4 inline-flex items-center gap-2 bg-blue-600/10 border border-blue-500/20 px-4 py-2 rounded-xl">
                        <span class="text-blue-400 text-sm font-bold">📞 Contact:</span>
                        <a href="tel:''' + b.get('phones', [''])[0] + '''" class="text-base font-extrabold text-white hover:text-blue-400 transition">''' + b.get('phones', ['N/A'])[0] + '''</a>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2 border-t border-gray-800">
                    <div class="bg-gray-800/50 p-6 rounded-2xl border border-gray-700/50">
                        <h3 class="text-lg font-bold text-blue-400 mb-2">''' + cat_meta['info_title'] + '''</h3>
                        <p class="text-gray-300 text-sm leading-relaxed whitespace-pre-line">''' + special_info + '''</p>
                    </div>
                    <div class="bg-gray-800/50 p-6 rounded-2xl border border-gray-700/50">
                        <h3 class="text-lg font-bold text-emerald-400 mb-2">''' + cat_meta['extra_title'] + '''</h3>
                        <p class="text-gray-300 text-sm leading-relaxed whitespace-pre-line">''' + tests_dishes + '''</p>
                    </div>
                </div>

                <div class="pt-4 border-t border-gray-800 flex justify-between items-center">
                    <span class="text-xs text-gray-500">🔒 Secure Client Access Active</span>
                    <a href="/category/''' + b['category'] + '''" class="bg-gray-800 hover:bg-gray-700 px-5 py-2.5 rounded-xl text-sm font-semibold transition transform hover:-translate-x-1">← Back to Category</a>
                </div>
            </div>
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/register', methods=['GET', 'POST'])
def register_business():
    if request.method == 'POST':
        b_id = str(len(BUSINESSES) + 1)
        
        # Combine repeated field entries into structured string
        names = request.form.getlist('repeater_col1[]')
        col2_vals = request.form.getlist('repeater_col2[]')
        col3_vals = request.form.getlist('repeater_col3[]')
        col4_vals = request.form.getlist('repeater_col4[]')
        col5_vals = request.form.getlist('repeater_col5[]')

        formatted_repeater_list = []
        for i in range(len(names)):
            if names[i].strip():
                entry_str = f"• {names[i].strip()}"
                if i < len(col2_vals) and col2_vals[i].strip(): entry_str += f" ({col2_vals[i].strip()})"
                if i < len(col3_vals) and col3_vals[i].strip(): entry_str += f" | Timing: {col3_vals[i].strip()}"
                if i < len(col4_vals) and col4_vals[i].strip(): entry_str += f" | Hours: {col4_vals[i].strip()}"
                if i < len(col5_vals) and col5_vals[i].strip(): entry_str += f" | Location/Room: {col5_vals[i].strip()}"
                formatted_repeater_list.append(entry_str)

        combined_repeater_text = "\n".join(formatted_repeater_list) if formatted_repeater_list else request.form.get('special_info', 'N/A')

        BUSINESSES[b_id] = {
            'id': b_id,
            'category': request.form.get('category'),
            'subcategory': request.form.get('subcategory', 'General'),
            'name': request.form.get('name'),
            'address': request.form.get('address'),
            'phones': [request.form.get('phone', '')],
            'special_info': combined_repeater_text,
            'tests_dishes': request.form.get('tests_dishes', 'N/A'),
            'status': 'pending',
            'payment_method': request.form.get('payment_method', 'Free Trial'),
            'payment_ref': request.form.get('payment_ref', 'TRIAL-60DAYS'),
            'payment_status': 'paid',
            'joining_date': datetime.now(),
            'expiry_date': datetime.now() + timedelta(days=60),
            'client_password': request.form.get('client_password', 'client123')
        }
        return redirect('/')

    opts = ""
    for k, v in CATEGORIES.items():
        opts += '<option value="' + k + '">' + v["title"] + '</option>'

    html = BASE_HEAD + '''
    <main class="max-w-3xl mx-auto px-4 py-12">
        <h2 class="text-3xl font-extrabold text-center mb-2">Register Business</h2>
        <p class="text-center text-sm text-gray-400 mb-8">Enjoy 2 Months Free Trial upon registration!</p>
        <form method="POST" class="space-y-4">
            <input type="text" name="name" required placeholder="Business / Hospital / Restaurant Name" class="w-full p-3.5 rounded-xl bg-gray-900 border border-gray-800 focus:ring-2 focus:ring-blue-500 outline-none transition">
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-bold text-gray-400 mb-1">Category</label>
                    <select name="category" id="categorySelect" class="w-full p-3.5 rounded-xl bg-gray-900 border border-gray-800 focus:ring-2 focus:ring-blue-500 outline-none transition">''' + opts + '''</select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-400 mb-1">Subcategory</label>
                    <select name="subcategory" id="subcategorySelect" class="w-full p-3.5 rounded-xl bg-gray-900 border border-gray-800 focus:ring-2 focus:ring-blue-500 outline-none transition"></select>
                </div>
            </div>

            <input type="text" name="address" required placeholder="Address (e.g. Mingora, Swat)" class="w-full p-3.5 rounded-xl bg-gray-900 border border-gray-800 focus:ring-2 focus:ring-blue-500 outline-none transition">
            <input type="text" name="phone" required placeholder="Phone Number" class="w-full p-3.5 rounded-xl bg-gray-900 border border-gray-800 focus:ring-2 focus:ring-blue-500 outline-none transition">
            
            <div class="border-t border-gray-800 pt-4 mt-4">
                <label class="block text-xs font-bold text-gray-400 mb-2">🔒 Secure Client Password (Required for secure access)</label>
                <input type="password" name="client_password" required placeholder="Enter secret client password" class="w-full p-3.5 rounded-xl bg-gray-900 border border-gray-800 focus:ring-2 focus:ring-blue-500 outline-none text-sm transition">
            </div>

            <!-- Dynamic Repeating Rows Section (e.g. Doctors, Menu, Courses) -->
            <div class="border-t border-gray-800 pt-4 mt-4">
                <div class="flex justify-between items-center mb-3">
                    <label class="block text-sm font-bold text-blue-400" id="repeaterTitle">🩺 Doctors, Clinic & Timings</label>
                </div>
                
                <div id="repeaterContainer" class="space-y-4"></div>
                
                <button type="button" id="addRowBtn" onclick="addNewRow()" class="mt-4 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs px-5 py-3 rounded-xl transition transform hover:scale-105 inline-flex items-center gap-1.5 shadow-lg">
                    + Add Another Entry
                </button>
            </div>

            <div class="border-t border-gray-800 pt-4 mt-4">
                <label class="block text-xs font-bold text-gray-400 mb-2" id="extraTitle">Tests, Menu Items or Products (Optional)</label>
                <textarea name="tests_dishes" id="dishesField" placeholder="Tests & Services, Special Dishes / Menu items, or Products..." class="w-full p-3.5 rounded-xl bg-gray-900 border border-gray-800 focus:ring-2 focus:ring-blue-500 outline-none text-sm transition" rows="2"></textarea>
            </div>

            <div class="border-t border-gray-800 pt-4 mt-4">
                <label class="block text-xs font-bold text-gray-400 mb-2">Payment Details (Optional - Free for first 2 Months)</label>
                <select name="payment_method" class="w-full p-3.5 rounded-xl bg-gray-900 border border-gray-800 focus:ring-2 focus:ring-blue-500 outline-none transition">
                    <option value="Free Trial">2 Months Free Trial (Active)</option>
                    <option value="EasyPaisa">EasyPaisa</option>
                    <option value="JazzCash">JazzCash</option>
                    <option value="Bank Transfer">Bank Transfer</option>
                </select>
                <input type="text" name="payment_ref" placeholder="TID / Ref Number (Optional)" class="w-full p-3.5 rounded-xl bg-gray-900 border border-gray-800 focus:ring-2 focus:ring-blue-500 outline-none mt-3 transition">
            </div>

            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 py-3.5 rounded-xl font-bold transition transform hover:-translate-y-0.5 shadow-lg">Submit Business</button>
        </form>
    </main>

    <script>
        const subcategoriesData = {
            'hospitals': ['General Hospital', 'Dental Clinic', 'Eye Specialist', 'Cardiology Clinic', 'Laboratory & Diagnostics'],
            'pharmacies': ['Medical Store', 'Homeopathic Store', 'Herbal & Organic', 'Surgical Equipment'],
            'restaurants': ['Traditional / Shinwari', 'Fast Food & Burgers', 'BBQ & Grill', 'Coffee Shop & Cafe', 'Desi Restaurant'],
            'supermarts': ['General Store', 'Supermarket', 'Vegetables & Fruits', 'Bakery & Sweets'],
            'property': ['Plot & Land Dealer', 'House & Villa Rentals', 'Commercial Plaza', 'Real Estate Agency'],
            'hotels': ['Luxury Hotel', 'Guest House', 'Resort', 'Budget Inn'],
            'education': ['School & College', 'University', 'Academy & Tuition', 'Language & Computer Center']
        };

        const categoryRowConfigs = {
            'hospitals': {
                title: '🩺 Doctors, Clinic & Timings',
                addBtnText: '+ Add Another Doctor',
                c1: 'Doctor Name (Dr. Ahmad)', c2: 'Specialty (Cardiologist)',
                c3: 'Appointment Timing (9 AM - 2 PM)', c4: 'Clinic Timing (Mon-Sat, 9 AM - 5 PM)',
                c5: 'Clinic / Room (Room 12, OPD Block)'
            },
            'restaurants': {
                title: '👨‍🍳 Chefs, Special Dishes & Menu Items',
                addBtnText: '+ Add Menu Item / Dish',
                c1: 'Item / Dish Name (Dumba Karahi)', c2: 'Category (BBQ / Main Course)',
                c3: 'Price (Rs. 2400)', c4: 'Availability (Daily)',
                c5: 'Description / Special Serving Notes'
            },
            'education': {
                title: '🎓 Faculty, Teachers & Courses',
                addBtnText: '+ Add Teacher / Course',
                c1: 'Teacher / Course Name (Prof. Ali)', c2: 'Department / Course (Computer Science)',
                c3: 'Timing (Morning / Evening)', c4: 'Days (Mon-Fri)',
                c5: 'Fee / Room No (Lab 2)'
            },
            'pharmacies': {
                title: '💊 Pharmacists & Staff Info',
                addBtnText: '+ Add Staff / Pharmacist',
                c1: 'Staff Name (Dr. Bilal)', c2: 'Qualification (Pharm-D)',
                c3: 'Shift Timing (8 AM - 4 PM)', c4: 'Available Days (Mon-Sat)',
                c5: 'Counter / Section'
            },
            'supermarts': {
                title: '🏬 Store Sections & Managers',
                addBtnText: '+ Add Section / Manager',
                c1: 'Manager / Section (Tariq - Grocery)', c2: 'Department',
                c3: 'Timing', c4: 'Days', c5: 'Floor / Location'
            },
            'property': {
                title: '🏡 Real Estate Agents & Deals',
                addBtnText: '+ Add Agent / Featured Property',
                c1: 'Agent / Property Title (Malik Zubair)', c2: 'Type (5 Marla Plot)',
                c3: 'Price / Contact', c4: 'Area / Location', c5: 'Details'
            },
            'hotels': {
                title: '🛏️ Rooms, Suites & Rates',
                addBtnText: '+ Add Room Type',
                c1: 'Room Type (Deluxe Family Suite)', c2: 'Capacity (4 Persons)',
                c3: 'Rate per Night (Rs. 8000)', c4: 'Facilities (AC, WiFi, River View)', c5: 'Floor / Block'
            }
        };

        const catSelect = document.getElementById('categorySelect');
        const subcatSelect = document.getElementById('subcategorySelect');
        const repeaterTitle = document.getElementById('repeaterTitle');
        const addRowBtn = document.getElementById('addRowBtn');
        const repeaterContainer = document.getElementById('repeaterContainer');

        function addNewRow() {
            const cat = catSelect.value;
            const cfg = categoryRowConfigs[cat] || categoryRowConfigs['hospitals'];

            const rowCard = document.createElement('div');
            rowCard.className = 'bg-gray-900/90 border border-gray-800 p-4 rounded-2xl space-y-3 relative group';

            rowCard.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input type="text" name="repeater_col1[]" placeholder="${cfg.c1}" class="p-3 bg-gray-950 border border-gray-800 rounded-xl text-xs text-white focus:ring-2 focus:ring-blue-500 outline-none">
                    <input type="text" name="repeater_col2[]" placeholder="${cfg.c2}" class="p-3 bg-gray-950 border border-gray-800 rounded-xl text-xs text-white focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input type="text" name="repeater_col3[]" placeholder="${cfg.c3}" class="p-3 bg-gray-950 border border-gray-800 rounded-xl text-xs text-white focus:ring-2 focus:ring-blue-500 outline-none">
                    <input type="text" name="repeater_col4[]" placeholder="${cfg.c4}" class="p-3 bg-gray-950 border border-gray-800 rounded-xl text-xs text-white focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                <div class="flex gap-2">
                    <input type="text" name="repeater_col5[]" placeholder="${cfg.c5}" class="w-full p-3 bg-gray-950 border border-gray-800 rounded-xl text-xs text-white focus:ring-2 focus:ring-blue-500 outline-none">
                    <button type="button" onclick="this.closest('.group').remove()" class="bg-red-600/20 text-red-400 hover:bg-red-600 hover:text-white px-3 rounded-xl text-xs font-bold transition">✕</button>
                </div>
            `;
            repeaterContainer.appendChild(rowCard);
        }

        function updateFormFields() {
            const val = catSelect.value;
            
            // 1. Subcategories Dropdown
            subcatSelect.innerHTML = '';
            if(subcategoriesData[val]) {
                subcategoriesData[val].forEach(sub => {
                    const opt = document.createElement('option');
                    opt.value = sub;
                    opt.textContent = sub;
                    subcatSelect.appendChild(opt);
                });
            }

            // 2. Repeater Row Setup
            const cfg = categoryRowConfigs[val] || categoryRowConfigs['hospitals'];
            repeaterTitle.innerText = cfg.title;
            addRowBtn.innerText = cfg.addBtnText;

            // Clear & Add initial row
            repeaterContainer.innerHTML = '';
            addNewRow();
        }

        catSelect.addEventListener('change', updateFormFields);
        window.addEventListener('DOMContentLoaded', updateFormFields);
    </script>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin')

    if not session.get('admin_logged_in'):
        html = BASE_HEAD + '''
        <main class="max-w-md mx-auto px-4 py-20 text-center">
            <div class="bg-gray-900 p-8 rounded-3xl border border-gray-800 shadow-xl">
                <h2 class="text-2xl font-bold mb-4">🔒 Admin Portal Login</h2>
                <form method="POST" class="space-y-4">
                    <input type="password" name="password" required placeholder="Password" class="w-full p-3 rounded-xl bg-gray-800 border border-gray-700 text-center focus:ring-2 focus:ring-blue-500 outline-none">
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold transition">Login</button>
                </form>
            </div>
        </main>
        ''' + FOOTER
        return render_template_string(html)

    module = request.args.get('module')
    tab = request.args.get('tab', 'pending')
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
            BUSINESSES[biz_id]['expiry_date'] = datetime.now() + timedelta(days=60)
        elif action == 'delete':
            BUSINESSES[biz_id]['status'] = 'deleted'
        return redirect('/admin?module=' + str(module) + '&tab=' + str(tab))

    now = datetime.now()
    pending_biz = {k: v for k, v in BUSINESSES.items() if v.get('status') == 'pending'}
    approved_biz = {k: v for k, v in BUSINESSES.items() if v.get('status') == 'approved'}
    pending_pay = {k: v for k, v in BUSINESSES.items() if v.get('payment_status') == 'unpaid'}
    paid_pay = {k: v for k, v in BUSINESSES.items() if v.get('payment_status') == 'paid' and v.get('expiry_date', now) >= now}
    
    expiring_alerts = {}
    for k, v in BUSINESSES.items():
        if v.get('status') != 'deleted' and v.get('expiry_date'):
            days_diff = (v.get('expiry_date') - now).days
            if 0 <= days_diff <= 5:
                expiring_alerts[k] = v

    expired_subs = {}
    for k, v in BUSINESSES.items():
        if v.get('status') != 'deleted' and v.get('expiry_date'):
            if (v.get('expiry_date') - now).days < 0:
                expired_subs[k] = v

    if not module:
        html = ADMIN_HEAD + '''
        <main class="max-w-5xl mx-auto px-4 py-12">
            <div class="flex justify-between items-center mb-10">
                <h2 class="text-3xl font-extrabold">🛠️ Admin Control Center</h2>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <a href="/admin?module=business&tab=pending" class="bg-gray-900 p-8 rounded-3xl border border-gray-800 hover:border-blue-500 transition-all duration-300 transform hover:-translate-y-2 shadow-2xl flex flex-col justify-between group">
                    <div>
                        <div class="flex justify-between items-center mb-6">
                            <span class="text-6xl group-hover:scale-110 transition-transform">🏢</span>
                            <span class="bg-yellow-500/20 text-yellow-400 text-xs px-3 py-1.5 rounded-full font-bold">''' + str(len(pending_biz)) + ''' Pending</span>
                        </div>
                        <h3 class="text-2xl font-black group-hover:text-blue-500 transition-colors">1. Business Directory Module</h3>
                        <p class="text-gray-400 text-sm mt-2">Manage new business registration approvals and live directory listings.</p>
                    </div>
                    <div class="mt-8 text-blue-500 font-bold text-sm flex justify-between items-center">
                        <span>Open Business Portal →</span>
                        <span class="text-xs text-gray-500">''' + str(len(approved_biz)) + ''' Live Listings</span>
                    </div>
                </a>

                <a href="/admin?module=payment&tab=pending" class="bg-gray-900 p-8 rounded-3xl border border-gray-800 hover:border-indigo-500 transition-all duration-300 transform hover:-translate-y-2 shadow-2xl flex flex-col justify-between group">
                    <div>
                        <div class="flex justify-between items-center mb-6">
                            <span class="text-6xl group-hover:scale-110 transition-transform">💳</span>
                            <span class="bg-red-500/20 text-red-400 text-xs px-3 py-1.5 rounded-full font-bold">''' + str(len(expired_subs)) + ''' Expired</span>
                        </div>
                        <h3 class="text-2xl font-black group-hover:text-indigo-500 transition-colors">2. Payment & Subscription Module</h3>
                        <p class="text-gray-400 text-sm mt-2">Verify payments, 5-day expiry alerts, and fully expired subscriptions.</p>
                    </div>
                    <div class="mt-8 text-indigo-500 font-bold text-sm flex justify-between items-center">
                        <span>Open Payment Portal →</span>
                        <span class="text-xs text-red-400 font-bold">''' + str(len(expired_subs)) + ''' Expired / ''' + str(len(expiring_alerts)) + ''' Alerts</span>
                    </div>
                </a>
            </div>
        </main>
        ''' + FOOTER
        return render_template_string(html)

    elif module == 'business':
        content = ""
        if tab == 'pending':
            for b_id, b in pending_biz.items():
                j_date = b.get('joining_date', datetime.now()).strftime('%Y-%m-%d')
                content += '''
                <div class="bg-gray-800/60 p-4 rounded-2xl flex justify-between items-center hover:bg-gray-800 transition">
                    <div>
                        <h4 class="font-bold">''' + b["name"] + ''' <span class="text-xs text-indigo-400">(''' + b.get('subcategory', 'General') + ''')</span></h4>
                        <p class="text-xs text-gray-400">📍 ''' + b["address"] + ''' | 📅 Joined: <span class="text-blue-400 font-semibold">''' + j_date + '''</span></p>
                    </div>
                    <div class="flex gap-2 items-center">
                        <a href="/business/''' + b_id + '''" target="_blank" class="bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white px-3 py-2 rounded-xl text-xs font-bold transition">Preview</a>
                        <a href="/admin?module=business&tab=pending&action=approve&id=''' + b_id + '''" class="bg-green-600 hover:bg-green-500 px-4 py-2 rounded-xl text-xs font-bold transition">Approve</a>
                        <a href="/admin?module=business&tab=pending&action=delete&id=''' + b_id + '''" class="bg-red-600/20 text-red-400 hover:bg-red-600 hover:text-white px-3 py-2 rounded-xl text-xs font-bold transition">Delete</a>
                    </div>
                </div>
                '''
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No pending business approvals.</p>'
        else:
            for b_id, b in approved_biz.items():
                j_date = b.get('joining_date', datetime.now()).strftime('%Y-%m-%d')
                content += '''
                <div class="bg-gray-800/40 p-4 rounded-2xl flex justify-between items-center hover:bg-gray-800/70 transition">
                    <div>
                        <h4 class="font-bold">''' + b["name"] + ''' <span class="text-xs text-indigo-400">(''' + b.get('subcategory', 'General') + ''')</span></h4>
                        <p class="text-xs text-gray-400">📍 ''' + b["address"] + ''' | 📅 Joined: <span class="text-blue-400 font-semibold">''' + j_date + '''</span></p>
                    </div>
                    <div class="flex gap-2 items-center">
                        <a href="/business/''' + b_id + '''" target="_blank" class="bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white px-3 py-1.5 rounded-xl text-xs font-bold transition">View</a>
                        <a href="/admin?module=business&tab=approved&action=delete&id=''' + b_id + '''" class="bg-red-600/20 text-red-400 hover:bg-red-600 hover:text-white px-3 py-1.5 rounded-xl text-xs font-bold transition">Delete</a>
                    </div>
                </div>
                '''
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No approved listings.</p>'

        html = ADMIN_SUB_HEAD + '''
        <main class="max-w-4xl mx-auto px-4 py-12">
            <h2 class="text-2xl font-bold mb-6">🏢 Business Directory Management</h2>
            <div class="flex space-x-3 mb-6">
                <a href="/admin?module=business&tab=pending" class="px-5 py-2.5 rounded-xl font-bold text-sm transition ''' + ('bg-blue-600 text-white shadow-lg' if tab=='pending' else 'bg-gray-900 text-gray-400 hover:bg-gray-800') + '''">Pending (''' + str(len(pending_biz)) + ''')</a>
                <a href="/admin?module=business&tab=approved" class="px-5 py-2.5 rounded-xl font-bold text-sm transition ''' + ('bg-blue-600 text-white shadow-lg' if tab=='approved' else 'bg-gray-900 text-gray-400 hover:bg-gray-800') + '''">Approved (''' + str(len(approved_biz)) + ''')</a>
            </div>
            <div class="bg-gray-900 p-6 rounded-3xl border border-gray-800 space-y-4">
                ''' + content + '''
            </div>
        </main>
        ''' + FOOTER
        return render_template_string(html)

    elif module == 'payment':
        content = ""
        if tab == 'pending':
            for b_id, b in pending_pay.items():
                content += '''
                <div class="bg-gray-800/60 p-4 rounded-2xl flex justify-between items-center">
                    <div>
                        <h4 class="font-bold">''' + b["name"] + '''</h4>
                        <p class="text-xs text-gray-400">Method: <span class="text-blue-400 font-bold">''' + b.get('payment_method', 'N/A') + '''</span> | Ref: <span class="text-indigo-400 font-mono font-bold">''' + b.get('payment_ref', 'N/A') + '''</span></p>
                    </div>
                    <a href="/admin?module=payment&tab=pending&action=approve_pay&id=''' + b_id + '''" class="bg-green-600 hover:bg-green-500 px-4 py-2 rounded-xl text-xs font-bold transition">Verify & Activate (60 Days)</a>
                </div>
                '''
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No pending payment verifications.</p>'
        elif tab == 'alerts':
            for b_id, b in expiring_alerts.items():
                ed = b.get('expiry_date').strftime('%Y-%m-%d')
                content += '''
                <div class="bg-yellow-500/10 border border-yellow-500/30 p-4 rounded-2xl flex justify-between items-center">
                    <div>
                        <h4 class="font-bold">''' + b["name"] + '''</h4>
                        <p class="text-xs text-yellow-400 font-semibold">⚠️ Expires on: ''' + ed + '''</p>
                    </div>
                    <a href="/admin?module=payment&tab=alerts&action=approve_pay&id=''' + b_id + '''" class="bg-yellow-600 hover:bg-yellow-500 text-gray-950 px-4 py-2 rounded-xl text-xs font-bold transition">Renew 60 Days</a>
                </div>
                '''
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No subscriptions expiring in the next 5 days.</p>'
        else:
            for b_id, b in expired_subs.items():
                ed = b.get('expiry_date').strftime('%Y-%m-%d')
                content += '''
                <div class="bg-red-500/10 border border-red-500/30 p-4 rounded-2xl flex justify-between items-center">
                    <div>
                        <h4 class="font-bold">''' + b["name"] + '''</h4>
                        <p class="text-xs text-red-400 font-semibold">❌ Expired on: ''' + ed + '''</p>
                    </div>
                    <a href="/admin?module=payment&tab=expired&action=approve_pay&id=''' + b_id + '''" class="bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded-xl text-xs font-bold transition">Restore & Renew</a>
                </div>
                '''
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No expired subscriptions found.</p>'

        html = ADMIN_SUB_HEAD + '''
        <main class="max-w-4xl mx-auto px-4 py-12">
            <h2 class="text-2xl font-bold mb-6">💳 Payment & Subscription Hub</h2>
            <div class="flex space-x-3 mb-6">
                <a href="/admin?module=payment&tab=pending" class="px-5 py-2.5 rounded-xl font-bold text-sm transition ''' + ('bg-indigo-600 text-white shadow-lg' if tab=='pending' else 'bg-gray-900 text-gray-400 hover:bg-gray-800') + '''">Unpaid (''' + str(len(pending_pay)) + ''')</a>
                <a href="/admin?module=payment&tab=alerts" class="px-5 py-2.5 rounded-xl font-bold text-sm transition ''' + ('bg-yellow-600 text-gray-950 shadow-lg' if tab=='alerts' else 'bg-gray-900 text-gray-400 hover:bg-gray-800') + '''">Expiry Alerts (''' + str(len(expiring_alerts)) + ''')</a>
                <a href="/admin?module=payment&tab=expired" class="px-5 py-2.5 rounded-xl font-bold text-sm transition ''' + ('bg-red-600 text-white shadow-lg' if tab=='expired' else 'bg-gray-900 text-gray-400 hover:bg-gray-800') + '''">Expired (''' + str(len(expired_subs)) + ''')</a>
            </div>
            <div class="bg-gray-900 p-6 rounded-3xl border border-gray-800 space-y-4">
                ''' + content + '''
            </div>
        </main>
        ''' + FOOTER
        return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
