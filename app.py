from flask import Flask, request, render_template, redirect, url_for, flash
from playwright.sync_api import sync_playwright
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Sample list of proxies (replace with actual proxy IPs if available)
proxies = [
    'http://proxy1.com:8080',
    'http://proxy2.com:8080',
    'http://proxy3.com:8080'
]

# Function to log in to Pinterest with random proxy
def login_to_pinterest(email_or_username, password):
    with sync_playwright() as p:
        # Choose a random proxy for IP change simulation
        proxy = random.choice(proxies)
        
        browser = p.chromium.launch(headless=True, proxy={"server": proxy})  # Use proxy for the session
        context = browser.new_context()
        page = context.new_page()
        
        # Go to Pinterest login page
        page.goto('https://www.pinterest.com/login/')
        page.fill('#email', email_or_username)
        page.fill('#password', password)
        page.press('#password', 'Enter')
        
        # Check if login is successful by waiting for a specific element
        page.wait_for_timeout(5000)  # Wait for the page to load
        return page  # Return the page for further actions

# Function to save the pin
def save_pin(page, pin_url):
    page.goto(pin_url)
    save_button = page.query_selector('[aria-label="Save"]')
    if save_button:
        save_button.click()
        flash("Pin saved successfully!", "success")
    else:
        flash("Save button not found!", "danger")

# Function to like the pin
def like_pin(page, pin_url, num_likes):
    page.goto(pin_url)
    like_button = page.query_selector('[aria-label="Like"]')
    if like_button:
        for _ in range(num_likes):
            like_button.click()
        flash(f"Pin liked {num_likes} times!", "success")
    else:
        flash("Like button not found!", "danger")

# Function to simulate impressions (scrolling the page)
def simulate_impressions(page, pin_url, num_impressions):
    for _ in range(num_impressions):
        page.goto(pin_url)
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    flash(f"Simulated {num_impressions} impressions!", "success")

# Route to handle login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pinterest_email_or_username = request.form.get('email_or_username')
        pinterest_password = request.form.get('password')
        
        try:
            page = login_to_pinterest(pinterest_email_or_username, pinterest_password)
            return redirect(url_for('pin_interaction', page_id=id(page)))
        except Exception as e:
            flash("Login failed. Please try again.", "danger")
    
    return render_template('login.html')

# New route for Gmail login (to be implemented using OAuth)
@app.route('/login-with-gmail', methods=['POST'])
def login_with_gmail():
    # Here you would implement Google OAuth login, but for now, we'll just simulate it
    try:
        # Simulate successful Gmail login
        flash("Logged in with Gmail successfully!", "success")
        return redirect(url_for('pin_interaction'))
    except Exception as e:
        flash("Failed to log in with Gmail. Please try again.", "danger")
        return redirect(url_for('login'))

# Route to handle pin interactions after login
@app.route('/pin-interaction', methods=['GET', 'POST'])
def pin_interaction():
    if request.method == 'POST':
        pin_url = request.form['pin_url']
        action = request.form['action']
        num_likes = int(request.form.get('num_likes', 0))
        num_impressions = int(request.form.get('num_impressions', 0))
        
        page_id = request.form['page_id']  # Retrieve the browser session (in reality, store sessions properly)
        page = sync_playwright().chromium.connect(id=page_id)
        
        if action == 'save':
            save_pin(page, pin_url)
        elif action == 'like':
            like_pin(page, pin_url, num_likes)
        elif action == 'impressions':
            simulate_impressions(page, pin_url, num_impressions)
        
        page.close()  # Close the browser once done
        return redirect(url_for('login'))
    
    return render_template('pin_interaction.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
