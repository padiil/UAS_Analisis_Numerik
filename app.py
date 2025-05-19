from flask import Flask, render_template
import pandas as pd
import os
import sys
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

def load_and_preprocess_data():
    data_dir = 'data'
    all_data = {}
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith('.csv') and 'Laju Pertumbuhan Produk Domestik Regional Bruto' in filename:
            year_str = filename.split(',')[-1].split('.')[0].strip()
            try:
                year = int(year_str)
            except ValueError:
                try:
                    year = int(year_str.split('(')[0].strip())
                except ValueError:
                    print(f"Could not extract year from filename: {filename}", file=sys.stderr)
                    continue

            filepath = os.path.join(data_dir, filename)
            try:
                df = pd.read_csv(filepath, engine="python", on_bad_lines="skip", skip_blank_lines=True)
            except Exception as e:
                print(f"[ERROR] Failed to read {filename}: {e}", file=sys.stderr)
                continue

            # Cari kolom pertumbuhan yang benar
            growth_col = [col for col in df.columns if 'Laju Pertumbuhan Produk Domestik Bruto' in col or 'Laju Pertumbuhan Produk Domestik Regional Bruto' in col][0]
            df = df.rename(columns={growth_col: 'Laju_Pertumbuhan'})

            # --- FIX: Filter baris provinsi valid, buang baris agregat seperti "Jumlah 34 Provinsi" dan baris kosong ---
            def is_valid_provinsi(x):
                if not isinstance(x, str):
                    return False
                x_strip = x.strip()
                if x_strip in ['', 'Provinsi', 'Catatan']:
                    return False
                if 'jumlah' in x_strip.lower() or 'total' in x_strip.lower():
                    return False
                if x_strip == ',' or x_strip == '.':
                    return False
                return True

            df = df[df['Provinsi'].apply(is_valid_provinsi)]
            # --- FIX: Only keep numeric values, drop ... and other non-numeric ---
            df['Laju_Pertumbuhan'] = pd.to_numeric(df['Laju_Pertumbuhan'], errors='coerce')
            df = df.dropna(subset=['Laju_Pertumbuhan'])

            for index, row in df.iterrows():
                provinsi = row['Provinsi'].strip()
                pertumbuhan = row['Laju_Pertumbuhan']
                if provinsi not in all_data:
                    all_data[provinsi] = {}
                # --- Jangan timpa data tahun yang sudah ada, hanya isi jika belum ada ---
                if year not in all_data[provinsi]:
                    all_data[provinsi][year] = pertumbuhan

    filtered_all_data = {}
    for provinsi in all_data:
        yearly_dict = all_data[provinsi]
        tahun_list = sorted(yearly_dict.items(), key=lambda item: item[0])
        if len(tahun_list) > 1:
            filtered_all_data[provinsi] = tahun_list

    national_data = []
    years = sorted(list(set(year for data_list in filtered_all_data.values() for year, _ in data_list)))
    for year in years:
        yearly_growths = []
        for provinsi in filtered_all_data:
            yearly_growths.extend([growth for y, growth in filtered_all_data[provinsi] if y == year])
        if yearly_growths:
            national_data.append((year, np.mean(yearly_growths)))

    filtered_all_data['Nasional'] = sorted(national_data, key=lambda item: item[0])
    return filtered_all_data

def train_and_predict(data, n_years=3):
    predictions = {}
    current_year = 2024
    future_years = np.array([current_year + i for i in range(1, n_years + 1)]).reshape(-1, 1)

    for entity, yearly_data in data.items():
        valid_data = [(y, g) for y, g in yearly_data if not np.isnan(g)]
        if len(valid_data) >= 2:
            years = np.array([item[0] for item in valid_data]).reshape(-1, 1)
            growths = np.array([item[1] for item in valid_data])

            model = LinearRegression()
            model.fit(years, growths)

            future_predictions = model.predict(future_years)
            predictions[entity] = [(int(year[0]), float(pred)) for year, pred in zip(future_years, future_predictions)]
        else:
            predictions[entity] = [("Tidak cukup data untuk prediksi", "")]
    return predictions

@app.route('/', methods=['GET', 'POST'])
def index():
    pdrb_data = load_and_preprocess_data()
    predictions = train_and_predict(pdrb_data, n_years=3)
    # Ambil semua data CSV di folder data/
    data_dir = 'data'
    semua_sumber_data = []
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith('.csv') and 'Laju Pertumbuhan Produk Domestik Regional Bruto' in filename:
            # Ekstrak tahun dari nama file
            year_str = filename.split(',')[-1].split('.')[0].strip()
            try:
                tahun = int(year_str)
            except ValueError:
                try:
                    tahun = int(year_str.split('(')[0].strip())
                except ValueError:
                    tahun = year_str
            filepath = os.path.join(data_dir, filename)
            df = pd.read_csv(filepath)
            header = list(df.columns)
            data = df.values.tolist()
            semua_sumber_data.append({'tahun': tahun, 'header': header, 'data': data, 'filename': filename})
    semua_sumber_data.sort(key=lambda x: x['tahun'])
    return render_template('index.html', predictions=predictions, pdrb_data=pdrb_data, semua_sumber_data=semua_sumber_data)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)