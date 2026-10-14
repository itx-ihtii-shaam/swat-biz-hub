"""SwatBiz Hub - Qualifications Field & Smart Admin Navigation Fix with Dynamic Registration Form."""
from datetime import datetime, timedelta
import os
import json
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
        'phones': ['+92 946 9240123', '+92 946 9240124'],
        'image': 'https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=800&q=80',
        'images': ['https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=800&q=80'],
        'status': 'approved',
        'payment_method': 'Free Trial',
        'payment_ref': 'TRIAL-FREE',
        'payment_status': 'paid',
        'joining_date': datetime.now() - timedelta(days=10),
        'expiry_date': datetime.now() + timedelta(days=50),
        'doctors': [
            {
                'name': 'Dr. Muhammad Ali',
                'specialty': 'Cardiologist',
                'qualifications': 'MBBS, FCPS (Cardiology), Head of Cardiology Dept',
                'appt_timing': '9:00 AM - 2:00 PM',
                'clinic_timing': 'Mon - Sat (9 AM - 5 PM)',
                'room': 'OPD Block - Room 12',
                'appt_numbers': '+92 300 9240001, +92 946 9240123'
            },
            {
                'name': 'Dr. Ayesha Khan',
                'specialty': 'Pediatrician',
                'qualifications': 'MBBS, DCH, MCPS (Pediatrics)',
                'appt_timing': '10:00 AM - 4:00 PM',
                'clinic_timing': 'Mon - Fri (10 AM - 4 PM)',
                'room': 'Children Ward - Room 04',
                'appt_numbers': '+92 301 8881122'
            }
        ],
        'special_info': 'Dr. Muhammad Ali (Cardiologist), Dr. Ayesha Khan (Pediatrician)',
        'tests_dishes': 'MRI, CT Scan, X-Ray, Ultrasound, Emergency Care',
        'client_email': 'owner1@swatbiz.com',
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
        'images': ['https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80'],
        'status': 'pending',
        'payment_method': 'Free Trial',
        'payment_ref': 'TRIAL-FREE',
        'payment_status': 'paid',
        'joining_date': datetime.now(),
        'expiry_date': datetime.now() + timedelta(days=60),
        'doctors': [
            {
                'name': 'Chef Rashid',
                'specialty': 'Master Grill & BBQ Chef',
                'qualifications': '15+ Years Culinary Experience',
                'appt_timing': '12:00 PM - 11:00 PM',
                'clinic_timing': 'Daily Open',
                'room': 'Main Grill Section / Family Cabin',
                'appt_numbers': '+92 946 881122'
            }
        ],
        'special_info': 'Special Family Cabin Available | Chef Rashid',
        'tests_dishes': 'Dumba Karahi (Rs. 2400/kg), Shinwari Tikka (Rs. 1800/kg), Mutton Kabab, Green Tea',
        'client_email': 'owner2@swatbiz.com',
        'client_password': 'client123'
    },
    '3': {
        'id': '3',
        'category': 'education',
        'subcategory': 'School & College',
        'name': 'Swat Public School & Science College',
        'address': 'Saidu Sharif, Mingora, Swat',
        'phones': ['+92 946 720111'],
        'image': 'https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80',
        'images': ['https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80'],
        'status': 'approved',
        'payment_method': 'Free Trial',
        'payment_ref': 'TRIAL-FREE',
        'payment_status': 'paid',
        'joining_date': datetime.now() - timedelta(days=5),
        'expiry_date': datetime.now() + timedelta(days=55),
        'doctors': [
            {
                'name': 'Prof. Shah Zarin',
                'specialty': 'Principal & Academic Head',
                'qualifications': 'M.Phil Education, Gold Medalist',
                'appt_timing': '8:00 AM - 2:00 PM',
                'clinic_timing': 'Mon - Sat',
                'room': 'Main Administration Block',
                'appt_numbers': '+92 946 720111'
            }
        ],
        'special_info': 'Prof. Shah Zarin (Principal), Admissions open for Metric & FSc',
        'tests_dishes': 'Science Labs, Computer Labs, Library, Sports Ground',
        'client_email': 'owner3@swatbiz.com',
        'client_password': 'client123'
    }
}

CATEGORIES = {
    'hospitals': {
        'title': 'Hospitals & Healthcare', 'icon': '🏥', 'search_hint': 'Search name, doctor or location (e.g. Saidu)...', 'info_title': '👨‍⚕️ Doctors, Clinic & Timings', 'extra_title': '🔬 Available Tests & Medical Services',
        'subcategories': ['General Hospital', 'Dental Clinic', 'Eye Specialist', 'Cardiology Clinic', 'Laboratory & Diagnostics']
    },
    'pharmacies': {
        'title': 'Pharmacies & Medical Stores', 'icon': '💊', 'search_hint': 'Search medicine, store or place...', 'info_title': '🧑‍⚕️ Qualified Pharmacists & Staff', 'extra_title': '💊 Available Medicines & Supplies',
        'subcategories': ['Medical Store', 'Homeopathic Store', 'Herbal & Organic', 'Surgical Equipment']
    },
    'restaurants': {
        'title': 'Restaurants & Cafes', 'icon': '🍽️', 'search_hint': 'Search restaurant, dish or location (e.g. Fizagat)...', 'info_title': '👨‍🍳 Chefs & Dining Features', 'extra_title': '🍲 Menu, Special Dishes & Prices',
        'subcategories': ['Traditional / Shinwari', 'Fast Food & Burgers', 'BBQ & Grill', 'Coffee Shop & Cafe', 'Desi Restaurant']
    },
    'supermarts': {
        'title': 'Supermarts & Grocery', 'icon': '🛒', 'search_hint': 'Search store, item or area...', 'info_title': '🏬 Store Facilities & Staff', 'extra_title': '🛍️ Available Groceries & Products',
        'subcategories': ['General Store', 'Supermarket', 'Vegetables & Fruits', 'Bakery & Sweets']
    },
    'property': {
        'title': 'Property Dealers', 'icon': '🏠', 'search_hint': 'Search plot, house or dealer...', 'info_title': '🧑‍💼 Agents & Dealers', 'extra_title': '🏡 Featured Plots & Properties',
        'subcategories': ['Plot & Land Dealer', 'House & Villa Rentals', 'Commercial Plaza', 'Real Estate Agency']
    },
    'hotels': {
        'title': 'Hotels & Guest Houses', 'icon': '🏨', 'search_hint': 'Search hotel or area...', 'info_title': '🛎️ Management & Reception', 'extra_title': '🛏️ Rooms, Rates & Facilities',
        'subcategories': ['Luxury Hotel', 'Guest House', 'Resort', 'Budget Inn']
    },
    'education': {
        'title': 'Educational Institutes', 'icon': '🎓', 'search_hint': 'Search school, college, university or place (e.g. Saidu)...', 'info_title': '👨‍🏫 Faculty & Teachers Info', 'extra_title': '📚 Offered Courses & Programs',
        'subcategories': ['School', 'School & College', 'College', 'University', 'Academy & Tuition', 'Language & Computer Center']
    }
}

