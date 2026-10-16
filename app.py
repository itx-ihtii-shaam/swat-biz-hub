"""SwatBiz Hub - Complete & Fully Functional Code with Fixed Maps & Dynamic Theme Toggle Buttons."""
from datetime import datetime, timedelta
import os
import json
import urllib.parse
import re
import random
import requests
from flask import Flask, abort, redirect, render_template_string, request, url_for, session

SITE_NAME = 'SwatBiz Hub'
ADMIN_PASSWORD = 'admin123'

app = Flask(__name__)
app.secret_key = 'swat_biz_hub_secret_key'

# Temporary storage for email verification codes & password reset tokens
EMAIL_VERIFICATION_CODES = {}
PASSWORD_RESET_CODES = {}

# ============================================================
# REAL EMAIL SENDING (Brevo / Sendinblue transactional email API)
# ------------------------------------------------------------
# PythonAnywhere's FREE tier blocks normal SMTP connections
# (smtp.gmail.com etc are NOT on its outbound whitelist), but it
# DOES allow plain HTTPS requests to api.brevo.com, so this uses
# Brevo's HTTP API instead of smtplib to actually deliver email.
#
# Setup (one-time, takes ~3 minutes):
#   1) Create a free account at https://www.brevo.com (300 emails/day free)
#   2) Go to: SMTP & API -> API Keys -> "Generate a new API key"
#      Paste that key into BREVO_API_KEY below.
#   3) Go to: Senders, Domains & Dedicated IPs -> Senders -> Add a Sender
#      Verify an email address you own (e.g. your Gmail) and put it in
#      MAIL_FROM_EMAIL below. Every email this site sends will be sent
#      "from" that verified address.
# ============================================================
BREVO_API_KEY = 'PASTE-YOUR-BREVO-API-KEY-HERE'
MAIL_FROM_EMAIL = 'youremail@gmail.com'   # must be verified as a Sender in Brevo
MAIL_FROM_NAME = SITE_NAME


def send_email(to_email, subject, html_body):
    """Sends a real email via Brevo's HTTPS API.
    Returns True if the email was actually sent, False otherwise.
    Never raises - so registration/login never crashes even if email fails."""
    if not BREVO_API_KEY or BREVO_API_KEY.startswith('PASTE-'):
        # Not configured yet - fall back to printing in the server log so
        # you can still test locally. Visible in PythonAnywhere's error log.
        print(f"[EMAIL NOT SENT - set BREVO_API_KEY first] To: {to_email} | Subject: {subject}\n{html_body}")
        return False
    try:
        resp = requests.post(
            'https://api.brevo.com/v3/smtp/email',
            headers={
                'accept': 'application/json',
                'api-key': BREVO_API_KEY,
                'content-type': 'application/json',
            },
            json={
                'sender': {'name': MAIL_FROM_NAME, 'email': MAIL_FROM_EMAIL},
                'to': [{'email': to_email}],
                'subject': subject,
                'htmlContent': html_body,
            },
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            print(f"[EMAIL SEND FAILED] {resp.status_code}: {resp.text}")
            return False
        return True
    except Exception as e:
        print(f"[EMAIL SEND ERROR] {e}")
        return False

def get_google_maps_url(name, address):
    """Smart Google Maps URL builder: extracts GPS coords if available, else builds name+address query."""
    if not address:
        return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(name)}"
    
    coords_match = re.search(r'(-?\d+\.\d+),\s*(-?\d+\.\d+)', address)
    if coords_match:
        lat, lon = coords_match.groups()
        return f"https://www.google.com/maps?q={lat},{lon}"
    else:
        query_str = f"{name} {address}".strip()
        return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query_str)}"

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
        'payment_method': 'Bank Transfer',
        'payment_ref': 'TXN-9842103',
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
                'appt_numbers': '+92 300 9240001, +92 946 9240123',
                'doc_image': 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?auto=format&fit=crop&w=400&q=80'
            },
            {
                'name': 'Dr. Ayesha Khan',
                'specialty': 'Pediatrician',
                'qualifications': 'MBBS, DCH, MCPS (Pediatrics)',
                'appt_timing': '10:00 AM - 4:00 PM',
                'clinic_timing': 'Mon - Fri (10 AM - 4 PM)',
                'room': 'Children Ward - Room 04',
                'appt_numbers': '+92 301 8881122',
                'doc_image': 'https://images.unsplash.com/photo-1594824813566-78a9c240902c?auto=format&fit=crop&w=400&q=80'
            }
        ],
        'special_info': 'Dr. Muhammad Ali (Cardiologist), Dr. Ayesha Khan (Pediatrician)',
        'tests_dishes': 'MRI, CT Scan, X-Ray, Ultrasound, Emergency Care, Blood Bank Services, ICU & CCU Facilities, OPD & IPD Services, Pathology Lab',
        'extra_img': 'https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=800&q=80',
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
        'payment_method': 'EasyPaisa',
        'payment_ref': 'EP-8837261',
        'payment_status': 'pending',
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
                'appt_numbers': '+92 946 881122',
                'doc_image': ''
            }
        ],
        'special_info': 'Special Family Cabin Available | Chef Rashid',
        'tests_dishes': 'Dumba Karahi (Rs. 2400/kg), Shinwari Tikka (Rs. 1800/kg), Mutton Kabab, Green Tea',
        'extra_img': '',
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
        'payment_method': 'JazzCash',
        'payment_ref': 'JC-5528190',
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
                'appt_numbers': '+92 946 720111',
                'doc_image': ''
            }
        ],
        'special_info': 'Prof. Shah Zarin (Principal), Admissions open for Metric & FSc',
        'tests_dishes': 'Science Labs, Computer Labs, Library, Sports Ground',
        'extra_img': '',
        'client_email': 'owner3@swatbiz.com',
        'client_password': 'client123'
    }
}

