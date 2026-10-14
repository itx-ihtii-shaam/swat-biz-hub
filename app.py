"""SwatBiz Hub - Qualifications Field, Smart Admin Navigation & Client Dashboard Integration."""
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

def get_header_nav(extra_link=""):
    client_logged_in = session.get('client_logged_in_id')
    client_nav = f'<a href="/client/dashboard" class="bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 px-3.5 py-2 rounded-xl text-xs font-bold hover:bg-emerald-600 hover:text-white transition">📂 My Dashboard</a>' if client_logged_in else f'<a href="/client/login" class="bg-white/10 hover:bg-white/20 px-3.5 py-2 rounded-xl text-xs font-semibold transition">🔐 Client Login</a>'
    
    return f'''
    <header class="bg-white dark:bg-slate-900/90 border-b border-gray-200 dark:border-gray-800 text-gray-900 dark:text-white shadow-md sticky top-0 z-40 backdrop-blur-md">
        <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <div class="flex items-center gap-3">
                {extra_link}
                <a href="/" class="text-2xl font-extrabold tracking-tight text-blue-600 dark:text-blue-400 hover:opacity-80 transition transform hover:scale-105">🏙️ {SITE_NAME}</a>
            </div>
            <div class="flex items-center space-x-3">
                {client_nav}
                {HEADER_THEME_BTN}
                <a href="/register" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-xl text-sm font-bold shadow-lg btn-hover-effect">＋ Register Business</a>
            </div>
        </div>
    </header>
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
    ''' + get_header_nav()

FOOTER = '''
    <footer class="text-center py-8 text-sm text-gray-500 border-t border-gray-200 dark:border-gray-800/80 mt-20 animate-fade-in">
        <p>&copy; 2026 ''' + SITE_NAME + '''. All rights reserved.</p>
    </footer>
</body>
</html>
'''

def get_base_head(back_url="/", back_text="Back to Home"):
    extra = f'<a href="{back_url}" class="text-sm font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-600/10 border border-blue-200 dark:border-blue-500/20 px-3.5 py-2 rounded-xl hover:bg-blue-600 hover:text-white transition flex items-center gap-2 shadow-sm">← {back_text}</a>'
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
    ''' + get_header_nav(extra_link=extra)

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

@app.route('/client/login', methods=['GET', 'POST'])
def client_login():
    error = ""
    if request.method == 'POST':
        biz_id = request.form.get('biz_id', '').strip()
        password = request.form.get('password', '').strip()
        
        if biz_id in BUSINESSES and BUSINESSES[biz_id].get('client_password', 'client123') == password:
            session['client_logged_in_id'] = biz_id
            return redirect(url_for('client_dashboard'))
        else:
            error = "Invalid Business ID or Client Password!"

    html = get_base_head(back_url="/", back_text="Back to Home") + '''
    <main class="max-w-md mx-auto px-4 py-20 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6">
            <div class="text-center">
                <span class="text-5xl inline-block mb-2">🔐</span>
                <h1 class="text-2xl font-black text-gray-900 dark:text-white">Client Portal Login</h1>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Manage your business listing, edit details or update menu/doctors.</p>
            </div>

            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold mb-1 text-gray-700 dark:text-gray-300">Business ID number</label>
                    <input type="text" name="biz_id" required placeholder="e.g. 1, 2, 3..." class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm focus:border-blue-500 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold mb-1 text-gray-700 dark:text-gray-300">Client Password</label>
                    <input type="password" name="password" required placeholder="Enter your password" class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm focus:border-blue-500 outline-none">
                </div>
                ''' + (f'<p class="text-red-500 text-xs font-bold text-center">{error}</p>' if error else '') + '''
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3.5 rounded-xl text-sm btn-hover-effect shadow-md">Login to Dashboard</button>
            </form>
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/client/logout')
def client_logout():
    session.pop('client_logged_in_id', None)
    return redirect(url_for('home'))

