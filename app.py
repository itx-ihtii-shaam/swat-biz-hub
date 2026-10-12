"""SwatBiz Hub - Clean & Stable Categorized Admin Control Center with Expired Subscriptions Tab."""
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
        'name': 'Saidu Group of Teaching Hospital',
        'address': 'Saidu Sharif, Mingora, Swat',
        'phones': ['+92 946 9240123'],
        'image': 'https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=800&q=80',
        'status': 'approved',
        'payment_method': 'Bank Transfer',
        'payment_ref': 'TXN-984210',
        'payment_status': 'paid',
        'expiry_date': datetime.now() - timedelta(days=2)
    },
    '2': {
        'id': '2',
        'category': 'restaurants',
        'name': 'Khyber Shinwari Restaurant',
        'address': 'Fizagat, Swat',
        'phones': ['+92 946 881122'],
        'image': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80',
        'status': 'pending',
        'payment_method': 'EasyPaisa',
        'payment_ref': 'TID-9920182',
        'payment_status': 'unpaid',
        'expiry_date': datetime.now() + timedelta(days=30)
    },
    '3': {
        'id': '3',
        'category': 'pharmacies',
        'name': 'Shifa Medical & Pharmacy',
        'address': 'Green Chowk, Mingora, Swat',
        'phones': ['+92 946 7123456'],
        'image': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80',
        'status': 'approved',
        'payment_method': 'EasyPaisa',
        'payment_ref': 'TID-7782194',
        'payment_status': 'paid',
        'expiry_date': datetime.now() + timedelta(days=3)
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

BASE_HEAD = """
<!DOCTYPE html>
<html lang="en" id="html-root" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>""" + SITE_NAME + """</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config = { darkMode: 'class' }</script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen">
    <header class="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white shadow-xl">
        <div class="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
            <a href="/" class="text-2xl font-extrabold tracking-tight">🏙️ """ + SITE_NAME + """</a>
            <div class="flex items-center space-x-3">
                <a href="/register" class="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-xl text-sm font-bold shadow-lg transition">＋ Register Business</a>
            </div>
        </div>
    </header>
"""

FOOTER = """
    <footer class="text-center py-8 text-sm text-gray-500 border-t border-gray-800 mt-20">
        <p>&copy; 2026 """ + SITE_NAME + """. All rights reserved.</p>
    </footer>
</body>
</html>
"""

@app.route('/')
def home():
    items_html = ""
    for slug, cat in CATEGORIES.items():
        items_html += f"""
        <a href="/category/{slug}" class="bg-gray-900 p-8 rounded-3xl border border-gray-800 shadow-sm hover:shadow-2xl transition-all flex items-center space-x-5 group">
            <span class="text-5xl p-4 bg-gray-800 rounded-2xl">{cat["icon"]}</span>
            <div>
                <h3 class="text-xl font-bold group-hover:text-blue-500 transition-colors">{cat["title"]}</h3>
                <p class="text-sm text-gray-400 mt-1">Browse listings →</p>
            </div>
        </a>
        """
    
    body = f"""
    <section class="py-16 px-4 text-center">
        <h2 class="text-4xl md:text-5xl font-black tracking-tight">Discover Swat & Mingora Businesses</h2>
        <p class="text-gray-400 text-lg mt-2">Find verified local services instantly.</p>
    </section>
    <main class="max-w-7xl mx-auto px-4 pb-20">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items_html}
        </div>
    </main>
    """
    return render_template_string(BASE_HEAD + body + FOOTER)

@app.route('/category/<cat_slug>')
def category_page(cat_slug):
    if cat_slug not in CATEGORIES:
        abort(404)
    
    cat = CATEGORIES[cat_slug]
    biz_list = [b for b in BUSINESSES.values() if b.get('category') == cat_slug and b.get('status') == 'approved']
    
    cards = ""
    for b in biz_list:
        cards += f"""
        <div class="bg-gray-900 p-6 rounded-2xl border border-gray-800">
            <h3 class="font-bold text-lg">{b["name"]}</h3>
            <p class="text-sm text-gray-400">📍 {b["address"]}</p>
        </div>
        """
    if not cards:
        cards = '<p class="text-gray-500 col-span-3 text-center py-12">No approved listings in this category yet.</p>'

    body = f"""
    <main class="max-w-7xl mx-auto px-4 py-12">
        <h2 class="text-3xl font-bold mb-6">{cat["icon"]} {cat["title"]}</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            {cards}
        </div>
    </main>
    """
    return render_template_string(BASE_HEAD + body + FOOTER)

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

    opts = "".join([f'<option value="{k}">{v["title"]}</option>' for k, v in CATEGORIES.items()])
    
    body = f"""
    <main class="max-w-2xl mx-auto px-4 py-12">
        <h2 class="text-3xl font-bold text-center mb-6">Register Business</h2>
        <form method="POST" class="space-y-4">
            <input type="text" name="name" required placeholder="Business Name" class="w-full p-3 rounded-xl bg-gray-900 border border-gray-800">
            <select name="category" class="w-full p-3 rounded-xl bg-gray-900 border border-gray-800">{opts}</select>
            <input type="text" name="address" required placeholder="Address" class="w-full p-3 rounded-xl bg-gray-900 border border-gray-800">
            <input type="text" name="phone" required placeholder="Phone Number" class="w-full p-3 rounded-xl bg-gray-900 border border-gray-800">
            <select name="payment_method" class="w-full p-3 rounded-xl bg-gray-900 border border-gray-800">
                <option value="EasyPaisa">EasyPaisa</option>
                <option value="JazzCash">JazzCash</option>
                <option value="Bank Transfer">Bank Transfer</option>
            </select>
            <input type="text" name="payment_ref" placeholder="TID / Ref Number" class="w-full p-3 rounded-xl bg-gray-900 border border-gray-800">
            <button type="submit" class="w-full bg-blue-600 py-3 rounded-xl font-bold">Submit Business</button>
        </form>
    </main>
    """
    return render_template_string(BASE_HEAD + body + FOOTER)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin')

    if not session.get('admin_logged_in'):
        body = """
        <main class="max-w-md mx-auto px-4 py-20 text-center">
            <div class="bg-gray-900 p-8 rounded-3xl border border-gray-800">
                <h2 class="text-2xl font-bold mb-4">🔒 Admin Portal Login</h2>
                <form method="POST" class="space-y-4">
                    <input type="password" name="password" required placeholder="Password" class="w-full p-3 rounded-xl bg-gray-800 border border-gray-700 text-center">
                    <button type="submit" class="w-full bg-blue-600 py-3 rounded-xl font-bold">Login</button>
                </form>
            </div>
        </main>
        """
        return render_template_string(BASE_HEAD + body + FOOTER)

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
            BUSINESSES[biz_id]['expiry_date'] = datetime.now() + timedelta(days=30)
        elif action == 'delete':
            BUSINESSES[biz_id]['status'] = 'deleted'
        return redirect(f'/admin?module={module}&tab={tab}')

    now = datetime.now()
    pending_biz = {k: v for k, v in BUSINESSES.items() if v.get('status') == 'pending'}
    approved_biz = {k: v for k, v in BUSINESSES.items() if v.get('status') == 'approved'}
    pending_pay = {k: v for k, v in BUSINESSES.items() if v.get('payment_status') == 'unpaid'}
    paid_pay = {k: v for k, v in BUSINESSES.items() if v.get('payment_status') == 'paid' and v.get('expiry_date', now) >= now}
    
    expiring_alerts = {k: v for k, v in BUSINESSES.items() if 0 <= (v.get('expiry_date') - now).days <= 5 and v.get('status') != 'deleted'}
    expired_subs = {k: v for k, v in BUSINESSES.items() if (v.get('expiry_date') - now).days < 0 and v.get('status') != 'deleted'}

    if not module:
        body = f"""
        <main class="max-w-5xl mx-auto px-4 py-12">
            <div class="flex justify-between items-center mb-10">
                <h2 class="text-3xl font-extrabold">🛠️ Admin Control Center</h2>
                <a href="/admin?action=logout" class="bg-red-600/20 text-red-400 px-4 py-2 rounded-xl text-sm font-bold">Logout</a>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <a href="/admin?module=business&tab=pending" class="bg-gray-900 p-8 rounded-3xl border border-gray-800 hover:border-blue-500 transition-all shadow-2xl flex flex-col justify-between group">
                    <div>
                        <div class="flex justify-between items-center mb-6">
                            <span class="text-6xl">🏢</span>
                            <span class="bg-yellow-500/20 text-yellow-400 text-xs px-3 py-1.5 rounded-full font-bold">{len(pending_biz)} Pending</span>
                        </div>
                        <h3 class="text-2xl font-black group-hover:text-blue-500 transition-colors">1. Business Directory Module</h3>
                        <p class="text-gray-400 text-sm mt-2">Manage new business registration approvals and live directory listings.</p>
                    </div>
                    <div class="mt-8 text-blue-500 font-bold text-sm flex justify-between items-center">
                        <span>Open Business Portal →</span>
                        <span class="text-xs text-gray-500">{len(approved_biz)} Live Listings</span>
                    </div>
                </a>

                <a href="/admin?module=payment&tab=pending" class="bg-gray-900 p-8 rounded-3xl border border-gray-800 hover:border-indigo-500 transition-all shadow-2xl flex flex-col justify-between group">
                    <div>
                        <div class="flex justify-between items-center mb-6">
                            <span class="text-6xl">💳</span>
                            <span class="bg-red-500/20 text-red-400 text-xs px-3 py-1.5 rounded-full font-bold">{len(expired_subs)} Expired</span>
                        </div>
                        <h3 class="text-2xl font-black group-hover:text-indigo-500 transition-colors">2. Payment & Subscription Module</h3>
                        <p class="text-gray-400 text-sm mt-2">Verify payments, 5-day expiry alerts, and fully expired subscriptions.</p>
                    </div>
                    <div class="mt-8 text-indigo-500 font-bold text-sm flex justify-between items-center">
                        <span>Open Payment Portal →</span>
                        <span class="text-xs text-red-400 font-bold">{len(expired_subs)} Expired / {len(expiring_alerts)} Alerts</span>
                    </div>
                </a>
            </div>
        </main>
        """
        return render_template_string(BASE_HEAD + body + FOOTER)

    elif module == 'business':
        content = ""
        if tab == 'pending':
            for b_id, b in pending_biz.items():
                content += f"""
                <div class="bg-gray-800/60 p-4 rounded-2xl flex justify-between items-center">
                    <div>
                        <h4 class="font-bold">{b["name"]}</h4>
                        <p class="text-xs text-gray-400">📍 {b["address"]}</p>
                    </div>
                    <div class="flex gap-2">
                        <a href="/admin?module=business&tab=pending&action=approve&id={b_id}" class="bg-green-600 px-4 py-2 rounded-xl text-xs font-bold">Approve</a>
                        <a href="/admin?module=business&tab=pending&action=delete&id={b_id}" class="bg-red-600/20 text-red-400 px-3 py-2 rounded-xl text-xs font-bold">Delete</a>
                    </div>
                </div>
                """
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No pending business approvals.</p>'
        else:
            for b_id, b in approved_biz.items():
                content += f"""
                <div class="bg-gray-800/40 p-4 rounded-2xl flex justify-between items-center">
                    <div>
                        <h4 class="font-bold">{b["name"]}</h4>
                        <p class="text-xs text-gray-400">📍 {b["address"]}</p>
                    </div>
                    <a href="/admin?module=business&tab=approved&action=delete&id={b_id}" class="bg-red-600/20 text-red-400 px-3 py-1.5 rounded-xl text-xs font-bold">Delete</a>
                </div>
                """

        body = f"""
        <main class="max-w-5xl mx-auto px-4 py-12">
            <div class="flex justify-between items-center mb-8">
                <a href="/admin" class="text-sm font-bold text-blue-500 hover:underline">← Back to Admin Hub</a>
                <h2 class="text-2xl font-extrabold">🏢 Business Directory Module</h2>
            </div>
            <div class="flex space-x-3 mb-8">
                <a href="/admin?module=business&tab=pending" class="px-5 py-2.5 rounded-xl text-sm font-bold {"bg-blue-600 text-white" if tab == "pending" else "bg-gray-900 text-gray-400"}">
                    Pending Approvals ({len(pending_biz)})
                </a>
                <a href="/admin?module=business&tab=approved" class="px-5 py-2.5 rounded-xl text-sm font-bold {"bg-blue-600 text-white" if tab == "approved" else "bg-gray-900 text-gray-400"}">
                    Approved Directory ({len(approved_biz)})
                </a>
            </div>
            <div class="bg-gray-900 p-6 rounded-3xl border border-gray-800 space-y-4">
                {content}
            </div>
        </main>
        """
        return render_template_string(BASE_HEAD + body + FOOTER)

    elif module == 'payment':
        content = ""
        if tab == 'pending':
            for b_id, b in pending_pay.items():
                content += f"""
                <div class="bg-gray-800/60 p-4 rounded-2xl flex justify-between items-center">
                    <div>
                        <h4 class="font-bold">{b["name"]}</h4>
                        <p class="text-xs text-blue-400">Method: {b.get("payment_method")} | Ref: <code>{b.get("payment_ref")}</code></p>
                    </div>
                    <a href="/admin?module=payment&tab=pending&action=approve_pay&id={b_id}" class="bg-blue-600 px-4 py-2 rounded-xl text-xs font-bold">Confirm Payment</a>
                </div>
                """
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No pending payments to verify.</p>'
        elif tab == 'alerts':
            for b_id, b in expiring_alerts.items():
                content += f"""
                <div class="bg-red-950/40 border border-red-500/50 p-4 rounded-2xl flex justify-between items-center">
                    <div>
                        <h4 class="font-bold text-white">{b["name"]}</h4>
                        <p class="text-xs text-red-400 font-bold mt-1">⏳ Expiry Alert: Less than 5 Days Remaining!</p>
                    </div>
                    <a href="/admin?module=payment&tab=alerts&action=approve_pay&id={b_id}" class="bg-red-600 px-4 py-2 rounded-xl text-xs font-bold">Renew (+30 Days)</a>
                </div>
                """
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No 5-day expiry alerts right now.</p>'
        elif tab == 'expired':
            for b_id, b in expired_subs.items():
                days_ago = abs((b.get('expiry_date') - now).days)
                content += f"""
                <div class="bg-red-900/30 border-2 border-red-600 p-4 rounded-2xl flex justify-between items-center">
                    <div>
                        <h4 class="font-bold text-white">{b["name"]}</h4>
                        <p class="text-xs text-gray-400">📞 {b.get("phones", ["N/A"])[0]} | 📍 {b["address"]}</p>
                        <p class="text-xs text-red-400 font-bold mt-1">❌ Subscription Ended {days_ago} day(s) ago!</p>
                    </div>
                    <a href="/admin?module=payment&tab=expired&action=approve_pay&id={b_id}" class="bg-red-600 hover:bg-red-500 px-4 py-2 rounded-xl text-xs font-bold text-white shadow">Remind / Renew (+30 Days)</a>
                </div>
                """
            if not content:
                content = '<p class="text-gray-500 text-center py-8">No expired subscriptions found. Great!</p>'
        else:
            for b_id, b in paid_pay.items():
                content += f"""
                <div class="bg-gray-800/40 p-4 rounded-2xl">
                    <h4 class="font-bold">{b["name"]}</h4>
                    <p class="text-xs text-gray-400 mt-1">Method: {b.get("payment_method")} | Ref: <code>{b.get("payment_ref")}</code></p>
                    <span class="text-xs font-bold text-green-400 mt-1 block">✓ Active Subscription</span>
                </div>
                """

        body = f"""
        <main class="max-w-5xl mx-auto px-4 py-12">
            <div class="flex justify-between items-center mb-8">
                <a href="/admin" class="text-sm font-bold text-indigo-500 hover:underline">← Back to Admin Hub</a>
                <h2 class="text-2xl font-extrabold">💳 Payment & Subscription Module</h2>
            </div>
            <div class="flex flex-wrap gap-3 mb-8">
                <a href="/admin?module=payment&tab=pending" class="px-5 py-2.5 rounded-xl text-sm font-bold {"bg-indigo-600 text-white" if tab == "pending" else "bg-gray-900 text-gray-400"}">
                    Unpaid ({len(pending_pay)})
                </a>
                <a href="/admin?module=payment&tab=alerts" class="px-5 py-2.5 rounded-xl text-sm font-bold {"bg-red-600 text-white" if tab == "alerts" else "bg-gray-900 text-gray-400"}">
                    🚨 5-Day Alerts ({len(expiring_alerts)})
                </a>
                <a href="/admin?module=payment&tab=expired" class="px-5 py-2.5 rounded-xl text-sm font-bold {"bg-red-700 text-white animate-pulse" if tab == "expired" else "bg-gray-900 text-red-400"}">
                    ❌ Expired / Ended ({len(expired_subs)})
                </a>
                <a href="/admin?module=payment&tab=history" class="px-5 py-2.5 rounded-xl text-sm font-bold {"bg-indigo-600 text-white" if tab == "history" else "bg-gray-900 text-gray-400"}">
                    Verified History ({len(paid_pay)})
                </a>
            </div>
            <div class="bg-gray-900 p-6 rounded-3xl border border-gray-800 space-y-4">
                {content}
            </div>
        </main>
        """
        return render_template_string(BASE_HEAD + body + FOOTER)

handler = app

if __name__ == '__main__':
    app.run(debug=True)
