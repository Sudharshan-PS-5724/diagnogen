from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Path to your ChromeDriver
driver_path = '/path/to/chromedriver'

# Initialize the WebDriver (Make sure you have ChromeDriver installed)
driver = webdriver.Chrome()

# Open the Streamlit app
driver.get('http://localhost:8501')

# Wait for the page to load
time.sleep(2)

# Test Signup and Login
# Navigate to the signup form
email = "testuser@example.com"
password = "testpassword"
username = "testuser"

# Check if the "Signup" option is selected
signup_radio = driver.find_element(By.XPATH, "//span[contains(text(), 'Signup')]")
signup_radio.click()

# Input fields for signup
username_input = driver.find_element(By.XPATH, "//input[@placeholder='Username']")
email_input = driver.find_element(By.XPATH, "//input[@placeholder='Email']")
password_input = driver.find_element(By.XPATH, "//input[@placeholder='Password']")

# Fill out the signup form
username_input.send_keys(username)
email_input.send_keys(email)
password_input.send_keys(password)

# Submit the signup form
signup_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Signup')]")
signup_button.click()

# Wait for the page to reload and login
time.sleep(2)

# Now log in using the created account
login_radio = driver.find_element(By.XPATH, "//span[contains(text(), 'Login')]")
login_radio.click()

email_input = driver.find_element(By.XPATH, "//input[@placeholder='Email']")
password_input = driver.find_element(By.XPATH, "//input[@placeholder='Password']")

email_input.send_keys(email)
password_input.send_keys(password)

login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
login_button.click()

# Wait for the user to be logged in
time.sleep(2)

# Test the Heart Disease Prediction
# Select features for prediction
gender_select = driver.find_element(By.XPATH, "//select[@aria-label='Gender']")
gender_select.send_keys('Male')  # Choose 'Male'

# Select other inputs as needed (add more select statements here)

# Click the predict button
predict_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Predict')]")
predict_button.click()

# Wait for the prediction result
time.sleep(3)

# Check the prediction result (success or warning message)
prediction_result = driver.find_element(By.XPATH, "//div[contains(@class, 'stAlert')]")
assert "Heart disease predicted" in prediction_result.text or "No heart disease predicted!" in prediction_result.text

# Test the chatbot
# Interact with the chatbot
chat_input = driver.find_element(By.XPATH, "//textarea[@aria-label='Type a message']")
chat_input.send_keys("What are the symptoms of heart disease?")

# Send the message
chat_input.send_keys(Keys.RETURN)

# Wait for the response
time.sleep(3)

# Check if the assistant replied
chatbot_reply = driver.find_element(By.XPATH, "//div[contains(text(), 'assistant')]")
assert "How may I assist you" in chatbot_reply.text or "symptoms of heart disease" in chatbot_reply.text

# Close the browser after the test
driver.quit()