from flask import Flask, render_template, request
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

def load_and_preprocess_data():
    data_dir = 'data'
    all_data = {}
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv') and 'Laju Pertumbuhan Produk Domestik Regional Bruto' in filename:
            year_str = filename.split(',')[-1].split('.')[0].strip()
            try:
                year = int(year_str)
            except ValueError:
                try:
                    year = int(year_str.split('(')[0].strip())
                except ValueError:
                    print(f"Could not extract year from filename: {filename}")
                    continue

            filepath = os.path.join(data_dir, filename)
            df = pd.read_csv(filepath)

            data_start_row = None
            for i, row in df.iterrows():
                if isinstance(row.iloc[0], str) and row.iloc[0] not in ['Provinsi', '']:
                    data_start_row = i
                    break

            if data_start_row is None:
                print(f"Could not find data start in {filename}")
                continue

            df = pd.read_csv(filepath, skiprows=data_start_row)

            data_end_row = None
            for i, row in df.iterrows():
                if pd.isna(row.iloc[0]) or row.iloc[0] in ['Catatan', 'The difference between the total of GRDP of 34 Provinces and the GDP of Indonesia due to the statistical discrepancies.Data 2021: Preliminary figuresData 2022: Very Preliminary figures,']:
                    data_end_row = i
                    break

            if data_end_row is not None:
                df = df.iloc[:data_end_row]

            growth_col = [col for col in df.columns if 'Laju Pertumbuhan Produk Domestik Bruto' in col][0]
            df = df.rename(columns={'Provinsi': 'Provinsi', growth_col: 'Laju_Pertumbuhan'})

            df['Laju_Pertumbuhan'] = pd.to_numeric(df['Laju_Pertumbuhan'], errors='coerce')
            df = df.dropna(subset=['Laju_Pertumbuhan'])

            for index, row in df.iterrows():
                provinsi = row['Provinsi']
                pertumbuhan = row['Laju_Pertumbuhan']
                if provinsi not in all_data:
                    all_data[provinsi] = []
                all_data[provinsi].append((year, pertumbuhan))

    national_data = []
    years = sorted(list(set(year for data_list in all_data.values() for year, _ in data_list)))
    for year in years:
        yearly_growths = []
        for provinsi in all_data:
            yearly_growths.extend([growth for y, growth in all_data[provinsi] if y == year])
        if yearly_growths:
            national_data.append((year, np.mean(yearly_growths)))

    all_data['Nasional'] = national_data
    return all_data

def train_and_predict(data, n_years=3):
    predictions = {}
    current_year = 2024
    future_years = np.array([current_year + i for i in range(1, n_years + 1)]).reshape(-1, 1)

    for entity, yearly_data in data.items():
        if len(yearly_data) >= 2:
            years = np.array([item[0] for item in yearly_data]).reshape(-1, 1)
            growths = np.array([item[1] for item in yearly_data])

            model = LinearRegression()
            model.fit(years, growths)

            future_predictions = model.predict(future_years)
            predictions[entity] = [(int(year[0]), float(pred)) for year, pred in zip(future_years, future_predictions)]
        else:
            predictions[entity] = [("Tidak cukup data untuk prediksi", "")]
    return predictions

@app.route('/', methods=['GET', 'POST'])
def index():
    predictions = None
    pdrb_data = None
    if request.method == 'POST':
        pdrb_data = load_and_preprocess_data()
        predictions = train_and_predict(pdrb_data, n_years=3)
    return render_template('index.html', predictions=predictions, pdrb_data=pdrb_data)

if __name__ == '__main__':
    app.run(debug=True)