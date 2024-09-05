from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Function to run Pinterest bot
def run_pinterest_bot(email, password, pin_url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Automatically manage ChromeDriver version
    service = Service(ChromeDriverManager().install())

    # Create browser instance
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Log in to Pinterest
        driver.get('https://www.pinterest.com/login/')
        username_input = driver.find_element(By.ID, "email")
        password_input = driver.find_element(By.ID, "password")
        username_input.send_keys(email)
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

        # Navigate to the pin URL and save it
        driver.get(pin_url)
        save_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Save"]')
        save_button.click()

        # Like the pin
        like_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Like"]')
        like_button.click()

    finally:
        # Close the browser
        driver.quit()

# Route to handle form submission
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pinterest_email = request.form['email']
        pinterest_password = request.form['password']
        pin_url = request.form['pin_url']

        # Run the Pinterest bot
        run_pinterest_bot(pinterest_email, pinterest_password, pin_url)

        return "Pin saved and liked successfully!"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
