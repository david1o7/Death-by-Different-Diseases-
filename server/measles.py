from flask import Flask , jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
cors = CORS(app, origins="*")
@app.route("/api/measles/data", methods=["GET"])
def get_death_data():
    try:
        df = pd.read_csv("data.csv", header=1)
        df.rename(columns={"Countries, territories and areas": "country"}, inplace=True)
        
        melted_df = df.melt(id_vars='country', var_name='year', value_name='cases')
        
        melted_df.dropna(subset=['cases'], inplace=True)
        
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
    app.run(debug=True, port=8080)