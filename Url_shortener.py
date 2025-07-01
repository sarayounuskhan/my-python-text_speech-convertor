import os
import shortuuid # Handy for unique short codes!
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash # For secure passwords

# --- Our Awesome Flask Web Application! ---
# Giving our Flask app a friendly, unique name.
my_personal_url_buddy = Flask(__name__) # Renamed Flask app instance again

# --- App Settings ---
# This secret key is SUPER important for keeping user sessions safe.
# We'll generate a fresh random one each time (in a real app, you'd set it once securely).
my_personal_url_buddy.config['SECRET_KEY'] = os.urandom(24)
# Database setup: SQLite is super convenient for a simple project.
# It'll create 'my_tiny_links_data.sqlite' in your project folder.
my_personal_url_buddy.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_tiny_links_data.sqlite' # Changed DB filename
my_personal_url_buddy.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Keeps SQLAlchemy quiet

# Get our database object ready to work with data
db_helper = SQLAlchemy(my_personal_url_buddy) # Renamed 'db_connector' to 'db_helper'

# --- Database Blueprints (Our Data Models) ---
# User model: Defines user accounts.
class User(db_helper.Model):
    id = db_helper.Column(db_helper.Integer, primary_key=True)
    username_str = db_helper.Column(db_helper.String(80), unique=True, nullable=False) # Renamed 'user_name'
    password_hash_str = db_helper.Column(db_helper.String(120), nullable=False) # Renamed 'pass_hash'
    # Users can create many short URLs. This links them!
    their_shortened_urls = db_helper.relationship('ShortURL', backref='owner_user', lazy=True) # Renamed relationship and backref

    def __repr__(self):
        # How a User object looks when printed.
        return f'<User: {self.username_str}>'

# ShortURL model: Stores original and tiny URLs.
class ShortURL(db_helper.Model):
    id = db_helper.Column(db_helper.Integer, primary_key=True)
    original_long_url_str = db_helper.Column(db_helper.String(500), nullable=False) # Renamed
    the_short_code_str = db_helper.Column(db_helper.String(10), unique=True, nullable=False) # Renamed
    creation_timestamp = db_helper.Column(db_helper.DateTime, default=datetime.utcnow) # Renamed
    # Links this short URL to its creator.
    creator_user_id = db_helper.Column(db_helper.Integer, db_helper.ForeignKey('user.id'), nullable=False) # Renamed
    # Tracks all clicks on this specific short URL.
    all_recorded_clicks = db_helper.relationship('Click', backref='linked_short_url', lazy=True) # Renamed relationship and backref

    def __repr__(self):
        # How a ShortURL object looks when printed.
        return f'<Tiny URL: {self.the_short_code_str} (points to {self.original_long_url_str[:30]}... )>'

# Click model: Records every click for analytics.
class Click(db_helper.Model):
    id = db_helper.Column(db_helper.Integer, primary_key=True)
    click_moment = db_helper.Column(db_helper.DateTime, default=datetime.utcnow) # Renamed
    client_ip_address = db_helper.Column(db_helper.String(45)) # Renamed
    # Links the click to the short URL that was clicked.
    clicked_url_id = db_helper.Column(db_helper.Integer, db_helper.ForeignKey('short_url.id'), nullable=False) # Renamed

    def __repr__(self):
        # How a Click object looks when printed.
        return f'<Click on {self.linked_short_url.the_short_code_str} at {self.click_moment}>'

# --- Database Setup (Run this ONCE to get ready!) ---
# Creates database file and tables if they don't exist.
with my_personal_url_buddy.app_context():
    db_helper.create_all()
    print("Database tables are all set up (or already existed). Ready for your awesome links!")


# --- Handy Functions for User Sessions ---
# Checks if someone is currently logged in.
def is_user_currently_signed_in(): # Renamed
    return 'user_id' in session

# Gets the logged-in user's details.
def retrieve_current_user_info(): # Renamed
    if is_user_currently_signed_in():
        return User.query.get(session['user_id'])
    return None # No user if not logged in


# --- HTML Page Templates (Each is a complete HTML string) ---
# This approach avoids Jinja2 block conflicts when not using {% extends %} with separate files.

