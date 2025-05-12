# E-Commerce Delivery & Review Dashboard

## Deskripsi Proyek

Proyek ini menganalisis dataset publik E-Commerce Brasil untuk menjawab pertanyaan bisnis terkait hubungan waktu pengiriman dengan rating review, serta perilaku pembelian ulang pelanggan setelah pengalaman negatif. Analisis dilakukan mulai dari data wrangling, eksplorasi, visualisasi, hingga insight dan rekomendasi bisnis.  
Dashboard interaktif berbasis Streamlit disediakan untuk eksplorasi insight secara dinamis, termasuk filter tanggal, rating, dan analisis geospasial.

## Struktur Dataset

- customers_dataset.csv
- geolocation_dataset.csv
- order_items_dataset.csv
- order_payments_dataset.csv
- order_reviews_dataset.csv
- orders_dataset.csv
- product_category_name_translation.csv
- products_dataset.csv
- sellers_dataset.csv

## Fitur Dashboard

- Filter interaktif berdasarkan rentang tanggal dan rating review.
- Visualisasi boxplot hubungan waktu pengiriman dan rating.
- Barplot rata-rata rating berdasarkan status ketepatan pengiriman.
- Pie chart persentase pembelian ulang ≤30 hari setelah review negatif.
- Lineplot tren rating bulanan (opsional, toggle).
- Analisis geospasial:
  - Sebaran pelanggan & penjual (pydeck map).
  - Choropleth map rata-rata waktu pengiriman per state.
  - Choropleth map rata-rata rating review per state.
- Insight & rekomendasi utama langsung di dashboard.

## Langkah Analisis

1. Data Wrangling

   - Penggabungan, penilaian, dan pembersihan data (handling missing values, konversi tipe data).
   - Data siap digunakan untuk analisis korelasi, tren, dan geospasial.

2. Exploratory Data Analysis (EDA)
   - Analisis korelasi waktu pengiriman dengan rating review (6 bulan terakhir).
   - Analisis ketepatan pengiriman, kategori produk bermasalah, dan tren rating bulanan.
   - Analisis pembelian ulang setelah review negatif (1-2 bintang) dalam 30 hari.
   - Analisis geospasial: sebaran pelanggan/penjual, performa pengiriman, dan rating per state.

## Hasil Utama & Insight

- Korelasi negatif antara waktu pengiriman dan rating review (korelasi: -0.22). Semakin lama pengiriman, rating cenderung menurun.
- Rata-rata waktu pengiriman rating 5: 8.63 hari, rating 1: 13.78 hari.
- Pengiriman tepat waktu (±1 hari) mendapat rating rata-rata 4.38, sangat terlambat (>3 hari) hanya 2.34.
- Hanya 0.64% pelanggan review negatif yang melakukan pembelian ulang dalam 30 hari, namun dari yang repurchase, 37% (rating 1) dan 31% (rating 2) melakukannya.
- Kategori produk dan wilayah tertentu memiliki performa pengiriman dan rating lebih rendah.
- Analisis geospasial mengidentifikasi area prioritas untuk perbaikan layanan.

## Rekomendasi Bisnis

- Fokus percepatan & ketepatan pengiriman, terutama di kategori/wilayah bermasalah.
- Edukasi dan monitoring seller terkait standar pengiriman.
- Proaktif memberi kompensasi pada kasus keterlambatan.
- Lakukan follow-up personal (voucher/diskon) ke pelanggan review buruk.
- Implementasi program loyalitas khusus untuk pelanggan yang pernah kecewa.
- Pantau tren rating dan repurchase secara bulanan untuk evaluasi strategi.

## Visualisasi

- Boxplot & barplot: hubungan waktu pengiriman dan rating.
- Barplot: rata-rata rating per status pengiriman.
- Pie chart: repurchase setelah review negatif.
- Lineplot: tren rating bulanan (toggle).
- Pydeck scatter map: sebaran pelanggan & penjual.
- Choropleth map: performa pengiriman & rating per state.

## Cara Menjalankan

1. Pastikan semua file dataset tersedia di folder data/.
2. Install dependencies:

   pip install -r requirements.txt

3. Jalankan aplikasi Streamlit:

   streamlit run dashboard.py

4. Ikuti instruksi pada dashboard untuk eksplorasi insight.

## Author

Hammam Alfarisy
