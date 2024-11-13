import streamlit as st
import pandas as pd
import pickle
import toml
import pymongo
import bcrypt
import replicate
import os

# Load secrets (assuming secrets.toml file for API keys and Mongo URI)
secrets = toml.load("secrets.toml")
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["hospital_finder"]
users_collection = db["users"]

# Replicate API token setup
replicate_api = "r8_NxcEZua2zw5Sx8UYPJhhbx5PjUu8ceg1T2Cn7"
os.environ['REPLICATE_API_TOKEN'] = replicate_api

# Load the heart disease prediction model
with open('bin_cat.pkl', 'rb') as file:
    model = pickle.load(file)

# Streamlit UI
st.title("Heart Disease Prediction System with Chatbot Assistance")

# Authentication Functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def signup(username, email, password):
    hashed_password = hash_password(password)
    users_collection.insert_one({
        "username": username,
        "email": email,
        "password": hashed_password
    })
    st.success("Signup successful! Please log in.")

def login(email, password):
    user = users_collection.find_one({"email": email})
    if user and check_password(password, user["password"]):
        st.session_state.logged_in = True
        st.session_state.username = user["username"]
        st.success(f"Welcome back, {user['username']}!")
    else:
        st.error("Invalid email or password.")

# Authentication: Signup/Login Form
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    option = st.selectbox("Choose Option", ["Login", "Signup"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if option == "Signup":
        username = st.text_input("Username")
        if st.button("Signup"):
            if users_collection.find_one({"email": email}):
                st.error("Email already exists.")
            else:
                signup(username, email, password)
    elif option == "Login":
        if st.button("Login"):
            login(email, password)

# Main Application for Heart Disease Prediction and Chatbot
if st.session_state.logged_in:
    st.subheader("Heart Disease Prediction System")
    st.write("Please provide the following information:")

    # Feature dictionaries for prediction
    options = {
        'gender': ['Female', 'Male', 'Nonbinary'],
        'race': [
            'White only (Non-Hispanic)', 'Black only (Non-Hispanic)', 'Asian only (Non-Hispanic)',
            'American Indian or Alaskan Native only (Non-Hispanic)', 'Multiracial (Non-Hispanic)',
            'Hispanic', 'Native Hawaiian or Other Pacific Islander only (Non-Hispanic)'
        ],
        'general_health': ['Very Good', 'Excellent', 'Fair', 'Poor', 'Good'],
        'health_care_provider': ['Yes, only one', 'More than one', 'No'],
        'could_not_afford_to_see_doctor': ['No', 'Yes'],
        'length_of_time_since_last_routine_checkup': [
            'Past year', 'Never', 'Past 2 years', 'Past 5 years', '5+ years ago'
        ],
        'ever_diagnosed_with_heart_attack': ['No', 'Yes'],
        'ever_diagnosed_with_a_stroke': ['No', 'Yes'],
        'ever_told_you_had_a_depressive_disorder': ['No', 'Yes'],
        'ever_told_you_have_kidney_disease': ['No', 'Yes'],
        'ever_told_you_had_diabetes': [
            'Yes', 'No', 'No, Prediabetes', 'Yes, During Pregnancy'
        ],
        'BMI': [
            'Overweight (BMI 25 to 29.9)', 'Normal Weight (BMI 18.5 to 24.9)',
            'Obese (BMI 30 or more)', 'Underweight (BMI less than 18.5)'
        ],
        'difficulty_walking_or_climbing_stairs': ['No', 'Yes'],
        'physical_health_status': [
            'Zero days not good', '1 to 13 days not good', '14+ days not good'
        ],
        'mental_health_status': [
            'Zero days not good', '1 to 13 days not good', '14+ days not good'
        ],
        'asthma_Status': ['Never Asthma', 'Current Asthma', 'Former Asthma'],
        'smoking_status': [
            'Never Smoked', 'Current Smoker (Some Days)', 'Former Smoker', 'Current Smoker (Every Day)'
        ],
        'binge_drinking_status': ['No', 'Yes'],
        'exercise_status_in_past_30_Days': ['No', 'Yes'],
        'age_category': [
            '80 or older', '55 to 59', '70 to 74', '40 to 44', '75 to 79', '65 to 69', '60 to 64',
            '50 to 54', '45 to 49', '35 to 39', '25 to 29', '30 to 34', '18 to 24'
        ],
        'sleep_category': [
            'Normal Sleep (6 to 8 hours)', 'Short Sleep (4 to 5 hours)', 'Long Sleep (9 to 10 hours)',
            'Very Short Sleep (0 to 3 hours)', 'Very Long Sleep (11 or more hours)'
        ],
        'drinks_category': [
            'Did Not Drink', 'Low Consumption (1.01 to 5 drinks)', 'Very Low Consumption (0.01 to 1 drinks)',
            'High Consumption (10.01 to 20 drinks)', 'Moderate Consumption (5.01 to 10 drinks)',
            'Very High Consumption (More than 20 drinks)'
        ]
    }

    # Collect user inputs
    user_input = {}
    for feature, labels in options.items():
        user_input[feature] = st.selectbox(f"{feature.replace('_', ' ').capitalize()}", labels)

    if st.button("Predict"):
        # Convert labels to indices for model
        for feature, labels in options.items():
            user_input[feature] = labels.index(user_input[feature])

        input_data = pd.DataFrame([user_input])
        prediction = model.predict(input_data)[0]

        if prediction == 0:
            st.success("No heart disease predicted!")
        else:
            st.warning("Heart disease predicted.")
            ecg_image = st.file_uploader("Upload your ECG image:", type=["png", "jpg", "jpeg"])
            if ecg_image:
                st.image(ecg_image, caption="Uploaded ECG Image", use_column_width=True)
                st.write("ECG image has been uploaded for further analysis.")

    # Chatbot Section
    st.subheader("Heart Health Chatbot")
    if replicate_api:
        st.sidebar.title('Chatbot')
        selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
        if selected_model == 'Llama2-7B':
            llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
        elif selected_model == 'Llama2-13B':
            llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'

        temperature = st.sidebar.slider('Temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
        top_p = st.sidebar.slider('Top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
        max_length = st.sidebar.slider('Max Length', min_value=32, max_value=128, value=120, step=8)

        if "messages" not in st.session_state.keys():
            st.session_state.messages = [{"role": "assistant", "content": "How may I assist you with heart health queries today?"}]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if prompt := st.chat_input(disabled=not replicate_api):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = replicate.run(llm, input={"prompt": prompt, "temperature": temperature, "top_p": top_p, "max_length": max_length})
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})