# HTML for user registration page
REGISTER_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register for an Account - My Super Tiny URL Maker</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .flash-message {
            padding: 0.75rem 1.25rem;
            margin-bottom: 1rem;
            border: 1px solid transparent;
            border-radius: 0.25rem;
        }
        .flash-success { background-color: #d4edda; border-color: #c3e6cb; color: #155724; }
        .flash-error { background-color: #f8d7da; border-color: #f5c6cb; color: #721c24; }
        .flash-info { background-color: #d1ecf1; border-color: #bee5eb; color: #0c5460; }
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex flex-col items-center py-8">
    <div class="w-full max-w-2xl bg-white p-8 rounded-lg shadow-md">
        <h1 class="text-3xl font-bold text-center text-gray-800 mb-6">Register for an Account</h1>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <ul class="mb-4">
                    {% for category, message in messages %}
                        <li class="flash-message flash-{{ category }}">{{ message }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
        {% endwith %}

        <form method="POST" action="{{ url_for('register_a_brand_new_account') }}" class="space-y-4">
            <div>
                <label for="username" class="block text-sm font-medium text-gray-700">Pick a cool Username:</label>
                <input type="text" id="username" name="username" required
                       class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            </div>
            <div>
                <label for="password" class="block text-sm font-medium text-gray-700">Create a Password (make it strong!):</label>
                <input type="password" id="password" name="password" required
                       class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            </div>
            <button type="submit"
                    class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                Let's Get Started!
            </button>
        </form>
        <p class="mt-4 text-center text-sm text-gray-600">
            Already have an account with us? <a href="{{ url_for('user_login_page_view') }}" class="font-medium text-indigo-600 hover:text-indigo-500">Log in here</a>.
        </p>
    </div>
</body>
</html>
"""

# HTML for user login page
LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login to Your Account - My Super Tiny URL Maker</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .flash-message {
            padding: 0.75rem 1.25rem;
            margin-bottom: 1rem;
            border: 1px solid transparent;
            border-radius: 0.25rem;
        }
        .flash-success { background-color: #d4edda; border-color: #c3e6cb; color: #155724; }
        .flash-error { background-color: #f8d7da; border-color: #f5c6cb; color: #721c24; }
        .flash-info { background-color: #d1ecf1; border-color: #bee5eb; color: #0c5460; }
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex flex-col items-center py-8">
    <div class="w-full max-w-2xl bg-white p-8 rounded-lg shadow-md">
        <h1 class="text-3xl font-bold text-center text-gray-800 mb-6">Login to Your Account</h1>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <ul class="mb-4">
                    {% for category, message in messages %}
                        <li class="flash-message flash-{{ category }}">{{ message }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
        {% endwith %}

        <form method="POST" action="{{ url_for('user_login_page_view') }}" class="space-y-4">
            <div>
                <label for="username" class="block text-sm font-medium text-gray-700">Your Username:</label>
                <input type="text" id="username" name="username" required
                       class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            </div>
            <div>
                <label for="password" class="block text-sm font-medium text-gray-700">Your Password:</label>
                <input type="password" id="password" name="password" required
                       class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            </div>
            <button type="submit"
                    class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                Sign Me In!
            </button>
        </form>
        <p class="mt-4 text-center text-sm text-gray-600">
            New here? <a href="{{ url_for('register_a_brand_new_account') }}" class="font-medium text-indigo-600 hover:text-indigo-500">Create an account</a>.
        </p>
    </div>
</body>
</html>
"""

# HTML for user dashboard (main page after logging in)
DASHBOARD_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Link Dashboard - My Super Tiny URL Maker</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .flash-message {
            padding: 0.75rem 1.25rem;
            margin-bottom: 1rem;
            border: 1px solid transparent;
            border-radius: 0.25rem;
        }
        .flash-success { background-color: #d4edda; border-color: #c3e6cb; color: #155724; }
        .flash-error { background-color: #f8d7da; border-color: #f5c6cb; color: #721c24; }
        .flash-info { background-color: #d1ecf1; border-color: #bee5eb; color: #0c5460; }
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex flex-col items-center py-8">
    <div class="w-full max-w-2xl bg-white p-8 rounded-lg shadow-md">
        <h1 class="text-3xl font-bold text-center text-gray-800 mb-6">Your Link Dashboard</h1>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <ul class="mb-4">
                    {% for category, message in messages %}
                        <li class="flash-message flash-{{ category }}">{{ message }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
        {% endwith %}

        <p class="text-center text-gray-700 mb-6">Hey there, {{ user.username_str }}! <a href="{{ url_for('log_out_user_session') }}" class="font-medium text-red-600 hover:text-red-500">Log Out</a></p>

        <h2 class="text-2xl font-semibold text-gray-800 mb-4">Time to Make a New Tiny Link!</h2>
        <form method="POST" action="{{ url_for('create_a_new_shortened_link') }}" class="space-y-4 mb-8">
            <div>
                <label for="original_url" class="block text-sm font-medium text-gray-700">Your Super Long URL:</label>
                <input type="url" id="original_url" name="original_url" required placeholder="e.g., https://your-favorite-website.com/super-long-article-about-cats"
                       class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            </div>
            <button type="submit"
                    class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                Shrink It Down!
            </button>
        </form>

        <h2 class="text-2xl font-semibold text-gray-800 mb-4">Your Collection of Tiny Links</h2>
        {% if urls %}
            <ul class="space-y-4">
                {% for url_item in urls %}
                    <li class="bg-gray-50 p-4 rounded-md shadow-sm border border-gray-200">
                        <p class="text-gray-700 break-words">Original: <a href="{{ url_item.original_full_url_str }}" target="_blank" class="text-blue-600 hover:underline">{{ url_item.original_full_url_str }}</a></p>
                        <p class="text-gray-900 font-semibold mt-2">Tiny Link: <a href="{{ url_for('redirect_to_the_original_url', short_code=url_item.the_short_code_str, _external=True) }}" target="_blank" class="text-indigo-600 hover:underline">{{ request.url_root }}{{ url_item.the_short_code_str }}</a></p>
                        <p class="text-sm text-gray-500">Made On: {{ url_item.creation_timestamp.strftime('%Y-%m-%d %H:%M') }}</p>
                        <p class="text-sm text-gray-500">Total Clicks: {{ url_item.all_recorded_clicks|length }}</p>
                        <a href="{{ url_for('show_link_click_stats', short_code=url_item.the_short_code_str) }}" class="inline-block mt-2 text-sm font-medium text-purple-600 hover:underline">See Click Stats</a>
                    </li>
                {% endfor %}
            </ul>
        {% else %}
            <p class="text-gray-600 text-center">Looks like you haven't made any tiny links yet. Get started above!</p>
        {% endif %}
    </div>
</body>
</html>
"""

# HTML for analytics page (showing click details for a specific link)
ANALYTICS_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Link Analytics - My Super Tiny URL Maker</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .flash-message {
            padding: 0.75rem 1.25rem;
            margin-bottom: 1rem;
            border: 1px solid transparent;
            border-radius: 0.25rem;
        }
        .flash-success { background-color: #d4edda; border-color: #c3e6cb; color: #155724; }
        .flash-error { background-color: #f8d7da; border-color: #f5c6cb; color: #721c24; }
        .flash-info { background-color: #d1ecf1; border-color: #bee5eb; color: #0c5460; }
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex flex-col items-center py-8">
    <div class="w-full max-w-2xl bg-white p-8 rounded-lg shadow-md">
        <h1 class="text-3xl font-bold text-center text-gray-800 mb-6">Deep Dive into Clicks for:</h1>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <ul class="mb-4">
                    {% for category, message in messages %}
                        <li class="flash-message flash-{{ category }}">{{ message }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
        {% endwith %}

        <p class="text-center text-gray-700 mb-6"><a href="{{ url_for('user_dashboard_view') }}" class="font-medium text-indigo-600 hover:text-indigo-500">&larr; Back to Your Links</a></p>

        <p class="text-gray-700 break-words mb-4">Original URL: <a href="{{ short_url.original_full_url_str }}" target="_blank" class="text-blue-600 hover:underline">{{ short_url.original_full_url_str }}</a></p>
        <p class="text-gray-900 font-semibold mb-6">Tiny Link: <a href="{{ url_for('redirect_to_the_original_url', short_code=short_url.the_short_code_str, _external=True) }}" target="_blank" class="text-indigo-600 hover:underline">{{ request.url_root }}{{ short_url.the_short_code_str }}</a></p>

        <h3 class="text-xl font-semibold text-gray-800 mb-3">Overall Clicks: {{ clicks|length }}</h3>

        {% if clicks %}
            <h4 class="text-lg font-medium text-gray-700 mb-2">Recent Visits:</h4>
            <ul class="space-y-2">
                {% for click_detail in clicks %}
                    <li class="bg-white p-3 rounded-md shadow-sm border border-gray-200 text-sm text-gray-600">
                        Visited at: {{ click_detail.click_moment.strftime('%Y-%m-%d %H:%M:%S') }} (From IP: {{ click_detail.client_ip_address if click_detail.client_ip_address else 'Unknown IP' }})
                    </li>
                {% endfor %}
            </ul>
        {% else %}
            <p class="text-gray-600 text-center">No one has clicked this tiny link yet. Time to share it around!</p>
        {% endif %}
    </div>
</body>
</html>
"""


# --- Web Routes (These define what happens when you visit different URLs in our app) ---

@my_personal_url_buddy.route('/') # The very first page people see when they open our app
def home_page_redirect():
    if is_user_currently_signed_in(): # Check if they're already signed in
        return redirect(url_for('user_dashboard_view')) # Take them straight to their dashboard
    return render_template_string(LOGIN_PAGE_HTML, title="Login to Your Account") # Directly render login page

@my_personal_url_buddy.route('/register', methods=['GET', 'POST'])
def register_a_brand_new_account(): # Renamed
    if request.method == 'POST':
        # Get username and password from the form
        new_username_input = request.form['username']
        new_password_input = request.form['password']

        # Basic checks to make sure fields aren't empty
        if not new_username_input or not new_password_input:
            flash('Oops! Both username and password are needed to sign up.', 'error')
            return render_template_string(REGISTER_PAGE_HTML, title="Register for an Account")

        # See if that username is already taken (can't have two of the same!)
        existing_user_check = User.query.filter_by(username_str=new_username_input).first()
        if existing_user_check:
            flash('That username is already taken. Please pick a different one!', 'error')
            return render_template_string(REGISTER_PAGE_HTML, title="Register for an Account")

        # Hash the password for security (NEVER store plain passwords!)
        hashed_pw_for_db = generate_password_hash(new_password_input)
        # Create a new user entry in our database
        new_user_db_entry = User(username_str=new_username_input, password_hash_str=hashed_pw_for_db)
        db_helper.session.add(new_user_db_entry)
        db_helper.session.commit()
        flash('Success! Your account is created. Now please log in.', 'success')
        return redirect(url_for('user_login_page_view'))
    return render_template_string(REGISTER_PAGE_HTML, title="Register for an Account")

@my_personal_url_buddy.route('/login', methods=['GET', 'POST'])
def user_login_page_view(): # Renamed
    if request.method == 'POST':
        # Get username and password from the form
        entered_username_val = request.form['username']
        entered_password_val = request.form['password']

        # Find the user in the database
        user_account_found = User.query.filter_by(username_str=entered_username_val).first()
        # Check if user exists and if the password is correct
        if user_account_found and check_password_hash(user_account_found.password_hash_str, entered_password_val):
            session['user_id'] = user_account_found.id # Store user ID in session to keep them logged in
            flash('Welcome back! You are logged in.', 'success')
            return redirect(url_for('user_dashboard_view'))
        else:
            flash('Login failed. Please double-check your username and password.', 'error')
    return render_template_string(LOGIN_PAGE_HTML, title="Login to Your Account")

@my_personal_url_buddy.route('/logout')
def log_out_user_session(): # Renamed
    session.pop('user_id', None) # Clear the user ID from the session
    flash('You have been successfully logged out. See you soon!', 'info')
    return redirect(url_for('user_login_page_view'))

@my_personal_url_buddy.route('/dashboard')
def user_dashboard_view(): # Renamed
    if not is_user_currently_signed_in():
        flash('Please log in to see your personalized dashboard.', 'info')
        return redirect(url_for('user_login_page_view'))

    current_active_user_obj = retrieve_current_user_info()
    if not current_active_user_obj: # Safety check in case session ID is invalid
        session.pop('user_id', None)
        flash('Hmm, something went wrong with your session. Please log in again.', 'error')
        return redirect(url_for('user_login_page_view'))

    # Get all the tiny URLs this user has created, sorted by newest firs
        return render_template_string(DASHBOARD_PAGE_HTML, title="Your Link Dashboard", user=current_active_user_obj, urls=users_short_links_list)

@my_personal_url_buddy.route('/shorten', methods=['POST'])
def create_a_new_shortened_link(): # Renamed
    if not is_user_currently_signed_in():
        flash('You need to be logged in to make tiny URLs!', 'info')
        return redirect(url_for('user_login_page_view'))

    the_original_long_url_input = request.form['original_url'].strip()
    if not the_original_long_url_input:
        flash('The URL field can not be empty, please try again!', 'error')
        return redirect(url_for('user_dashboard_view'))

    # A quick check to ensure it looks like a proper URL (starts with http/https)
    if not (the_original_long_url_input.startswith('http://') or the_original_long_url_input.startswith('https://')):
        flash('Please enter a full URL, starting with http:// or https://', 'error')
        return redirect(url_for('user_dashboard_view'))

    current_link_creator_obj = retrieve_current_user_info()

    # Generate a unique, short string for our tiny URL (8 characters long for neatness)
    a_brand_new_tiny_code = shortuuid.uuid()[:8]

    # Just in case (very rare!), let's make sure this code isn't already used in our database
    while ShortURL.query.filter_by(the_short_code_str=a_brand_new_tiny_code).first():
        a_brand_new_tiny_code = shortuuid.uuid()[:8] # If it exists, generate a new one!

    # Create a new entry in our database for this shortened link
    new_link_db_record = ShortURL(original_full_url_str=the_original_long_url_input, the_short_code_str=a_brand_new_tiny_code, creator_user_id=current_link_creator_obj.id)
    db_helper.session.add(new_link_db_record)
    db_helper.session.commit()

    flash(f'Awesome! Your URL is now tiny: {request.url_root}{a_brand_new_tiny_code}', 'success')
    return redirect(url_for('user_dashboard_view'))

@my_personal_url_buddy.route('/<short_code>')
def redirect_to_the_original_url(short_code): # Renamed
    # Find the short URL in our database using the provided short_code
    the_short_link_object = ShortURL.query.filter_by(the_short_code_str=short_code).first()

    if the_short_link_object:
        # Record this click for analytics!
        visitor_ip_info = request.remote_addr # Get the IP address of the person clicking
        new_click_db_entry = Click(short_link_id=the_short_link_object.id, visitor_ip_address=visitor_ip_info)
        db_helper.session.add(new_click_db_entry)
        db_helper.session.commit()
        # Redirect the user to the original long URL
        return redirect(the_short_link_object.original_full_url_str)
    else:
        flash('Oops! That tiny URL was not found.', 'error')
        return redirect(url_for('user_dashboard_view')) # Send them back to the dashboard or a custom 404 page

@my_personal_url_buddy.route('/analytics/<short_code>')
def show_link_click_stats(short_code): # Renamed
    if not is_user_currently_signed_in():
        flash('Please log in to check out link analytics.', 'info')
        return redirect(url_for('user_login_page_view'))

    current_user_for_stats_obj = retrieve_current_user_info()
    # Find the short URL, making sure it belongs to the current user
    short_url_for_stats_obj = ShortURL.query.filter_by(the_short_code_str=short_code, creator_user_id=current_user_for_stats_obj.id).first()

    if not short_url_for_stats_obj:
        flash('Link not found or you do not have permission to see its stats.', 'error')
        return redirect(url_for('user_dashboard_view'))

    # Get all the clicks associated with this specific short URL
    all_clicks_for_this_link = Click.query.filter_by(short_link_id=short_url_for_stats_obj.id).order_by(Click.click_moment.desc()).all()
    return render_template_string(ANALYTICS_PAGE_HTML, title=f"Stats for {short_code}", short_url=short_url_for_stats_obj, clicks=all_clicks_for_this_link)

# --- Run the Flask app! ---
# This part is now removed from the main script.
# You will run the app using 'flask run' in your terminal.
