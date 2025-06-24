from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import re

app = Flask(__name__)
cors = CORS(app, origins="*")
@app.route("/api/malaria/data", methods=["GET"])
def get_malaria_data():
    try:
        df = pd.read_csv("malaria_data.csv", header=1)
        df.rename(columns={"Countries, territories and areas": "country"}, inplace=True)
        
        melted_df = df.melt(id_vars='country', var_name='year', value_name='cases')
        
        # Clean the 'cases' column: extract the first number, replace NaN with 0, convert to int
        def extract_number(val):
            if pd.isna(val):
                return 0
            match = re.search(r'\d+', str(val).replace(',', ''))
            return int(match.group()) if match else 0
        melted_df['cases'] = melted_df['cases'].apply(extract_number)
        result = []
        for country, group in melted_df.groupby('country'):
            result.append({
                "country": country,
                "data": group[['year', 'cases']].to_dict(orient='records')
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)