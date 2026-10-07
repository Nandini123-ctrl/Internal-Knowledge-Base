import io
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This allows the browser to talk to the server

@app.route('/run-audit', methods=['POST'])
def run_audit():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file selected"}), 400
        
        file = request.files['file']
        df = pd.read_excel(io.BytesIO(file.read()))

        # Logic to find errors
        total_items = len(df)
        missing_count = int(df.isnull().sum().sum())
        numeric_cols = df.select_dtypes(include=['number']).columns
        negatives = int((df[numeric_cols] < 0).sum().sum())
        duplicates = int(df.duplicated().sum())

        rows = []
        for _, row in df.iterrows():
            row_dict = row.fillna("N/A").to_dict()
            # Mark as error if there is N/A or a negative number
            has_error = "N/A" in row_dict.values() or any(
                isinstance(v, (int, float)) and v < 0 for v in row_dict.values()
            )
            row_dict['has_error'] = bool(has_error)
            rows.append(row_dict)

        return jsonify({
            "total_items": total_items,
            "missing_data": missing_count,
            "negatives": negatives,
            "duplicates": duplicates,
            "rows": rows
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