@app.route('/client/dashboard')
def client_dashboard():
    biz_id = session.get('client_logged_in_id')
    if not biz_id or biz_id not in BUSINESSES:
        return redirect(url_for('client_login'))
    
    b = BUSINESSES[biz_id]
    
    html = get_base_head(back_url="/", back_text="Back to Home") + '''
    <main class="max-w-4xl mx-auto px-4 py-12 animate-fade-in space-y-8">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-xl flex flex-col md:flex-row justify-between items-center gap-6">
            <div class="flex items-center gap-4">
                <img src="''' + b.get('image', '') + '''" class="w-20 h-20 rounded-2xl object-cover border border-gray-200 dark:border-gray-700">
                <div>
                    <span class="text-xs uppercase font-bold tracking-widest text-blue-500">''' + b.get('category', '') + '''</span>
                    <h1 class="text-2xl font-black text-gray-900 dark:text-white">''' + b['name'] + '''</h1>
                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">📍 ''' + b['address'] + '''</p>
                </div>
            </div>
            <div class="flex items-center gap-3">
                <a href="/client/edit/''' + biz_id + '''" class="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-xl text-xs font-bold shadow-md btn-hover-effect">✏️ Edit Details</a>
                <a href="/client/logout" class="bg-red-500/10 text-red-500 border border-red-500/30 px-4 py-2.5 rounded-xl text-xs font-bold hover:bg-red-500 hover:text-white transition">Logout</a>
            </div>
        </div>

        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-xl space-y-6">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white">Listing Status & Info</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div class="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-2xl border border-gray-200 dark:border-gray-700/50">
                    <p class="text-xs text-gray-500 dark:text-gray-400">Status</p>
                    <p class="font-bold text-base mt-1 uppercase text-emerald-500">''' + b.get('status', 'pending') + '''</p>
                </div>
                <div class="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-2xl border border-gray-200 dark:border-gray-700/50">
                    <p class="text-xs text-gray-500 dark:text-gray-400">Contact Phones</p>
                    <p class="font-bold text-sm mt-1">''' + ", ".join(b.get('phones', [])) + '''</p>
                </div>
                <div class="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-2xl border border-gray-200 dark:border-gray-700/50">
                    <p class="text-xs text-gray-500 dark:text-gray-400">Listing ID</p>
                    <p class="font-bold text-base mt-1"># ''' + biz_id + '''</p>
                </div>
            </div>
            <div class="pt-4 flex items-center justify-between border-t border-gray-100 dark:border-gray-800">
                <a href="/business/''' + biz_id + '''" target="_blank" class="text-xs font-bold text-blue-500 hover:underline">👁️ View Public Page as Visitor →</a>
                <a href="/client/delete/''' + biz_id + '''" onclick="return confirm('Are you sure you want to delete your business listing?');" class="text-xs font-bold text-red-500 hover:underline">🗑️ Delete Listing</a>
            </div>
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/client/edit/<biz_id>', methods=['GET', 'POST'])
def client_edit(biz_id):
    logged_id = session.get('client_logged_in_id')
    if not logged_id or logged_id != biz_id or biz_id not in BUSINESSES:
        return redirect(url_for('client_login'))
    
    b = BUSINESSES[biz_id]
    
    if request.method == 'POST':
        b['name'] = request.form.get('name', b['name'])
        b['address'] = request.form.get('address', b['address'])
        phones = request.form.getlist('phone[]')
        if phones:
            b['phones'] = [p.strip() for p in phones if p.strip()]
        
        img_url = request.form.get('image_url', '').strip()
        if img_url:
            b['image'] = img_url
            b['images'] = [img_url]
        
        return redirect(url_for('client_dashboard'))

    html = get_base_head(back_url="/client/dashboard", back_text="Back to Dashboard") + '''
    <main class="max-w-2xl mx-auto px-4 py-12 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6">
            <h1 class="text-2xl font-black text-gray-900 dark:text-white">Edit Business Details</h1>
            
            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold mb-1 text-gray-700 dark:text-gray-300">Business Name</label>
                    <input type="text" name="name" value="''' + b['name'] + '''" required class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm outline-none focus:border-blue-500">
                </div>
                <div>
                    <label class="block text-xs font-bold mb-1 text-gray-700 dark:text-gray-300">Address Location</label>
                    <input type="text" name="address" value="''' + b['address'] + '''" required class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm outline-none focus:border-blue-500">
                </div>
                <div>
                    <label class="block text-xs font-bold mb-1 text-gray-700 dark:text-gray-300">Phone Numbers</label>
                    <input type="text" name="phone[]" value="''' + (b['phones'][0] if b.get('phones') else '') + '''" required class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm outline-none focus:border-blue-500">
                </div>
                <div>
                    <label class="block text-xs font-bold mb-1 text-gray-700 dark:text-gray-300">Image URL</label>
                    <input type="url" name="image_url" value="''' + b.get('image', '') + '''" class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm outline-none focus:border-blue-500">
                </div>
                <div class="flex gap-3 pt-4">
                    <a href="/client/dashboard" class="w-1/2 bg-gray-200 dark:bg-gray-800 text-center py-3 rounded-xl text-sm font-bold hover:bg-gray-300 dark:hover:bg-gray-700 transition">Cancel</a>
                    <button type="submit" class="w-1/2 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl text-sm shadow-md">Save Changes</button>
                </div>
            </form>
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/client/delete/<biz_id>')
def client_delete(biz_id):
    logged_id = session.get('client_logged_in_id')
    if not logged_id or logged_id != biz_id or biz_id not in BUSINESSES:
        return redirect(url_for('client_login'))
    
    BUSINESSES.pop(biz_id, None)
    session.pop('client_logged_in_id', None)
    return redirect(url_for('home'))

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
                <button type="button" onclick="closeDoctorModal()" class="text-gray-400 hover:text-gray-600 dark:hover:text-white text-xl font-bold bg-gray-100 dark:bg-gray-800 w-8 h-8 rounded-full flex items-center justify-center">✕</button>
            </div>

            <div class="space-y-3 pt-2 text-xs text-gray-700 dark:text-gray-300 border-t border-gray-100 dark:border-gray-800">
                <div class="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-xl border border-gray-200 dark:border-gray-700/50">
                    <p class="font-bold text-gray-500 dark:text-gray-400 mb-1">🏥 Hospital / Clinic Location:</p>
                    <p id="mDocHospital" class="font-extrabold text-sm text-gray-900 dark:text-white">Hospital Name</p>
                    <p id="mDocAddress" class="text-gray-600 dark:text-gray-400">Address Location</p>
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div class="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-xl border border-gray-200 dark:border-gray-700/50">
                        <p class="font-bold text-gray-500 dark:text-gray-400 mb-1">🕒 Appt Timing:</p>
                        <p id="mDocAppt" class="font-bold text-gray-900 dark:text-white">9 AM - 2 PM</p>
                    </div>
                    <div class="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-xl border border-gray-200 dark:border-gray-700/50">
                        <p class="font-bold text-gray-500 dark:text-gray-400 mb-1">📅 Clinic Days:</p>
                        <p id="mDocClinic" class="font-bold text-gray-900 dark:text-white">Mon-Sat</p>
                    </div>
                </div>
                <div class="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-xl border border-gray-200 dark:border-gray-700/50">
                    <p class="font-bold text-gray-500 dark:text-gray-400 mb-1">🚪 Room / OPD Block:</p>
                    <p id="mDocRoom" class="font-bold text-gray-900 dark:text-white">Room 12</p>
                </div>
                <div class="bg-blue-50 dark:bg-blue-600/10 p-3 rounded-xl border border-blue-200 dark:border-blue-500/20">
                    <p class="font-bold text-blue-600 dark:text-blue-400 mb-1">📞 Appointment Phone(s):</p>
                    <p id="mDocPhones" class="font-extrabold text-sm text-gray-900 dark:text-white">+92 300...</p>
                </div>
            </div>
            <button type="button" onclick="closeDoctorModal()" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl text-xs shadow-md">Close Window</button>
        </div>
    </div>

    <main class="max-w-5xl mx-auto px-4 py-10 animate-fade-in space-y-8">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div class="space-y-2">
                <span class="bg-blue-100 dark:bg-blue-600/20 text-blue-700 dark:text-blue-400 text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider">''' + b.get('subcategory', 'General') + '''</span>
                <h1 class="text-3xl font-black text-gray-900 dark:text-white">''' + b['name'] + '''</h1>
                <p class="text-sm text-gray-600 dark:text-gray-400">📍 ''' + b['address'] + '''</p>
            </div>
            <div class="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-2xl border border-gray-200 dark:border-gray-700/50 text-right space-y-1">
                <p class="text-xs text-gray-500 dark:text-gray-400">Direct Phone(s)</p>
                <p class="text-sm font-black text-blue-600 dark:text-blue-400">''' + phones_html + '''</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div class="lg:col-span-2 space-y-8">
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 md:p-8 shadow-xl space-y-4">
                    <h3 class="text-xl font-black text-gray-900 dark:text-white border-b border-gray-100 dark:border-gray-800 pb-3">''' + cat_meta['info_title'] + '''</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        ''' + doctors_cards_html + '''
                    </div>
                </div>

                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 md:p-8 shadow-xl space-y-4">
                    <h3 class="text-xl font-black text-gray-900 dark:text-white border-b border-gray-100 dark:border-gray-800 pb-3">''' + cat_meta['extra_title'] + '''</h3>
                    <p class="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-line">''' + tests_dishes + '''</p>
                </div>
            </div>

            <div class="space-y-6">
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 shadow-xl space-y-4">
                    <h3 class="text-lg font-bold text-gray-900 dark:text-white">Photo Gallery</h3>
                    <div class="space-y-3">
                        ''' + gallery_html + '''
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        function openDoctorModal(doc) {
            document.getElementById('mDocName').innerText = doc.name;
            document.getElementById('mDocSpec').innerText = doc.specialty;
            document.getElementById('mDocQuals').innerText = doc.qualifications || '';
            document.getElementById('mDocHospital').innerText = doc.hospital_name;
            document.getElementById('mDocAddress').innerText = doc.hospital_address;
            document.getElementById('mDocAppt').innerText = doc.appt_timing || 'N/A';
            document.getElementById('mDocClinic').innerText = doc.clinic_timing || 'N/A';
            document.getElementById('mDocRoom').innerText = doc.room || 'N/A';
            document.getElementById('mDocPhones').innerText = doc.appt_numbers || doc.hospital_phones;
            document.getElementById('doctorModal').classList.remove('hidden');
        }

        function closeDoctorModal() {
            document.getElementById('doctorModal').classList.add('hidden');
        }
    </script>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/register', methods=['GET', 'POST'])
