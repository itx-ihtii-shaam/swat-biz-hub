"""SwatBiz Hub - Local Business Directory with Subscription & Expiry System."""
from datetime import datetime, timedelta
import os
import base64
from flask import Flask, abort, redirect, render_template_string, request, url_for

SITE_NAME = 'SwatBiz Hub'

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
        'status': 'approved',
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
        'status': 'approved',
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
        'last_paid_date': datetime.now(),
        'status': 'approved',
    },
    '5': {
        'id': '5',
        'category': 'supermarts',
        'sub_category': 'general',
        'name': 'Mingora General Superstore',
        'address': 'Bank Square, Mingora, Swat',
        'phones': ['+92 946 7144556'],
        'image': 'https://images.unsplash.com/photo-1578916171728-46686eac8d58?auto=format&fit=crop&w=800&q=80',
        'joined_date': datetime.now() - timedelta(days=4),
        'last_paid_date': datetime.now(),
        'status': 'approved',
    }
}

CATEGORIES = {
    'hospitals': {'title': 'Hospitals & Healthcare', 'icon': '🏥', 'search_hint': 'Search name or location (e.g. Mingora, Saidu)...'},
    'pharmacies': {'title': 'Pharmacies & Medical Stores', 'icon': '💊', 'search_hint': 'Search medicine, store or location...'},
    'restaurants': {'title': 'Restaurants & Cafes', 'icon': '🍽️', 'search_hint': 'Search restaurant, dish or area...'},
    'supermarts': {'title': 'Supermarts & Grocery', 'icon': '🛒', 'search_hint': 'Search store, item or location...'},
    'property': {'title': 'Property Dealers', 'icon': '🏠', 'search_hint': 'Search plot, house or area...'},
    'hotels': {'title': 'Hotels & Guest Houses', 'icon': '🏨', 'search_hint': 'Search hotel or location...'},
    'education': {'title': 'Educational Institutes', 'icon': '🎓', 'search_hint': 'Search school, college, area (e.g. Mingora)...'}
}

SUB_CATEGORIES = {
    'education': [
        {'slug': 'all', 'title': 'All Institutes', 'icon': '🎓'},
        {'slug': 'schools', 'title': 'Schools', 'icon': '🏫'},
        {'slug': 'colleges', 'title': 'Colleges', 'icon': '🏛️'},
        {'slug': 'school_college', 'title': 'School & College', 'icon': '🏫🏛️'},
        {'slug': 'universities', 'title': 'Universities', 'icon': '🎓'},
        {'slug': 'academies', 'title': 'Academies', 'icon': '📚'}
    ],
    'supermarts': [
        {'slug': 'all', 'title': 'All Stores', 'icon': '🛒'},
        {'slug': 'general', 'title': 'General Store & Mart', 'icon': '🏪'},
        {'slug': 'bakery', 'title': 'Bakery & Sweets', 'icon': '🍞'},
        {'slug': 'meat', 'title': 'Meat & Vegetables', 'icon': '🥩'},
        {'slug': 'wholesale', 'title': 'Wholesale Dealers', 'icon': '📦'}
    ]
}

