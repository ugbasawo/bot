from flask import Flask, request, render_template, redirect, url_for, flash
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Path to store context data (cookies, storage)
context_storage_file = "context_storage.json"

# Function to log in to Pinterest
def login_to_pinterest(email_or_username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Load session if available
        if os.path.exists(context_storage_file):
            context.storage_state(path=context_storage_file)

        page = context.new_page()

        # Go to Pinterest login page
        page.goto('https://www.pinterest.com/login/')
        page.fill('#email', email_or_username)
        page.fill('#password', password)
        page.press('#password', 'Enter')
        
        # Check if login is successful
        page.wait_for_timeout(5000)  # Adjust this based on Pinterest's load time

        # Save the browser state (cookies, localStorage)
        context.storage_state(path=context_storage_file)
        
        return True  # Return True on successful login

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pinterest_email_or_username = request.form.get('email_or_username')
        pinterest_password = request.form.get('password')

        try:
            if login_to_pinterest(pinterest_email_or_username, pinterest_password):
                flash("Login successful!", "success")
                return redirect(url_for('pin_interaction'))
        except Exception as e:
            flash("Login failed. Please try again.", "danger")

    return render_template('login.html')

@app.route('/pin-interaction', methods=['GET', 'POST'])
def pin_interaction():
    if request.method == 'POST':
        pin_url = request.form.get('pin_url')
        action = request.form.get('action')
        num_likes = int(request.form.get('num_likes', 0))
        num_impressions = int(request.form.get('num_impressions', 0))

        if not os.path.exists(context_storage_file):
            flash("No active session. Please login again.", "danger")
            return redirect(url_for('login'))

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            # Load the stored session
            context.storage_state(path=context_storage_file)
            page = context.new_page()

            if action == 'save':
                save_pin(page, pin_url)
            elif action == 'like':
                like_pin(page, pin_url, num_likes)
            elif action == 'impressions':
                simulate_impressions(page, pin_url, num_impressions)

            return redirect(url_for('pin_interaction'))

    return render_template('pin_interaction.html')

def save_pin(page, pin_url):
    page.goto(pin_url)
    save_button = page.query_selector('[aria-label="Save"]')
    if save_button:
        save_button.click()
        flash("Pin saved successfully!", "success")
    else:
        flash("Save button not found!", "danger")

def like_pin(page, pin_url, num_likes):
    page.goto(pin_url)
    like_button = page.query_selector('[aria-label="Like"]')
    if like_button:
        for _ in range(num_likes):
            like_button.click()
        flash(f"Pin liked {num_likes} times!", "success")
    else:
        flash("Like button not found!", "danger")

def simulate_impressions(page, pin_url, num_impressions):
    for _ in range(num_impressions):
        page.goto(pin_url)
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    flash(f"Simulated {num_impressions} impressions!", "success")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