def register_business():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        address = request.form.get('address', '').strip()
        phones = request.form.getlist('phone[]')
        phones = [p.strip() for p in phones if p.strip()]
        
        image_url = request.form.get('image_url', '').strip()
        image = image_url if image_url else 'https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=800&q=80'
        
        doc_names = request.form.getlist('doc_name[]')
        doc_specs = request.form.getlist('doc_spec[]')
        doc_quals = request.form.getlist('doc_quals[]')
        doc_app_times = request.form.getlist('doc_app_time[]')
        doc_clinic_times = request.form.getlist('doc_clinic_time[]')
        doc_clinics = request.form.getlist('doc_clinic[]')
        
        doctors = []
        for i in range(len(doc_names)):
            if doc_names[i].strip():
                doctors.append({
                    'name': doc_names[i].strip(),
                    'specialty': doc_specs[i].strip() if i < len(doc_specs) else '',
                    'qualifications': doc_quals[i].strip() if i < len(doc_quals) else '',
                    'appt_timing': doc_app_times[i].strip() if i < len(doc_app_times) else '',
                    'clinic_timing': doc_clinic_times[i].strip() if i < len(doc_clinic_times) else '',
                    'room': doc_clinics[i].strip() if i < len(doc_clinics) else '',
                    'appt_numbers': ", ".join(phones)
                })

        item_names = request.form.getlist('item_name[]')
        item_prices = request.form.getlist('item_price[]')
        item_offers = request.form.getlist('item_offer[]')
        
        tests_list = []
        for i in range(len(item_names)):
            if item_names[i].strip():
                part = item_names[i].strip()
                if i < len(item_prices) and item_prices[i].strip():
                    part += f" (Rs. {item_prices[i].strip()})"
                if i < len(item_offers) and item_offers[i].strip():
                    part += f" - {item_offers[i].strip()}"
                tests_list.append(part)
        
        tests_dishes = ", ".join(tests_list) if tests_list else "General Services Available"
        
        new_id = str(len(BUSINESSES) + 1)
        BUSINESSES[new_id] = {
            'id': new_id,
            'category': category,
            'subcategory': 'General',
            'name': name,
            'address': address,
            'phones': phones if phones else ['+92 946 0000000'],
            'image': image,
            'images': [image],
            'status': 'pending',
            'payment_method': 'Free Trial',
            'payment_ref': 'TRIAL-FREE',
            'payment_status': 'paid',
            'joining_date': datetime.now(),
            'expiry_date': datetime.now() + timedelta(days=30),
            'doctors': doctors,
            'special_info': ", ".join([d['name'] + " (" + d['specialty'] + ")" for d in doctors]) if doctors else '',
            'tests_dishes': tests_dishes,
            'client_password': 'client123'
        }
        
        session['client_logged_in_id'] = new_id
        return redirect(url_for('client_dashboard'))

    html = get_base_head(back_url="/", back_text="Back to Home") + '''
    <main class="max-w-3xl mx-auto px-4 py-12 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 md:p-10 shadow-2xl space-y-6">
            <div class="text-center">
                <h1 class="text-3xl font-black text-gray-900 dark:text-white">Register Your Business</h1>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Get listed instantly with a 30-day free trial!</p>
            </div>

            <form method="POST" class="space-y-6">
                <div>
                    <label class="block text-xs font-bold mb-1 text-gray-700 dark:text-gray-300">Business Name</label>
                    <input type="text" name="name" required placeholder="e.g. Al-Shifa Hospital or City Mart" class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm outline-none focus:border-blue-500">
                </div>

                <div>
                    <label class="block text-xs font-bold mb-1 text-gray-700 dark:text-gray-300">Category</label>
                    <select name="category" class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm outline-none focus:border-blue-500 cursor-pointer">
                        ''' + "".join([f'<option value="{slug}">{cat["icon"]} {cat["title"]}</option>' for slug, cat in CATEGORIES.items()]) + '''
                    </select>
                </div>

                <div>
                    <label class="block text-xs font-bold mb-1 text-gray-700 dark:text-gray-300">Address / Location</label>
                    <input type="text" name="address" required placeholder="e.g. Mingora, Swat" class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm outline-none focus:border-blue-500">
                </div>

                <div>
                    <label class="block text-xs font-bold mb-1 text-gray-700 dark:text-gray-300">Phone Number</label>
                    <input type="text" name="phone[]" required placeholder="+92 946 XXXXXXX" class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm outline-none focus:border-blue-500">
                </div>

                <div>
                    <label class="block text-xs font-bold mb-1 text-gray-700 dark:text-gray-300">Image URL</label>
                    <input type="url" name="image_url" placeholder="https://images.unsplash.com/..." class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm outline-none focus:border-blue-500">
                </div>

                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-2xl text-base btn-hover-effect shadow-xl">Submit & Activate Free Listing</button>
            </form>
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
        return redirect(url_for('admin_panel'))
    
    if not session.get('admin_logged_in'):
        html = get_base_head(back_url="/", back_text="Back to Home") + '''
        <main class="max-w-md mx-auto px-4 py-20 animate-fade-in">
            <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6 text-center">
                <span class="text-5xl inline-block">🛡️</span>
                <h1 class="text-2xl font-black text-gray-900 dark:text-white">Admin Login</h1>
                <form method="POST" class="space-y-4">
                    <input type="password" name="password" required placeholder="Enter Admin Password" class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm text-center outline-none focus:border-blue-500">
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl text-sm shadow-md">Login to Admin</button>
                </form>
            </div>
        </main>
        ''' + FOOTER
        return render_template_string(html)

    rows = ""
    for b_id, biz in BUSINESSES.items():
        rows += f'''
        <tr class="border-b border-gray-100 dark:border-gray-800">
            <td class="py-4 px-4 font-semibold flex items-center space-x-3">
                <img src="{biz.get('image', '')}" class="w-10 h-10 rounded-lg object-cover">
                <a href="/business/{biz['id']}" class="hover:text-blue-500">{biz['name']}</a>
            </td>
            <td class="py-4 px-4 uppercase text-xs font-bold text-gray-500">{biz.get('category', '')}</td>
            <td class="py-4 px-4">
                <span class="px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300">{biz.get('status', 'active').capitalize()}</span>
            </td>
            <td class="py-4 px-4 text-gray-600 dark:text-gray-400">''' + (biz.get('phones', [''])[0]) + '''</td>
        </tr>
        '''

    html = '''
    <!DOCTYPE html>
    <html lang="en" id="html-root" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Panel - ''' + SITE_NAME + '''</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>tailwind.config = { darkMode: 'class' }</script>
    </main>
    </head>
    <body class="bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 min-h-screen">
        <header class="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white shadow-xl">
            <div class="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
                <h1 class="text-2xl font-extrabold"><a href="/">🛡️ Admin Panel</a></h1>
                <a href="/" class="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-xl text-sm font-semibold transition">← View Website</a>
            </div>
        </header>

        <main class="max-w-6xl mx-auto px-4 py-10 space-y-10">
            <div class="bg-white dark:bg-gray-900 p-8 rounded-3xl shadow-xl border border-gray-100 dark:border-gray-800">
                <h2 class="text-2xl font-bold mb-6">All Registered Businesses</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="border-b border-gray-200 dark:border-gray-800 text-gray-400 text-sm">
                                <th class="py-3 px-4">Business Name</th>
                                <th class="py-3 px-4">Category</th>
                                <th class="py-3 px-4">Status</th>
                                <th class="py-3 px-4">Phone</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                            ''' + rows + '''
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