INDEX_BASE_HEAD = '''
<!DOCTYPE html>
<html lang="en" id="html-root" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - ''' + SITE_NAME + '''</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏙️</text></svg>">
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
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏙️</text></svg>">
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

CATEGORY_TEMPLATE = BASE_HEAD + '''
    <main class="max-w-7xl mx-auto px-4 py-12">
        <div class="mb-8 text-center">
            <span class="text-6xl">{{ category.icon }}</span>
            <h2 class="text-4xl font-extrabold mt-4">{{ category.title }}</h2>
            <p class="text-gray-500 dark:text-gray-400 mt-2">Explore verified listings in Swat & Mingora</p>
            
            {% if sub_categories %}
            <!-- Sub Categories Tabs -->
            <div class="flex flex-wrap justify-center gap-2 mt-6">
                {% for sub in sub_categories %}
                <a href="/category/{{ cat_slug }}?sub={{ sub.slug }}" class="px-5 py-2.5 rounded-xl font-semibold text-sm transition-all {% if active_sub == sub.slug %} bg-blue-600 text-white shadow-lg {% else %} bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 {% endif %}">
                    {{ sub.icon }} {{ sub.title }}
                </a>
                {% endfor %}
            </div>
            {% endif %}

            <div class="mt-6 max-w-xl mx-auto relative">
                <form method="GET" action="/category/{{ cat_slug }}" class="flex gap-3">
                    {% if active_sub %}
                    <input type="hidden" name="sub" value="{{ active_sub }}">
                    {% endif %}
                    <input type="text" id="searchInput" name="q" value="{{ search_query }}" placeholder="{{ category.search_hint }}" autocomplete="off" class="w-full px-5 py-3.5 rounded-2xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                    <button type="submit" class="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3.5 rounded-2xl font-semibold shadow-md transition">Search</button>
                    {% if search_query %}
                    <a href="/category/{{ cat_slug }}{% if active_sub %}?sub={{ active_sub }}{% endif %}" class="bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 px-4 py-3.5 rounded-2xl font-semibold flex items-center justify-center">Reset</a>
                    {% endif %}
                </form>
                <!-- Live Suggestions Dropdown -->
                <div id="suggestionsBox" class="absolute left-0 right-0 mt-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-xl hidden z-50 overflow-hidden text-left"></div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            {% if businesses %}
                {% for biz in businesses %}
                <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-sm hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100 dark:border-gray-800 overflow-hidden flex flex-col justify-between">
                    <div>
                        <img src="{{ biz.image }}" alt="{{ biz.name }}" class="w-full h-48 object-cover">
                        <div class="p-6">
                            <h3 class="text-xl font-bold hover:text-blue-500 transition-colors">
                                <a href="/business/{{ biz.id }}">{{ biz.name }}</a>
                            </h3>
                            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">📍 {{ biz.address }}</p>
                        </div>
                    </div>
                    <div class="p-6 pt-0">
                        <a href="/business/{{ biz.id }}" class="block w-full text-center bg-blue-600 hover:bg-blue-500 text-white py-2.5 rounded-xl text-sm font-semibold transition">View Details & Contact</a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="col-span-3 text-center py-20 text-gray-500">
                    <p class="text-xl">No listings found matching your criteria.</p>
                    <a href="/category/{{ cat_slug }}" class="inline-block mt-4 text-blue-500 underline font-semibold">Reset Filter</a>
                </div>
            {% endif %}
        </div>
    </main>

    <script>
        const allListings = [
            {% for b in all_category_businesses %}
                { name: "{{ b.name }}", address: "{{ b.address }}" },
            {% endfor %}
        ];

        const searchInput = document.getElementById('searchInput');
        const suggestionsBox = document.getElementById('suggestionsBox');

        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            if (!query) {
                suggestionsBox.classList.add('hidden');
                suggestionsBox.innerHTML = '';
                return;
            }

            const matches = allListings.filter(b => 
                b.name.toLowerCase().includes(query) || b.address.toLowerCase().includes(query)
            );

            if (matches.length > 0) {
                let html = '';
                matches.forEach(match => {
                    html += `<div class="px-5 py-3 hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer border-b border-gray-100 dark:border-gray-800 last:border-none" onclick="selectSuggestion('${match.name}')">
                        <div class="text-sm font-medium">${match.name}</div>
                        <div class="text-xs text-gray-400">📍 ${match.address}</div>
                    </div>`;
                });
                suggestionsBox.innerHTML = html;
                suggestionsBox.classList.remove('hidden');
            } else {
                suggestionsBox.classList.add('hidden');
                suggestionsBox.innerHTML = '';
            }
        });

        function selectSuggestion(val) {
            searchInput.value = val;
            suggestionsBox.classList.add('hidden');
            searchInput.form.submit();
        }

        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
                suggestionsBox.classList.add('hidden');
            }
        });
    </script>
