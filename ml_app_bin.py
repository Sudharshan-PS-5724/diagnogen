import streamlit as st
import pandas as pd
import pickle

# Load the model
with open('bin_cat.pkl', 'rb') as file:
    model = pickle.load(file)

# Title and description
st.title("Heart Disease Prediction System")
st.write("Please provide the following information:")

# Feature dictionaries with user-friendly display names
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

# Collect user inputs with improved display labels
user_input = {}
for feature, labels in options.items():
    user_input[feature] = st.selectbox(f"{feature.replace('_', ' ').capitalize()}", labels)

# Prediction button
if st.button("Predict"):
    # Convert user-friendly labels back to model-readable format
    for feature, labels in options.items():
        user_input[feature] = labels.index(user_input[feature])

    # Convert input to DataFrame
    input_data = pd.DataFrame([user_input])

    # Make prediction
    prediction = model.predict(input_data)[0]
    
    # Display results
    if prediction == 0:
        st.success("No heart disease predicted!")
    else:
        st.warning("Heart disease predicted :(")
        
        # Prompt user for ECG image upload
        ecg_image = st.file_uploader("Please upload your ECG image for further analysis:", type=["png", "jpg", "jpeg"])
        
        if ecg_image is not None:
            st.image(ecg_image, caption="Uploaded ECG Image", use_column_width=True)
            st.write("Your ECG image has been uploaded successfully! Further analysis will be done.")