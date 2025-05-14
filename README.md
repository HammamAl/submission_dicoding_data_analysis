# E-commerce Analysis Dashboard ✨

Dashboard analisis data e-commerce Brazil yang menampilkan insight tentang pola pembelian, distribusi geografis, dan analisis review pelanggan.

## Setup Environment

### Menggunakan Anaconda

bash

# Membuat environment baru

conda create –name brazil-ecommerce python=3.9

# Mengaktifkan environment

conda activate brazil-ecommerce

# Menginstall dependencies

pip install -r requirements.txt

### Menggunakan Pip Virtual Environment

bash

# Membuat virtual environment

python -m venv env

# Mengaktifkan virtual environment

# Untuk Windows

env# Untuk MacOS/Linux
source env/bin/activate

# Menginstall dependencies

pip install -r requirements.txt

## Struktur Direktori

submission/
├── dashboard/
│ ├── dashboard.py
│ └── main_data.csv
├── data/
│ ├── brazil_states_shapefile/
│ │ ├── brazil_states_shapefile.shp
│ │ └── ...
│ ├── customers_dataset.csv
│ ├── sellers_dataset.csv
│ ├── products_dataset.csv
│ └── ...
├── notebook.ipynb
├── README.md
└── requirements.txt

## Menjalankan Dashboard

1. Pastikan Anda berada di direktori utama (submission/)
2. Jalankan perintah berikut:
   bash
   streamlit run dashboard/dashboard.py

3. Dashboard akan terbuka secara otomatis di browser Anda pada alamat http://localhost:8501

## Fitur Dashboard

- Visualisasi peta distribusi pelanggan dan penjual di Brazil
- Analisis tren penjualan berdasarkan waktu
- Analisis sentimen review pelanggan
- Insight tentang pola pembelian ulang setelah review negatif
- Analisis ketepatan waktu pengiriman

## Sumber Data

Dataset ini berisi informasi e-commerce Brazil dari tahun 2016 hingga 2018, mencakup informasi tentang:

- Pelanggan dan lokasi geografis mereka
- Penjual dan distribusi mereka
- Produk dan kategorinya
- Pesanan dan status pengirimannya
- Review pelanggan

## Dibuat Oleh

Hammam Alfarisy