''' + FOOTER


@app.route('/')
def home():
    return render_template_string(INDEX_TEMPLATE, categories=CATEGORIES, title="Home")


@app.route('/category/<cat_slug>')
def category_page(cat_slug):
    if cat_slug not in CATEGORIES:
        abort(404)
    
    search_query = request.args.get('q', '').lower().strip()
    sub_query = request.args.get('sub', 'all')
    
    cat_businesses = []
    all_cat_biz = []

    for b in BUSINESSES.values():
        # Only show approved businesses on public pages
        if b.get('category') == cat_slug and b.get('status') == 'approved':
            all_cat_biz.append(b)
            
            # Sub-category filter
            if sub_query != 'all' and b.get('sub_category') != sub_query:
                continue
                
            # Search query filter (checks name AND location address)
            if search_query:
                b_name = b.get('name', '').lower()
                b_addr = b.get('address', '').lower()
                if search_query in b_name or search_query in b_addr:
                    cat_businesses.append(b)
            else:
                cat_businesses.append(b)

    return render_template_string(
        CATEGORY_TEMPLATE,
        category=CATEGORIES[cat_slug],
        businesses=cat_businesses,
        all_category_businesses=all_cat_biz,
        sub_categories=SUB_CATEGORIES.get(cat_slug, []),
        active_sub=sub_query,
        site_name=SITE_NAME,
        search_query=search_query,
        cat_slug=cat_slug,
        title=CATEGORIES[cat_slug]['title']
    )


@app.route('/business/<b_id>')
def business_detail(b_id):
    biz = BUSINESSES.get(b_id)
    if not biz or biz.get('status') != 'approved':
        abort(404)
    
    detail_html = BASE_HEAD + f'''
    <main class="max-w-4xl mx-auto px-4 py-12">
        <div class="bg-white dark:bg-gray-900 rounded-3xl p-8 shadow-2xl border border-gray-100 dark:border-gray-800 space-y-6">
            <img src="{biz['image']}" class="w-full h-72 object-cover rounded-2xl">
            <h1 class="text-3xl font-black">{biz['name']}</h1>
            <p class="text-gray-500">📍 {biz['address']}</p>
            <p class="text-blue-500 font-bold">📞 {biz['phones'][0] if biz.get('phones') else 'N/A'}</p>
            <a href="/" class="inline-block bg-blue-600 text-white px-6 py-2.5 rounded-xl font-semibold">← Back to Home</a>
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(detail_html, title=biz['name'])


@app.route('/register', methods=['GET', 'POST'])
def register_business():
    if request.method == 'POST':
        b_id = str(len(BUSINESSES) + 1)
        name = request.form.get('name')
        category = request.form.get('category')
        sub_category = request.form.get('sub_category', '')
        address = request.form.get('address')
        phone = request.form.get('phone[]', '+92 946 0000000')

        BUSINESSES[b_id] = {
            'id': b_id,
            'category': category,
            'sub_category': sub_category,
            'name': name,
            'address': address,
            'phones': [phone],
            'image': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80',
            'doctors': [],
            'items': [],
            'joined_date': datetime.now(),
            'status': 'pending'  # Require Admin Approval
        }
        return render_template_string(BASE_HEAD + '''
        <main class="max-w-2xl mx-auto px-4 py-20 text-center">
            <div class="bg-white dark:bg-gray-900 p-8 rounded-3xl shadow-xl border border-gray-100 dark:border-gray-800 space-y-4">
                <span class="text-6xl">🎉</span>
                <h2 class="text-3xl font-bold">Registration Submitted!</h2>
                <p class="text-gray-400">Your listing has been submitted for review. It will be live on SwatBiz Hub once approved by Admin.</p>
                <a href="/" class="inline-block mt-4 bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold">Return to Home</a>
            </div>
        </main>
        ''' + FOOTER, title="Submitted")

    reg_html = BASE_HEAD + '''
    <main class="max-w-3xl mx-auto px-4 py-12">
        <div class="bg-white dark:bg-gray-900 p-8 rounded-3xl shadow-2xl border border-gray-100 dark:border-gray-800">
            <h2 class="text-3xl font-extrabold text-center mb-6">Register Your Listing</h2>
            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-1">Name</label>
                    <input type="text" name="name" required placeholder="e.g. Swat Public School & College" class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-700 outline-none">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Category</label>
                    <select id="categorySelect" name="category" onchange="updateSubCategories()" class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-700 outline-none cursor-pointer">
                        {% for slug, cat in categories.items() %}
                        <option value="{{ slug }}">{{ cat.icon }} {{ cat.title }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Sub-Category</label>
                    <select id="subCategorySelect" name="sub_category" class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-700 outline-none cursor-pointer">
                        <option value="">None / Not Applicable</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Phone Number</label>
                    <input type="text" name="phone[]" required placeholder="+92 946 XXXXXXX" class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-700 outline-none">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Address / Location</label>
                    <input type="text" name="address" required placeholder="e.g. Circular Road, Mingora, Swat" class="w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-700 outline-none">
                </div>
                <button type="submit" class="w-full bg-blue-600 text-white font-bold py-3.5 rounded-xl shadow-lg mt-4">Submit Listing</button>
            </form>
        </div>
    </main>

    <script>
        const subCatData = {
            'education': [
                {value: 'schools', text: '🏫 School'},
                {value: 'colleges', text: '🏛️ College'},
                {value: 'school_college', text: '🏫🏛️ School & College'},
                {value: 'universities', text: '🎓 University'},
                {value: 'academies', text: '📚 Academy'}
            ],
            'supermarts': [
                {value: 'general', text: '🏪 General Store & Mart'},
                {value: 'bakery', text: '🍞 Bakery & Sweets'},
                {value: 'meat', text: '🥩 Meat & Vegetables'},
                {value: 'wholesale', text: '📦 Wholesale Dealer'}
            ]
        };

        function updateSubCategories() {
            const catSelect = document.getElementById('categorySelect');
            const subSelect = document.getElementById('subCategorySelect');
            const selectedCat = catSelect.value;

            subSelect.innerHTML = '<option value="">None / Not Applicable</option>';

            if (subCatData[selectedCat]) {
                subCatData[selectedCat].forEach(sub => {
                    const opt = document.createElement('option');
                    opt.value = sub.value;
                    opt.text = sub.text;
                    subSelect.appendChild(opt);
                });
            }
        }

        window.onload = updateSubCategories;
    </script>
    ''' + FOOTER
    return render_template_string(reg_html, categories=CATEGORIES, title="Register")


