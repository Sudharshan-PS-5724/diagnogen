import streamlit as st
from pymongo import MongoClient
from utils import hash_password, verify_password, get_coordinates
import pickle
import pandas as pd
import os
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["hospital_finder"]

# Load the heart disease prediction model
with open('bin_cat.pkl', 'rb') as file:
    model = pickle.load(file)

# Paths to ECG analysis models
model1_path = r'C:\Users\Srinivas\Downloads\Heart_Disease_Predictor.h5'  # VGG16 Model
model2_path = 'model_vgg19.h5'  # VGG19 Model

# Load the ECG analysis models
model1 = load_model(model1_path, compile=False)
model2 = load_model(model2_path, compile=False)

# Class labels for ECG analysis models
class_labels_model1 = ["Normal beat", "MI/History of MI", "Arrhythmia"]
class_labels_model2 = ["Normal beat", "Supraventricular ectopic beat", "Ventricular ectopic beat",
                       "Fusion beat", "Unknown beat", "Class6"]

# Session state to manage image and prediction results
if 'ecg_image' not in st.session_state:
    st.session_state.ecg_image = None
if 'prediction_results' not in st.session_state:
    st.session_state.prediction_results = None
if 'heart_disease_prediction' not in st.session_state:
    st.session_state.heart_disease_prediction = None

# Landing page with options to login or signup
def landing_page():
    st.title("Welcome to Hospital Finder")
    # Check if user is logged in and show dashboard directly if so
    if "user_logged_in" in st.session_state and st.session_state.user_logged_in:
        user_dashboard(st.session_state.username)
        return

    option = st.radio("Select an option:", ["Login", "Signup"])
    if option == "Login":
        login_page()
    elif option == "Signup":
        signup_page()

# Login page logic
def login_page():
    role = st.selectbox("Select your role:", ["User", "Hospital", "Admin"])
    if role == "User":
        user_login()
    elif role == "Hospital":
        hospital_login()
    elif role == "Admin":
        admin_login()

# User Login
def user_login():
    st.subheader("User Login")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = db.users.find_one({"name": username, "email": email})
        if user and verify_password(user["password"], password):
            st.success("Login Successful!")
            # Store login status and username in session state
            st.session_state.user_logged_in = True
            st.session_state.username = username
            user_dashboard(username)
        else:
            st.error("Invalid username, email, or password.")

# Hospital Login
def hospital_login():
    st.subheader("Hospital Login")
    hospital_name = st.text_input("Hospital Name")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        hospital = db.hospitals.find_one({"name": hospital_name})
        if hospital and verify_password(hospital["password"], password):
            st.success("Hospital login successful!")
            st.session_state.hospital_logged_in = True
            st.session_state.hospital_name = hospital_name
            hospital_dashboard(hospital_name)
        else:
            st.error("Invalid hospital name or password.")

# Admin Login
def admin_login():
    st.subheader("Admin Login")
    admin_username = st.text_input("Admin Username")
    admin_password = st.text_input("Admin Password", type="password")
    if st.button("Login"):
        admin = db.admins.find_one({"username": admin_username})
        if admin and verify_password(admin["password"], admin_password):
            st.success("Admin login successful!")
            st.session_state.admin_logged_in = True
            st.session_state.admin_username = admin_username
            admin_dashboard(admin_username)
        else:
            st.error("Invalid admin username or password.")

# User Dashboard (ML Model Integration)
def user_dashboard(username):
    st.subheader("Heart Disease Prediction System")
    st.write(f"Welcome, {username}. Please provide the following information:")

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
        'ever_told_you_had_diabetes': ['Yes', 'No', 'No, Prediabetes', 'Yes, During Pregnancy'],
        'BMI': [
            'Overweight (BMI 25 to 29.9)', 'Normal Weight (BMI 18.5 to 24.9)', 'Obese (BMI 30 or more)',
            'Underweight (BMI less than 18.5)'
        ],
        'difficulty_walking_or_climbing_stairs': ['No', 'Yes'],
        'physical_health_status': ['Zero days not good', '1 to 13 days not good', '14+ days not good'],
        'mental_health_status': ['Zero days not good', '1 to 13 days not good', '14+ days not good'],
        'asthma_Status': ['Never Asthma', 'Current Asthma', 'Former Asthma'],
        'smoking_status': ['Never Smoked', 'Current Smoker (Some Days)', 'Former Smoker', 'Current Smoker (Every Day)'],
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
            st.warning("Heart disease predicted :(")
            st.session_state.heart_disease_prediction = 1  # Indicate prediction for ECG analysis

    # Display file uploader and ECG image preview if heart disease is predicted
    if st.session_state.heart_disease_prediction == 1:
        ecg_image = st.file_uploader("Upload your ECG image for further analysis:", type=["png", "jpg", "jpeg"])

        if ecg_image:
            st.image(ecg_image, caption="Uploaded ECG Image", use_column_width=True)
            st.write("ECG image has been uploaded for further analysis.")
            st.session_state.ecg_image = ecg_image  # Store uploaded image in session state

    # Analyze ECG image if uploaded
    if st.session_state.ecg_image is not None and st.button("Analyze ECG Image"):
        try:
            # Preprocess image for model 1 (VGG16)
            img_model1 = Image.open(st.session_state.ecg_image).resize((224, 224))
            img_model1 = np.array(img_model1) / 255.0  # Normalize
            img_model1 = np.expand_dims(img_model1, axis=0)

            # Predict using model 1 (VGG16)
            output_model1 = model1.predict(img_model1)
            predicted_class_label_model1 = class_labels_model1[np.argmax(output_model1)]

            # Secondary prediction with model 2 (VGG19) if model 1 predicts 'Arrhythmia'
            if predicted_class_label_model1 == "Arrhythmia":
                img_model2 = Image.open(st.session_state.ecg_image).resize((224, 224))
                img_model2 = np.array(img_model2) / 255.0
                img_model2 = np.expand_dims(img_model2, axis=0)

                output_model2 = model2.predict(img_model2)
                predicted_class_label_model2 = class_labels_model2[np.argmax(output_model2)]
            else:
                output_model2 = None
                predicted_class_label_model2 = "Not applicable (Model 2 not used)"

            # Save results in session state
            st.session_state.prediction_results = {
                "Model 1 (Type of Beat)": predicted_class_label_model1,
                "Model 2 (Condition)": predicted_class_label_model2,
                "Model 1 Output": output_model1,
                "Model 2 Output": output_model2
            }

        except Exception as e:
            st.error(f"Error in prediction: {e}")

    # Display prediction results if available
    if st.session_state.prediction_results:
        st.write("*Analysis Results:*")
        for key, value in st.session_state.prediction_results.items():
            st.write(f"{key}: {value}")

# Hospital Dashboard
def hospital_dashboard(hospital_name):
    st.subheader(f"Welcome, {hospital_name}")
    st.write("Hospital dashboard features here.")

# Admin Dashboard
def admin_dashboard(admin_username):
    st.subheader(f"Welcome, Admin {admin_username}")
    st.write("Admin dashboard features here.")

# Run landing page as main entry point
landing_page()