ANIMATION_STYLES = '''
<style>
    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes modalPop {
        0% { opacity: 0; transform: scale(0.85) translateY(-20px); }
        100% { opacity: 1; transform: scale(1) translateY(0); }
    }
    .animate-fade-in { animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    .animate-modal { animation: modalPop 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    
    .input-hover-effect {
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .input-hover-effect:hover {
        border-color: #3b82f6;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.25);
        transform: translateY(-1px);
    }
    .input-hover-effect:focus {
        border-color: #60a5fa;
        box-shadow: 0 0 18px rgba(59, 130, 246, 0.45);
        transform: translateY(-1px);
    }

    .btn-hover-effect {
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .btn-hover-effect:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 20px -4px rgba(59, 130, 246, 0.4);
    }

    .card-hover-effect {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .card-hover-effect:hover {
        transform: translateY(-4px);
        border-color: #3b82f6;
        box-shadow: 0 12px 28px -6px rgba(0, 0, 0, 0.15), 0 0 15px rgba(59, 130, 246, 0.2);
    }
</style>
'''

HEADER_THEME_BTN = '''
<button id="themeToggleBtn" type="button" class="bg-gray-800 dark:bg-gray-800/80 light:bg-gray-200 text-gray-200 dark:text-gray-200 light:text-gray-800 p-2.5 rounded-xl border border-gray-700 dark:border-gray-700 light:border-gray-300 font-bold text-xs transition transform hover:scale-105 flex items-center gap-2">
    <span id="themeIcon">🌙</span> <span id="themeText" class="hidden sm:inline">Dark</span>
</button>
'''

THEME_JS = '''
<script>
    (function() {
        var root = document.documentElement;
        var savedTheme = localStorage.getItem('theme') || 'dark';
        
        function applyTheme(theme) {
            if (theme === 'dark') {
                root.classList.add('dark');
                root.classList.remove('light');
            } else {
                root.classList.remove('dark');
                root.classList.add('light');
            }
            localStorage.setItem('theme', theme);
            updateBtn(theme);
        }

        function updateBtn(theme) {
            var btnIcon = document.getElementById('themeIcon');
            var btnText = document.getElementById('themeText');
            if (btnIcon && btnText) {
                if (theme === 'dark') {
                    btnIcon.innerText = '🌙';
                    btnText.innerText = 'Dark';
                } else {
                    btnIcon.innerText = '☀️';
                    btnText.innerText = 'Light';
                }
            }
        }

        applyTheme(savedTheme);

        window.addEventListener('DOMContentLoaded', function() {
            var btn = document.getElementById('themeToggleBtn');
            if (btn) {
                updateBtn(savedTheme);
                btn.addEventListener('click', function() {
                    savedTheme = (savedTheme === 'dark') ? 'light' : 'dark';
                    applyTheme(savedTheme);
                });
            }
        });
    })();
</script>
'''

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
    ''' + ANIMATION_STYLES + THEME_JS + '''
</head>
<body class="bg-gray-100 dark:bg-gray-950 text-gray-900 dark:text-gray-100 min-h-screen transition-colors duration-300">
    <header class="bg-white dark:bg-slate-900/90 border-b border-gray-200 dark:border-gray-800 text-gray-900 dark:text-white shadow-md sticky top-0 z-40 backdrop-blur-md">
        <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <a href="/" class="text-2xl font-extrabold tracking-tight text-blue-600 dark:text-blue-400 hover:opacity-80 transition transform hover:scale-105">🏙️ ''' + SITE_NAME + '''</a>
            <div class="flex items-center space-x-3">
                ''' + HEADER_THEME_BTN + '''
                <a href="/client/login" class="bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-4 py-2.5 rounded-xl text-sm font-bold transition">🔑 Login / Dashboard</a>
                <a href="/register" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-xl text-sm font-bold shadow-lg btn-hover-effect">＋ Register Business</a>
            </div>
        </div>
    </header>
'''

FOOTER = '''
    <footer class="text-center py-8 text-sm text-gray-500 border-t border-gray-200 dark:border-gray-800/80 mt-20 animate-fade-in">
        <p>&copy; 2026 ''' + SITE_NAME + '''. All rights reserved.</p>
    </footer>
</body>
</html>
'''

def get_base_head(back_url="/", back_text="Back to Home"):
    return '''
