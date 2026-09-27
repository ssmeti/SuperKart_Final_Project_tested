import numpy as np
import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
superkart_api = Flask("superkart_sales_api")
CORS(superkart_api)

# Load the trained model pipeline (preprocessing + model)
model = joblib.load("superkart_sales_forecast_model_v1_0.joblib")

# Health check route
@superkart_api.get('/')
def home():
    return "✅ Welcome to the SuperKart Sales Prediction API"

# Prediction route
@superkart_api.post('/v1/predict')
def predict_sales():
    try:
        # Parse JSON payload
        data = request.get_json()
        print("Raw incoming data:", data)

        # Validate expected fields
        required_fields = [
            'Product_Weight',
            'Product_Sugar_Content',
            'Product_Allocated_Area',
            'Product_MRP',
            'Store_Size',
            'Store_Location_City_Type',
            'Store_Type',
            'Store_Age_Years',
            'Product_Type_Category'
        ]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return jsonify({'error': f"Missing fields: {missing_fields}"}), 400

        # Convert and transform input
        sample = {
            'Product_Weight': float(data['Product_Weight']),
            'Product_Sugar_Content': data['Product_Sugar_Content'],
            'Product_Allocated_Area_Log': np.log1p(float(data['Product_Allocated_Area'])),  # transform here
            'Product_MRP': float(data['Product_MRP']),
            'Store_Size': data['Store_Size'],
            'Store_Location_City_Type': data['Store_Location_City_Type'],
            'Store_Type': data['Store_Type'],
            'Store_Age_Years': int(data['Store_Age_Years']),
            'Product_Type_Category': data['Product_Type_Category']
        }

        input_df = pd.DataFrame([sample])
        print("Transformed input for model:\n", input_df)

        # Make prediction
        prediction = model.predict(input_df).tolist()[0]
        return jsonify({'Predicted_Sales': prediction})

    except Exception as e:
        print("❌ Error during prediction:", str(e))
        return jsonify({'error': f"Prediction failed: {str(e)}"}), 500
@superkart_api.post('/v1/predictbatch')
def predict_sales_batch():
    try:
        # Accept an uploaded CSV file, or a JSON list of records
        if 'file' in request.files:
            df = pd.read_csv(request.files['file'])
        else:
            df = pd.DataFrame(request.get_json())

        required_fields = [
            'Product_Weight', 'Product_Sugar_Content', 'Product_Allocated_Area',
            'Product_MRP', 'Store_Size', 'Store_Location_City_Type',
            'Store_Type', 'Store_Age_Years', 'Product_Type_Category'
        ]
        missing_fields = [f for f in required_fields if f not in df.columns]
        if missing_fields:
            return jsonify({'error': f"Missing columns: {missing_fields}"}), 400

        # Same transforms and column order as /v1/predict
        input_df = pd.DataFrame({
            'Product_Weight': df['Product_Weight'].astype(float),
            'Product_Sugar_Content': df['Product_Sugar_Content'],
            'Product_Allocated_Area_Log': np.log1p(df['Product_Allocated_Area'].astype(float)),
            'Product_MRP': df['Product_MRP'].astype(float),
            'Store_Size': df['Store_Size'],
            'Store_Location_City_Type': df['Store_Location_City_Type'],
            'Store_Type': df['Store_Type'],
            'Store_Age_Years': df['Store_Age_Years'].astype(int),
            'Product_Type_Category': df['Product_Type_Category']
        })

        predictions = model.predict(input_df)
        return jsonify({'Predicted_Sales': [float(p) for p in predictions]})

    except Exception as e:
        print("❌ Error during batch prediction:", str(e))
        return jsonify({'error': f"Batch prediction failed: {str(e)}"}), 500
        
# Run the app (for local testing only)
if __name__ == '__main__':
    superkart_api.run(debug=True)
