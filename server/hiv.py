from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
cors = CORS(app, origins="*")

@app.route("/api/aids/data", methods=["GET"])
def get_aids_data():
    try:
        df = pd.read_csv("aids.csv")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Rename columns for easier access
        df.rename(columns={
            'Country': 'country',
            'Year': 'year'
        }, inplace=True)

        # Select and rename data columns to be more friendly
        data_columns = {
            'Data.AIDS-Related Deaths.All Ages': 'aids_related_deaths_all_ages',
            'Data.New HIV Infections.All Ages': 'new_hiv_infections_all_ages',
            'Data.People Living with HIV.Total': 'people_living_with_hiv_total'
        }
        
        # Keep only the columns we need
        required_columns = ['country', 'year'] + list(data_columns.keys())
        df_filtered = df[required_columns].copy()
        
        # Rename the data columns
        df_filtered.rename(columns=data_columns, inplace=True)
        
        # Convert to a list of records grouped by country
        result = []
        for country, group in df_filtered.groupby('country'):
            result.append({
                "country": country,
                "data": group.to_dict(orient='records')
            })
            
        return jsonify(result)
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