# --- ADMIN APPROVAL PANEL ---
@app.route('/admin')
def admin_panel():
    action = request.args.get('action')
    biz_id = request.args.get('id')

    if action and biz_id in BUSINESSES:
        if action == 'approve':
            BUSINESSES[biz_id]['status'] = 'approved'
        elif action == 'delete':
            BUSINESSES[biz_id]['status'] = 'deleted'
        return redirect('/admin')

    admin_html = BASE_HEAD + '''
    <main class="max-w-6xl mx-auto px-4 py-12">
        <h2 class="text-3xl font-bold mb-8">🛠️ Admin Approval & Management Panel</h2>
        
        <div class="space-y-6">
            {% for b_id, biz in all_biz.items() %}
            {% if biz.status != 'deleted' %}
            <div class="bg-white dark:bg-gray-900 rounded-2xl p-6 border border-gray-200 dark:border-gray-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <div class="flex items-center space-x-3">
                        <h3 class="text-xl font-bold">{{ biz.name }}</h3>
                        {% if biz.status == 'approved' %}
                        <span class="bg-green-500/20 text-green-400 text-xs px-3 py-1 rounded-full font-bold">Approved</span>
                        {% else %}
                        <span class="bg-yellow-500/20 text-yellow-400 text-xs px-3 py-1 rounded-full font-bold">Pending Review</span>
                        {% endif %}
                    </div>
                    <p class="text-sm text-gray-400 mt-1">📍 {{ biz.address }} | 📞 {{ biz.phones[0] if biz.phones else 'N/A' }}</p>
                    <p class="text-xs text-gray-500 mt-1">Category: {{ biz.category }} {% if biz.sub_category %}({{ biz.sub_category }}){% endif %}</p>
                </div>
                <div class="flex items-center gap-3">
                    {% if biz.status == 'pending' %}
                    <a href="/admin?action=approve&id={{ b_id }}" class="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded-xl text-sm font-bold shadow transition">Approve</a>
                    {% endif %}
                    <a href="/admin?action=delete&id={{ b_id }}" class="bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white px-4 py-2 rounded-xl text-sm font-bold transition">Delete</a>
                </div>
            </div>
            {% endif %}
            {% endfor %}
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(admin_html, all_biz=BUSINESSES, title="Admin Panel")


handler = app

if __name__ == '__main__':
    app.run(debug=True)
