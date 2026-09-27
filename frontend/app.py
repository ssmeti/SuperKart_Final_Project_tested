
# Streamlit Web App for SuperKart Sales Forecasting
import streamlit as st
import requests
import numpy as np
import pandas as pd
# Base URL of the Flask backend
import os
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:7860")

# App Title
st.title("🛒 SuperKart Sales Forecasting App")

# Instructions
st.markdown("🔍 Enter product and store attributes to forecast **monthly product sales revenue**.\n\n_All sales are reported in ($) USD._")

# User Inputs
Product_Weight = st.number_input("Product Weight (oz)", min_value=0.0, value=12.66)
Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
Product_Allocated_Area = st.number_input("Product Allocated Area (linear in.)", min_value=0.0, value=100.0)
Product_MRP = st.number_input("Maximum Retail Price (USD)", min_value=0.0, value=150.0)
Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"])
Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
Store_Type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])
Store_Age_Years = st.slider("Store Age (years)", min_value=0, max_value=30, value=10)
Product_Type_Category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])

# Apply log1p transform (must match backend model training)
Product_Allocated_Area_Log = np.log1p(Product_Allocated_Area)

# Prepare JSON payload for the backend
product_data = {
    "Product_Weight": str(Product_Weight),
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": str(Product_Allocated_Area),
    "Product_MRP": str(Product_MRP),
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Store_Age_Years": str(Store_Age_Years),
    "Product_Type_Category": Product_Type_Category
}

# Single Prediction
if st.button("Predict", type='primary'):

    response = requests.post(
        f"{BACKEND_URL}/v1/predict",
        json=product_data
    )

    if response.status_code == 200:
        result = response.json()
        predicted_sales = result["Predicted_Sales"]
        st.success(f"Predicted Product Store Sales Total: ₹{predicted_sales:.2f}")
    else:
        try:
            error_msg = response.json().get("error", response.text)
        except ValueError:
            error_msg = response.text
        st.error(f"Prediction failed ({response.status_code}): {error_msg}")

# Batch Prediction
st.subheader("Batch Prediction")

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    if st.button("Predict for Batch", type='primary'):

        response = requests.post(
            f"{BACKEND_URL}/v1/predictbatch",
            files={"file": uploaded_file}
        )

        if response.status_code == 200:
            results = response.json()

            st.success("Predictions completed successfully!")

            try:
                if isinstance(results, list):
                    df = pd.DataFrame(results)
                elif isinstance(results, dict):
                    # Check if all values are scalars
                    if all(not isinstance(v, (list, dict)) for v in results.values()):
                        df = pd.DataFrame([results])
                    else:
                        df = pd.DataFrame(results)
                else:
                    df = pd.DataFrame({"Result": [results]})

                st.dataframe(df, use_container_width=True)

            except Exception as e:
                st.error(f"Unable to display results as a table: {e}")
                st.json(results)

        else:
            st.error("Unable to connect to the prediction API.")