<!DOCTYPE html>
<html lang="en" id="html-root" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>''' + SITE_NAME + '''</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏙️</text></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config = { darkMode: 'class' }</script>
    ''' + ANIMATION_STYLES + THEME_JS + '''
</head>
<body class="bg-gray-100 dark:bg-gray-950 text-gray-900 dark:text-gray-100 min-h-screen transition-colors duration-300">
    <header class="bg-white dark:bg-slate-900/90 border-b border-gray-200 dark:border-gray-800 text-gray-900 dark:text-white shadow-md sticky top-0 z-40 backdrop-blur-md">
        <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <a href="''' + back_url + '''" class="text-sm font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-600/10 border border-blue-200 dark:border-blue-500/20 px-4 py-2 rounded-xl hover:bg-blue-600 hover:text-white transition flex items-center gap-2 shadow-sm">
                ← ''' + back_text + '''
            </a>
            <div class="flex items-center space-x-3">
                ''' + HEADER_THEME_BTN + '''
                <a href="/client/login" class="bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-4 py-2.5 rounded-xl text-sm font-bold transition">🔑 Login / Dashboard</a>
                <a href="/register" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-xl text-sm font-bold shadow-lg btn-hover-effect">＋ Register Business</a>
            </div>
        </div>
    </header>
'''

@app.route('/')
def home():
    cards = ""
    for slug, cat in CATEGORIES.items():
        cards += '''
        <a href="/category/''' + slug + '''" class="bg-white dark:bg-gray-900/90 p-8 rounded-3xl border border-gray-200 dark:border-gray-800/80 card-hover-effect flex items-center space-x-5 group shadow-sm dark:shadow-xl">
            <span class="text-5xl p-4 bg-gray-100 dark:bg-gray-800/80 rounded-2xl group-hover:scale-110 transition-transform duration-300">''' + cat["icon"] + '''</span>
            <div>
                <h3 class="text-xl font-bold text-gray-800 dark:text-white group-hover:text-blue-500 dark:group-hover:text-blue-400 transition-colors duration-200">''' + cat["title"] + '''</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Browse listings →</p>
            </div>
        </a>
        '''
    
    html = HOME_HEAD + '''
    <section class="py-16 px-4 text-center animate-fade-in">
        <h2 class="text-4xl md:text-5xl font-black tracking-tight text-blue-600 dark:text-transparent dark:bg-clip-text dark:bg-gradient-to-r dark:from-blue-400 dark:via-indigo-300 dark:to-white">Discover Swat & Mingora Businesses</h2>
        <p class="text-gray-600 dark:text-gray-400 text-lg mt-3">Find verified local services instantly.</p>
    </section>
    <main class="max-w-7xl mx-auto px-4 pb-20 animate-fade-in">
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
    selected_subcat = request.args.get('subcat', '').strip()
    
    now = datetime.now()
    all_biz = [b for b in BUSINESSES.values() if b.get('category') == cat_slug and b.get('status') == 'approved' and b.get('expiry_date', now) >= now]
    filtered = []
    
    for b in all_biz:
        match_search = True
        match_subcat = True
        
        if search_query:
            doctors_str = " ".join([d.get('name', '') + " " + d.get('specialty', '') + " " + d.get('qualifications', '') for d in b.get('doctors', [])]).lower()
            if not (search_query in b.get('name', '').lower() or 
                    search_query in b.get('address', '').lower() or 
                    search_query in b.get('subcategory', '').lower() or 
                    search_query in doctors_str or
                    search_query in b.get('special_info', '').lower() or 
                    search_query in b.get('tests_dishes', '').lower()):
                match_search = False

        if selected_subcat:
            if b.get('subcategory', '').lower() != selected_subcat.lower():
                match_subcat = False

        if match_search and match_subcat:
            filtered.append(b)

    pills_html = f'<a href="/category/{cat_slug}?q={search_query}" class="px-4 py-2 rounded-xl text-xs font-bold transition btn-hover-effect ' + \
                 ('bg-blue-600 text-white shadow-md' if not selected_subcat else 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-700') + '">All</a>'
    
    for sc in cat['subcategories']:
        is_active = (selected_subcat.lower() == sc.lower())
        active_cls = 'bg-blue-600 text-white shadow-md' if is_active else 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-700'
        pills_html += f'<a href="/category/{cat_slug}?subcat={sc}&q={search_query}" class="px-4 py-2 rounded-xl text-xs font-bold transition btn-hover-effect {active_cls}">{sc}</a>'

    cards = ""
    for b in filtered:
        subcat_badge = '<span class="bg-indigo-100 dark:bg-indigo-600/20 text-indigo-700 dark:text-indigo-400 text-xs px-2.5 py-1 rounded-md font-semibold">' + b.get('subcategory', 'General') + '</span>' if b.get('subcategory') else ''
        cards += '''
        <a href="/business/''' + b['id'] + '''" class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800/80 overflow-hidden card-hover-effect flex flex-col justify-between group shadow-sm dark:shadow-lg">
            <img src="''' + b.get('image', 'https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=800&q=80') + '''" class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-500">
            <div class="p-6">
                <div class="mb-2">''' + subcat_badge + '''</div>
                <h3 class="text-xl font-bold text-gray-900 dark:text-white group-hover:text-blue-500 dark:group-hover:text-blue-400 transition-colors">''' + b['name'] + '''</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">📍 ''' + b['address'] + '''</p>
                <p class="text-xs text-blue-600 dark:text-blue-400 mt-2 font-bold">📞 ''' + b.get('phones', ['N/A'])[0] + '''</p>
                <span class="inline-block mt-4 text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-500/10 px-3 py-1.5 rounded-lg group-hover:bg-blue-600 group-hover:text-white transition">View Details →</span>
            </div>
        </a>
        '''
    if not cards:
        cards = '<div class="col-span-3 text-center py-20 text-gray-500 dark:text-gray-400"><p class="text-xl">No active or approved listings found matching your search.</p></div>'

    biz_json_data = json.dumps([{
        'id': b['id'],
        'name': b['name'],
        'address': b['address'],
        'subcategory': b.get('subcategory', '')
    } for b in all_biz])

    html = get_base_head(back_url="/", back_text="Back to Home") + '''
    <main class="max-w-7xl mx-auto px-4 py-12 animate-fade-in">
        <div class="mb-8 text-center">
            <span class="text-6xl inline-block animate-bounce">''' + cat['icon'] + '''</span>
            <h2 class="text-4xl font-extrabold mt-4 text-gray-900 dark:text-white">''' + cat['title'] + '''</h2>
            
            <div class="mt-6 max-w-xl mx-auto relative">
                <form method="GET" action="/category/''' + cat_slug + '''" class="flex gap-3">
                    <input type="hidden" name="subcat" value="''' + selected_subcat + '''">
                    <div class="relative w-full">
                        <input type="text" id="searchInput" name="q" value="''' + search_query + '''" placeholder="''' + cat['search_hint'] + '''" autocomplete="off" class="w-full px-5 py-3.5 rounded-2xl bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                        <div id="suggestionsDropdown" class="absolute left-0 right-0 top-full mt-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-2xl z-50 max-h-60 overflow-y-auto hidden"></div>
                    </div>
                    <button type="submit" class="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3.5 rounded-2xl font-semibold btn-hover-effect shadow-md">Search</button>
                </form>
            </div>

            <div class="mt-6 flex flex-wrap justify-center gap-2 max-w-4xl mx-auto">
                ''' + pills_html + '''
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            ''' + cards + '''
        </div>
    </main>

    <script>
        var categoryBusinesses = ''' + biz_json_data + ''';

        window.addEventListener('DOMContentLoaded', function() {
            var input = document.getElementById('searchInput');
            var dropdown = document.getElementById('suggestionsDropdown');

            if (!input || !dropdown) return;

            input.addEventListener('input', function() {
                var q = this.value.trim().toLowerCase();
                dropdown.innerHTML = '';
                
                if (q.length < 1) {
                    dropdown.classList.add('hidden');
                    return;
                }

                var matches = categoryBusinesses.filter(function(b) {
                    return b.name.toLowerCase().includes(q) || 
                           b.address.toLowerCase().includes(q) || 
                           b.subcategory.toLowerCase().includes(q);
                });

                if (matches.length > 0) {
                    matches.forEach(function(b) {
                        var div = document.createElement('div');
                        div.className = 'p-3 hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer flex justify-between items-center text-left border-b border-gray-100 dark:border-gray-800/50 last:border-0';
                        div.innerHTML = '<div><p class="font-bold text-sm text-gray-900 dark:text-white">' + b.name + '</p><p class="text-xs text-gray-500 dark:text-gray-400">📍 ' + b.address + '</p></div><span class="text-xs bg-blue-100 dark:bg-blue-600/20 text-blue-600 dark:text-blue-400 px-2 py-0.5 rounded-md font-semibold">' + b.subcategory + '</span>';
                        div.addEventListener('click', function() {
                            window.location.href = '/business/' + b.id;
                        });
                        dropdown.appendChild(div);
                    });
                    dropdown.classList.remove('hidden');
                } else {
                    dropdown.classList.add('hidden');
                }
            });

            document.addEventListener('click', function(e) {
                if (!input.contains(e.target) && !dropdown.contains(e.target)) {
                    dropdown.classList.add('hidden');
                }
            });
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
    client_auth_key = 'client_auth_' + str(b_id)
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
    category_back_url = f"/category/{b['category']}"
    
    if (b.get('status') != 'approved' or b.get('expiry_date', now) < now) and not is_admin and not is_client:
        html = get_base_head(back_url=category_back_url, back_text="Back to Category") + '''
        <main class="max-w-xl mx-auto px-4 py-20 text-center animate-fade-in">
            <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-10 shadow-xl space-y-4">
                <span class="text-6xl inline-block">🔒</span>
                <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Listing Inactive or Password Protected</h1>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Please enter the Client Password to unlock and view this listing.</p>
                
                <form method="POST" class="space-y-3 pt-2">
                    <input type="password" name="client_password" required placeholder="Enter Client Password" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-center text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-xl font-bold btn-hover-effect text-sm">Unlock Listing</button>
                </form>
                ''' + (f'<p class="text-red-500 text-xs font-semibold">{error_msg}</p>' if error_msg else '') + '''

                <div class="pt-4">
                    <a href="''' + category_back_url + '''" class="text-gray-500 dark:text-gray-400 hover:underline text-xs">Return to Category</a>
                </div>
            </div>
        </main>
        ''' + FOOTER
        return render_template_string(html)

    cat_meta = CATEGORIES.get(b['category'], {'info_title': 'Special Info', 'extra_title': 'Tests & Services'})
    doctors_data = b.get('doctors', [])
    
    doctors_cards_html = ""
    if doctors_data:
        for idx, doc in enumerate(doctors_data):
            appt_nums = doc.get('appt_numbers', ", ".join(b.get('phones', [])))
            quals = doc.get('qualifications', '')
            
            doc_json = json.dumps({
                'name': doc.get('name', ''),
                'specialty': doc.get('specialty', ''),
                'qualifications': quals,
                'appt_timing': doc.get('appt_timing', ''),
                'clinic_timing': doc.get('clinic_timing', ''),
                'room': doc.get('room', ''),
                'appt_numbers': appt_nums,
                'hospital_name': b['name'],
                'hospital_address': b['address'],
                'hospital_phones': ", ".join(b.get('phones', []))
            }).replace("'", "&#39;")
            
            quals_badge = f'<p class="text-[11px] text-gray-500 dark:text-gray-400 italic">🎓 {quals}</p>' if quals else ''
            
            doctors_cards_html += f'''
            <div onclick='openDoctorModal({doc_json})' class="doc-card-item bg-gray-50 dark:bg-gray-950 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 card-hover-effect space-y-2 cursor-pointer group">
                <div class="flex justify-between items-start">
                    <div>
                        <h4 class="text-base font-extrabold text-blue-600 dark:text-blue-400 group-hover:underline">{doc.get('name', 'N/A')}</h4>
                        <p class="text-xs font-semibold text-indigo-600 dark:text-indigo-400">{doc.get('specialty', 'Specialist')}</p>
                        {quals_badge}
                    </div>
                    <span class="bg-blue-100 dark:bg-blue-600/20 text-blue-700 dark:text-blue-400 text-[10px] px-2.5 py-1 rounded-full font-bold">View Info →</span>
                </div>
                <div class="pt-2 border-t border-gray-200 dark:border-gray-800/80 text-xs space-y-1 text-gray-700 dark:text-gray-300">
                    <p>🕒 <strong>Appt Timing:</strong> {doc.get('appt_timing', 'N/A')}</p>
                    <p>📅 <strong>Clinic Days:</strong> {doc.get('clinic_timing', 'N/A')}</p>
                    <p>🚪 <strong>Room / Block:</strong> {doc.get('room', 'N/A')}</p>
                    <p>📞 <strong>Appt Phone(s):</strong> <span class="text-blue-600 dark:text-blue-400 font-bold">{appt_nums}</span></p>
                    <p class="text-[11px] text-gray-500 dark:text-gray-400 pt-1">🏥 <strong>Hospital:</strong> {b['name']} ({b['address']})</p>
                </div>
            </div>
            '''
    else:
        doctors_cards_html = f'''<p class="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-line">{b.get('special_info', 'Not specified')}</p>'''

    tests_dishes = b.get('tests_dishes', 'Not specified')
    phones_list = b.get('phones', ['N/A'])
    phones_html = ", ".join([f'<a href="tel:{p}" class="text-blue-600 dark:text-white hover:underline font-bold">{p}</a>' for p in phones_list])

    gallery_imgs = b.get('images', [b.get('image')])
    gallery_html = ""
    for img_url in gallery_imgs:
        if img_url:
            gallery_html += f'<img src="{img_url}" class="w-full h-64 object-cover rounded-2xl border border-gray-200 dark:border-gray-800 hover:scale-105 transition duration-300 shadow-md">'

    html = get_base_head(back_url=category_back_url, back_text="Back to Category") + '''
    <div id="doctorModal" class="fixed inset-0 bg-black/60 dark:bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 md:p-8 max-w-md w-full shadow-2xl animate-modal space-y-4">
            <div class="flex justify-between items-start">
                <div class="flex items-center gap-3">
                    <span class="text-4xl p-2 bg-blue-50 dark:bg-blue-600/20 rounded-2xl">👨‍⚕️</span>
                    <div>
                        <h3 id="mDocName" class="text-xl font-black text-gray-900 dark:text-white">Dr. Name</h3>
                        <p id="mDocSpec" class="text-xs font-bold text-blue-600 dark:text-blue-400">Specialty</p>
                        <p id="mDocQuals" class="text-[11px] text-gray-500 dark:text-gray-400 italic">Qualifications</p>
                    </div>
                </div>
                <button type="button" onclick="closeDoctorModal()" class="text-gray-400 hover:text-gray-600 dark:hover:text-white text-xl font-bold bg-gray-100 dark:bg-gray-800 w-8 h-8 rounded-full flex items-center justify-center">×</button>
            </div>
            <div class="space-y-2 text-xs text-gray-700 dark:text-gray-300 pt-2 border-t border-gray-100 dark:border-gray-800">
                <p>🕒 <strong>Appointment Timing:</strong> <span id="mApptTiming" class="font-semibold text-gray-900 dark:text-white"></span></p>
                <p>📅 <strong>Clinic Days / Timing:</strong> <span id="mClinicTiming" class="font-semibold text-gray-900 dark:text-white"></span></p>
                <p>🚪 <strong>Room / Department:</strong> <span id="mRoom" class="font-semibold text-gray-900 dark:text-white"></span></p>
                <p>📞 <strong>Appointment Phone(s):</strong> <a id="mApptPhoneLink" href="#" class="text-blue-600 dark:text-blue-400 font-bold underline"></a></p>
            </div>
            <div class="bg-gray-50 dark:bg-gray-950 p-3 rounded-xl border border-gray-200 dark:border-gray-800 text-[11px] text-gray-600 dark:text-gray-400 space-y-1">
                <p>🏥 <strong id="mHospName"></strong></p>
                <p>📍 <span id="mHospAddress"></span></p>
            </div>
            <button type="button" onclick="closeDoctorModal()" class="w-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 py-2.5 rounded-xl font-bold text-xs">Close</button>
        </div>
    </div>

    <main class="max-w-5xl mx-auto px-4 py-12 animate-fade-in space-y-8">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 md:p-10 shadow-xl space-y-6">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-gray-100 dark:border-gray-800 pb-6">
                <div>
                    <span class="bg-blue-100 dark:bg-blue-600/20 text-blue-600 dark:text-blue-400 text-xs px-3 py-1 rounded-md font-bold uppercase tracking-wider">''' + b['category'] + '''</span>
                    <h1 class="text-3xl md:text-4xl font-black text-gray-900 dark:text-white mt-2">''' + b['name'] + '''</h1>
                    <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">📍 ''' + b['address'] + '''</p>
                </div>
                <div class="text-left md:text-right space-y-1">
                    <p class="text-xs text-gray-400">Contact Number(s)</p>
                    <p class="text-sm">📞 ''' + phones_html + '''</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                ''' + gallery_html + '''
            </div>

            <div class="space-y-4 pt-4 border-t border-gray-100 dark:border-gray-800">
                <h3 class="text-xl font-bold text-gray-900 dark:text-white">''' + cat_meta['info_title'] + '''</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    ''' + doctors_cards_html + '''
                </div>
            </div>

            <div class="space-y-2 pt-4 border-t border-gray-100 dark:border-gray-800">
                <h3 class="text-xl font-bold text-gray-900 dark:text-white">''' + cat_meta['extra_title'] + '''</h3>
                <p class="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-line bg-gray-50 dark:bg-gray-950 p-4 rounded-2xl border border-gray-200 dark:border-gray-800">''' + tests_dishes + '''</p>
            </div>
        </div>
    </main>

    <script>
        function openDoctorModal(doc) {
            document.getElementById('mDocName').innerText = doc.name;
            document.getElementById('mDocSpec').innerText = doc.specialty;
            document.getElementById('mDocQuals').innerText = doc.qualifications ? '🎓 ' + doc.qualifications : '';
            document.getElementById('mApptTiming').innerText = doc.appt_timing;
            document.getElementById('mClinicTiming').innerText = doc.clinic_timing;
            document.getElementById('mRoom').innerText = doc.room;
            
            var phoneLink = document.getElementById('mApptPhoneLink');
            phoneLink.innerText = doc.appt_numbers;
            phoneLink.href = 'tel:' + doc.appt_numbers.split(',')[0].trim();
            
            document.getElementById('mHospName').innerText = doc.hospital_name;
            document.getElementById('mHospAddress').innerText = doc.hospital_address;
            
            document.getElementById('doctorModal').classList.remove('hidden');
        }

        function closeDoctorModal() {
            document.getElementById('doctorModal').classList.add('hidden');
        }
    </script>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_msg = ""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        subcategory = request.form.get('subcategory', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        client_email = request.form.get('client_email', '').strip().lower()
        client_password = request.form.get('client_password', '').strip()
        tests_dishes = request.form.get('tests_dishes', '').strip()
        
        # Collect dynamic doctors / staff
        doc_names = request.form.getlist('doc_name')
        doc_specs = request.form.getlist('doc_spec')
        doc_quals = request.form.getlist('doc_qual')
        doc_appts = request.form.getlist('doc_appt')
        doc_clinics = request.form.getlist('doc_clinic')
        doc_rooms = request.form.getlist('doc_room')
        doc_phones = request.form.getlist('doc_phone')
        
        doctors_list = []
        for i in range(len(doc_names)):
            if doc_names[i].strip():
                doctors_list.append({
                    'name': doc_names[i].strip(),
                    'specialty': doc_specs[i].strip() if i < len(doc_specs) else '',
                    'qualifications': doc_quals[i].strip() if i < len(doc_quals) else '',
                    'appt_timing': doc_appts[i].strip() if i < len(doc_appts) else '',
                    'clinic_timing': doc_clinics[i].strip() if i < len(doc_clinics) else '',
                    'room': doc_rooms[i].strip() if i < len(doc_rooms) else '',
                    'appt_numbers': doc_phones[i].strip() if i < len(doc_phones) else phone
                })
        
        if name and category and client_email and client_password:
            new_id = str(len(BUSINESSES) + 1)
            BUSINESSES[new_id] = {
                'id': new_id,
                'category': category,
                'subcategory': subcategory,
                'name': name,
                'address': address,
                'phones': [phone] if phone else ['+92 300 0000000'],
                'image': 'https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=800&q=80',
                'images': ['https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=800&q=80'],
                'status': 'approved',
                'payment_method': 'Free Trial',
                'payment_ref': 'TRIAL-FREE',
                'payment_status': 'paid',
                'joining_date': datetime.now(),
                'expiry_date': datetime.now() + timedelta(days=30),
                'doctors': doctors_list,
                'special_info': f"{len(doctors_list)} Staff / Specialist(s) Registered",
                'tests_dishes': tests_dishes if tests_dishes else 'Services available.',
                'client_email': client_email,
                'client_password': client_password
            }
            session['client_logged_email'] = client_email
            return redirect(url_for('client_dashboard'))
        else:
            error_msg = "Please fill in all required fields."

    cats_options = "".join([f'<option value="{k}">{v["title"]}</option>' for k, v in CATEGORIES.items()])
    categories_json = json.dumps({k: v['subcategories'] for k, v in CATEGORIES.items()})

    html = get_base_head(back_url="/", back_text="Back to Home") + '''
    <main class="max-w-2xl mx-auto px-4 py-12 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6">
            <div class="text-center space-y-2">
                <span class="text-5xl inline-block">🚀</span>
                <h1 class="text-2xl font-black text-gray-900 dark:text-white">Register Your Business</h1>
                <p class="text-xs text-gray-500 dark:text-gray-400">Create an account with Email & Password to manage your listings.</p>
            </div>

            <form method="POST" class="space-y-6">
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Business Name *</label>
                    <input type="text" name="name" required placeholder="e.g. Swat Best Store" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Category *</label>
                        <select id="categorySelect" name="category" required onchange="updateSubcategories()" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white outline-none text-sm">
                            ''' + cats_options + '''
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Subcategory / Type *</label>
                        <select id="subcategorySelect" name="subcategory" required class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white outline-none text-sm">
                        </select>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Address / Location *</label>
                    <input type="text" name="address" required placeholder="e.g. Mingora Bazaar, Swat" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>

                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Phone Number *</label>
                    <input type="text" name="phone" required placeholder="e.g. +92 300 1234567" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>

                <!-- Dynamic Doctors / Staff Section -->
                <div class="pt-4 border-t border-gray-100 dark:border-gray-800 space-y-4">
                    <div class="flex justify-between items-center">
                        <label class="block text-sm font-extrabold text-blue-600 dark:text-blue-400">🩺 Doctors, Clinic & Timings</label>
                    </div>

                    <div id="doctorsContainer" class="space-y-4">
                        <div class="doc-entry bg-gray-50 dark:bg-gray-950 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 space-y-3 relative">
                            <button type="button" onclick="removeDoctor(this)" class="absolute top-3 right-3 text-red-500 bg-red-100 dark:bg-red-900/40 w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs">✕</button>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <input type="text" name="doc_name" placeholder="Doctor Name (Dr. Ahmad)" class="p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                                <input type="text" name="doc_spec" placeholder="Specialty (Cardiologist)" class="p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                            </div>
                            <div>
                                <input type="text" name="doc_qual" placeholder="Qualifications (MBBS, FCPS)" class="w-full p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                            </div>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <input type="text" name="doc_appt" placeholder="Appointment Timing (9 AM - 2 PM)" class="p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                                <input type="text" name="doc_clinic" placeholder="Clinic Timing (Mon-Sat, 9 AM - 5 PM)" class="p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                            </div>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <input type="text" name="doc_room" placeholder="Clinic / Room (Room 12, OPD Block)" class="p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                                <input type="text" name="doc_phone" placeholder="Appointment Phone Number(s)" class="p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                            </div>
                        </div>
                    </div>

                    <button type="button" onclick="addDoctorRow()" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-xl text-xs font-bold btn-hover-effect flex items-center gap-2 shadow-md">
                        + Add New Doctor
                    </button>
                </div>

                <!-- Tests & Services Section -->
                <div class="pt-4 border-t border-gray-100 dark:border-gray-800 space-y-2">
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300">🧪 Tests & Medical Services (Optional)</label>
                    <textarea name="tests_dishes" rows="3" placeholder="e.g. MRI, CT Scan, Blood Tests, Ultrasound, OPD Services..." class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm"></textarea>
                </div>

                <!-- Account Credentials Section -->
                <div class="pt-4 border-t border-gray-100 dark:border-gray-800 space-y-4">
                    <p class="text-xs font-extrabold text-blue-600 dark:text-blue-400">🔒 Account Credentials for Future Login</p>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Owner Email *</label>
                            <input type="email" name="client_email" required placeholder="owner@gmail.com" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Owner Password *</label>
                            <input type="password" name="client_password" required placeholder="Choose a secure password" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                        </div>
                    </div>
                </div>

                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3.5 rounded-xl font-bold btn-hover-effect text-sm shadow-lg">Register & Open Dashboard</button>
            </form>

            ''' + (f'<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-3 rounded-xl text-red-600 dark:text-red-400 text-xs text-center font-semibold">{error_msg}</div>' if error_msg else '') + '''
        </div>
    </main>

    <script>
        var categoriesData = ''' + categories_json + ''';

        function updateSubcategories() {
            var catSelect = document.getElementById('categorySelect');
            var subcatSelect = document.getElementById('subcategorySelect');
            var selectedCat = catSelect.value;
            
            subcatSelect.innerHTML = '';
            if (categoriesData[selectedCat]) {
                categoriesData[selectedCat].forEach(function(sub) {
                    var option = document.createElement('option');
                    option.value = sub;
                    option.text = sub;
                    subcatSelect.appendChild(option);
                });
            }
        }

        function addDoctorRow() {
            var container = document.getElementById('doctorsContainer');
            var div = document.createElement('div');
            div.className = 'doc-entry bg-gray-50 dark:bg-gray-950 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 space-y-3 relative mt-3';
            div.innerHTML = `
                <button type="button" onclick="removeDoctor(this)" class="absolute top-3 right-3 text-red-500 bg-red-100 dark:bg-red-900/40 w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs">✕</button>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input type="text" name="doc_name" placeholder="Doctor Name (Dr. Ahmad)" class="p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                    <input type="text" name="doc_spec" placeholder="Specialty (Cardiologist)" class="p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                </div>
                <div>
                    <input type="text" name="doc_qual" placeholder="Qualifications (MBBS, FCPS)" class="w-full p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input type="text" name="doc_appt" placeholder="Appointment Timing (9 AM - 2 PM)" class="p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                    <input type="text" name="doc_clinic" placeholder="Clinic Timing (Mon-Sat, 9 AM - 5 PM)" class="p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input type="text" name="doc_room" placeholder="Clinic / Room (Room 12, OPD Block)" class="p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                    <input type="text" name="doc_phone" placeholder="Appointment Phone Number(s)" class="p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none">
                </div>
            `;
            container.appendChild(div);
        }

        function removeDoctor(btn) {
            var row = btn.closest('.doc-entry');
            if (document.querySelectorAll('.doc-entry').length > 1) {
                row.remove();
            } else {
                row.querySelectorAll('input').forEach(input => input.value = '');
            }
        }

        window.addEventListener('DOMContentLoaded', function() {
            updateSubcategories();
        });
    </script>
    ''' + FOOTER
    return render_template_string(html)

# ==========================================
# CLIENT LOGIN & DASHBOARD ROUTES
# ==========================================

@app.route('/client/login', methods=['GET', 'POST'])
def client_login():
    error_msg = ""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        matched_biz = None
        for b in BUSINESSES.values():
            if b.get('client_email', '').lower() == email and b.get('client_password') == password:
                matched_biz = b
                break
                
        if matched_biz:
            session['client_logged_email'] = email
            return redirect(url_for('client_dashboard'))
        else:
            error_msg = "Invalid Email or Password!"

    html = get_base_head(back_url="/", back_text="Back to Home") + '''
    <main class="max-w-md mx-auto px-4 py-20 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6">
            <div class="text-center space-y-2">
                <span class="text-5xl inline-block">🔑</span>
                <h1 class="text-2xl font-black text-gray-900 dark:text-white">Owner Login</h1>
                <p class="text-xs text-gray-500 dark:text-gray-400">Access your business dashboard.</p>
            </div>

            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Email Address</label>
                    <input type="email" name="email" required placeholder="owner@gmail.com" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Password</label>
                    <input type="password" name="password" required placeholder="••••••••" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3.5 rounded-xl font-bold btn-hover-effect text-sm shadow-lg">Login to Dashboard</button>
            </form>
            ''' + (f'<p class="text-red-500 text-xs text-center font-semibold">{error_msg}</p>' if error_msg else '') + '''
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/client/dashboard')
def client_dashboard():
    client_email = session.get('client_logged_email')
    if not client_email:
        return redirect(url_for('client_login'))
        
    owner_businesses = [b for b in BUSINESSES.values() if b.get('client_email', '').lower() == client_email.lower()]
    
    cards_html = ""
    for b in owner_businesses:
        cards_html += f'''
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-md flex flex-col justify-between space-y-4">
            <div class="flex items-start gap-4">
                <img src="{b.get('image', '')}" class="w-20 h-20 object-cover rounded-xl border border-gray-200 dark:border-gray-800">
                <div class="space-y-1">
                    <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-md bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{b.get('status', 'pending')}</span>
                    <h3 class="text-lg font-bold text-gray-900 dark:text-white">{b['name']}</h3>
                    <p class="text-xs text-gray-500 dark:text-gray-400">📍 {b['address']}</p>
                </div>
            </div>
            <div class="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-800">
                <a href="/business/{b['id']}" class="text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline">View Listing →</a>
                <div class="flex items-center gap-2">
                    <a href="/client/edit/{b['id']}" class="bg-blue-50 dark:bg-blue-600/20 text-blue-600 dark:text-blue-400 px-3 py-1.5 rounded-xl text-xs font-bold transition hover:bg-blue-600 hover:text-white">Edit ✏️</a>
                    <a href="/client/delete/{b['id']}" onclick="return confirm('Delete this business?');" class="bg-red-50 dark:bg-red-600/20 text-red-600 dark:text-red-400 px-3 py-1.5 rounded-xl text-xs font-bold transition hover:bg-red-600 hover:text-white">Delete 🗑️</a>
                </div>
            </div>
        </div>
        '''

    if not cards_html:
        cards_html = '<div class="col-span-2 text-center py-12 text-gray-500"><p>No businesses found under this email.</p></div>'

    html = get_base_head(back_url="/", back_text="Back to Home") + '''
    <main class="max-w-5xl mx-auto px-4 py-12 animate-fade-in space-y-8">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white dark:bg-gray-900 p-6 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-xl">
            <div>
                <h1 class="text-2xl font-black text-gray-900 dark:text-white">Client Dashboard</h1>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Logged in as: <strong class="text-blue-600 dark:text-blue-400">''' + client_email + '''</strong></p>
            </div>
            <div class="flex items-center gap-3">
                <a href="/register" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-md btn-hover-effect">＋ Register Business</a>
                <a href="/client/logout" class="bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 hover:bg-red-600 hover:text-white px-4 py-2.5 rounded-xl text-xs font-bold transition">Logout</a>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            ''' + cards_html + '''
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/client/logout')
def client_logout():
    session.pop('client_logged_email', None)
    return redirect(url_for('home'))

@app.route('/client/edit/<b_id>', methods=['GET', 'POST'])
def client_edit_business(b_id):
    client_email = session.get('client_logged_email')
    if not client_email or b_id not in BUSINESSES:
        return redirect(url_for('client_login'))
        
    b = BUSINESSES[b_id]
    if b.get('client_email', '').lower() != client_email.lower():
        abort(403)

    if request.method == 'POST':
        b['name'] = request.form.get('name', b['name'])
        b['address'] = request.form.get('address', b['address'])
        b['phones'] = [p.strip() for p in request.form.get('phones', '').split(',') if p.strip()]
        return redirect(url_for('client_dashboard'))

    html = get_base_head(back_url="/client/dashboard", back_text="Back to Dashboard") + '''
    <main class="max-w-xl mx-auto px-4 py-12 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6">
            <h1 class="text-2xl font-black text-gray-900 dark:text-white">Edit Business: ''' + b['name'] + '''</h1>

            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Business Name</label>
                    <input type="text" name="name" value="''' + b['name'] + '''" required class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Address / Location</label>
                    <input type="text" name="address" value="''' + b['address'] + '''" required class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Phone Numbers</label>
                    <input type="text" name="phones" value="''' + ", ".join(b.get('phones', [])) + '''" required class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3.5 rounded-xl font-bold btn-hover-effect text-sm shadow-lg">Save Changes</button>
            </form>
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/client/delete/<b_id>')
def client_delete_business(b_id):
    client_email = session.get('client_logged_email')
    if not client_email or b_id not in BUSINESSES:
        return redirect(url_for('client_login'))
        
    b = BUSINESSES[b_id]
    if b.get('client_email', '').lower() == client_email.lower():
        del BUSINESSES[b_id]
        
    return redirect(url_for('client_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
