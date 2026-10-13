"""SwatBiz Hub - Admin Navigation Fixed to Admin Dashboard."""
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
                'appt_timing': '9:00 AM - 2:00 PM',
                'clinic_timing': 'Mon - Sat (9 AM - 5 PM)',
                'room': 'OPD Block - Room 12',
                'appt_numbers': '+92 300 9240001, +92 946 9240123'
            },
            {
                'name': 'Dr. Ayesha Khan',
                'specialty': 'Pediatrician',
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
            doctors_str = " ".join([d.get('name', '') + " " + d.get('specialty', '') for d in b.get('doctors', [])]).lower()
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
            doc_json = json.dumps({
                'name': doc.get('name', ''),
                'specialty': doc.get('specialty', ''),
                'appt_timing': doc.get('appt_timing', ''),
                'clinic_timing': doc.get('clinic_timing', ''),
                'room': doc.get('room', ''),
                'appt_numbers': appt_nums,
                'hospital_name': b['name'],
                'hospital_address': b['address'],
                'hospital_phones': ", ".join(b.get('phones', []))
            }).replace("'", "&#39;")
            
            doctors_cards_html += f'''
            <div onclick='openDoctorModal({doc_json})' class="doc-card-item bg-gray-50 dark:bg-gray-950 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 card-hover-effect space-y-2 cursor-pointer group">
                <div class="flex justify-between items-start">
                    <div>
                        <h4 class="text-base font-extrabold text-blue-600 dark:text-blue-400 group-hover:underline">{doc.get('name', 'N/A')}</h4>
                        <p class="text-xs font-semibold text-indigo-600 dark:text-indigo-400">{doc.get('specialty', 'Specialist')}</p>
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
                        <p class="font-bold text-gray-500 dark:text-gray-400 mb-0.5">🕒 Appt Timing:</p>
                        <p id="mDocAppt" class="font-semibold text-gray-900 dark:text-white">9 AM - 2 PM</p>
                    </div>
                    <div class="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-xl border border-gray-200 dark:border-gray-700/50">
                        <p class="font-bold text-gray-500 dark:text-gray-400 mb-0.5">📅 Clinic Days:</p>
                        <p id="mDocDays" class="font-semibold text-gray-900 dark:text-white">Mon - Sat</p>
                    </div>
                </div>

                <div class="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-xl border border-gray-200 dark:border-gray-700/50">
                    <p class="font-bold text-gray-500 dark:text-gray-400 mb-0.5">🚪 Room / Location:</p>
                    <p id="mDocRoom" class="font-semibold text-gray-900 dark:text-white">Room 12, OPD Block</p>
                </div>

                <div class="bg-blue-50 dark:bg-blue-600/10 p-3 rounded-xl border border-blue-200 dark:border-blue-500/20 flex flex-col gap-1">
                    <span class="font-bold text-blue-600 dark:text-blue-400">📞 Doctor / Appointment Number(s):</span>
                    <span id="mDocApptNums" class="font-bold text-gray-900 dark:text-white text-sm">Numbers</span>
                </div>
            </div>

            <button type="button" onclick="closeDoctorModal()" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-xl font-bold btn-hover-effect text-xs shadow-lg">Close Details</button>
        </div>
    </div>

    <main class="max-w-4xl mx-auto px-4 py-12 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl overflow-hidden shadow-xl space-y-6 p-8">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                ''' + gallery_html + '''
            </div>

            <div>
                <div class="flex items-center gap-3 mb-2">
                    <span class="bg-blue-100 dark:bg-blue-600/20 text-blue-700 dark:text-blue-400 text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider">Verified Listing</span>
                    <span class="bg-indigo-100 dark:bg-indigo-600/20 text-indigo-700 dark:text-indigo-400 text-xs px-3 py-1 rounded-full font-semibold">''' + b.get('subcategory', 'General') + '''</span>
                </div>
                <h1 class="text-3xl md:text-4xl font-black mt-3 text-gray-900 dark:text-white">''' + b['name'] + '''</h1>
                <p class="text-gray-600 dark:text-gray-400 mt-1 text-base">📍 ''' + b['address'] + '''</p>
                <div class="mt-4 inline-flex items-center gap-2 bg-blue-50 dark:bg-blue-600/10 border border-blue-200 dark:border-blue-500/20 px-4 py-2.5 rounded-xl">
                    <span class="text-blue-600 dark:text-blue-400 text-sm font-bold">📞 Hospital Landline / Main Numbers:</span>
                    <span class="text-sm">''' + phones_html + '''</span>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-gray-200 dark:border-gray-800">
                <div class="bg-gray-50 dark:bg-gray-800/50 p-6 rounded-2xl border border-gray-200 dark:border-gray-700/50 card-hover-effect space-y-3">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                        <h3 class="text-lg font-bold text-blue-600 dark:text-blue-400">''' + cat_meta['info_title'] + '''</h3>
                        <input type="text" id="docSearchInput" placeholder="🔍 Search Doctor..." class="px-3 py-1.5 rounded-xl bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect w-full sm:w-40">
                    </div>

                    <div id="doctorsContainer" class="space-y-3">
                        ''' + doctors_cards_html + '''
                    </div>
                </div>
                
                <div class="bg-gray-50 dark:bg-gray-800/50 p-6 rounded-2xl border border-gray-200 dark:border-gray-700/50 card-hover-effect">
                    <h3 class="text-lg font-bold text-emerald-600 dark:text-emerald-400 mb-2">''' + cat_meta['extra_title'] + '''</h3>
                    <p class="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-line">''' + tests_dishes + '''</p>
                </div>
            </div>

            <div class="pt-4 border-t border-gray-200 dark:border-gray-800 flex justify-between items-center">
                <span class="text-xs text-gray-500">🔒 Secure Client Access Active</span>
                <a href="''' + category_back_url + '''" class="bg-blue-600 text-white hover:bg-blue-500 px-5 py-2.5 rounded-xl text-sm font-semibold transition transform hover:-translate-x-1 shadow-md">← Back to Category</a>
            </div>
        </div>
    </main>

    <script>
        function openDoctorModal(doc) {
            document.getElementById('mDocName').innerText = doc.name || 'N/A';
            document.getElementById('mDocSpec').innerText = doc.specialty || 'Specialist';
            document.getElementById('mDocHospital').innerText = doc.hospital_name || 'N/A';
            document.getElementById('mDocAddress').innerText = '📍 ' + (doc.hospital_address || 'N/A');
            document.getElementById('mDocAppt').innerText = doc.appt_timing || 'N/A';
            document.getElementById('mDocDays').innerText = doc.clinic_timing || 'N/A';
            document.getElementById('mDocRoom').innerText = doc.room || 'N/A';
            
            var rawApptNums = doc.appt_numbers || doc.hospital_phones || 'N/A';
            var numArr = rawApptNums.split(',');
            var linksHtml = numArr.map(function(num) {
                var clean = num.trim();
                return '<a href="tel:' + clean + '" class="hover:underline text-blue-600 dark:text-blue-400 font-bold block">' + clean + '</a>';
            }).join('');

            document.getElementById('mDocApptNums').innerHTML = linksHtml;

            var modal = document.getElementById('doctorModal');
            if (modal) modal.classList.remove('hidden');
        }

        function closeDoctorModal() {
            var modal = document.getElementById('doctorModal');
            if (modal) modal.classList.add('hidden');
        }

        window.addEventListener('DOMContentLoaded', function() {
            var docInput = document.getElementById('docSearchInput');
            if (docInput) {
                docInput.addEventListener('input', function() {
                    var val = this.value.toLowerCase().trim();
                    var cards = document.querySelectorAll('.doc-card-item');
                    cards.forEach(function(card) {
                        var txt = card.innerText.toLowerCase();
                        if (txt.includes(val)) {
                            card.style.display = 'block';
                        } else {
                            card.style.display = 'none';
                        }
                    });
                });
            }
        });
    </script>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/register', methods=['GET', 'POST'])
def register_business():
    if request.method == 'POST':
        b_id = str(len(BUSINESSES) + 1)
        
        phones = request.form.getlist('phones[]')
        clean_phones = [p.strip() for p in phones if p.strip()]

        names = request.form.getlist('repeater_col1[]')
        col2_vals = request.form.getlist('repeater_col2[]')
        col3_vals = request.form.getlist('repeater_col3[]')
        col4_vals = request.form.getlist('repeater_col4[]')
        col5_vals = request.form.getlist('repeater_col5[]')
        col6_vals = request.form.getlist('repeater_col6[]')

        doctors_list = []
        formatted_repeater_list = []
        for i in range(len(names)):
            if names[i].strip():
                doc_obj = {
                    'name': names[i].strip(),
                    'specialty': col2_vals[i].strip() if i < len(col2_vals) else 'N/A',
                    'appt_timing': col3_vals[i].strip() if i < len(col3_vals) else 'N/A',
                    'clinic_timing': col4_vals[i].strip() if i < len(col4_vals) else 'N/A',
                    'room': col5_vals[i].strip() if i < len(col5_vals) else 'N/A',
                    'appt_numbers': col6_vals[i].strip() if i < len(col6_vals) else ', '.join(clean_phones)
                }
                doctors_list.append(doc_obj)
                
                entry_str = "• " + names[i].strip()
                if i < len(col2_vals) and col2_vals[i].strip(): entry_str += " (" + col2_vals[i].strip() + ")"
                formatted_repeater_list.append(entry_str)

        combined_repeater_text = "\n".join(formatted_repeater_list) if formatted_repeater_list else request.form.get('special_info', 'N/A')
        
        subcat = request.form.get('subcategory', '').strip()
        if not subcat:
            subcat = 'General'

        img_urls = [url.strip() for url in request.form.getlist('image_urls[]') if url.strip()]
        primary_img = img_urls[0] if img_urls else 'https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=800&q=80'

        BUSINESSES[b_id] = {
            'id': b_id,
            'category': request.form.get('category'),
            'subcategory': subcat,
            'name': request.form.get('name'),
            'address': request.form.get('address'),
            'phones': clean_phones if clean_phones else ['N/A'],
            'image': primary_img,
            'images': img_urls if img_urls else [primary_img],
            'doctors': doctors_list,
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

    subcat_json_data = json.dumps({k: v['subcategories'] for k, v in CATEGORIES.items()})

    html = get_base_head(back_url="/", back_text="Back to Home") + '''
    <div id="confirmModal" class="fixed inset-0 bg-black/60 dark:bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center hidden">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 md:p-8 max-w-sm w-full mx-4 shadow-2xl animate-modal text-center space-y-4">
            <div class="w-14 h-14 bg-red-100 dark:bg-red-500/10 text-red-600 dark:text-red-500 rounded-2xl flex items-center justify-center mx-auto text-2xl font-bold">⚠️</div>
            <div>
                <h3 class="text-xl font-bold text-gray-900 dark:text-white">Delete Entry?</h3>
                <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">Are you sure you want to remove this entry? This action cannot be undone.</p>
            </div>
            <div class="flex gap-3 pt-2">
                <button type="button" id="cancelDeleteBtn" class="w-1/2 bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700 py-3 rounded-xl font-bold text-xs transition btn-hover-effect">Cancel</button>
                <button type="button" id="confirmDeleteBtn" class="w-1/2 bg-red-600 hover:bg-red-500 text-white py-3 rounded-xl font-bold text-xs transition btn-hover-effect shadow-lg">Yes, Delete</button>
            </div>
        </div>
    </div>

    <main class="max-w-3xl mx-auto px-4 py-12 animate-fade-in">
        <div class="text-center mb-8">
            <h2 class="text-3xl font-black tracking-tight text-gray-900 dark:text-white">Register Business</h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Enjoy 2 Months Free Trial upon registration!</p>
        </div>

        <form method="POST" class="space-y-5 bg-white dark:bg-gray-900/90 p-8 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-xl">
            <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-400 mb-1">Business / Entity Name *</label>
                <input type="text" name="name" required placeholder="Name (e.g. Saidu Hospital / Khyber Restaurant)" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-400 mb-1">Category *</label>
                    <select name="category" id="categorySelect" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">''' + opts + '''</select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-400 mb-1">Subcategory (Optional)</label>
                    <select name="subcategory" id="subcategorySelect" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white input-hover-effect outline-none text-sm"></select>
                </div>
            </div>

            <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-400 mb-1">Address *</label>
                <input type="text" name="address" required placeholder="Address (e.g. Saidu Sharif, Mingora Swat)" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
            </div>

            <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-400 mb-1">Main Phone Number(s) *</label>
                <div id="phonesContainer" class="space-y-2">
                    <div class="flex gap-2">
                        <input type="text" name="phones[]" required placeholder="e.g. +92 946 9240123" class="w-full p-3 bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white rounded-xl text-xs input-hover-effect outline-none">
                    </div>
                </div>
                <button type="button" id="addPhoneBtn" class="mt-2 text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline">+ Add Another Phone Number</button>
            </div>
            
            <div class="border-t border-gray-200 dark:border-gray-800 pt-4">
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-400 mb-1">🔒 Client Password * (For editing and secure access)</label>
                <input type="password" name="client_password" required placeholder="Enter secret password" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
            </div>

            <div class="border-t border-gray-200 dark:border-gray-800 pt-4">
                <label class="block text-sm font-bold text-blue-600 dark:text-blue-400 mb-3" id="repeaterTitle">🩺 Doctors, Clinic & Timings</label>
                <div id="repeaterContainer" class="space-y-3"></div>
                <button type="button" id="addRowBtn" class="mt-3 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs px-5 py-3 rounded-xl btn-hover-effect inline-flex items-center shadow-lg">
                    + Add New Entry
                </button>
            </div>

            <div class="border-t border-gray-200 dark:border-gray-800 pt-4">
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-400 mb-1" id="extraTitle">Tests & Medical Services (Optional)</label>
                <textarea name="tests_dishes" id="dishesField" placeholder="Enter details..." class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white input-hover-effect outline-none text-sm" rows="2"></textarea>
            </div>

            <div class="border-t border-gray-200 dark:border-gray-800 pt-4">
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-400 mb-1">Business Images (Optional - Enter URLs)</label>
                <div id="imagesContainer" class="space-y-2">
                    <input type="url" name="image_urls[]" placeholder="Image URL (e.g. https://images.unsplash.com/...)" class="w-full p-3 bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white rounded-xl text-xs input-hover-effect outline-none">
                </div>
                <button type="button" id="addImageBtn" class="mt-2 text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline">+ Add Another Image URL</button>
            </div>

            <div class="border-t border-gray-200 dark:border-gray-800 pt-4">
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-400 mb-1">Payment Plan (Free 2 Months Active)</label>
                <select name="payment_method" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                    <option value="Free Trial">2 Months Free Trial (Active)</option>
                    <option value="EasyPaisa">EasyPaisa</option>
                    <option value="JazzCash">JazzCash</option>
                    <option value="Bank Transfer">Bank Transfer</option>
                </select>
            </div>

            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3.5 rounded-xl font-bold btn-hover-effect shadow-xl text-sm">Submit Business Listing</button>
        </form>
    </main>

    <script>
        var subcategoriesData = ''' + subcat_json_data + ''';

        var categoryRowConfigs = {
            'hospitals': {
                title: '🩺 Doctors, Clinic & Timings',
                addBtnText: '+ Add New Doctor',
                extraTitle: '🔬 Tests & Medical Services (Optional)',
                extraPlaceholder: 'e.g. MRI, CT Scan, Blood Tests, Ultrasound, OPD Services...',
                c1: 'Doctor Name (Dr. Ahmad)', c2: 'Specialty (Cardiologist)',
                c3: 'Appointment Timing (9 AM - 2 PM)', c4: 'Clinic Timing (Mon-Sat, 9 AM - 5 PM)',
                c5: 'Clinic / Room (Room 12, OPD Block)',
                c6: 'Appointment Phone Number(s) (e.g. +92 300 1234567, +92 946 9240125)'
            },
            'restaurants': {
                title: '👨‍🍳 Chefs, Special Dishes & Menu Items',
                addBtnText: '+ Add New Dish / Menu Item',
                extraTitle: '🍲 Special Dishes & Menu Highlights (Optional)',
                extraPlaceholder: 'e.g. Dumba Karahi (Rs. 2400/kg), Shinwari Tikka, Kabab...',
                c1: 'Item / Dish Name (Dumba Karahi)', c2: 'Category (BBQ / Main Course)',
                c3: 'Price (Rs. 2400)', c4: 'Availability (Daily)',
                c5: 'Description / Special Serving Notes',
                c6: 'Order / Reservation Contact Number(s)'
            },
            'education': {
                title: '🎓 Faculty, Teachers & Courses',
                addBtnText: '+ Add New Teacher / Course',
                extraTitle: '📚 Offered Courses & Academic Programs (Optional)',
                extraPlaceholder: 'e.g. FSc Pre-Medical, ICS, English Language Diploma...',
                c1: 'Teacher / Course Name (Prof. Ali)', c2: 'Department / Course (Computer Science)',
                c3: 'Timing (Morning / Evening)', c4: 'Days (Mon-Fri)',
                c5: 'Fee / Room No (Lab 2)',
                c6: 'Direct Contact / Helpline Number(s)'
            },
            'pharmacies': {
                title: '💊 Pharmacists & Staff Info',
                addBtnText: '+ Add New Pharmacist / Staff',
                extraTitle: '💊 Available Medicines & Healthcare Products (Optional)',
                extraPlaceholder: 'e.g. BP Checking, Sugar Testing Kits, Surgical Items...',
                c1: 'Staff Name (Dr. Bilal)', c2: 'Qualification (Pharm-D)',
                c3: 'Shift Timing (8 AM - 4 PM)', c4: 'Available Days (Mon-Sat)',
                c5: 'Counter / Section',
                c6: 'Direct Contact / Order Number(s)'
            },
            'supermarts': {
                title: '🏬 Store Sections & Managers',
                addBtnText: '+ Add New Section / Manager',
                extraTitle: '🛍️ Featured Groceries & Products (Optional)',
                extraPlaceholder: 'e.g. Fresh Vegetables, Bakery Items, Household Goods...',
                c1: 'Manager / Section (Tariq - Grocery)', c2: 'Department',
                c3: 'Timing', c4: 'Days', c5: 'Floor / Location',
                c6: 'Section Contact Number(s)'
            },
            'property': {
                title: '🏡 Real Estate Agents & Deals',
                addBtnText: '+ Add New Agent / Property',
                extraTitle: '🏡 Featured Plots & Real Estate Deals (Optional)',
                extraPlaceholder: 'e.g. 5 Marla Plot in Kanju Township, Commercial Shops...',
                c1: 'Agent / Property Title (Malik Zubair)', c2: 'Type (5 Marla Plot)',
                c3: 'Price / Contact', c4: 'Area / Location', c5: 'Details',
                c6: 'Agent Contact Number(s)'
            },
            'hotels': {
                title: '🛏️ Rooms, Suites & Rates',
                addBtnText: '+ Add New Room Type',
                extraTitle: '🛏️ Hotel Services & Room Amenities (Optional)',
                extraPlaceholder: 'e.g. Deluxe Family Rooms, Mountain View, Free Breakfast...',
                c1: 'Room Type (Deluxe Family Suite)', c2: 'Capacity (4 Persons)',
                c3: 'Rate per Night (Rs. 8000)', c4: 'Facilities (AC, WiFi, River View)', c5: 'Floor / Block',
                c6: 'Booking / Reception Contact Number(s)'
            }
        };

        (function() {
            var targetRowToDelete = null;

            function showConfirmModal(elementToRemove) {
                targetRowToDelete = elementToRemove;
                var modal = document.getElementById('confirmModal');
                if(modal) modal.classList.remove('hidden');
            }

            function hideConfirmModal() {
                var modal = document.getElementById('confirmModal');
                if(modal) modal.classList.add('hidden');
                targetRowToDelete = null;
            }

            function initForm() {
                var catSelect = document.getElementById('categorySelect');
                var subcatSelect = document.getElementById('subcategorySelect');
                var repeaterTitle = document.getElementById('repeaterTitle');
                var addRowBtn = document.getElementById('addRowBtn');
                var repeaterContainer = document.getElementById('repeaterContainer');
                var extraTitle = document.getElementById('extraTitle');
                var dishesField = document.getElementById('dishesField');

                var addPhoneBtn = document.getElementById('addPhoneBtn');
                var addImageBtn = document.getElementById('addImageBtn');

                var cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
                var confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

                if(cancelDeleteBtn) cancelDeleteBtn.addEventListener('click', hideConfirmModal);
                if(confirmDeleteBtn) {
                    confirmDeleteBtn.addEventListener('click', function() {
                        if(targetRowToDelete) {
                            targetRowToDelete.remove();
                        }
                        hideConfirmModal();
                    });
                }

                if(!catSelect) return;

                if(addPhoneBtn) {
                    addPhoneBtn.addEventListener('click', function() {
                        var container = document.getElementById('phonesContainer');
                        var div = document.createElement('div');
                        div.className = 'flex gap-2 animate-fade-in';
                        div.innerHTML = '<input type="text" name="phones[]" placeholder="e.g. +92 300 1234567" class="w-full p-3 bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white rounded-xl text-xs input-hover-effect outline-none">' +
                                        '<button type="button" class="del-phone-btn bg-red-100 dark:bg-red-600/20 text-red-600 dark:text-red-400 hover:bg-red-600 hover:text-white px-3 rounded-xl text-xs font-bold btn-hover-effect">✕</button>';
                        container.appendChild(div);
                        div.querySelector('.del-phone-btn').addEventListener('click', function() {
                            showConfirmModal(div);
                        });
                    });
                }

                if(addImageBtn) {
                    addImageBtn.addEventListener('click', function() {
                        var container = document.getElementById('imagesContainer');
                        var div = document.createElement('div');
                        div.className = 'flex gap-2 animate-fade-in';
                        div.innerHTML = '<input type="url" name="image_urls[]" placeholder="Another Image URL..." class="w-full p-3 bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white rounded-xl text-xs input-hover-effect outline-none">' +
                                        '<button type="button" class="del-img-btn bg-red-100 dark:bg-red-600/20 text-red-600 dark:text-red-400 hover:bg-red-600 hover:text-white px-3 rounded-xl text-xs font-bold btn-hover-effect">✕</button>';
                        container.appendChild(div);
                        div.querySelector('.del-img-btn').addEventListener('click', function() {
                            showConfirmModal(div);
                        });
                    });
                }

                function addNewRow() {
                    var cat = catSelect.value;
                    var cfg = categoryRowConfigs[cat] || categoryRowConfigs['hospitals'];

                    var rowCard = document.createElement('div');
                    rowCard.className = 'bg-gray-50 dark:bg-gray-950 border border-gray-200 dark:border-gray-800/80 p-4 rounded-2xl space-y-3 relative group shadow-sm animate-fade-in card-hover-effect';

                    rowCard.innerHTML = '<div class="grid grid-cols-1 md:grid-cols-2 gap-3">' +
                        '<input type="text" name="repeater_col1[]" placeholder="' + cfg.c1 + '" class="p-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white rounded-xl text-xs input-hover-effect outline-none">' +
                        '<input type="text" name="repeater_col2[]" placeholder="' + cfg.c2 + '" class="p-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white rounded-xl text-xs input-hover-effect outline-none">' +
                        '</div>' +
                        '<div class="grid grid-cols-1 md:grid-cols-2 gap-3">' +
                        '<input type="text" name="repeater_col3[]" placeholder="' + cfg.c3 + '" class="p-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white rounded-xl text-xs input-hover-effect outline-none">' +
                        '<input type="text" name="repeater_col4[]" placeholder="' + cfg.c4 + '" class="p-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white rounded-xl text-xs input-hover-effect outline-none">' +
                        '</div>' +
                        '<input type="text" name="repeater_col5[]" placeholder="' + cfg.c5 + '" class="w-full p-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white rounded-xl text-xs input-hover-effect outline-none">' +
                        '<div class="flex gap-2">' +
                        '<input type="text" name="repeater_col6[]" placeholder="' + cfg.c6 + '" class="w-full p-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white rounded-xl text-xs input-hover-effect outline-none">' +
                        '<button type="button" class="del-row-btn bg-red-100 dark:bg-red-600/20 text-red-600 dark:text-red-400 hover:bg-red-600 hover:text-white px-3 rounded-xl text-xs font-bold btn-hover-effect">✕</button>' +
                        '</div>';
                    
                    repeaterContainer.appendChild(rowCard);

                    rowCard.querySelector('.del-row-btn').addEventListener('click', function() {
                        showConfirmModal(rowCard);
                    });
                }

                function updateFormFields() {
                    var val = catSelect.value;
                    subcatSelect.innerHTML = '';
                    
                    var defaultOpt = document.createElement('option');
                    defaultOpt.value = '';
                    defaultOpt.textContent = '-- Select Subcategory (Optional) --';
                    subcatSelect.appendChild(defaultOpt);

                    if(subcategoriesData[val]) {
                        for(var i=0; i<subcategoriesData[val].length; i++) {
                            var opt = document.createElement('option');
                            opt.value = subcategoriesData[val][i];
                            opt.textContent = subcategoriesData[val][i];
                            subcatSelect.appendChild(opt);
                        }
                    }

                    var cfg = categoryRowConfigs[val] || categoryRowConfigs['hospitals'];
                    repeaterTitle.innerText = cfg.title;
                    addRowBtn.innerText = cfg.addBtnText;
                    extraTitle.innerText = cfg.extraTitle;
                    dishesField.placeholder = cfg.extraPlaceholder;

                    repeaterContainer.innerHTML = '';
                    addNewRow();
                }

                catSelect.addEventListener('change', updateFormFields);
                addRowBtn.addEventListener('click', addNewRow);
                
                updateFormFields();
            }

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initForm);
            } else {
                initForm();
            }
        })();
    </script>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin')

    admin_back_url = "/admin"
    admin_back_text = "Admin Dashboard"

    if not session.get('admin_logged_in'):
        html = get_base_head(back_url="/", back_text="Back to Home") + '''
        <main class="max-w-md mx-auto px-4 py-20 text-center animate-fade-in">
            <div class="bg-white dark:bg-gray-900 p-8 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-xl">
                <h2 class="text-2xl font-bold mb-4 text-gray-900 dark:text-white">🔒 Admin Portal Login</h2>
                <form method="POST" class="space-y-4">
                    <input type="password" name="password" required placeholder="Password" class="w-full p-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-center text-gray-900 dark:text-white input-hover-effect outline-none">
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-xl font-bold btn-hover-effect">Login</button>
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
        html = get_base_head(back_url=admin_back_url, back_text=admin_back_text) + '''
        <main class="max-w-5xl mx-auto px-4 py-12 animate-fade-in">
            <div class="flex justify-between items-center mb-10">
                <h2 class="text-3xl font-extrabold text-gray-900 dark:text-white">🛠️ Admin Control Center</h2>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <a href="/admin?module=business&tab=pending" class="bg-white dark:bg-gray-900 p-8 rounded-3xl border border-gray-200 dark:border-gray-800 card-hover-effect flex flex-col justify-between group shadow-xl">
                    <div>
                        <div class="flex justify-between items-center mb-6">
                            <span class="text-6xl group-hover:scale-110 transition-transform">🏢</span>
                            <span class="bg-yellow-100 dark:bg-yellow-500/20 text-yellow-700 dark:text-yellow-400 text-xs px-3 py-1.5 rounded-full font-bold">''' + str(len(pending_biz)) + ''' Pending</span>
                        </div>
                        <h3 class="text-2xl font-black text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-500 transition-colors">1. Business Directory Module</h3>
                        <p class="text-gray-600 dark:text-gray-400 text-sm mt-2">Manage new business registration approvals and live directory listings.</p>
                    </div>
                    <div class="mt-8 text-blue-600 dark:text-blue-500 font-bold text-sm flex justify-between items-center">
                        <span>Open Business Portal →</span>
                        <span class="text-xs text-gray-500">''' + str(len(approved_biz)) + ''' Live Listings</span>
                    </div>
                </a>

                <a href="/admin?module=payment&tab=pending" class="bg-white dark:bg-gray-900 p-8 rounded-3xl border border-gray-200 dark:border-gray-800 card-hover-effect flex flex-col justify-between group shadow-xl">
                    <div>
                        <div class="flex justify-between items-center mb-6">
                            <span class="text-6xl group-hover:scale-110 transition-transform">💳</span>
                            <span class="bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400 text-xs px-3 py-1.5 rounded-full font-bold">''' + str(len(expired_subs)) + ''' Expired</span>
                        </div>
                        <h3 class="text-2xl font-black text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-500 transition-colors">2. Payment & Subscription Module</h3>
                        <p class="text-gray-600 dark:text-gray-400 text-sm mt-2">Verify payments, 5-day expiry alerts, and fully expired subscriptions.</p>
                    </div>
                    <div class="mt-8 text-indigo-600 dark:text-indigo-500 font-bold text-sm flex justify-between items-center">
                        <span>Open Payment Portal →</span>
                        <span class="text-xs text-red-600 dark:text-red-400 font-bold">''' + str(len(expired_subs)) + ''' Expired / ''' + str(len(expiring_alerts)) + ''' Alerts</span>
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
                <div class="bg-gray-50 dark:bg-gray-800/60 p-4 rounded-2xl flex justify-between items-center hover:bg-gray-100 dark:hover:bg-gray-800 transition">
                    <div>
                        <h4 class="font-bold text-gray-900 dark:text-white">''' + b["name"] + ''' <span class="text-xs text-indigo-600 dark:text-indigo-400">(''' + b.get('subcategory', 'General') + ''')</span></h4>
                        <p class="text-xs text-gray-500 dark:text-gray-400">📍 ''' + b["address"] + ''' | 📅 Joined: <span class="text-blue-600 dark:text-blue-400 font-semibold">''' + j_date + '''</span></p>
                    </div>
                    <div class="flex gap-2 items-center">
                        <a href="/business/''' + b_id + '''" target="_blank" class="bg-blue-100 dark:bg-blue-600/20 text-blue-600 dark:text-blue-400 hover:bg-blue-600 hover:text-white px-3 py-2 rounded-xl text-xs font-bold btn-hover-effect">Preview</a>
                        <a href="/admin?module=business&tab=pending&action=approve&id=''' + b_id + '''" class="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded-xl text-xs font-bold btn-hover-effect">Approve</a>
                        <a href="/admin?module=business&tab=pending&action=delete&id=''' + b_id + '''" class="bg-red-100 dark:bg-red-600/20 text-red-600 dark:text-red-400 hover:bg-red-600 hover:text-white px-3 py-2 rounded-xl text-xs font-bold btn-hover-effect">Delete</a>
                    </div>
                </div>
                '''
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No pending business approvals.</p>'
        else:
            for b_id, b in approved_biz.items():
                j_date = b.get('joining_date', datetime.now()).strftime('%Y-%m-%d')
                content += '''
                <div class="bg-gray-50 dark:bg-gray-800/40 p-4 rounded-2xl flex justify-between items-center hover:bg-gray-100 dark:hover:bg-gray-800/70 transition">
                    <div>
                        <h4 class="font-bold text-gray-900 dark:text-white">''' + b["name"] + ''' <span class="text-xs text-indigo-600 dark:text-indigo-400">(''' + b.get('subcategory', 'General') + ''')</span></h4>
                        <p class="text-xs text-gray-500 dark:text-gray-400">📍 ''' + b["address"] + ''' | 📅 Joined: <span class="text-blue-600 dark:text-blue-400 font-semibold">''' + j_date + '''</span></p>
                    </div>
                    <div class="flex gap-2 items-center">
                        <a href="/business/''' + b_id + '''" target="_blank" class="bg-blue-100 dark:bg-blue-600/20 text-blue-600 dark:text-blue-400 hover:bg-blue-600 hover:text-white px-3 py-1.5 rounded-xl text-xs font-bold btn-hover-effect">View</a>
                        <a href="/admin?module=business&tab=approved&action=delete&id=''' + b_id + '''" class="bg-red-100 dark:bg-red-600/20 text-red-600 dark:text-red-400 hover:bg-red-600 hover:text-white px-3 py-1.5 rounded-xl text-xs font-bold btn-hover-effect">Delete</a>
                    </div>
                </div>
                '''
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No approved listings.</p>'

        html = get_base_head(back_url=admin_back_url, back_text=admin_back_text) + '''
        <main class="max-w-4xl mx-auto px-4 py-12 animate-fade-in">
            <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">🏢 Business Directory Management</h2>
            <div class="flex space-x-3 mb-6">
                <a href="/admin?module=business&tab=pending" class="px-5 py-2.5 rounded-xl font-bold text-sm transition ''' + ('bg-blue-600 text-white shadow-lg' if tab=='pending' else 'bg-gray-200 dark:bg-gray-900 text-gray-700 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-800') + '''">Pending (''' + str(len(pending_biz)) + ''')</a>
                <a href="/admin?module=business&tab=approved" class="px-5 py-2.5 rounded-xl font-bold text-sm transition ''' + ('bg-blue-600 text-white shadow-lg' if tab=='approved' else 'bg-gray-200 dark:bg-gray-900 text-gray-700 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-800') + '''">Approved (''' + str(len(approved_biz)) + ''')</a>
            </div>
            <div class="bg-white dark:bg-gray-900 p-6 rounded-3xl border border-gray-200 dark:border-gray-800 space-y-4 shadow-lg">
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
                <div class="bg-gray-50 dark:bg-gray-800/60 p-4 rounded-2xl flex justify-between items-center">
                    <div>
                        <h4 class="font-bold text-gray-900 dark:text-white">''' + b["name"] + '''</h4>
                        <p class="text-xs text-gray-500 dark:text-gray-400">Method: <span class="text-blue-600 dark:text-blue-400 font-bold">''' + b.get('payment_method', 'N/A') + '''</span> | Ref: <span class="text-indigo-600 dark:text-indigo-400 font-mono font-bold">''' + b.get('payment_ref', 'N/A') + '''</span></p>
                    </div>
                    <a href="/admin?module=payment&tab=pending&action=approve_pay&id=''' + b_id + '''" class="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded-xl text-xs font-bold btn-hover-effect">Verify & Activate (60 Days)</a>
                </div>
                '''
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No pending payment verifications.</p>'
        elif tab == 'alerts':
            for b_id, b in expiring_alerts.items():
                ed = b.get('expiry_date').strftime('%Y-%m-%d')
                content += '''
                <div class="bg-yellow-50 dark:bg-yellow-500/10 border border-yellow-200 dark:border-yellow-500/30 p-4 rounded-2xl flex justify-between items-center">
                    <div>
                        <h4 class="font-bold text-gray-900 dark:text-white">''' + b["name"] + '''</h4>
                        <p class="text-xs text-yellow-600 dark:text-yellow-400 font-semibold">⚠️ Expires on: ''' + ed + '''</p>
                    </div>
                    <a href="/admin?module=payment&tab=alerts&action=approve_pay&id=''' + b_id + '''" class="bg-yellow-500 hover:bg-yellow-400 text-gray-950 px-4 py-2 rounded-xl text-xs font-bold btn-hover-effect">Renew 60 Days</a>
                </div>
                '''
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No subscriptions expiring in the next 5 days.</p>'
        else:
            for b_id, b in expired_subs.items():
                ed = b.get('expiry_date').strftime('%Y-%m-%d')
                content += '''
                <div class="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 p-4 rounded-2xl flex justify-between items-center">
                    <div>
                        <h4 class="font-bold text-gray-900 dark:text-white">''' + b["name"] + '''</h4>
                        <p class="text-xs text-red-600 dark:text-red-400 font-semibold">❌ Expired on: ''' + ed + '''</p>
                    </div>
                    <a href="/admin?module=payment&tab=expired&action=approve_pay&id=''' + b_id + '''" class="bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded-xl text-xs font-bold btn-hover-effect">Restore & Renew</a>
                </div>
                '''
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No expired subscriptions found.</p>'

        html = get_base_head(back_url=admin_back_url, back_text=admin_back_text) + '''
        <main class="max-w-4xl mx-auto px-4 py-12 animate-fade-in">
            <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">💳 Payment & Subscription Hub</h2>
            <div class="flex space-x-3 mb-6">
                <a href="/admin?module=payment&tab=pending" class="px-5 py-2.5 rounded-xl font-bold text-sm transition ''' + ('bg-indigo-600 text-white shadow-lg' if tab=='pending' else 'bg-gray-200 dark:bg-gray-900 text-gray-700 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-800') + '''">Unpaid (''' + str(len(pending_pay)) + ''')</a>
                <a href="/admin?module=payment&tab=alerts" class="px-5 py-2.5 rounded-xl font-bold text-sm transition ''' + ('bg-yellow-500 text-gray-950 shadow-lg' if tab=='alerts' else 'bg-gray-200 dark:bg-gray-900 text-gray-700 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-800') + '''">Expiry Alerts (''' + str(len(expiring_alerts)) + ''')</a>
                <a href="/admin?module=payment&tab=expired" class="px-5 py-2.5 rounded-xl font-bold text-sm transition ''' + ('bg-red-600 text-white shadow-lg' if tab=='expired' else 'bg-gray-200 dark:bg-gray-900 text-gray-700 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-800') + '''">Expired (''' + str(len(expired_subs)) + ''')</a>
            </div>
            <div class="bg-white dark:bg-gray-900 p-6 rounded-3xl border border-gray-200 dark:border-gray-800 space-y-4 shadow-lg">
                ''' + content + '''
            </div>
        </main>
        ''' + FOOTER
        return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
