# Prediksi Pertumbuhan PDRB Provinsi di Indonesia

Website interaktif untuk visualisasi, prediksi, dan penyajian sumber data pertumbuhan Produk Domestik Regional Bruto (PDRB) provinsi di Indonesia berbasis data BPS, menggunakan model regresi linier sederhana.

---

## Fitur Utama

- **Visualisasi Grafik Interaktif**: Tren historis dan prediksi pertumbuhan PDRB nasional & provinsi (2015–2027) dengan D3.js.
- **Tabel Data & Prediksi**: Tabel pertumbuhan aktual dan hasil prediksi untuk tiap provinsi dan nasional.
- **Sumber Data Transparan**: Semua file CSV sumber data dapat dilihat langsung di halaman utama.
- **Responsive Design**: Tampilan optimal di desktop dan mobile (TailwindCSS).
- **Penjelasan Metode**: Penjelasan lengkap alur, metode regresi, dan analisis hasil.

---

## Struktur Folder

```
UAS ANUM/
├── app.py
├── requirements.txt
├── static/
│   ├── main.js
│   ├── style.css
│   └── img/
│       └── logoUnsil.png
├── templates/
│   └── index.html
├── data/
│   └── *.csv
└── README.md
```

---

## Cara Menjalankan

### 1. Persiapan Lingkungan

Pastikan Python 3.8+ sudah terinstall.

**Install dependencies:**
```bash
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi

```bash
python app.py
```

Akses di browser: [http://localhost:5000](http://localhost:5000)

---

## Penjelasan Alur Sistem

1. **Input Data**  
   - Membaca file CSV pertumbuhan PDRB per provinsi (2015–2024) dari folder `data/`.
   - Data diolah dan dibersihkan, hanya baris provinsi valid yang digunakan.

2. **Prediksi Regresi Linier**  
   - Untuk setiap provinsi & nasional, dilakukan fitting regresi linier sederhana (`sklearn.LinearRegression`) pada data historis.
   - Prediksi pertumbuhan 3 tahun ke depan (2025–2027) dihitung.

3. **Visualisasi & Tabel**  
   - Data historis dan prediksi divisualisasikan dengan grafik interaktif (D3.js).
   - Tabel prediksi dan sumber data CSV ditampilkan di halaman utama.

---

## Teknologi yang Digunakan

- **Backend**: Python Flask, pandas, numpy, scikit-learn
- **Frontend**: HTML, TailwindCSS, JavaScript (D3.js)
- **Deployment**: Gunicorn (opsional)

---

## Sumber Data

- Data diambil dari Badan Pusat Statistik (BPS) Indonesia:  
  *Laju Pertumbuhan Produk Domestik Regional Bruto Atas Dasar Harga Konstan 2010 Menurut Provinsi, 2015–2024*

---

## Catatan & Limitasi

- Model regresi linier cocok untuk tren stabil, kurang akurat untuk provinsi dengan fluktuasi ekstrem.
- Provinsi baru (misal Papua Selatan, Papua Tengah, dst) prediksinya kurang andal karena data historis minim.
- Prediksi tidak mempertimbangkan faktor eksternal/non-linier.

---

## Anggota Kelompok

- SHELVA NUR FATIMAH - 237006069
- FADHIL GANI - 237006082
- BAJSAN ARSYURROHMAN - 237006088
- YUSA PUTRA ROSDIANA - 237006091

Universitas Siliwangi  
Fakultas Teknik - Informatika  
UAS Analisis Numerik 2025

---