CATEGORIES = {
    'hospitals': {
        'title': 'Hospitals & Healthcare', 'icon': '🏥', 'place_label': 'Hospitals', 'staff_label': 'Doctors',
        'search_all_ph': 'Search hospital name, doctor or location (e.g. Saidu)...',
        'search_doc_ph': '🔍 Search Doctors by name, specialty (e.g. Cardiologist, Dr. Ali)...',
        'search_place_ph': '🏥 Search Hospitals or Clinics by name or location...',
        'info_title': '👨‍⚕️ Doctors, Clinic & Timings', 'extra_title': '🔬 Available Tests & Medical Services',
        'subcategories': ['General Hospital', 'Dental Clinic', 'Eye Specialist', 'Cardiology Clinic', 'Laboratory & Diagnostics'],
        'biz_ph': 'e.g. Saidu Teaching Hospital',
        'staff_heading': '🩺 Doctors, Clinic & Timings',
        'btn_text': '+ Add New Doctor',
        'extra_label': '🔬 Tests & Medical Services',
        'extra_ph': 'e.g. MRI, CT Scan, Blood Tests, Ultrasound, OPD Services...',
        'img_label': '🖼️ Hospital Services / Charges Banner Image (Optional)',
        'ph_name': 'Doctor Name (e.g. Dr. Ahmad)',
        'ph_spec': 'Specialty (e.g. Cardiologist)',
        'ph_qual': 'Qualifications (e.g. MBBS, FCPS)',
        'ph_appt': 'Appointment Timing (e.g. 9 AM - 2 PM)',
        'ph_clinic': 'Clinic Timing (e.g. Mon-Sat, 9 AM - 5 PM)',
        'ph_room': 'Clinic / Room (e.g. Room 12, OPD Block)',
        'ph_phone': 'Appointment Phone Number(s) (comma separated)'
    },
    'pharmacies': {
        'title': 'Pharmacies & Medical Stores', 'icon': '💊', 'place_label': 'Pharmacies', 'staff_label': 'Pharmacists',
        'search_all_ph': 'Search medicine, store or location...',
        'search_doc_ph': '🧑‍⚕️ Search Pharmacist or Staff by name...',
        'search_place_ph': '💊 Search Pharmacy or Medical Store by name...',
        'info_title': '🧑‍⚕️ Qualified Pharmacists & Staff', 'extra_title': '💊 Available Medicines & Supplies',
        'subcategories': ['Medical Store', 'Homeopathic Store', 'Herbal & Organic', 'Surgical Equipment'],
        'biz_ph': 'e.g. Swat City Pharmacy',
        'staff_heading': '🧑‍⚕️ Pharmacists & Key Staff',
        'btn_text': '+ Add New Pharmacist',
        'extra_label': '💊 Available Medicines & Supplies',
        'extra_ph': 'e.g. Life-saving drugs, Surgical tools, Vaccines, Homeopathic remedies...',
        'img_label': '🖼️ Medicines Price List / Store Image (Optional)',
        'ph_name': 'Pharmacist Name (e.g. Ali Khan)',
        'ph_spec': 'Role / Specialty (e.g. Senior Pharmacist)',
        'ph_qual': 'Qualifications (e.g. Pharm-D, B-Pharm)',
        'ph_appt': 'Shift Timing (e.g. 8 AM - 10 PM)',
        'ph_clinic': 'Store Working Days (e.g. Daily Open)',
        'ph_room': 'Counter / Section (e.g. Main Counter)',
        'ph_phone': 'Direct Phone / WhatsApp (comma separated)'
    },
    'restaurants': {
        'title': 'Restaurants & Cafes', 'icon': '🍽️', 'place_label': 'Restaurants', 'staff_label': 'Chefs',
        'search_all_ph': 'Search restaurant, dish or location (e.g. Fizagat)...',
        'search_doc_ph': '👨‍🍳 Search Chef or Manager by name...',
        'search_place_ph': '🍽️ Search Restaurants or Cafes by name...',
        'info_title': '👨‍🍳 Chefs & Dining Features', 'extra_title': '🍲 Menu, Special Dishes & Prices',
        'subcategories': ['Traditional / Shinwari', 'Fast Food & Burgers', 'BBQ & Grill', 'Coffee Shop & Cafe', 'Desi Restaurant'],
        'biz_ph': 'e.g. Khyber Shinwari Restaurant',
        'staff_heading': '👨‍🍳 Chefs, Staff & Dining Features',
        'btn_text': '+ Add New Staff / Chef',
        'extra_label': '🍲 Menu, Special Dishes & Prices',
        'extra_ph': 'e.g. Dumba Karahi (Rs. 2400/kg), Shinwari Tikka (Rs. 1800/kg), Zinger Burger...',
        'img_label': '🖼️ Menu / Rate Card Image (Optional)',
        'ph_name': 'Chef / Manager Name (e.g. Chef Rashid)',
        'ph_spec': 'Specialty (e.g. Master Grill & BBQ)',
        'ph_qual': 'Experience (e.g. 15+ Years Culinary Exp)',
        'ph_appt': 'Serving Hours (e.g. 12 PM - 11 PM)',
        'ph_clinic': 'Operating Days (e.g. Daily Open)',
        'ph_room': 'Dining Section (e.g. Family Cabin / Main Hall)',
        'ph_phone': 'Order / Booking Phone Number(s)'
    },
    'supermarts': {
        'title': 'Supermarts & Grocery', 'icon': '🛒', 'place_label': 'Supermarts', 'staff_label': 'Staff',
        'search_all_ph': 'Search store, item or area...',
        'search_doc_ph': '🏬 Search Store Contact Person / Manager...',
        'search_place_ph': '🛒 Search Supermarts or Stores by name...',
        'info_title': '🏬 Store Facilities & Staff', 'extra_title': '🛍️ Available Groceries & Products',
        'subcategories': ['General Store', 'Supermarket', 'Vegetables & Fruits', 'Bakery & Sweets'],
        'biz_ph': 'e.g. Swat Supermart',
        'staff_heading': '🏬 Store Management & Contacts',
        'btn_text': '+ Add New Contact / Staff',
        'extra_label': '🛍️ Featured Items & Groceries',
        'extra_ph': 'e.g. Fresh Fruits, Imported Chocolates, Bakery Items, Household Groceries...',
        'img_label': '🖼️ Products Rate List / Supermart Image (Optional)',
        'ph_name': 'Contact Person / Manager Name',
        'ph_spec': 'Designation / Role (e.g. Store Manager)',
        'ph_qual': 'Services (e.g. Home Delivery Specialist)',
        'ph_appt': 'Delivery Hours (e.g. 9 AM - 9 PM)',
        'ph_clinic': 'Store Timings (e.g. Mon-Sun, 8 AM - 11 PM)',
        'ph_room': 'Branch / Counter Name',
        'ph_phone': 'Home Delivery Phone Number(s)'
    },
    'property': {
        'title': 'Property Dealers', 'icon': '🏠', 'place_label': 'Agencies', 'staff_label': 'Agents',
        'search_all_ph': 'Search plot, house or dealer...',
        'search_doc_ph': '🧑‍💼 Search Real Estate Agent by name...',
        'search_place_ph': '🏠 Search Real Estate Agency or Office...',
        'info_title': '🧑‍💼 Agents & Dealers', 'extra_title': '🏡 Featured Plots & Properties',
        'subcategories': ['Plot & Land Dealer', 'House & Villa Rentals', 'Commercial Plaza', 'Real Estate Agency'],
        'biz_ph': 'e.g. Swat Real Estate Agency',
        'staff_heading': '🧑‍💼 Real Estate Agents & Consultants',
        'btn_text': '+ Add New Agent',
        'extra_label': '🏡 Available Plots & Property Deals',
        'extra_ph': 'e.g. 5 Marla Plot in Saidu Sharif, Commercial Shops on Canal Road...',
        'img_label': '🖼️ Property Brochure / Map Image (Optional)',
        'ph_name': 'Agent / Dealer Name (e.g. Usman Khan)',
        'ph_spec': 'Specialty (e.g. Residential Plots Specialist)',
        'ph_qual': 'Experience / Certification',
        'ph_appt': 'Meeting Hours (e.g. 10 AM - 6 PM)',
        'ph_clinic': 'Office Days (e.g. Mon - Sat)',
        'ph_room': 'Office Address / Desk',
        'ph_phone': 'Agent Direct Phone / WhatsApp'
    },
    'hotels': {
        'title': 'Hotels & Guest Houses', 'icon': '🏨', 'place_label': 'Hotels', 'staff_label': 'Receptionists',
        'search_all_ph': 'Search hotel or area...',
        'search_doc_ph': '🛎️ Search Reception / Manager by name...',
        'search_place_ph': '🏨 Search Hotels or Guest Houses...',
        'info_title': '🛎️ Management & Reception', 'extra_title': '🛏️ Rooms, Rates & Facilities',
        'subcategories': ['Luxury Hotel', 'Guest House', 'Resort', 'Budget Inn'],
        'biz_ph': 'e.g. Swat Serena Hotel',
        'staff_heading': '🛎️ Front Desk & Reception Contacts',
        'btn_text': '+ Add Receptionist / Manager',
        'extra_label': '🛏️ Room Types, Rates & Amenities',
        'extra_ph': 'e.g. Deluxe Family Room (Rs. 6000/night), Executive Suite, Free Wi-Fi, Hot Water...',
        'img_label': '🖼️ Room Tariffs / Hotel Banner Image (Optional)',
        'ph_name': 'Manager / Receptionist Name',
        'ph_spec': 'Role (e.g. Front Desk Manager)',
        'ph_qual': 'Services Provided',
        'ph_appt': 'Check-in / Check-out Hours',
        'ph_clinic': 'Reception Availability (e.g. 24/7)',
        'ph_room': 'Reception Desk / Block',
        'ph_phone': 'Booking Phone / WhatsApp Number(s)'
    },
    'education': {
        'title': 'Educational Institutes', 'icon': '🎓', 'place_label': 'Institutes', 'staff_label': 'Faculty',
        'search_all_ph': 'Search school, college, university or place (e.g. Saidu)...',
        'search_doc_ph': '👨‍🏫 Search Principal, Teacher or Faculty Name...',
        'search_place_ph': '🎓 Search School, College or Institute Name...',
        'info_title': '👨‍🏫 Faculty & Teachers Info', 'extra_title': '📚 Offered Courses & Programs',
        'subcategories': ['School', 'School & College', 'College', 'University', 'Academy & Tuition', 'Language & Computer Center'],
        'biz_ph': 'e.g. Swat Public School & College',
        'staff_heading': '👨‍🏫 Principal, Faculty & Admin Staff',
        'btn_text': '+ Add New Faculty / Staff',
        'extra_label': '📚 Offered Courses & Facilities',
        'extra_ph': 'e.g. Metric Science, FSc Pre-Medical, Computer Science Labs, Library, Transport...',
        'img_label': '🖼️ Fee Structure / Prospectus Image (Optional)',
        'ph_name': 'Faculty / Principal Name (e.g. Prof. Shah Zarin)',
        'ph_spec': 'Designation / Subject (e.g. Principal / Physics)',
        'ph_qual': 'Qualifications (e.g. M.Phil, PhD)',
        'ph_appt': 'Visiting Hours (e.g. 8 AM - 2 PM)',
        'ph_clinic': 'Working Days (e.g. Mon - Sat)',
        'ph_room': 'Office / Department Room',
        'ph_phone': 'Admission Office Phone Number(s)'
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
    @keyframes fadeOut {
        0% { opacity: 1; transform: scale(1); }
        100% { opacity: 0; transform: scale(0.9); }
    }
    .animate-fade-in { animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    .animate-modal { animation: modalPop 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    .animate-fade-out { animation: fadeOut 0.25s ease-out forwards; }
    
    .input-hover-effect { transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); }
    .input-hover-effect:hover { border-color: #3b82f6; box-shadow: 0 0 12px rgba(59, 130, 246, 0.25); transform: translateY(-1px); }
    .input-hover-effect:focus { border-color: #60a5fa; box-shadow: 0 0 18px rgba(59, 130, 246, 0.45); transform: translateY(-1px); }

    .btn-hover-effect { transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); }
    .btn-hover-effect:hover { transform: translateY(-2px) scale(1.02); box-shadow: 0 8px 20px -4px rgba(59, 130, 246, 0.4); }

    .card-hover-effect { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
    .card-hover-effect:hover { transform: translateY(-4px); border-color: #3b82f6; box-shadow: 0 12px 28px -6px rgba(0, 0, 0, 0.15), 0 0 15px rgba(59, 130, 246, 0.2); }

    /* DYNAMIC LIGHT / DARK MODE TOGGLE BUTTONS */
    .mode-toggle-btn {
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(203, 213, 225, 0.8);
        background-color: #f1f5f9;
        color: #475569;
    }
    .light .mode-toggle-btn:hover {
        background-color: #e2e8f0;
        color: #0f172a;
    }
    .light .mode-toggle-btn.active {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-color: #1d4ed8 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        font-weight: 800;
    }
    
    .dark .mode-toggle-btn {
        border: 1px solid rgba(255, 255, 255, 0.1);
        background-color: rgba(15, 23, 42, 0.6);
        color: #94a3b8;
    }
    .dark .mode-toggle-btn:hover {
        background-color: rgba(30, 41, 59, 0.9);
        color: #f8fafc;
        border-color: rgba(255, 255, 255, 0.25);
    }
    .dark .mode-toggle-btn.active {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1.5px solid #475569 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.15);
        font-weight: 800;
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
                <a href="/client/login" class="bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-4 py-2.5 rounded-xl text-sm font-bold transition">🔑 Login</a>
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
            <a href="''' + back_url + '''" class="text-sm font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-600/10 border border-blue-200 dark:border-blue-500/20 px-4 py-2 rounded-xl hover:bg-blue-600 hover:text-white transition flex items-center gap-2 shadow-sm btn-hover-effect">
                ← ''' + back_text + '''
            </a>
            <div class="flex items-center space-x-3">
                ''' + HEADER_THEME_BTN + '''
                <a href="/client/login" class="bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-4 py-2.5 rounded-xl text-sm font-bold transition">🔑 Login</a>
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
    
    search_mode = request.args.get('mode', 'all').strip()
    if search_mode not in ['all', 'doctors', 'hospitals']:
        search_mode = 'all'
    
    now = datetime.now()
    all_biz = [b for b in BUSINESSES.values() if b.get('category') == cat_slug and b.get('status') == 'approved' and b.get('expiry_date', now) >= now]
    filtered = []
    
    for b in all_biz:
        match_search = True
        match_subcat = True
        
        if search_query:
            doctors_str = " ".join([d.get('name', '') + " " + d.get('specialty', '') + " " + d.get('qualifications', '') for d in b.get('doctors', [])]).lower()
            
            if search_mode == 'doctors':
                if not (search_query in doctors_str):
                    match_search = False
            elif search_mode == 'hospitals':
                if not (search_query in b.get('name', '').lower() or search_query in b.get('address', '').lower() or search_query in b.get('subcategory', '').lower()):
                    match_search = False
            else:
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

    pills_html = f'<a href="/category/{cat_slug}?mode={search_mode}&q={search_query}" class="px-4 py-2 rounded-xl text-xs font-bold transition btn-hover-effect ' + \
                 ('bg-blue-600 text-white shadow-md' if not selected_subcat else 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-700') + '">All</a>'
    
    for sc in cat['subcategories']:
        is_active = (selected_subcat.lower() == sc.lower())
        active_cls = 'bg-blue-600 text-white shadow-md' if is_active else 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-700'
        pills_html += f'<a href="/category/{cat_slug}?subcat={sc}&mode={search_mode}&q={search_query}" class="px-4 py-2 rounded-xl text-xs font-bold transition btn-hover-effect {active_cls}">{sc}</a>'

    cards = ""
    for b in filtered:
        subcat_badge = '<span class="bg-indigo-100 dark:bg-indigo-600/20 text-indigo-700 dark:text-indigo-400 text-xs px-2.5 py-1 rounded-md font-semibold">' + b.get('subcategory', 'General') + '</span>' if b.get('subcategory') else ''
        map_url = get_google_maps_url(b['name'], b['address'])
        
        cards += '''
        <a href="/business/''' + b['id'] + '''" class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800/80 overflow-hidden card-hover-effect flex flex-col justify-between group shadow-sm dark:shadow-lg animate-modal">
            <img src="''' + b.get('image', 'https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=800&q=80') + '''" class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-500">
            <div class="p-6">
                <div class="mb-2">''' + subcat_badge + '''</div>
                <h3 class="text-xl font-bold text-gray-900 dark:text-white group-hover:text-blue-500 dark:group-hover:text-blue-400 transition-colors">''' + b['name'] + '''</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1 flex items-center gap-1.5">
                    📍 ''' + b['address'] + '''
                    <object><a href="''' + map_url + '''" target="_blank" onclick="event.stopPropagation();" class="text-[10px] font-bold bg-blue-100 dark:bg-blue-600/20 text-blue-600 dark:text-blue-400 px-2 py-0.5 rounded-md hover:underline">Map 🗺️</a></object>
                </p>
                <p class="text-xs text-blue-600 dark:text-blue-400 mt-2 font-bold">📞 ''' + b.get('phones', ['N/A'])[0] + '''</p>
                <span class="inline-block mt-4 text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-500/10 px-3 py-1.5 rounded-lg group-hover:bg-blue-600 group-hover:text-white transition">View Details →</span>
            </div>
        </a>
        '''
    if not cards:
        cards = '<div class="col-span-3 text-center py-20 text-gray-500 dark:text-gray-400"><p class="text-xl">No active or approved listings found matching your search.</p></div>'

    biz_data_list = []
    for b in all_biz:
        biz_data_list.append({
            'id': b['id'],
            'name': b['name'],
            'address': b['address'],
            'subcategory': b.get('subcategory', ''),
            'image': b.get('image', ''),
            'doctors': b.get('doctors', [])
        })
    biz_json_data = json.dumps(biz_data_list)

    initial_ph = cat['search_all_ph']
    if search_mode == 'doctors':
        initial_ph = cat['search_doc_ph']
    elif search_mode == 'hospitals':
        initial_ph = cat['search_place_ph']

    html = get_base_head(back_url="/", back_text="Back to Home") + '''
    <main class="max-w-7xl mx-auto px-4 py-12 animate-fade-in">
        <div class="mb-8 text-center">
            <span class="text-6xl inline-block animate-bounce">''' + cat['icon'] + '''</span>
            <h2 class="text-4xl font-extrabold mt-4 text-gray-900 dark:text-white">''' + cat['title'] + '''</h2>
            
            <!-- SEARCH BAR WRAPPER -->
            <div class="mt-6 max-w-2xl mx-auto">
                <form id="searchForm" method="GET" action="/category/''' + cat_slug + '''" class="space-y-2 text-left">
                    <input type="hidden" name="subcat" value="''' + selected_subcat + '''">
                    <input type="hidden" id="modeInput" name="mode" value="''' + search_mode + '''">
                    
                    <!-- DYNAMIC LIGHT & DARK MODE COMPATIBLE TOGGLE BUTTONS -->
                    <div class="flex items-center justify-start mb-1">
                        <div class="inline-flex items-center gap-1.5 bg-gray-200/80 dark:bg-slate-900/90 p-1.5 rounded-2xl border border-gray-300 dark:border-gray-800 shadow-md">
                            <button type="button" onclick="setSearchMode('all')" id="btnModeAll" class="mode-toggle-btn px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1 ` + ('active' if search_mode == 'all' else '') + `">
                                🔍 All
                            </button>
                            <button type="button" onclick="setSearchMode('doctors')" id="btnModeDoc" class="mode-toggle-btn px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1 ` + ('active' if search_mode == 'doctors' else '') + `">
                                👨‍⚕️ ''' + cat['staff_label'] + '''
                            </button>
                            <button type="button" onclick="setSearchMode('hospitals')" id="btnModePlace" class="mode-toggle-btn px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1 ` + ('active' if search_mode == 'hospitals' else '') + `">
                                🏥 ''' + cat['place_label'] + '''
                            </button>
                        </div>
                    </div>

                    <!-- BIG SEARCH BAR WITH DYNAMIC PLACEHOLDER -->
                    <div class="relative flex items-center gap-2">
                        <div class="relative w-full">
                            <input type="text" id="searchInput" name="q" value="''' + search_query + '''" placeholder="''' + initial_ph + '''" autocomplete="off" class="w-full px-6 py-4 rounded-2xl bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-white input-hover-effect outline-none text-base shadow-sm">
                            
                            <!-- DROPDOWN SUGGESTIONS -->
                            <div id="suggestionsDropdown" class="absolute left-0 right-0 top-full mt-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-2xl z-50 max-h-80 overflow-y-auto hidden"></div>
                        </div>
                        <button type="submit" class="bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-2xl font-bold btn-hover-effect shadow-md flex-shrink-0 text-base">Search</button>
                    </div>
                </form>
            </div>

            <!-- SUBCATEGORY FILTER PILLS -->
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
        var catPhAll = "''' + cat['search_all_ph'] + '''";
        var catPhDoc = "''' + cat['search_doc_ph'] + '''";
        var catPhPlace = "''' + cat['search_place_ph'] + '''";

        function setSearchMode(mode) {
            document.getElementById('modeInput').value = mode;
            var input = document.getElementById('searchInput');

            document.getElementById('btnModeAll').classList.remove('active');
            document.getElementById('btnModeDoc').classList.remove('active');
            document.getElementById('btnModePlace').classList.remove('active');

            if (mode === 'doctors') {
                document.getElementById('btnModeDoc').classList.add('active');
                input.placeholder = catPhDoc;
            } else if (mode === 'hospitals') {
                document.getElementById('btnModePlace').classList.add('active');
                input.placeholder = catPhPlace;
            } else {
                document.getElementById('btnModeAll').classList.add('active');
                input.placeholder = catPhAll;
            }

            var event = new Event('input', { bubbles: true });
            input.dispatchEvent(event);
        }

        window.addEventListener('DOMContentLoaded', function() {
            var currentMode = document.getElementById('modeInput').value || 'all';
            setSearchMode(currentMode);

            var input = document.getElementById('searchInput');
            var dropdown = document.getElementById('suggestionsDropdown');

            if (!input || !dropdown) return;

            input.addEventListener('input', function() {
                var q = this.value.trim().toLowerCase();
                var mode = document.getElementById('modeInput').value || 'all';
                
                dropdown.innerHTML = '';
                
                if (q.length < 1) {
                    dropdown.classList.add('hidden');
                    return;
                }

                var matchedItems = [];

                categoryBusinesses.forEach(function(b) {
                    var matchBiz = (b.name.toLowerCase().includes(q) || b.address.toLowerCase().includes(q) || b.subcategory.toLowerCase().includes(q));
                    
                    if ((mode === 'all' || mode === 'hospitals') && matchBiz) {
                        matchedItems.push({
                            type: 'business',
                            id: b.id,
                            title: b.name,
                            sub: '📍 ' + b.address,
                            badge: b.subcategory,
                            image: b.image || 'https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=150&q=80'
                        });
                    }

                    if (mode === 'all' || mode === 'doctors') {
                        if (b.doctors && b.doctors.length > 0) {
                            b.doctors.forEach(function(doc) {
                                var docName = doc.name || '';
                                var docSpec = doc.specialty || '';
                                var docQual = doc.qualifications || '';

                                if (docName.toLowerCase().includes(q) || docSpec.toLowerCase().includes(q) || docQual.toLowerCase().includes(q)) {
                                    matchedItems.push({
                                        type: 'doctor',
                                        id: b.id,
                                        title: '👨‍⚕️ ' + docName + ' (' + docSpec + ')',
                                        sub: '🏥 Hospital: ' + b.name,
                                        badge: docSpec,
                                        image: doc.doc_image || b.image || 'https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=150&q=80'
                                    });
                                }
                            });
                        }
                    }
                });

                if (matchedItems.length > 0) {
                    matchedItems.forEach(function(item) {
                        var div = document.createElement('div');
                        div.className = 'p-3 hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer flex justify-between items-center text-left border-b border-gray-100 dark:border-gray-800/50 last:border-0 gap-3';
                        div.innerHTML = `
                            <div class="flex items-center gap-3 min-w-0">
                                <img src="${item.image}" class="w-10 h-10 rounded-full object-cover border border-blue-500 shadow-sm flex-shrink-0">
                                <div class="truncate">
                                    <p class="font-bold text-sm text-gray-900 dark:text-white truncate">${item.title}</p>
                                    <p class="text-xs text-gray-500 dark:text-gray-400 truncate">${item.sub}</p>
                                </div>
                            </div>
                            <span class="text-[10px] bg-blue-100 dark:bg-blue-600/20 text-blue-600 dark:text-blue-400 px-2.5 py-1 rounded-md font-semibold flex-shrink-0 whitespace-nowrap">${item.badge}</span>
                        `;
                        div.addEventListener('click', function() {
                            window.location.href = '/business/' + item.id;
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
            <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-10 shadow-xl space-y-4 animate-modal">
                <span class="text-6xl inline-block">🔒</span>
                <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Listing Inactive or Password Protected</h1>
                <p class="text-gray-600 dark:text-gray-400 text-sm">Please enter the Client Password to unlock and view this listing.</p>
                
                <form method="POST" class="space-y-3 pt-2">
                    <input type="password" name="client_password" required placeholder="Enter Client Password" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
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
            doc_img = doc.get('doc_image', '')
            
            doc_json = json.dumps({
                'name': doc.get('name', ''),
                'specialty': doc.get('specialty', ''),
                'qualifications': quals,
                'appt_timing': doc.get('appt_timing', ''),
                'clinic_timing': doc.get('clinic_timing', ''),
                'room': doc.get('room', ''),
                'appt_numbers': appt_nums,
                'doc_image': doc_img,
                'hospital_name': b['name'],
                'hospital_address': b['address'],
                'hospital_phones': ", ".join(b.get('phones', []))
            }).replace("'", "&#39;")
            
            quals_badge = f'<p class="text-[11px] text-gray-500 dark:text-gray-400 italic">🎓 {quals}</p>' if quals else ''
            
            doc_avatar = f'<img src="{doc_img}" onclick="openImageZoom(\'{doc_img}\'); event.stopPropagation();" class="w-12 h-12 rounded-full object-cover border-2 border-blue-500 shadow-sm cursor-pointer hover:scale-110 transition duration-200" title="Click to zoom picture">' if doc_img else '<span class="text-2xl p-2 bg-blue-50 dark:bg-blue-600/20 rounded-full">👤</span>'

            doctors_cards_html += f'''
            <div onclick='openDoctorModal({doc_json})' class="doc-card-item bg-gray-50 dark:bg-gray-950 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 card-hover-effect space-y-2 cursor-pointer group animate-modal">
                <div class="flex justify-between items-start">
                    <div class="flex items-center gap-3">
                        {doc_avatar}
                        <div>
                            <h4 class="text-base font-extrabold text-blue-600 dark:text-blue-400 group-hover:underline">{doc.get('name', 'N/A')}</h4>
                            <p class="text-xs font-semibold text-indigo-600 dark:text-indigo-400">{doc.get('specialty', 'Specialist')}</p>
                            {quals_badge}
                        </div>
                    </div>
                    <span class="bg-blue-100 dark:bg-blue-600/20 text-blue-700 dark:text-blue-400 text-[10px] px-2.5 py-1 rounded-full font-bold">View Info →</span>
                </div>
                <div class="pt-2 border-t border-gray-200 dark:border-gray-800/80 text-xs space-y-1 text-gray-700 dark:text-gray-300">
                    <p>🕒 <strong>Appt Timing:</strong> {doc.get('appt_timing', 'N/A')}</p>
                    <p>📅 <strong>Clinic Days:</strong> {doc.get('clinic_timing', 'N/A')}</p>
                    <p>🚪 <strong>Room / Block:</strong> {doc.get('room', 'N/A')}</p>
                    <p>📞 <strong>Appt Phone(s):</strong> <span class="text-blue-600 dark:text-blue-400 font-bold">{appt_nums}</span></p>
                    <p class="text-[11px] text-gray-500 dark:text-gray-400 pt-1">🏥 <strong>Business:</strong> {b['name']} ({b['address']})</p>
                </div>
            </div>
            '''
    else:
        doctors_cards_html = f'''<p class="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-line">{b.get('special_info', 'Not specified')}</p>'''

    tests_dishes = b.get('tests_dishes', 'Not specified')
    extra_img = b.get('extra_img', '')
    
    extra_img_preview = f'''
    <div class="mt-2 flex items-center gap-3 bg-gray-100 dark:bg-gray-900 p-2 rounded-xl border border-gray-200 dark:border-gray-800 cursor-pointer" onclick="openImageZoom('{extra_img}'); event.stopPropagation();">
        <img src="{extra_img}" class="h-12 w-20 object-cover rounded-lg border border-gray-300 dark:border-gray-700">
        <span class="text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline">📸 View Attached Rates Banner / Picture →</span>
    </div>
    ''' if extra_img else ''

    phones_list = b.get('phones', ['N/A'])
    phones_html = ", ".join([f'<a href="tel:{p}" class="text-blue-600 dark:text-white hover:underline font-bold">{p}</a>' for p in phones_list])

    gallery_imgs = b.get('images', [b.get('image')])
    gallery_html = ""
    for img_url in gallery_imgs:
        if img_url:
            gallery_html += f'<img src="{img_url}" onclick="openImageZoom(\'{img_url}\')" title="Click to zoom" class="w-full h-48 md:h-56 object-cover rounded-2xl border border-gray-200 dark:border-gray-800 hover:scale-105 transition duration-300 shadow-md cursor-pointer">'

    map_direct_url = get_google_maps_url(b['name'], b['address'])

    html = get_base_head(back_url=category_back_url, back_text="Back to Category") + '''
    <div id="imageZoomModal" class="fixed inset-0 bg-black/80 backdrop-blur-md z-[99] flex items-center justify-center hidden p-4" onclick="closeImageZoom()">
        <div class="relative max-w-4xl max-h-[90vh] flex items-center justify-center animate-modal" onclick="event.stopPropagation()">
            <button type="button" onclick="closeImageZoom()" class="absolute -top-12 right-0 text-white hover:text-gray-300 text-2xl font-bold bg-gray-800/80 w-10 h-10 rounded-full flex items-center justify-center shadow-lg">×</button>
            <img id="zoomedImageElement" src="" class="max-w-full max-h-[85vh] object-contain rounded-2xl shadow-2xl border-2 border-gray-700">
        </div>
    </div>

    <div id="doctorModal" class="fixed inset-0 bg-black/60 dark:bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 md:p-8 max-w-md w-full shadow-2xl animate-modal space-y-4">
            <div class="flex justify-between items-start">
                <div class="flex items-center gap-3">
                    <div id="mDocAvatarContainer">
                        <span class="text-4xl p-2 bg-blue-50 dark:bg-blue-600/20 rounded-2xl">👤</span>
                    </div>
                    <div>
                        <h3 id="mDocName" class="text-xl font-black text-gray-900 dark:text-white">Name</h3>
                        <p id="mDocSpec" class="text-xs font-bold text-blue-600 dark:text-blue-400">Specialty</p>
                        <p id="mDocQuals" class="text-[11px] text-gray-500 dark:text-gray-400 italic">Qualifications</p>
                    </div>
                </div>
                <button type="button" onclick="closeDoctorModal()" class="text-gray-400 hover:text-gray-600 dark:hover:text-white text-xl font-bold bg-gray-100 dark:bg-gray-800 w-8 h-8 rounded-full flex items-center justify-center">×</button>
            </div>
            <div class="space-y-2 text-xs text-gray-700 dark:text-gray-300 pt-2 border-t border-gray-100 dark:border-gray-800">
                <p>🕒 <strong>Timing / Hours:</strong> <span id="mApptTiming" class="font-semibold text-gray-900 dark:text-white"></span></p>
                <p>📅 <strong>Days / Schedule:</strong> <span id="mClinicTiming" class="font-semibold text-gray-900 dark:text-white"></span></p>
                <p>🚪 <strong>Location / Room:</strong> <span id="mRoom" class="font-semibold text-gray-900 dark:text-white"></span></p>
                <p>📞 <strong>Direct Phone(s):</strong> <a id="mApptPhoneLink" href="#" class="text-blue-600 dark:text-blue-400 font-bold underline"></a></p>
            </div>
            <div class="bg-gray-50 dark:bg-gray-950 p-3 rounded-xl border border-gray-200 dark:border-gray-800 text-[11px] text-gray-600 dark:text-gray-400 space-y-1">
                <p>🏥 <strong id="mHospName"></strong></p>
                <p>📍 <span id="mHospAddress"></span></p>
            </div>
            <button type="button" onclick="closeDoctorModal()" class="w-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 py-2.5 rounded-xl font-bold text-xs">Close</button>
        </div>
    </div>

    <main class="max-w-5xl mx-auto px-4 py-8 animate-fade-in space-y-6">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 md:p-8 shadow-xl space-y-5 animate-modal">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-gray-100 dark:border-gray-800 pb-5">
                <div>
                    <span class="bg-blue-100 dark:bg-blue-600/20 text-blue-600 dark:text-blue-400 text-xs px-3 py-1 rounded-md font-bold uppercase tracking-wider">''' + b['category'] + '''</span>
                    <h1 class="text-2xl md:text-3xl font-black text-gray-900 dark:text-white mt-1">''' + b['name'] + '''</h1>
                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center gap-2">
                        📍 ''' + b['address'] + '''
                        <a href="''' + map_direct_url + '''" target="_blank" class="bg-blue-600 text-white text-[10px] font-bold px-2.5 py-1 rounded-lg hover:bg-blue-500 transition shadow-sm flex items-center gap-1">
                            🗺️ Open Live Map
                        </a>
                    </p>
                </div>
                <div class="text-left md:text-right space-y-1">
                    <p class="text-[11px] text-gray-400">Contact Number(s)</p>
                    <p class="text-xs">📞 ''' + phones_html + '''</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                ''' + gallery_html + '''
            </div>

            <div class="bg-gray-50 dark:bg-gray-950 p-3 rounded-2xl border border-gray-200 dark:border-gray-800">
                <input type="text" id="pageDetailSearch" onkeyup="filterPageStaff()" placeholder="🔍 Quick Search Doctors, Specialty or Services (e.g. Cardiologist, MRI, Dr. Ali)..." class="w-full p-2.5 rounded-xl bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-800 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
            </div>

            <div id="testsSectionBlock" class="bg-gray-50 dark:bg-gray-950 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 space-y-2 transition-all duration-300">
                <div class="flex justify-between items-center cursor-pointer" onclick="toggleTestsExpand()">
                    <h3 class="text-sm font-extrabold text-gray-900 dark:text-white flex items-center gap-2">
                        <span>''' + cat_meta['extra_title'] + '''</span>
                        <span id="expandBadge" class="bg-blue-100 dark:bg-blue-600/20 text-blue-600 dark:text-blue-400 text-[10px] px-2 py-0.5 rounded-md font-bold">Click to Expand</span>
                    </h3>
                    <button type="button" id="toggleExpandBtn" class="text-xs text-blue-600 dark:text-blue-400 font-bold hover:underline">View All ↓</button>
                </div>

                <p id="testsTextPreview" class="text-gray-700 dark:text-gray-300 text-xs leading-relaxed line-clamp-2">
                    ''' + tests_dishes + '''
                </p>

                <div id="testsFullContent" class="hidden space-y-3 pt-2 border-t border-gray-200 dark:border-gray-800">
                    <p class="text-gray-700 dark:text-gray-300 text-xs leading-relaxed whitespace-pre-line">''' + tests_dishes + '''</p>
                    ''' + extra_img_preview + '''
                </div>
            </div>

            <div id="doctorsSectionBlock" class="space-y-3 pt-2 border-t border-gray-100 dark:border-gray-800">
                <h3 class="text-lg font-black text-gray-900 dark:text-white">''' + cat_meta['info_title'] + '''</h3>
                <div id="doctorsListGrid" class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    ''' + doctors_cards_html + '''
                </div>
            </div>
        </div>
    </main>

    <script>
        function toggleTestsExpand() {
            var fullContent = document.getElementById('testsFullContent');
            var previewText = document.getElementById('testsTextPreview');
            var btn = document.getElementById('toggleExpandBtn');
            var badge = document.getElementById('expandBadge');

            if (fullContent.classList.contains('hidden')) {
                fullContent.classList.remove('hidden');
                previewText.classList.add('hidden');
                btn.innerText = 'Collapse ↑';
                badge.innerText = 'Expanded';
            } else {
                fullContent.classList.add('hidden');
                previewText.classList.remove('hidden');
                btn.innerText = 'View All ↓';
                badge.innerText = 'Click to Expand';
            }
        }

        function filterPageStaff() {
            var q = document.getElementById('pageDetailSearch').value.toLowerCase().trim();
            
            var docCards = document.querySelectorAll('.doc-card-item');
            docCards.forEach(function(card) {
                var text = card.innerText.toLowerCase();
                if (text.includes(q)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });

            var testsBlock = document.getElementById('testsSectionBlock');
            var testsText = document.getElementById('testsTextPreview').innerText.toLowerCase();
            if (q === '' || testsText.includes(q)) {
                testsBlock.style.display = 'block';
            } else {
                testsBlock.style.display = 'none';
            }
        }

        function openDoctorModal(doc) {
            document.getElementById('mDocName').innerText = doc.name;
            document.getElementById('mDocSpec').innerText = doc.specialty;
            document.getElementById('mDocQuals').innerText = doc.qualifications ? '🎓 ' + doc.qualifications : '';
            document.getElementById('mApptTiming').innerText = doc.appt_timing;
            document.getElementById('mClinicTiming').innerText = doc.clinic_timing;
            document.getElementById('mRoom').innerText = doc.room;
            
            var avatarContainer = document.getElementById('mDocAvatarContainer');
            if (doc.doc_image) {
                avatarContainer.innerHTML = '<img src="' + doc.doc_image + '" onclick="openImageZoom(\\'' + doc.doc_image + '\\')" title="Click to Zoom Image" class="w-16 h-16 rounded-full object-cover border-2 border-blue-500 shadow-md cursor-pointer hover:scale-110 transition duration-200">';
            } else {
                avatarContainer.innerHTML = '<span class="text-4xl p-2 bg-blue-50 dark:bg-blue-600/20 rounded-2xl">👤</span>';
            }

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

        function openImageZoom(imgSrc) {
            document.getElementById('zoomedImageElement').src = imgSrc;
            document.getElementById('imageZoomModal').classList.remove('hidden');
        }

        function closeImageZoom() {
            document.getElementById('imageZoomModal').classList.add('hidden');
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
        raw_phones = request.form.get('phone', '').strip()
        phones_list = [p.strip() for p in raw_phones.split(',') if p.strip()]
        client_email = request.form.get('client_email', '').strip().lower()
        client_password = request.form.get('client_password', '').strip()
        tests_dishes = request.form.get('tests_dishes', '').strip()
        extra_img = request.form.get('extra_img', '').strip()
        
        main_images = [img.strip() for img in request.form.getlist('main_images') if img.strip()]
        if not main_images:
            main_images = ['https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=800&q=80']

        doc_names = request.form.getlist('doc_name')
        doc_specs = request.form.getlist('doc_spec')
        doc_quals = request.form.getlist('doc_qual')
        doc_appts = request.form.getlist('doc_appt')
        doc_clinics = request.form.getlist('doc_clinic')
        doc_rooms = request.form.getlist('doc_room')
        doc_phones = request.form.getlist('doc_phone')
        doc_images = request.form.getlist('doc_image')
        
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
                    'appt_numbers': doc_phones[i].strip() if i < len(doc_phones) and doc_phones[i].strip() else raw_phones,
                    'doc_image': doc_images[i].strip() if i < len(doc_images) else ''
                })
        
        if name and category and client_email and client_password:
            # Generate 4-digit verification code and actually email it
            v_code = str(random.randint(1000, 9999))
            send_email(
                client_email,
                f"Your {SITE_NAME} verification code",
                f'''<div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px;">
                    <h2 style="color:#2563eb;margin-bottom:4px;">{SITE_NAME}</h2>
                    <p>Assalam o Alaikum,</p>
                    <p>Use the code below to verify your email and finish registering <strong>{name}</strong>:</p>
                    <p style="font-size:32px;font-weight:800;letter-spacing:6px;background:#f1f5f9;padding:14px 20px;border-radius:12px;text-align:center;">{v_code}</p>
                    <p style="color:#64748b;font-size:12px;">This code expires once used. If you didn't request this, you can ignore this email.</p>
                </div>'''
            )
            EMAIL_VERIFICATION_CODES[client_email] = {
                'code': v_code,
                'temp_data': {
                    'category': category,
                    'subcategory': subcategory if subcategory else 'General',
                    'name': name,
                    'address': address,
                    'phones': phones_list if phones_list else ['+92 300 0000000'],
                    'image': main_images[0],
                    'images': main_images,
                    'doctors': doctors_list,
                    'special_info': f"{len(doctors_list)} Staff / Specialist(s) Registered",
                    'tests_dishes': tests_dishes if tests_dishes else 'Services available.',
                    'extra_img': extra_img,
                    'client_email': client_email,
                    'client_password': client_password
                }
            }
            session['verify_email'] = client_email
            return redirect(url_for('verify_email_page'))
        else:
            error_msg = "Please fill in all required fields."

    cats_options = "".join([f'<option value="{k}">{v["title"]}</option>' for k, v in CATEGORIES.items()])
    categories_json = json.dumps(CATEGORIES)

    html = get_base_head(back_url="/", back_text="Back to Home") + '''
    <div id="deleteConfirmModal" class="fixed inset-0 bg-black/60 dark:bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 max-w-sm w-full shadow-2xl animate-modal text-center space-y-4">
            <span class="text-4xl inline-block">🗑️</span>
            <h3 class="text-lg font-extrabold text-gray-900 dark:text-white">Delete Entry?</h3>
            <p class="text-xs text-gray-500 dark:text-gray-400">Are you sure you want to remove this entry from your form?</p>
            <div class="flex items-center justify-center gap-3 pt-2">
                <button type="button" onclick="cancelDeleteDoctor()" class="w-1/2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 py-2.5 rounded-xl font-bold text-xs transition">Cancel</button>
                <button type="button" onclick="confirmDeleteDoctor()" class="w-1/2 bg-red-600 hover:bg-red-500 text-white py-2.5 rounded-xl font-bold text-xs shadow-md transition">Yes, Delete</button>
            </div>
        </div>
    </div>

    <main class="max-w-2xl mx-auto px-4 py-12 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6 animate-modal">
            <div class="text-center space-y-2">
                <span class="text-5xl inline-block">🚀</span>
                <h1 class="text-2xl font-black text-gray-900 dark:text-white">Register Your Business</h1>
                <p class="text-xs text-gray-500 dark:text-gray-400">Create an account with Email & Password to manage your listings.</p>
            </div>

            <form method="POST" class="space-y-6">
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Business Name *</label>
                    <input type="text" id="bizNameInput" name="name" required placeholder="e.g. Saidu Teaching Hospital" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Category *</label>
                        <select id="categorySelect" name="category" required onchange="updateCategoryFields()" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white outline-none text-sm">
                            ''' + cats_options + '''
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Subcategory / Type (Optional)</label>
                        <select id="subcategorySelect" name="subcategory" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white outline-none text-sm">
                        </select>
                    </div>
                </div>

                <!-- ADDRESS FIELD WITH LIVE LOCATION AUTO-DETECT GPS -->
                <div>
                    <div class="flex justify-between items-center mb-1">
                        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300">Address / Location *</label>
                        <button type="button" onclick="detectLiveLocation()" class="text-[11px] font-bold text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1">
                            📍 Detect My Live GPS Location
                        </button>
                    </div>
                    <input type="text" id="addressInput" name="address" required placeholder="e.g. Mingora Bazaar, Swat (OR Click Detect Live Location above)" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                    <p id="locationStatus" class="text-[10px] text-gray-400 mt-1 hidden"></p>
                </div>

                <div>
                    <div class="flex justify-between items-center mb-1">
                        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300">Phone Number(s) *</label>
                        <span class="text-[10px] text-gray-400">Separate multiple numbers with commas (,)</span>
                    </div>
                    <input type="text" name="phone" required placeholder="e.g. +92 300 1234567, +92 946 9240125" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>

                <div class="pt-2 border-t border-gray-100 dark:border-gray-800 space-y-3">
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300">🖼️ Main / Gallery Pictures (Multiple Pictures Allowed)</label>
                    <div id="mainImagesContainer" class="space-y-3">
                        <div class="main-img-row flex flex-col sm:flex-row gap-2 items-center">
                            <label class="w-full sm:w-auto bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-2 rounded-xl text-xs font-bold cursor-pointer transition flex items-center justify-center gap-1 border border-gray-300 dark:border-gray-700">
                                📁 Gallery
                                <input type="file" accept="image/*" onchange="handleMainFileUpload(event, this)" class="hidden">
                            </label>
                            <span class="text-[10px] text-gray-400">OR</span>
                            <input type="text" name="main_images" placeholder="Paste Image URL link..." class="w-full p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                        </div>
                    </div>
                    <button type="button" onclick="addMainImageRow()" class="text-xs bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-2 rounded-xl font-bold transition flex items-center gap-1">
                        + Add Another Main Picture
                    </button>
                </div>

                <div class="pt-4 border-t border-gray-100 dark:border-gray-800 space-y-4">
                    <div class="flex justify-between items-center">
                        <label id="staffSectionHeading" class="block text-sm font-extrabold text-blue-600 dark:text-blue-400">🩺 Doctors, Clinic & Timings</label>
                    </div>

                    <div id="doctorsContainer" class="space-y-4">
                        <div class="doc-entry animate-modal bg-gray-50 dark:bg-gray-950 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 space-y-3 relative">
                            <button type="button" onclick="requestDeleteDoctor(this)" title="Delete Entry" class="absolute top-3 right-3 bg-red-600 hover:bg-red-700 text-white w-8 h-8 rounded-full flex items-center justify-center font-black text-sm shadow-md transition transform hover:scale-110 z-10 border border-red-400">✕</button>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <input type="text" name="doc_name" placeholder="Name (e.g. Dr. Ahmad)" class="doc-input-name p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                                <input type="text" name="doc_spec" placeholder="Specialty (e.g. Cardiologist)" class="doc-input-spec p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                            </div>
                            <div>
                                <input type="text" name="doc_qual" placeholder="Qualifications (e.g. MBBS, FCPS)" class="doc-input-qual w-full p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                            </div>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <input type="text" name="doc_appt" placeholder="Timing (e.g. 9 AM - 2 PM)" class="doc-input-appt p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                                <input type="text" name="doc_clinic" placeholder="Days (e.g. Mon-Sat, 9 AM - 5 PM)" class="doc-input-clinic p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                            </div>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <input type="text" name="doc_room" placeholder="Location / Room (e.g. Room 12)" class="doc-input-room p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                                <input type="text" name="doc_phone" placeholder="Direct Phone (comma separated)" class="doc-input-phone p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                            </div>

                            <div class="pt-2 border-t border-gray-200 dark:border-gray-800/60 space-y-2">
                                <label class="block text-[11px] font-bold text-gray-500 dark:text-gray-400">🖼️ Doctor Profile Picture (Single Photo)</label>
                                <div class="flex flex-col sm:flex-row gap-2 items-center">
                                    <label class="w-full sm:w-auto bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-2 rounded-xl text-xs font-bold cursor-pointer transition flex items-center justify-center gap-1 border border-gray-300 dark:border-gray-700">
                                        📁 Gallery
                                        <input type="file" accept="image/*" onchange="handleDocFileUpload(event, this)" class="hidden">
                                    </label>
                                    <span class="text-[10px] text-gray-400">OR</span>
                                    <input type="text" name="doc_image" placeholder="Paste Image URL link..." class="doc-img-input w-full p-2 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                                </div>
                                <div class="doc-preview-box hidden flex items-center gap-2 pt-1">
                                    <img class="doc-preview-img w-8 h-8 rounded-full object-cover border border-blue-500">
                                    <span class="text-[10px] text-green-500 font-bold">✓ Photo Selected</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <button id="addStaffBtn" type="button" onclick="addDoctorRow()" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-xl text-xs font-bold btn-hover-effect flex items-center gap-2 shadow-md">
                        + Add New Entry
                    </button>
                </div>

                <div class="pt-4 border-t border-gray-100 dark:border-gray-800 space-y-3">
                    <label id="extraSectionLabel" class="block text-xs font-bold text-gray-700 dark:text-gray-300">🔬 Available Tests & Medical Services</label>
                    <textarea id="extraSectionTextarea" name="tests_dishes" rows="3" placeholder="e.g. MRI, CT Scan, Blood Tests, Ultrasound..." class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm"></textarea>
                    
                    <div class="space-y-2">
                        <label id="extraImgLabel" class="block text-[11px] font-bold text-gray-500 dark:text-gray-400">🖼️ Hospital Services / Charges Banner Image (Optional)</label>
                        
                        <div class="flex flex-col sm:flex-row gap-3 items-center">
                            <label class="w-full sm:w-auto bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-4 py-2.5 rounded-xl text-xs font-bold cursor-pointer transition flex items-center justify-center gap-2 border border-gray-300 dark:border-gray-700">
                                📁 Select from Gallery
                                <input type="file" accept="image/*" onchange="handleFileUpload(event)" class="hidden">
                            </label>
                            <span class="text-xs text-gray-400">OR</span>
                            <input type="text" id="extraImgInput" name="extra_img" placeholder="Paste Image URL link here..." class="w-full p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white input-hover-effect outline-none">
                        </div>

                        <div id="imagePreviewContainer" class="hidden mt-2 p-2 bg-gray-100 dark:bg-gray-950 rounded-2xl border border-gray-200 dark:border-gray-800 flex items-center gap-3">
                            <img id="previewImg" src="" class="w-16 h-16 object-cover rounded-xl">
                            <div class="text-xs">
                                <p class="font-bold text-green-500">✓ Image Selected</p>
                                <p class="text-gray-400 text-[10px]">Preview attached to listing</p>
                            </div>
                        </div>
                    </div>
                </div>

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

                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3.5 rounded-xl font-bold btn-hover-effect text-sm shadow-lg">Register & Verify Email</button>
            </form>

            ''' + (f'<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-3 rounded-xl text-red-600 dark:text-red-400 text-xs text-center font-semibold">{error_msg}</div>' if error_msg else '') + '''
        </div>
    </main>

    <script>
        var categoriesMeta = ''' + categories_json + ''';
        var pendingDeleteTarget = null;

        function detectLiveLocation() {
            var status = document.getElementById('locationStatus');
            var addrInput = document.getElementById('addressInput');
            status.classList.remove('hidden');
            status.innerText = "⏳ Detecting GPS location...";

            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    var lat = position.coords.latitude.toFixed(5);
                    var lon = position.coords.longitude.toFixed(5);
                    addrInput.value = lat + ", " + lon;
                    status.innerText = "✓ Live location captured successfully! (Coordinates saved)";
                    status.className = "text-[10px] text-green-500 mt-1";
                }, function(error) {
                    status.innerText = "⚠️ Location permission denied or unavailable. Please enter manually.";
                    status.className = "text-[10px] text-red-400 mt-1";
                });
            } else {
                status.innerText = "⚠️ Geolocation not supported by browser. Enter manually.";
                status.className = "text-[10px] text-red-400 mt-1";
            }
        }

        function handleMainFileUpload(event, fileInput) {
            var file = event.target.files[0];
            if (file) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    var base64Img = e.target.result;
                    var row = fileInput.closest('.main-img-row');
                    var urlInput = row.querySelector('input[name="main_images"]');
                    urlInput.value = base64Img;
                };
                reader.readAsDataURL(file);
            }
        }

        function addMainImageRow() {
            var container = document.getElementById('mainImagesContainer');
            var div = document.createElement('div');
            div.className = 'main-img-row flex flex-col sm:flex-row gap-2 items-center animate-modal';
            div.innerHTML = `
                <label class="w-full sm:w-auto bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-2 rounded-xl text-xs font-bold cursor-pointer transition flex items-center justify-center gap-1 border border-gray-300 dark:border-gray-700">
                    📁 Gallery
                    <input type="file" accept="image/*" onchange="handleMainFileUpload(event, this)" class="hidden">
                </label>
                <span class="text-[10px] text-gray-400">OR</span>
                <input type="text" name="main_images" placeholder="Paste Image URL link..." class="w-full p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
            `;
            container.appendChild(div);
        }

        function handleFileUpload(event) {
            var file = event.target.files[0];
            if (file) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    var base64Img = e.target.result;
                    document.getElementById('extraImgInput').value = base64Img;
                    document.getElementById('previewImg').src = base64Img;
                    document.getElementById('imagePreviewContainer').classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        }

        function handleDocFileUpload(event, fileInput) {
            var file = event.target.files[0];
            if (file) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    var base64Img = e.target.result;
                    var docEntry = fileInput.closest('.doc-entry');
                    var imgInput = docEntry.querySelector('.doc-img-input');
                    var previewBox = docEntry.querySelector('.doc-preview-box');
                    var previewImg = docEntry.querySelector('.doc-preview-img');

                    imgInput.value = base64Img;
                    previewImg.src = base64Img;
                    previewBox.classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        }

        function updateCategoryFields() {
            var catSelect = document.getElementById('categorySelect');
            var subcatSelect = document.getElementById('subcategorySelect');
            var bizNameInput = document.getElementById('bizNameInput');
            var selectedCatKey = catSelect.value;
            var catObj = categoriesMeta[selectedCatKey];

            if (!catObj) return;

            if (catObj.biz_ph) {
                bizNameInput.placeholder = catObj.biz_ph;
            }

            subcatSelect.innerHTML = '';
            var optNone = document.createElement('option');
            optNone.value = '';
            optNone.text = 'Select Subcategory (Optional)';
            subcatSelect.appendChild(optNone);

            if (catObj.subcategories) {
                catObj.subcategories.forEach(function(sub) {
                    var option = document.createElement('option');
                    option.value = sub;
                    option.text = sub;
                    subcatSelect.appendChild(option);
                });
            }

            document.getElementById('staffSectionHeading').innerText = catObj.staff_heading;
            document.getElementById('addStaffBtn').innerText = catObj.btn_text;
            document.getElementById('extraSectionLabel').innerText = catObj.extra_label;
            document.getElementById('extraSectionTextarea').placeholder = catObj.extra_ph;
            document.getElementById('extraImgLabel').innerText = catObj.img_label;

            document.querySelectorAll('.doc-entry').forEach(function(row) {
                applyPlaceholdersToRow(row, catObj);
            });
        }

        function applyPlaceholdersToRow(row, catObj) {
            row.querySelector('.doc-input-name').placeholder = catObj.ph_name;
            row.querySelector('.doc-input-spec').placeholder = catObj.ph_spec;
            row.querySelector('.doc-input-qual').placeholder = catObj.ph_qual;
            row.querySelector('.doc-input-appt').placeholder = catObj.ph_appt;
            row.querySelector('.doc-input-clinic').placeholder = catObj.ph_clinic;
            row.querySelector('.doc-input-room').placeholder = catObj.ph_room;
            row.querySelector('.doc-input-phone').placeholder = catObj.ph_phone;
        }

        function addDoctorRow() {
            var catSelect = document.getElementById('categorySelect');
            var catObj = categoriesMeta[catSelect.value];
            var container = document.getElementById('doctorsContainer');
            
            var div = document.createElement('div');
            div.className = 'doc-entry animate-modal bg-gray-50 dark:bg-gray-950 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 space-y-3 relative mt-3';
            div.innerHTML = `
                <button type="button" onclick="requestDeleteDoctor(this)" title="Delete Entry" class="absolute top-3 right-3 bg-red-600 hover:bg-red-700 text-white w-8 h-8 rounded-full flex items-center justify-center font-black text-sm shadow-md transition transform hover:scale-110 z-10 border border-red-400">✕</button>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input type="text" name="doc_name" placeholder="" class="doc-input-name p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                    <input type="text" name="doc_spec" placeholder="" class="doc-input-spec p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                </div>
                <div>
                    <input type="text" name="doc_qual" placeholder="" class="doc-input-qual w-full p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input type="text" name="doc_appt" placeholder="" class="doc-input-appt p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                    <input type="text" name="doc_clinic" placeholder="" class="doc-input-clinic p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input type="text" name="doc_room" placeholder="" class="doc-input-room p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                    <input type="text" name="doc_phone" placeholder="" class="doc-input-phone p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                </div>

                <div class="pt-2 border-t border-gray-200 dark:border-gray-800/60 space-y-2">
                    <label class="block text-[11px] font-bold text-gray-500 dark:text-gray-400">🖼️ Photo / Picture (Optional - Gallery or URL)</label>
                    <div class="flex flex-col sm:flex-row gap-2 items-center">
                        <label class="w-full sm:w-auto bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-2 rounded-xl text-xs font-bold cursor-pointer transition flex items-center justify-center gap-1 border border-gray-300 dark:border-gray-700">
                            📁 Gallery
                            <input type="file" accept="image/*" onchange="handleDocFileUpload(event, this)" class="hidden">
                        </label>
                        <span class="text-[10px] text-gray-400">OR</span>
                        <input type="text" name="doc_image" placeholder="Paste Image URL link..." class="doc-img-input w-full p-2 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                    </div>
                    <div class="doc-preview-box hidden flex items-center gap-2 pt-1">
                        <img class="doc-preview-img w-8 h-8 rounded-full object-cover border border-blue-500">
                        <span class="text-[10px] text-green-500 font-bold">✓ Photo Selected</span>
                    </div>
                </div>
            `;
            container.appendChild(div);
            applyPlaceholdersToRow(div, catObj);
        }

        function requestDeleteDoctor(btn) {
            pendingDeleteTarget = btn.closest('.doc-entry');
            document.getElementById('deleteConfirmModal').classList.remove('hidden');
        }

        function cancelDeleteDoctor() {
            pendingDeleteTarget = null;
            document.getElementById('deleteConfirmModal').classList.add('hidden');
        }

        function confirmDeleteDoctor() {
            if (pendingDeleteTarget) {
                var entries = document.querySelectorAll('.doc-entry');
                if (entries.length > 1) {
                    pendingDeleteTarget.classList.remove('animate-modal');
                    pendingDeleteTarget.classList.add('animate-fade-out');
                    setTimeout(function() {
                        pendingDeleteTarget.remove();
                        pendingDeleteTarget = null;
                    }, 200);
                } else {
                    pendingDeleteTarget.querySelectorAll('input').forEach(input => input.value = '');
                    pendingDeleteTarget = null;
                }
            }
            document.getElementById('deleteConfirmModal').classList.add('hidden');
        }

        window.addEventListener('DOMContentLoaded', function() {
            updateCategoryFields();
        });
    </script>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email_page():
    email = session.get('verify_email')
    if not email or email not in EMAIL_VERIFICATION_CODES:
        return redirect(url_for('register'))

    actual_code = EMAIL_VERIFICATION_CODES[email]['code']
    error_msg = ""

    if request.method == 'POST':
        entered_code = request.form.get('verification_code', '').strip()
        if entered_code == actual_code:
            # Save business permanently
            temp_data = EMAIL_VERIFICATION_CODES[email]['temp_data']
            new_id = str(len(BUSINESSES) + 1)
            temp_data['id'] = new_id
            temp_data['status'] = 'pending'
            temp_data['payment_method'] = 'Bank Transfer / JazzCash'
            temp_data['payment_ref'] = 'PENDING-VERIFY'
            temp_data['payment_status'] = 'pending'
            temp_data['joining_date'] = datetime.now()
            temp_data['expiry_date'] = datetime.now() + timedelta(days=30)
            
            BUSINESSES[new_id] = temp_data
            
            # Clear verification session and log in client
            session.pop('verify_email', None)
            del EMAIL_VERIFICATION_CODES[email]
            session['client_logged_email'] = email
            return redirect(url_for('client_dashboard'))
        else:
            error_msg = "Invalid 4-digit code! Please check and try again."

    html = get_base_head(back_url="/register", back_text="Back to Register") + '''
    <main class="max-w-md mx-auto px-4 py-20 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6 animate-modal text-center">
            <span class="text-5xl inline-block">✉️</span>
            <h1 class="text-2xl font-black text-gray-900 dark:text-white">Email Verification</h1>
            <p class="text-xs text-gray-500 dark:text-gray-400">We have sent a 4-digit verification code to <strong class="text-blue-600 dark:text-blue-400">''' + email + '''</strong>. Please check your inbox (and spam folder).</p>

            <form method="POST" class="space-y-4 text-left">
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Enter 4-Digit Code</label>
                    <input type="text" name="verification_code" required maxlength="4" placeholder="1234" class="w-full p-3.5 text-center tracking-widest text-xl font-bold rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none">
                </div>
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3.5 rounded-xl font-bold btn-hover-effect text-sm shadow-lg">Verify & Complete Registration</button>
            </form>
            ''' + (f'<p class="text-red-500 text-xs font-semibold">{error_msg}</p>' if error_msg else '') + '''
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/client/forgot-password', methods=['GET', 'POST'])
def client_forgot_password():
    error_msg = ""
    success_msg = ""
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        matched = False
        for b in BUSINESSES.values():
            if b.get('client_email', '').lower() == email:
                matched = True
                break
        
        if matched:
            reset_code = str(random.randint(1000, 9999))
            PASSWORD_RESET_CODES[email] = reset_code
            send_email(
                email,
                f"Your {SITE_NAME} password reset code",
                f'''<div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px;">
                    <h2 style="color:#2563eb;margin-bottom:4px;">{SITE_NAME}</h2>
                    <p>We received a request to reset your password. Use the code below:</p>
                    <p style="font-size:32px;font-weight:800;letter-spacing:6px;background:#f1f5f9;padding:14px 20px;border-radius:12px;text-align:center;">{reset_code}</p>
                    <p style="color:#64748b;font-size:12px;">If you didn't request this, you can safely ignore this email.</p>
                </div>'''
            )
            success_msg = "Password reset instructions sent! Please check your email for the 4-digit reset code."
            session['reset_email'] = email
        else:
            error_msg = "No business account found with this email address."

    html = get_base_head(back_url="/client/login", back_text="Back to Login") + '''
    <main class="max-w-md mx-auto px-4 py-20 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6 animate-modal">
            <div class="text-center space-y-2">
                <span class="text-5xl inline-block">🔑</span>
                <h1 class="text-2xl font-black text-gray-900 dark:text-white">Forgot Password</h1>
                <p class="text-xs text-gray-500 dark:text-gray-400">Enter your registered email to reset password.</p>
            </div>

            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Email Address</label>
                    <input type="email" name="email" required placeholder="owner@gmail.com" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3.5 rounded-xl font-bold btn-hover-effect text-sm shadow-lg">Send Reset Code</button>
            </form>

            ''' + (f'<div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 p-3 rounded-xl text-green-600 dark:text-green-400 text-xs text-center font-semibold space-y-2"><p>{success_msg}</p><a href="/client/reset-password" class="inline-block bg-green-600 text-white px-4 py-2 rounded-lg font-bold">Proceed to Reset Password →</a></div>' if success_msg else '') + '''
            ''' + (f'<p class="text-red-500 text-xs text-center font-semibold">{error_msg}</p>' if error_msg else '') + '''
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/client/reset-password', methods=['GET', 'POST'])
def client_reset_password():
    email = session.get('reset_email', '')
    error_msg = ""
    
    if request.method == 'POST':
        entered_code = request.form.get('code', '').strip()
        new_password = request.form.get('new_password', '').strip()
        
        if email in PASSWORD_RESET_CODES and PASSWORD_RESET_CODES[email] == entered_code:
            for b in BUSINESSES.values():
                if b.get('client_email', '').lower() == email.lower():
                    b['client_password'] = new_password
            
            PASSWORD_RESET_CODES.pop(email, None)
            session.pop('reset_email', None)
            return redirect(url_for('client_login'))
        else:
            error_msg = "Invalid verification code!"

    html = get_base_head(back_url="/client/login", back_text="Back to Login") + '''
    <main class="max-w-md mx-auto px-4 py-20 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6 animate-modal">
            <div class="text-center space-y-2">
                <span class="text-5xl inline-block">🔒</span>
                <h1 class="text-2xl font-black text-gray-900 dark:text-white">Reset Password</h1>
                <p class="text-xs text-gray-500 dark:text-gray-400">Enter code and set your new password.</p>
            </div>

            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">4-Digit Code</label>
                    <input type="text" name="code" required maxlength="4" placeholder="1234" class="w-full p-3.5 tracking-widest text-center text-lg font-bold rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">New Password</label>
                    <input type="password" name="new_password" required placeholder="Enter new secure password" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3.5 rounded-xl font-bold btn-hover-effect text-sm shadow-lg">Update Password</button>
            </form>
            ''' + (f'<p class="text-red-500 text-xs text-center font-semibold">{error_msg}</p>' if error_msg else '') + '''
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/admin', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
        
    error_msg = ""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error_msg = "Incorrect Admin Password!"

    html = get_base_head(back_url="/", back_text="Back to Home") + '''
    <main class="max-w-md mx-auto px-4 py-20 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6 animate-modal">
            <div class="text-center space-y-2">
                <span class="text-5xl inline-block">🛡️</span>
                <h1 class="text-2xl font-black text-gray-900 dark:text-white">Admin Login</h1>
                <p class="text-xs text-gray-500 dark:text-gray-400">Enter master password to access system control.</p>
            </div>

            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Admin Password</label>
                    <input type="password" name="password" required placeholder="••••••••" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>
                <button type="submit" class="w-full bg-red-600 hover:bg-red-500 text-white py-3.5 rounded-xl font-bold btn-hover-effect text-sm shadow-lg">Access Admin Dashboard</button>
            </form>
            ''' + (f'<p class="text-red-500 text-xs text-center font-semibold">{error_msg}</p>' if error_msg else '') + '''
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    active_tab = request.args.get('tab', 'businesses')
    filter_status = request.args.get('filter', 'all')

    total_listings = len(BUSINESSES)
    pending_biz_count = len([b for b in BUSINESSES.values() if b.get('status') == 'pending'])
    paid_pay_count = len([b for b in BUSINESSES.values() if b.get('payment_status') == 'paid'])
    pending_pay_count = len([b for b in BUSINESSES.values() if b.get('payment_status') == 'pending'])

    biz_rows = ""
    for b in BUSINESSES.values():
        status = b.get('status', 'pending')
        if filter_status == 'pending_biz' and status != 'pending':
            continue
        if filter_status == 'approved_biz' and status != 'approved':
            continue

        status_color = 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' if status == 'approved' else 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
        expiry_str = b.get('expiry_date').strftime('%d %b %Y') if b.get('expiry_date') else 'N/A'
        
        biz_rows += f'''
        <tr class="border-b border-gray-100 dark:border-gray-800 text-xs text-gray-800 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <td class="p-4 font-bold">{b['id']}</td>
            <td class="p-4">
                <p class="font-bold text-sm text-gray-900 dark:text-white">{b['name']}</p>
                <p class="text-[11px] text-gray-500">📧 {b.get('client_email', 'N/A')}</p>
            </td>
            <td class="p-4 uppercase font-semibold text-[11px]">{b['category']}</td>
            <td class="p-4">
                <span class="px-2.5 py-1 rounded-md text-[10px] font-extrabold uppercase {status_color}">{status}</span>
            </td>
            <td class="p-4">{expiry_str}</td>
            <td class="p-4 space-x-2 flex items-center flex-wrap gap-y-1">
                <a href="/admin/preview/{b['id']}" class="bg-indigo-600 hover:bg-indigo-500 text-white px-2.5 py-1 rounded-lg text-[11px] font-bold btn-hover-effect">👁️ Preview</a>
                <a href="/admin/status/{b['id']}/approved" class="bg-green-600 hover:bg-green-500 text-white px-2.5 py-1 rounded-lg text-[11px] font-bold btn-hover-effect">Approve</a>
                <a href="/admin/status/{b['id']}/pending" class="bg-yellow-600 hover:bg-yellow-500 text-white px-2.5 py-1 rounded-lg text-[11px] font-bold btn-hover-effect">Pending</a>
                <a href="/admin/extend/{b['id']}" class="bg-blue-600 hover:bg-blue-500 text-white px-2.5 py-1 rounded-lg text-[11px] font-bold btn-hover-effect">+30 Days</a>
                <a href="/admin/edit/{b['id']}" class="bg-gray-700 hover:bg-gray-600 text-white px-2.5 py-1 rounded-lg text-[11px] font-bold btn-hover-effect">✏️ Edit</a>
                <a href="/admin/delete/{b['id']}" onclick="return confirm('Delete listing?');" class="bg-red-600 hover:bg-red-500 text-white px-2.5 py-1 rounded-lg text-[11px] font-bold btn-hover-effect">Delete</a>
            </td>
        </tr>
        '''

    pay_rows = ""
    for b in BUSINESSES.values():
        pay_status = b.get('payment_status', 'pending')
        if filter_status == 'pending_pay' and pay_status != 'pending':
            continue
        if filter_status == 'paid_pay' and pay_status != 'paid':
            continue

        pay_color = 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' if pay_status == 'paid' else 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
        
        pay_rows += f'''
        <tr class="border-b border-gray-100 dark:border-gray-800 text-xs text-gray-800 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <td class="p-4 font-bold">{b['id']}</td>
            <td class="p-4 font-bold text-sm text-gray-900 dark:text-white">{b['name']}</td>
            <td class="p-4 font-semibold text-blue-600 dark:text-blue-400">{b.get('payment_method', 'N/A')}</td>
            <td class="p-4 text-gray-500">{b.get('payment_ref', 'N/A')}</td>
            <td class="p-4">
                <span class="px-2.5 py-1 rounded-md text-[10px] font-extrabold uppercase {pay_color}">{pay_status}</span>
            </td>
            <td class="p-4 space-x-2 flex items-center">
                <a href="/admin/payment/{b['id']}/paid" class="bg-green-600 hover:bg-green-500 text-white px-3 py-1 rounded-lg text-[11px] font-bold btn-hover-effect">Mark Paid</a>
                <a href="/admin/payment/{b['id']}/pending" class="bg-yellow-600 hover:bg-yellow-500 text-white px-3 py-1 rounded-lg text-[11px] font-bold btn-hover-effect">Mark Pending</a>
            </td>
        </tr>
        '''

    biz_tab_active = 'bg-blue-600 text-white shadow-md' if active_tab == 'businesses' else 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-700'
    pay_tab_active = 'bg-blue-600 text-white shadow-md' if active_tab == 'payments' else 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-700'

    active_table_html = ""
    if active_tab == 'payments':
        active_table_html = f'''
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl overflow-hidden shadow-xl animate-modal">
            <div class="p-6 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center">
                <h3 class="text-lg font-bold text-gray-900 dark:text-white">💳 Payment Requests & Verification</h3>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-gray-50 dark:bg-gray-800/80 text-[11px] font-extrabold uppercase text-gray-500 border-b border-gray-200 dark:border-gray-800">
                            <th class="p-4">ID</th>
                            <th class="p-4">Business Name</th>
                            <th class="p-4">Payment Method</th>
                            <th class="p-4">Reference / Receipt</th>
                            <th class="p-4">Payment Status</th>
                            <th class="p-4">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {pay_rows}
                    </tbody>
                </table>
            </div>
        </div>
        '''
    else:
        active_table_html = f'''
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl overflow-hidden shadow-xl animate-modal">
            <div class="p-6 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center">
                <h3 class="text-lg font-bold text-gray-900 dark:text-white">🏢 Business Registrations & Approvals</h3>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-gray-50 dark:bg-gray-800/80 text-[11px] font-extrabold uppercase text-gray-500 border-b border-gray-200 dark:border-gray-800">
                            <th class="p-4">ID</th>
                            <th class="p-4">Business Name & Owner</th>
                            <th class="p-4">Category</th>
                            <th class="p-4">Status</th>
                            <th class="p-4">Expiry Date</th>
                            <th class="p-4">Admin Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {biz_rows}
                    </tbody>
                </table>
            </div>
        </div>
        '''

    html = get_base_head(back_url="/", back_text="Back to Home") + '''
    <main class="max-w-7xl mx-auto px-4 py-12 animate-fade-in space-y-8">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white dark:bg-gray-900 p-6 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-xl">
            <div>
                <h1 class="text-3xl font-black text-gray-900 dark:text-white">🛡️ Master Admin Control Panel</h1>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Manage business approvals and payment verifications.</p>
            </div>
            <a href="/admin/logout" class="bg-red-600 hover:bg-red-500 text-white px-5 py-2.5 rounded-xl text-xs font-bold transition shadow-md">Admin Logout</a>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <a href="/admin/dashboard?tab=businesses&filter=all" class="bg-white dark:bg-gray-900 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm text-center card-hover-effect block">
                <p class="text-xs text-gray-500 font-bold uppercase">Total Listings</p>
                <p class="text-2xl font-black text-blue-600 dark:text-blue-400 mt-1">''' + str(total_listings) + '''</p>
            </a>
            <a href="/admin/dashboard?tab=businesses&filter=pending_biz" class="bg-white dark:bg-gray-900 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm text-center card-hover-effect block">
                <p class="text-xs text-gray-500 font-bold uppercase">Pending Business Approvals</p>
                <p class="text-2xl font-black text-yellow-500 mt-1">''' + str(pending_biz_count) + '''</p>
            </a>
            <a href="/admin/dashboard?tab=payments&filter=paid_pay" class="bg-white dark:bg-gray-900 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm text-center card-hover-effect block">
                <p class="text-xs text-gray-500 font-bold uppercase">Paid Payments</p>
                <p class="text-2xl font-black text-green-500 mt-1">''' + str(paid_pay_count) + '''</p>
            </a>
            <a href="/admin/dashboard?tab=payments&filter=pending_pay" class="bg-white dark:bg-gray-900 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm text-center card-hover-effect block">
                <p class="text-xs text-gray-500 font-bold uppercase">Pending Payments</p>
                <p class="text-2xl font-black text-yellow-500 mt-1">''' + str(pending_pay_count) + '''</p>
            </a>
        </div>

        <div class="flex gap-3">
            <a href="/admin/dashboard?tab=businesses" class="px-6 py-3 rounded-2xl font-bold text-xs transition btn-hover-effect ''' + biz_tab_active + '''">🏢 Business Registrations</a>
            <a href="/admin/dashboard?tab=payments" class="px-6 py-3 rounded-2xl font-bold text-xs transition btn-hover-effect ''' + pay_tab_active + '''">💳 Payment Requests</a>
        </div>

        ''' + active_table_html + '''
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/admin/status/<b_id>/<new_status>')
def admin_change_status(b_id, new_status):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if b_id in BUSINESSES:
        BUSINESSES[b_id]['status'] = new_status
    return redirect(url_for('admin_dashboard', tab='businesses'))

@app.route('/admin/payment/<b_id>/<new_pay_status>')
def admin_change_payment(b_id, new_pay_status):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if b_id in BUSINESSES:
        BUSINESSES[b_id]['payment_status'] = new_pay_status
    return redirect(url_for('admin_dashboard', tab='payments'))

@app.route('/admin/preview/<b_id>')
def admin_preview_business(b_id):
    """Lets admin see EXACTLY what the owner submitted (full details, images,
    doctors/staff, etc.) before approving - plus quick Approve/Edit/Delete actions."""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if b_id not in BUSINESSES:
        abort(404)

    b = BUSINESSES[b_id]
    cat_meta = CATEGORIES.get(b.get('category'), {})
    status = b.get('status', 'pending')
    status_color = 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' if status == 'approved' else 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
    pay_status = b.get('payment_status', 'pending')
    pay_color = 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' if pay_status == 'paid' else 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
    joining_str = b.get('joining_date').strftime('%d %b %Y') if b.get('joining_date') else 'N/A'
    expiry_str = b.get('expiry_date').strftime('%d %b %Y') if b.get('expiry_date') else 'N/A'

    images_html = ""
    for img in b.get('images', []) or ([b['image']] if b.get('image') else []):
        images_html += f'<img src="{img}" class="w-full h-40 object-cover rounded-xl border border-gray-200 dark:border-gray-800">'
    if not images_html:
        images_html = '<p class="text-xs text-gray-400">No pictures uploaded.</p>'

    staff_label = cat_meta.get('staff_label', 'Staff')
    staff_html = ""
    doctors = b.get('doctors', [])
    if doctors:
        for d in doctors:
            d_img = f'<img src="{d.get("doc_image")}" class="w-14 h-14 rounded-full object-cover border-2 border-blue-500">' if d.get('doc_image') else '<span class="text-3xl">👤</span>'
            staff_html += f'''
            <div class="bg-gray-50 dark:bg-gray-950 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 flex gap-4 items-start">
                {d_img}
                <div class="text-xs space-y-1">
                    <p class="text-sm font-extrabold text-blue-600 dark:text-blue-400">{d.get('name', 'N/A')}</p>
                    <p class="font-semibold text-indigo-600 dark:text-indigo-400">{d.get('specialty', '')}</p>
                    <p class="text-gray-500 dark:text-gray-400">🎓 {d.get('qualifications', '')}</p>
                    <p>🕒 {d.get('appt_timing', '')} &middot; 📅 {d.get('clinic_timing', '')}</p>
                    <p>🚪 {d.get('room', '')}</p>
                    <p class="font-bold text-blue-600 dark:text-blue-400">📞 {d.get('appt_numbers', '')}</p>
                </div>
            </div>
            '''
    else:
        staff_html = f'<p class="text-xs text-gray-400">No {staff_label.lower()} added.</p>'

    html = get_base_head(back_url="/admin/dashboard", back_text="Back to Admin Dashboard") + '''
    <main class="max-w-4xl mx-auto px-4 py-10 animate-fade-in space-y-6">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 shadow-xl space-y-4">
            <div class="flex flex-wrap justify-between items-start gap-3">
                <div>
                    <h1 class="text-2xl font-black text-gray-900 dark:text-white">👁️ Preview: ''' + b['name'] + '''</h1>
                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">This is exactly what will go live once approved. Review everything before approving.</p>
                </div>
                <div class="flex gap-2">
                    <span class="px-3 py-1.5 rounded-lg text-[11px] font-extrabold uppercase ''' + status_color + '''">''' + status + '''</span>
                    <span class="px-3 py-1.5 rounded-lg text-[11px] font-extrabold uppercase ''' + pay_color + '''">Payment: ''' + pay_status + '''</span>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-gray-700 dark:text-gray-300 pt-2 border-t border-gray-100 dark:border-gray-800">
                <p><strong>Category:</strong> ''' + cat_meta.get('title', b.get('category', 'N/A')) + ''' ''' + (('&middot; ' + b.get('subcategory')) if b.get('subcategory') else '') + '''</p>
                <p><strong>Address:</strong> ''' + b.get('address', 'N/A') + '''</p>
                <p><strong>Phone(s):</strong> ''' + ", ".join(b.get('phones', [])) + '''</p>
                <p><strong>Owner email:</strong> ''' + b.get('client_email', 'N/A') + '''</p>
                <p><strong>Joined:</strong> ''' + joining_str + '''</p>
                <p><strong>Expiry:</strong> ''' + expiry_str + '''</p>
                <p><strong>Payment method:</strong> ''' + b.get('payment_method', 'N/A') + '''</p>
                <p><strong>Payment reference:</strong> ''' + b.get('payment_ref', 'N/A') + '''</p>
            </div>

            <div class="pt-3 border-t border-gray-100 dark:border-gray-800">
                <h3 class="text-sm font-extrabold text-gray-800 dark:text-gray-200 mb-2">🖼️ Pictures</h3>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3">''' + images_html + '''</div>
            </div>

            <div class="pt-3 border-t border-gray-100 dark:border-gray-800">
                <h3 class="text-sm font-extrabold text-gray-800 dark:text-gray-200 mb-2">''' + cat_meta.get('info_title', staff_label) + '''</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">''' + staff_html + '''</div>
            </div>

            <div class="pt-3 border-t border-gray-100 dark:border-gray-800">
                <h3 class="text-sm font-extrabold text-gray-800 dark:text-gray-200 mb-2">''' + cat_meta.get('extra_title', 'Details') + '''</h3>
                <p class="text-xs text-gray-600 dark:text-gray-400 whitespace-pre-line">''' + (b.get('tests_dishes') or 'Not specified') + '''</p>
                ''' + (f'<img src="{b.get("extra_img")}" class="w-full max-w-sm mt-3 rounded-xl border border-gray-200 dark:border-gray-800">' if b.get('extra_img') else '') + '''
            </div>

            <div class="pt-4 border-t border-gray-100 dark:border-gray-800 flex flex-wrap gap-2">
                <a href="/admin/status/''' + b['id'] + '''/approved" class="bg-green-600 hover:bg-green-500 text-white px-4 py-2.5 rounded-xl text-xs font-bold btn-hover-effect">✓ Approve Listing</a>
                <a href="/admin/status/''' + b['id'] + '''/pending" class="bg-yellow-600 hover:bg-yellow-500 text-white px-4 py-2.5 rounded-xl text-xs font-bold btn-hover-effect">Mark Pending</a>
                <a href="/admin/edit/''' + b['id'] + '''" class="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2.5 rounded-xl text-xs font-bold btn-hover-effect">✏️ Edit Details</a>
                <a href="/admin/delete/''' + b['id'] + '''" onclick="return confirm('Delete this listing permanently?');" class="bg-red-600 hover:bg-red-500 text-white px-4 py-2.5 rounded-xl text-xs font-bold btn-hover-effect">🗑️ Delete</a>
            </div>
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/admin/edit/<b_id>', methods=['GET', 'POST'])
def admin_edit_business(b_id):
    """Lets admin fix/update any field of a submitted business (same fields the
    owner filled in at registration) without touching status/payment history."""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if b_id not in BUSINESSES:
        abort(404)

    b = BUSINESSES[b_id]
    error_msg = ""

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        subcategory = request.form.get('subcategory', '').strip()
        address = request.form.get('address', '').strip()
        raw_phones = request.form.get('phone', '').strip()
        phones_list = [p.strip() for p in raw_phones.split(',') if p.strip()]
        tests_dishes = request.form.get('tests_dishes', '').strip()
        extra_img = request.form.get('extra_img', '').strip()

        main_images = [img.strip() for img in request.form.getlist('main_images') if img.strip()]

        doc_names = request.form.getlist('doc_name')
        doc_specs = request.form.getlist('doc_spec')
        doc_quals = request.form.getlist('doc_qual')
        doc_appts = request.form.getlist('doc_appt')
        doc_clinics = request.form.getlist('doc_clinic')
        doc_rooms = request.form.getlist('doc_room')
        doc_phones = request.form.getlist('doc_phone')
        doc_images = request.form.getlist('doc_image')

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
                    'appt_numbers': doc_phones[i].strip() if i < len(doc_phones) and doc_phones[i].strip() else raw_phones,
                    'doc_image': doc_images[i].strip() if i < len(doc_images) else ''
                })

        if name and category and address:
            b['name'] = name
            b['category'] = category
            b['subcategory'] = subcategory if subcategory else 'General'
            b['address'] = address
            b['phones'] = phones_list if phones_list else b.get('phones', [])
            if main_images:
                b['images'] = main_images
                b['image'] = main_images[0]
            b['doctors'] = doctors_list
            b['tests_dishes'] = tests_dishes if tests_dishes else b.get('tests_dishes', '')
            b['extra_img'] = extra_img
            return redirect(url_for('admin_preview_business', b_id=b_id))
        else:
            error_msg = "Please fill in all required fields."

    cats_options = "".join([
        f'<option value="{k}" {"selected" if k == b.get("category") else ""}>{v["title"]}</option>'
        for k, v in CATEGORIES.items()
    ])
    categories_json = json.dumps(CATEGORIES)

    doctor_rows_html = ""
    doctors = b.get('doctors', []) or [{}]
    for d in doctors:
        img_val = d.get('doc_image', '')
        preview_html = f'''
            <div class="doc-preview-box flex items-center gap-2 pt-1">
                <img class="doc-preview-img w-8 h-8 rounded-full object-cover border border-blue-500" src="{img_val}">
                <span class="text-[10px] text-green-500 font-bold">✓ Photo Selected</span>
            </div>''' if img_val else '<div class="doc-preview-box hidden flex items-center gap-2 pt-1"><img class="doc-preview-img w-8 h-8 rounded-full object-cover border border-blue-500"><span class="text-[10px] text-green-500 font-bold">✓ Photo Selected</span></div>'
        doctor_rows_html += f'''
        <div class="doc-entry animate-modal bg-gray-50 dark:bg-gray-950 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 space-y-3 relative">
            <button type="button" onclick="requestDeleteDoctor(this)" title="Delete Entry" class="absolute top-3 right-3 bg-red-600 hover:bg-red-700 text-white w-8 h-8 rounded-full flex items-center justify-center font-black text-sm shadow-md transition transform hover:scale-110 z-10 border border-red-400">✕</button>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input type="text" name="doc_name" value="{d.get('name', '')}" placeholder="Name" class="doc-input-name p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                <input type="text" name="doc_spec" value="{d.get('specialty', '')}" placeholder="Specialty" class="doc-input-spec p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
            </div>
            <div>
                <input type="text" name="doc_qual" value="{d.get('qualifications', '')}" placeholder="Qualifications" class="doc-input-qual w-full p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input type="text" name="doc_appt" value="{d.get('appt_timing', '')}" placeholder="Timing" class="doc-input-appt p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                <input type="text" name="doc_clinic" value="{d.get('clinic_timing', '')}" placeholder="Days" class="doc-input-clinic p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input type="text" name="doc_room" value="{d.get('room', '')}" placeholder="Room" class="doc-input-room p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                <input type="text" name="doc_phone" value="{d.get('appt_numbers', '')}" placeholder="Phone(s)" class="doc-input-phone p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
            </div>
            <div class="pt-2 border-t border-gray-200 dark:border-gray-800/60 space-y-2">
                <label class="block text-[11px] font-bold text-gray-500 dark:text-gray-400">🖼️ Photo (Gallery or URL)</label>
                <div class="flex flex-col sm:flex-row gap-2 items-center">
                    <label class="w-full sm:w-auto bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-2 rounded-xl text-xs font-bold cursor-pointer transition flex items-center justify-center gap-1 border border-gray-300 dark:border-gray-700">
                        📁 Gallery
                        <input type="file" accept="image/*" onchange="handleDocFileUpload(event, this)" class="hidden">
                    </label>
                    <span class="text-[10px] text-gray-400">OR</span>
                    <input type="text" name="doc_image" value="{img_val}" placeholder="Paste Image URL link..." class="doc-img-input w-full p-2 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                </div>
                {preview_html}
            </div>
        </div>
        '''

    main_images_rows_html = ""
    existing_images = b.get('images', []) or ([b['image']] if b.get('image') else [])
    if not existing_images:
        existing_images = ['']
    for img in existing_images:
        main_images_rows_html += f'''
        <div class="main-img-row flex flex-col sm:flex-row gap-2 items-center">
            <label class="w-full sm:w-auto bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-2 rounded-xl text-xs font-bold cursor-pointer transition flex items-center justify-center gap-1 border border-gray-300 dark:border-gray-700">
                📁 Gallery
                <input type="file" accept="image/*" onchange="handleMainFileUpload(event, this)" class="hidden">
            </label>
            <span class="text-[10px] text-gray-400">OR</span>
            <input type="text" name="main_images" value="{img}" placeholder="Paste Image URL link..." class="w-full p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
        </div>
        '''

    html = get_base_head(back_url="/admin/preview/" + b_id, back_text="Back to Preview") + '''
    <div id="deleteConfirmModal" class="fixed inset-0 bg-black/60 dark:bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 max-w-sm w-full shadow-2xl animate-modal text-center space-y-4">
            <span class="text-4xl inline-block">🗑️</span>
            <h3 class="text-lg font-extrabold text-gray-900 dark:text-white">Delete Entry?</h3>
            <p class="text-xs text-gray-500 dark:text-gray-400">Are you sure you want to remove this entry from your form?</p>
            <div class="flex items-center justify-center gap-3 pt-2">
                <button type="button" onclick="cancelDeleteDoctor()" class="w-1/2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 py-2.5 rounded-xl font-bold text-xs transition">Cancel</button>
                <button type="button" onclick="confirmDeleteDoctor()" class="w-1/2 bg-red-600 hover:bg-red-500 text-white py-2.5 rounded-xl font-bold text-xs shadow-md transition">Yes, Delete</button>
            </div>
        </div>
    </div>

    <main class="max-w-2xl mx-auto px-4 py-12 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6 animate-modal">
            <div class="text-center space-y-2">
                <span class="text-5xl inline-block">✏️</span>
                <h1 class="text-2xl font-black text-gray-900 dark:text-white">Edit: ''' + b['name'] + '''</h1>
                <p class="text-xs text-gray-500 dark:text-gray-400">Admin edit - status, payment history and login are not affected.</p>
            </div>

            <form method="POST" class="space-y-6">
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Business Name *</label>
                    <input type="text" id="bizNameInput" name="name" required value="''' + b.get('name', '') + '''" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Category *</label>
                        <select id="categorySelect" name="category" required onchange="updateCategoryFields()" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white outline-none text-sm">
                            ''' + cats_options + '''
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Subcategory / Type</label>
                        <select id="subcategorySelect" name="subcategory" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white outline-none text-sm">
                        </select>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Address / Location *</label>
                    <input type="text" id="addressInput" name="address" required value="''' + b.get('address', '') + '''" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>

                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Phone Number(s) *</label>
                    <input type="text" name="phone" required value="''' + ", ".join(b.get('phones', [])) + '''" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>

                <div class="pt-2 border-t border-gray-100 dark:border-gray-800 space-y-3">
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300">🖼️ Main / Gallery Pictures</label>
                    <div id="mainImagesContainer" class="space-y-3">
                        ''' + main_images_rows_html + '''
                    </div>
                    <button type="button" onclick="addMainImageRow()" class="text-xs bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-2 rounded-xl font-bold transition flex items-center gap-1">
                        + Add Another Main Picture
                    </button>
                </div>

                <div class="pt-4 border-t border-gray-100 dark:border-gray-800 space-y-4">
                    <div class="flex justify-between items-center">
                        <label id="staffSectionHeading" class="block text-sm font-extrabold text-blue-600 dark:text-blue-400">Staff / Doctors</label>
                    </div>
                    <div id="doctorsContainer" class="space-y-4">
                        ''' + doctor_rows_html + '''
                    </div>
                    <button id="addStaffBtn" type="button" onclick="addDoctorRow()" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-xl text-xs font-bold btn-hover-effect flex items-center gap-2 shadow-md">
                        + Add New Entry
                    </button>
                </div>

                <div class="pt-4 border-t border-gray-100 dark:border-gray-800 space-y-3">
                    <label id="extraSectionLabel" class="block text-xs font-bold text-gray-700 dark:text-gray-300">Tests / Services / Menu</label>
                    <textarea id="extraSectionTextarea" name="tests_dishes" rows="3" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">''' + (b.get('tests_dishes') or '') + '''</textarea>

                    <div class="space-y-2">
                        <label id="extraImgLabel" class="block text-[11px] font-bold text-gray-500 dark:text-gray-400">Banner Image (Optional)</label>
                        <div class="flex flex-col sm:flex-row gap-3 items-center">
                            <label class="w-full sm:w-auto bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-4 py-2.5 rounded-xl text-xs font-bold cursor-pointer transition flex items-center justify-center gap-2 border border-gray-300 dark:border-gray-700">
                                📁 Select from Gallery
                                <input type="file" accept="image/*" onchange="handleFileUpload(event)" class="hidden">
                            </label>
                            <span class="text-xs text-gray-400">OR</span>
                            <input type="text" id="extraImgInput" name="extra_img" value="''' + (b.get('extra_img') or '') + '''" class="w-full p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white input-hover-effect outline-none">
                        </div>
                    </div>
                </div>

                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3.5 rounded-xl font-bold btn-hover-effect text-sm shadow-lg">Save Changes</button>
            </form>

            ''' + (f'<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-3 rounded-xl text-red-600 dark:text-red-400 text-xs text-center font-semibold">{error_msg}</div>' if error_msg else '') + '''
        </div>
    </main>

    <script>
        var categoriesMeta = ''' + categories_json + ''';
        var pendingDeleteTarget = null;
        var initialSubcategory = "''' + b.get('subcategory', '') + '''";

        function handleMainFileUpload(event, fileInput) {
            var file = event.target.files[0];
            if (file) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    var row = fileInput.closest('.main-img-row');
                    row.querySelector('input[name="main_images"]').value = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        }

        function addMainImageRow() {
            var container = document.getElementById('mainImagesContainer');
            var div = document.createElement('div');
            div.className = 'main-img-row flex flex-col sm:flex-row gap-2 items-center animate-modal';
            div.innerHTML = `
                <label class="w-full sm:w-auto bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-2 rounded-xl text-xs font-bold cursor-pointer transition flex items-center justify-center gap-1 border border-gray-300 dark:border-gray-700">
                    📁 Gallery
                    <input type="file" accept="image/*" onchange="handleMainFileUpload(event, this)" class="hidden">
                </label>
                <span class="text-[10px] text-gray-400">OR</span>
                <input type="text" name="main_images" placeholder="Paste Image URL link..." class="w-full p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
            `;
            container.appendChild(div);
        }

        function handleFileUpload(event) {
            var file = event.target.files[0];
            if (file) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('extraImgInput').value = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        }

        function handleDocFileUpload(event, fileInput) {
            var file = event.target.files[0];
            if (file) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    var docEntry = fileInput.closest('.doc-entry');
                    var imgInput = docEntry.querySelector('.doc-img-input');
                    var previewBox = docEntry.querySelector('.doc-preview-box');
                    var previewImg = docEntry.querySelector('.doc-preview-img');
                    imgInput.value = e.target.result;
                    previewImg.src = e.target.result;
                    previewBox.classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        }

        function updateCategoryFields() {
            var catSelect = document.getElementById('categorySelect');
            var subcatSelect = document.getElementById('subcategorySelect');
            var selectedCatKey = catSelect.value;
            var catObj = categoriesMeta[selectedCatKey];
            if (!catObj) return;

            subcatSelect.innerHTML = '';
            var optNone = document.createElement('option');
            optNone.value = '';
            optNone.text = 'Select Subcategory (Optional)';
            subcatSelect.appendChild(optNone);

            if (catObj.subcategories) {
                catObj.subcategories.forEach(function(sub) {
                    var option = document.createElement('option');
                    option.value = sub;
                    option.text = sub;
                    if (sub === initialSubcategory) option.selected = true;
                    subcatSelect.appendChild(option);
                });
            }

            document.getElementById('staffSectionHeading').innerText = catObj.staff_heading || 'Staff';
            document.getElementById('addStaffBtn').innerText = catObj.btn_text || '+ Add New Entry';
            document.getElementById('extraSectionLabel').innerText = catObj.extra_label || 'Details';
            document.getElementById('extraImgLabel').innerText = catObj.img_label || 'Banner Image';

            document.querySelectorAll('.doc-entry').forEach(function(row) {
                applyPlaceholdersToRow(row, catObj);
            });
        }

        function applyPlaceholdersToRow(row, catObj) {
            row.querySelector('.doc-input-name').placeholder = catObj.ph_name;
            row.querySelector('.doc-input-spec').placeholder = catObj.ph_spec;
            row.querySelector('.doc-input-qual').placeholder = catObj.ph_qual;
            row.querySelector('.doc-input-appt').placeholder = catObj.ph_appt;
            row.querySelector('.doc-input-clinic').placeholder = catObj.ph_clinic;
            row.querySelector('.doc-input-room').placeholder = catObj.ph_room;
            row.querySelector('.doc-input-phone').placeholder = catObj.ph_phone;
        }

        function addDoctorRow() {
            var catSelect = document.getElementById('categorySelect');
            var catObj = categoriesMeta[catSelect.value];
            var container = document.getElementById('doctorsContainer');
            var div = document.createElement('div');
            div.className = 'doc-entry animate-modal bg-gray-50 dark:bg-gray-950 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 space-y-3 relative mt-3';
            div.innerHTML = `
                <button type="button" onclick="requestDeleteDoctor(this)" title="Delete Entry" class="absolute top-3 right-3 bg-red-600 hover:bg-red-700 text-white w-8 h-8 rounded-full flex items-center justify-center font-black text-sm shadow-md transition transform hover:scale-110 z-10 border border-red-400">✕</button>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input type="text" name="doc_name" placeholder="" class="doc-input-name p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                    <input type="text" name="doc_spec" placeholder="" class="doc-input-spec p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                </div>
                <div>
                    <input type="text" name="doc_qual" placeholder="" class="doc-input-qual w-full p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input type="text" name="doc_appt" placeholder="" class="doc-input-appt p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                    <input type="text" name="doc_clinic" placeholder="" class="doc-input-clinic p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input type="text" name="doc_room" placeholder="" class="doc-input-room p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                    <input type="text" name="doc_phone" placeholder="" class="doc-input-phone p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                </div>
                <div class="pt-2 border-t border-gray-200 dark:border-gray-800/60 space-y-2">
                    <label class="block text-[11px] font-bold text-gray-500 dark:text-gray-400">🖼️ Photo (Optional - Gallery or URL)</label>
                    <div class="flex flex-col sm:flex-row gap-2 items-center">
                        <label class="w-full sm:w-auto bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-2 rounded-xl text-xs font-bold cursor-pointer transition flex items-center justify-center gap-1 border border-gray-300 dark:border-gray-700">
                            📁 Gallery
                            <input type="file" accept="image/*" onchange="handleDocFileUpload(event, this)" class="hidden">
                        </label>
                        <span class="text-[10px] text-gray-400">OR</span>
                        <input type="text" name="doc_image" placeholder="Paste Image URL link..." class="doc-img-input w-full p-2 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-xs text-gray-900 dark:text-white outline-none input-hover-effect">
                    </div>
                    <div class="doc-preview-box hidden flex items-center gap-2 pt-1">
                        <img class="doc-preview-img w-8 h-8 rounded-full object-cover border border-blue-500">
                        <span class="text-[10px] text-green-500 font-bold">✓ Photo Selected</span>
                    </div>
                </div>
            `;
            container.appendChild(div);
            applyPlaceholdersToRow(div, catObj);
        }

        function requestDeleteDoctor(btn) {
            pendingDeleteTarget = btn.closest('.doc-entry');
            document.getElementById('deleteConfirmModal').classList.remove('hidden');
        }

        function cancelDeleteDoctor() {
            pendingDeleteTarget = null;
            document.getElementById('deleteConfirmModal').classList.add('hidden');
        }

        function confirmDeleteDoctor() {
            if (pendingDeleteTarget) {
                var entries = document.querySelectorAll('.doc-entry');
                if (entries.length > 1) {
                    pendingDeleteTarget.classList.remove('animate-modal');
                    pendingDeleteTarget.classList.add('animate-fade-out');
                    setTimeout(function() {
                        pendingDeleteTarget.remove();
                        pendingDeleteTarget = null;
                    }, 200);
                } else {
                    pendingDeleteTarget.querySelectorAll('input').forEach(input => input.value = '');
                    pendingDeleteTarget = null;
                }
            }
            document.getElementById('deleteConfirmModal').classList.add('hidden');
        }

        window.addEventListener('DOMContentLoaded', function() {
            updateCategoryFields();
        });
    </script>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/admin/extend/<b_id>')
def admin_extend_expiry(b_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if b_id in BUSINESSES:
        curr_exp = BUSINESSES[b_id].get('expiry_date', datetime.now())
        BUSINESSES[b_id]['expiry_date'] = curr_exp + timedelta(days=30)
    return redirect(url_for('admin_dashboard', tab='businesses'))

@app.route('/admin/delete/<b_id>')
def admin_delete_business(b_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if b_id in BUSINESSES:
        del BUSINESSES[b_id]
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

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
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6 animate-modal">
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
                    <div class="flex justify-between items-center mb-1">
                        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300">Password</label>
                        <a href="/client/forgot-password" class="text-[11px] text-blue-600 dark:text-blue-400 font-bold hover:underline">Forgot Password?</a>
                    </div>
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
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-md flex flex-col justify-between space-y-4 card-hover-effect animate-modal">
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
                    <a href="/client/edit/{b['id']}" class="bg-blue-50 dark:bg-blue-600/20 text-blue-600 dark:text-blue-400 px-3 py-1.5 rounded-xl text-xs font-bold transition hover:bg-blue-600 hover:text-white btn-hover-effect">Edit ✏️</a>
                    <a href="/client/delete/{b['id']}" onclick="return confirm('Delete this business?');" class="bg-red-50 dark:bg-red-600/20 text-red-600 dark:text-red-400 px-3 py-1.5 rounded-xl text-xs font-bold transition hover:bg-red-600 hover:text-white btn-hover-effect">Delete 🗑️</a>
                </div>
            </div>
        </div>
        '''

    if not cards_html:
        cards_html = '<div class="col-span-2 text-center py-12 text-gray-500"><p>No businesses found under this email.</p></div>'

    html = get_base_head(back_url="/", back_text="Back to Home") + '''
    <main class="max-w-5xl mx-auto px-4 py-12 animate-fade-in space-y-8">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white dark:bg-gray-900 p-6 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-xl animate-modal">
            <div>
                <h1 class="text-2xl font-black text-gray-900 dark:text-white">Client Dashboard</h1>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Logged in as: <strong class="text-blue-600 dark:text-blue-400">''' + client_email + '''</strong></p>
            </div>
            <div class="flex items-center gap-3">
                <a href="/client/change-password" class="bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 px-4 py-2.5 rounded-xl text-xs font-bold transition">Change Password 🔒</a>
                <a href="/register" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-md btn-hover-effect">＋ Register Business</a>
                <a href="/client/logout" class="bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 hover:bg-red-600 hover:text-white px-4 py-2.5 rounded-xl text-xs font-bold transition btn-hover-effect">Logout</a>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            ''' + cards_html + '''
        </div>
    </main>
    ''' + FOOTER
    return render_template_string(html)

@app.route('/client/change-password', methods=['GET', 'POST'])
def client_change_password():
    client_email = session.get('client_logged_email')
    if not client_email:
        return redirect(url_for('client_login'))

    error_msg = ""
    success_msg = ""

    if request.method == 'POST':
        old_pass = request.form.get('old_password', '')
        new_pass = request.form.get('new_password', '')
        
        matched_biz = None
        for b in BUSINESSES.values():
            if b.get('client_email', '').lower() == client_email.lower():
                matched_biz = b
                break

        if matched_biz and matched_biz.get('client_password') == old_pass:
            for b in BUSINESSES.values():
                if b.get('client_email', '').lower() == client_email.lower():
                    b['client_password'] = new_pass
            success_msg = "Password updated successfully!"
        else:
            error_msg = "Incorrect old password!"

    html = get_base_head(back_url="/client/dashboard", back_text="Back to Dashboard") + '''
    <main class="max-w-md mx-auto px-4 py-20 animate-fade-in">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6 animate-modal">
            <div class="text-center space-y-2">
                <span class="text-5xl inline-block">🔒</span>
                <h1 class="text-2xl font-black text-gray-900 dark:text-white">Change Password</h1>
                <p class="text-xs text-gray-500 dark:text-gray-400">Update your account password securely.</p>
            </div>

            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Old Password</label>
                    <input type="password" name="old_password" required placeholder="••••••••" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">New Password</label>
                    <input type="password" name="new_password" required placeholder="••••••••" class="w-full p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white input-hover-effect outline-none text-sm">
                </div>
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3.5 rounded-xl font-bold btn-hover-effect text-sm shadow-lg">Update Password</button>
            </form>
            ''' + (f'<p class="text-green-500 text-xs text-center font-semibold">{success_msg}</p>' if success_msg else '') + '''
            ''' + (f'<p class="text-red-500 text-xs text-center font-semibold">{error_msg}</p>' if error_msg else '') + '''
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
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-8 shadow-2xl space-y-6 animate-modal">
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
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Phone Numbers (separated with commas)</label>
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
    app.run(debug=False, port=5000)
