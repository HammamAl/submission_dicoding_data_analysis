import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('dashboard/main_data.csv')

main_data = load_data()

# Load delivery_review_df.csv untuk visualisasi 1-4
@st.cache_data
def load_delivery_review():
    return pd.read_csv('dashboard/delivery_review_df.csv', parse_dates=[
        'order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date'
    ])
delivery_review_df = load_delivery_review()

# Helper functions
def get_chart_data(chart_name, subchart=""):
    if subchart:
        return main_data[(main_data['chart'] == chart_name) & (main_data['subchart'] == subchart)]
    return main_data[main_data['chart'] == chart_name]

def add_value_labels(ax, spacing=5):
    """Tambahkan label nilai di atas bar chart"""
    for rect in ax.patches:
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2
        space = spacing
        va = 'bottom'
        if y_value < 0:
            space = -spacing
            va = 'top'
        label = "{:.2f}".format(y_value)
        ax.annotate(
            label,
            (x_value, y_value),
            xytext=(0, space),
            textcoords="offset points",
            ha='center',
            va=va,
            fontsize=10,
            fontweight='bold')

# Sidebar
st.sidebar.title("E-Commerce Analytics Dashboard")
st.sidebar.image("https://img.icons8.com/color/96/000000/online-store.png", width=100)

page = st.sidebar.radio(
    "Pilih Analisis:",
    ["Delivery & Rating Analysis", "Repurchase Analysis"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("Dashboard ini menampilkan analisis data e-commerce untuk membantu meningkatkan rating dan tingkat pembelian ulang pelanggan.")
st.sidebar.markdown("Data source: E-Commerce Public Dataset")
st.sidebar.markdown("Created by: Hammam Alfarisy")

# Main content
if page == "Delivery & Rating Analysis":
    st.title("Analisis Waktu Pengiriman & Rating")
    st.markdown("Analisis korelasi antara waktu pengiriman dengan rating review dalam 6 bulan terakhir dan strategi untuk meningkatkan rating.")

    # 1. Korelasi Waktu Pengiriman dan Rating Review (scatter + regresi)
    st.header("1. Korelasi Waktu Pengiriman dan Rating Review")
    # Hitung korelasi pada SELURUH DATA, bukan sample
    correlation = delivery_review_df['delivery_time_days'].corr(delivery_review_df['review_score'])

    plt.figure(figsize=(10, 6))
    sample_size = min(5000, len(delivery_review_df))
    sample_df = delivery_review_df.sample(sample_size, random_state=42)
    ax = sns.regplot(x='delivery_time_days', y='review_score', 
                    data=sample_df, scatter_kws={'alpha':0.3, 's':20}, 
                    line_kws={'color':'red', 'linewidth':2})
    plt.text(0.05, 0.95, f'Korelasi: {correlation:.3f}', 
            transform=ax.transAxes, fontsize=12, 
            bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    x_limit = np.percentile(delivery_review_df['delivery_time_days'], 95)
    plt.xlim(0, x_limit)
    plt.title('Korelasi antara Waktu Pengiriman dan Rating Review', fontsize=14)
    plt.xlabel('Waktu Pengiriman (hari)', fontsize=12)
    plt.ylabel('Rating Review (1-5)', fontsize=12)
    plt.tight_layout()
    st.pyplot(plt.gcf())
    st.info(f"Korelasi antara waktu pengiriman dan rating review: *{correlation:.3f}*")
    st.markdown("_Interpretasi: Korelasi negatif menunjukkan semakin lama pengiriman, semakin rendah rating._")

    # 2. Boxplot waktu pengiriman per rating
    st.header("2. Distribusi Waktu Pengiriman per Rating")
    plt.figure(figsize=(10, 6))
    ax = sns.boxplot(x='review_score', y='delivery_time_days', data=delivery_review_df, 
                     order=[1, 2, 3, 4, 5], showfliers=False)
    sns.pointplot(x='review_score', y='delivery_time_days', data=delivery_review_df,
                  order=[1, 2, 3, 4, 5], color='red', markers='D', scale=0.7, ax=ax)
    y_limit = np.percentile(delivery_review_df['delivery_time_days'], 95)
    plt.ylim(0, y_limit)
    for i, score in enumerate([1, 2, 3, 4, 5]):
        mean_val = delivery_review_df[delivery_review_df['review_score']==score]['delivery_time_days'].mean()
        plt.text(i, mean_val + 0.5, f'{mean_val:.1f}', ha='center', fontsize=10, 
                 bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.2'))
    plt.title('Distribusi Waktu Pengiriman per Rating Review (6 Bulan Terakhir)', fontsize=14)
    plt.xlabel('Rating Review', fontsize=12)
    plt.ylabel('Waktu Pengiriman (hari)', fontsize=12)
    plt.tight_layout()
    st.pyplot(plt.gcf())

    # 3. Barplot rata-rata waktu pengiriman per rating
    st.header("3. Rata-rata Waktu Pengiriman per Rating")
    plt.figure(figsize=(10, 6))
    mean_delivery = delivery_review_df.groupby('review_score')['delivery_time_days'].mean().reset_index()
    ax = sns.barplot(x='review_score', y='delivery_time_days', data=mean_delivery)
    add_value_labels(ax)
    overall_mean = delivery_review_df['delivery_time_days'].mean()
    plt.axhline(y=overall_mean, color='red', linestyle='--', alpha=0.7)
    plt.text(4.5, overall_mean + 0.2, f'Rata-rata: {overall_mean:.2f}', color='red')
    plt.title('Rata-rata Waktu Pengiriman per Rating', fontsize=14)
    plt.xlabel('Rating Review', fontsize=12)
    plt.ylabel('Rata-rata Waktu Pengiriman (hari)', fontsize=12)
    plt.tight_layout()
    st.pyplot(plt.gcf())

    # 4. Rating berdasarkan status ketepatan pengiriman
    st.header("4. Rating Berdasarkan Status Ketepatan Pengiriman")
    # Buat kolom status ketepatan pengiriman jika belum ada
    if 'delivery_status' not in delivery_review_df.columns:
        def status(row):
            diff = (row['order_delivered_customer_date'] - row['order_estimated_delivery_date']).days
            if diff < -3:
                return 'Very Early (>3 days)'
            elif diff < -1:
                return 'Early (1-3 days)'
            elif diff <= 1:
                return 'On Time (±1 day)'
            elif diff <= 3:
                return 'Late (1-3 days)'
            else:
                return 'Very Late (>3 days)'
        delivery_review_df['delivery_status'] = delivery_review_df.apply(status, axis=1)
    delivery_status_order = ['Very Early (>3 days)', 'Early (1-3 days)', 'On Time (±1 day)', 
                             'Late (1-3 days)', 'Very Late (>3 days)']
    delivery_status_rating = delivery_review_df.groupby('delivery_status')['review_score'].mean().reindex(delivery_status_order).reset_index()
    delivery_status_rating.columns = ['delivery_status', 'mean']
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x='delivery_status', y='mean', data=delivery_status_rating, order=delivery_status_order)
    add_value_labels(ax)
    overall_rating_mean = delivery_review_df['review_score'].mean()
    plt.axhline(y=overall_rating_mean, color='red', linestyle='--', alpha=0.7)
    plt.text(4.5, overall_rating_mean + 0.05, f'Rata-rata: {overall_rating_mean:.2f}', color='red')
    plt.title('Rata-rata Rating Berdasarkan Status Ketepatan Pengiriman', fontsize=14)
    plt.xlabel('Status Ketepatan Pengiriman', fontsize=12)
    plt.ylabel('Rata-rata Rating', fontsize=12)
    plt.xticks(rotation=20)
    plt.tight_layout()
    st.pyplot(plt.gcf())

   # 5. Distribusi status ketepatan pengiriman
    st.header("5. Distribusi Status Ketepatan Pengiriman")
    status_dist_data = get_chart_data('barplot_status_distribution')

    if not status_dist_data.empty:
        # Tingkatkan ukuran figure untuk memberikan ruang lebih
        fig, ax = plt.subplots(figsize=(10, 7))  # Tinggi ditambah dari 6 ke 7
        
        # Urutkan status pengiriman secara logis
        delivery_status_order = ['Very Early (>3 days)', 'Early (1-3 days)', 'On Time (±1 day)', 
                                'Late (1-3 days)', 'Very Late (>3 days)']
        
        # Buat categorical type dengan urutan yang benar
        status_dist_data['x'] = pd.Categorical(
            status_dist_data['x'], 
            categories=delivery_status_order,
            ordered=True
        )
        
        # Urutkan data
        status_dist_data = status_dist_data.sort_values('x')
        
        # Plot bar chart
        bars = sns.barplot(x='x', y='value', data=status_dist_data, ax=ax)
        
        # Dapatkan nilai maksimum untuk mengatur batas y
        max_value = status_dist_data['value'].max()
        
        # Tambahkan label persentase dan jumlah di atas bar
        for i, p in enumerate(ax.patches):
            note = status_dist_data.iloc[i]['note']
            count = note.split('=')[1] if '=' in note else ''
            percentage = status_dist_data.iloc[i]['value']
            
            # Sesuaikan posisi vertikal anotasi
            ax.annotate(f'{percentage:.1f}%\n({count})', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', fontsize=10,
                        xytext=(0, 3),  # Kurangi jarak vertikal
                        textcoords='offset points')
        
        # Atur batas sumbu y dengan ruang tambahan di atas
        plt.ylim(0, max_value * 1.25)  # Tambahkan 25% ruang di atas nilai maksimum
        
        plt.title('Distribusi Status Ketepatan Pengiriman', fontsize=14, pad=15)  # Tambahkan padding pada judul
        plt.xlabel('Status Pengiriman', fontsize=12)
        plt.ylabel('Persentase (%)', fontsize=12)
        plt.xticks(rotation=20)
        plt.grid(axis='y', linestyle='--', alpha=0.3)
        
        # Tambahkan padding di sekitar plot
        plt.tight_layout(pad=2.0)
        
        st.pyplot(fig)

        
    # 6. Kategori produk dengan rating terendah dan waktu pengiriman terlama
    st.header("6. Kategori Produk dengan Rating Terendah dan Waktu Pengiriman Terlama")
    rating_data = get_chart_data('worst_categories', 'rating')
    delivery_data = get_chart_data('worst_categories', 'delivery_time')
    
    if not rating_data.empty and not delivery_data.empty:
        # Gabungkan data
        worst_categories = pd.merge(
            rating_data, 
            delivery_data, 
            on='x', 
            suffixes=('_rating', '_delivery')
        )
        
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        # Plot rating pada sumbu y kiri
        color = 'tab:blue'
        ax1.set_xlabel('Kategori Produk', fontsize=12)
        ax1.set_ylabel('Rating Rata-rata', fontsize=12, color=color)
        bars = ax1.barh(worst_categories['x'], 
                       worst_categories['value_rating'], color=color, alpha=0.7)
        ax1.tick_params(axis='y', labelsize=10)
        ax1.set_xlim(3.5, 5.0)  # Sesuaikan untuk menunjukkan perbedaan dengan jelas
        
        # Tambahkan nilai rating pada bar
        for i, bar in enumerate(bars):
            ax1.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2, 
                     f"{worst_categories['value_rating'].iloc[i]:.2f}", 
                     va='center', fontsize=9)
        
        # Plot waktu pengiriman pada sumbu y kanan
        ax2 = ax1.twiny()
        color = 'tab:red'
        ax2.set_xlabel('Waktu Pengiriman (hari)', fontsize=12, color=color)
        ax2.tick_params(axis='x', labelcolor=color)
        ax2.set_xlim(0, 20)  # Sesuaikan berdasarkan data
        
        # Plot waktu pengiriman sebagai titik
        for i, (_, row) in enumerate(worst_categories.iterrows()):
            ax2.scatter(row['value_delivery'], i, color=color, s=100, zorder=3)
            ax2.text(row['value_delivery'] + 0.5, i, 
                     f"{row['value_delivery']:.1f} hari", 
                     va='center', color=color, fontsize=9)
        
        plt.title('10 Kategori Produk dengan Rating Terendah', fontsize=14)
        plt.tight_layout()
        
        st.pyplot(fig)
        
        st.markdown("""
        **Insight:**
        - Kategori produk dengan rating terendah sering memiliki waktu pengiriman yang lebih lama.
        - Beberapa kategori seperti office_furniture memiliki waktu pengiriman sangat lama (>15 hari).
        - Fokus perbaikan pada kategori-kategori ini dapat meningkatkan rating keseluruhan.
        """)
    
    # 7. Tren rating bulanan dan proyeksi target
    st.header("7. Tren Rating Bulanan dan Proyeksi Target")
    trend_data = get_chart_data('monthly_ratings')
    proj_data = get_chart_data('monthly_ratings_projection')
    
    if not trend_data.empty:
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Pastikan bulan diurutkan secara kronologis
        trend_data['order_month_dt'] = pd.to_datetime(trend_data['x'], format='%Y-%m')
        trend_data = trend_data.sort_values('order_month_dt')
        
        # Plot tren rating bulanan
        ax = sns.lineplot(x='x', y='value', data=trend_data, 
                         marker='o', markersize=10, linewidth=2)
        
        # Tambahkan nilai di atas titik
        for i, row in enumerate(trend_data.itertuples()):
            ax.text(i, row.value + 0.02, f'{row.value:.3f}', ha='center', fontsize=10)
        
        # Tambahkan proyeksi untuk 3 bulan ke depan (90 hari)
        if not proj_data.empty:
            current_data = proj_data[proj_data['subchart'] == 'current']
            target_data = proj_data[proj_data['subchart'] == 'target']
            
            if not current_data.empty and not target_data.empty:
                last_rating = current_data['value'].values[0]
                target_rating = target_data['value'].values[0]
                
                # Tambahkan bulan proyeksi ke sumbu x
                all_months = list(trend_data['x']) + [target_data['x'].values[0]]
                plt.xticks(range(len(all_months)), all_months, rotation=45)
                
                # Gambar garis proyeksi
                x_current = len(trend_data) - 1
                x_target = len(trend_data)  # 90 hari ≈ 3 bulan
                plt.plot([x_current, x_target], [last_rating, target_rating], 'r--', linewidth=2)
                
                # Tambahkan anotasi target
                plt.scatter(x_target, target_rating, color='red', s=100, zorder=5)
                plt.text(x_target, target_rating + 0.05, f'Target: {target_rating:.2f}', 
                         color='red', ha='center', fontsize=12, fontweight='bold')
                
                # Tambahkan area yang menunjukkan peningkatan 0.5 poin
                plt.fill_between([x_current, x_target], [last_rating, last_rating], 
                                [last_rating, target_rating], color='red', alpha=0.1)
                plt.text((x_current + x_target)/2, (last_rating + target_rating)/2 - 0.05, 
                         '+0.5 poin', color='red', ha='center', fontsize=10)
        
        plt.title('Tren Rata-rata Rating Review per Bulan dan Target 90 Hari', fontsize=14)
        plt.xlabel('Bulan', fontsize=12)
        plt.ylabel('Rata-rata Rating', fontsize=12)
        plt.ylim(4.0, 5.0)  # Sesuaikan untuk melihat perbedaan dengan jelas
        plt.grid(True, linestyle='--', alpha=0.3)
        
        st.pyplot(fig)
        
        st.markdown("""
        **Strategi untuk Meningkatkan Rating 0.5 Poin dalam 90 Hari:**
        1. **Percepat Pengiriman**: Fokus pada pengurangan waktu pengiriman, terutama untuk kategori produk dengan rating rendah.
        2. **Tingkatkan Akurasi Estimasi**: Pastikan estimasi waktu pengiriman realistis untuk mengelola ekspektasi pelanggan.
        3. **Komunikasi Proaktif**: Beri tahu pelanggan jika ada keterlambatan dan berikan kompensasi.
        4. **Pelatihan Seller**: Edukasi seller tentang pentingnya pengiriman tepat waktu dan dampaknya pada rating.
        5. **Program Insentif**: Berikan insentif untuk seller dengan performa pengiriman terbaik.
        """)

elif page == "Repurchase Analysis":
    st.title("Analisis Pembelian Ulang Setelah Review Negatif")
    st.markdown("Analisis persentase pelanggan yang memberikan review negatif (1-2 bintang) namun melakukan pembelian kembali dalam 30 hari, dan strategi untuk meningkatkan tingkat pembelian ulang.")
    
    # 8. Persentase pembelian ulang setelah review negatif (pie chart)
    st.header("1. Persentase Pembelian Ulang Setelah Review Negatif")
    pie_data = get_chart_data('repurchase_pie')
    
    if not pie_data.empty:
        repurchase_rate = pie_data[pie_data['x'] == 'repurchase_rate']['value'].values[0]
        total_negative_reviews = pie_data[pie_data['x'] == 'total_negative_reviews']['value'].values[0]
        total_repurchase = pie_data[pie_data['x'] == 'total_repurchase']['value'].values[0]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        labels = ['Tidak Repurchase', 'Repurchase ≤30 hari']
        sizes = [100-repurchase_rate, repurchase_rate]
        colors = ['#ff9999','#66b3ff']
        
        # Buat pie chart dengan proporsi yang akurat
        ax.pie(sizes, labels=labels, autopct='%1.2f%%', startangle=90, colors=colors,
               textprops={'fontsize': 12}, wedgeprops={'linewidth': 1, 'edgecolor': 'white'})
        
        # Tambahkan jumlah absolut
        plt.annotate(f'Total review negatif: {int(total_negative_reviews):,}', 
                     xy=(0.5, 0.05), xycoords='figure fraction', 
                     ha='center', fontsize=12)
        plt.annotate(f'Repurchase dalam 30 hari: {int(total_repurchase):,}', 
                     xy=(0.5, 0.01), xycoords='figure fraction', 
                     ha='center', fontsize=10)
        
        plt.axis('equal') 
        plt.title('Persentase Pembelian Ulang ≤30 Hari Setelah Review Negatif', 
                  fontsize=13, 
                  pad=20) 
        
        st.pyplot(fig)
        
        st.markdown(f"""
        **Insight:**
        - Hanya **{repurchase_rate:.2f}%** pelanggan yang memberikan review negatif melakukan pembelian ulang dalam 30 hari.
        - Dari total {int(total_negative_reviews):,} review negatif, hanya {int(total_repurchase):,} yang melakukan pembelian ulang.
        - Ini menunjukkan bahwa sebagian besar pelanggan yang kecewa cenderung tidak kembali dalam jangka pendek.
        """)
    
   # 9. Pembelian ulang berdasarkan rating negatif
    st.header("2. Pembelian Ulang Berdasarkan Rating Negatif")
    rating_data = get_chart_data('repurchase_by_rating')

    if not rating_data.empty:
        # Tingkatkan ukuran figure untuk memberikan ruang lebih
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Plot bar chart
        bars = sns.barplot(x='x', y='value', data=rating_data, ax=ax)
        
        # Dapatkan nilai maksimum untuk mengatur batas y
        max_value = rating_data['value'].max()
        
        # Tambahkan nilai persentase dan jumlah di atas bar
        for i, p in enumerate(ax.patches):
            note = rating_data.iloc[i]['note']
            percentage = rating_data.iloc[i]['value']
            
            # Sesuaikan posisi vertikal anotasi (kurangi jarak dari bar)
            ax.annotate(f'{percentage:.2f}%\n({note})', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', fontsize=11,
                        xytext=(0, 5),  # Kurangi jarak vertikal
                        textcoords='offset points')
        
        # Atur batas sumbu y dengan ruang tambahan di atas
        plt.ylim(0, max_value * 1.25)  # Tambahkan 25% ruang di atas nilai maksimum
        
        plt.title('Persentase Repurchase ≤30 Hari per Rating Negatif', fontsize=14, pad=20)  # Tambahkan padding pada judul
        plt.xlabel('Rating Review', fontsize=12)
        plt.ylabel('Persentase Repurchase (%)', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.3)
        
        # Tambahkan padding di bagian atas
        plt.tight_layout(pad=3.0)
        
        st.pyplot(fig)

    
    # 10. Distribusi waktu hingga pembelian ulang
    st.header("3. Distribusi Waktu Hingga Pembelian Ulang")
    dist_data = get_chart_data('repurchase_time_distribution', '')
    median_data = get_chart_data('repurchase_time_distribution', 'median')

    if not dist_data.empty:
        # Tingkatkan ukuran figure untuk memberikan ruang lebih
        fig, ax = plt.subplots(figsize=(12, 7))  # Tinggi ditambah dari 6 ke 7
        
        # Plot histogram dengan persentase
        bars = sns.barplot(x='x', y='value', data=dist_data, ax=ax)
        
        # Dapatkan nilai maksimum untuk mengatur batas y
        max_value = dist_data['value'].max()
        
        # Tambahkan label persentase dan jumlah di atas bar
        for i, p in enumerate(ax.patches):
            note = dist_data.iloc[i]['note']
            count = note.split('=')[1] if '=' in note else ''
            percentage = dist_data.iloc[i]['value']
            
            # Sesuaikan posisi vertikal anotasi
            ax.annotate(f'{percentage:.1f}%\n({count})', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', fontsize=10,
                        xytext=(0, 3),  # Kurangi jarak vertikal
                        textcoords='offset points')
        
        # Atur batas sumbu y dengan ruang tambahan di atas
        plt.ylim(0, max_value * 1.3)  # Tambahkan 30% ruang di atas nilai maksimum
        
        # Tambahkan garis median jika tersedia
        if not median_data.empty:
            median_val = median_data['value'].values[0]
            
            # Cari bin yang berisi median
            bin_edges = [0, 5, 10, 15, 20, 25, 30]
            for i, (bin_start, bin_end) in enumerate(zip(bin_edges[:-1], bin_edges[1:])):
                if bin_start <= median_val < bin_end:
                    median_bin_index = i
                    break
            
            plt.axvline(x=median_bin_index, color='red', linestyle='--', linewidth=2)
            # Sesuaikan posisi teks median
            plt.text(median_bin_index-0.2, plt.ylim()[1]*0.85, f'Median: {median_val:.1f} hari', 
                    color='red', fontsize=12, ha='right')
    
    # Tambahkan padding pada judul
    plt.title('Distribusi Waktu Selama 30 Hari Hingga Pembelian Ulang Setelah Review Negatif', 
              fontsize=14, pad=20)
    plt.xlabel('Hari Hingga Pembelian Ulang', fontsize=12)
    plt.ylabel('Persentase (%)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Tambahkan padding di sekitar plot
    plt.tight_layout(pad=3.0)
    
    st.pyplot(fig)

    
    # 11. Kategori produk dengan repurchase tertinggi setelah review negatif selama 30 hari
    st.header("4. Kategori Produk dengan Repurchase Tertinggi Setelah Review Negatif")
    top_data = get_chart_data('top_repurchase_categories')
    
    if not top_data.empty:
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Plot bar chart
        bars = sns.barplot(x='value', y='x', data=top_data, ax=ax)
        
        # Tambahkan nilai persentase dan jumlah di samping bar
        for i, p in enumerate(ax.patches):
            note = top_data.iloc[i]['note']
            percentage = top_data.iloc[i]['value']
            
            ax.annotate(f'{percentage:.1f}% ({note})', 
                        (p.get_width() + 1, p.get_y() + p.get_height()/2), 
                        va = 'center', fontsize=10)
        
        plt.title('10 Kategori Produk dengan Repurchase Tertinggi Setelah Review Negatif Selama 30 Hari', fontsize=14)
        plt.xlabel('Persentase Repurchase (%)', fontsize=12)
        plt.ylabel('Kategori Produk', fontsize=12)
        plt.xlim(0, top_data['value'].max() * 1.3)  # Berikan ruang untuk anotasi
        plt.grid(axis='x', linestyle='--', alpha=0.3)
        
        st.pyplot(fig)
    
    # 12. Perbandingan persentase review negatif vs tingkat repurchase per kategori
    st.header("5. Perbandingan Review Negatif vs Repurchase per Kategori")
    rep_data = get_chart_data('category_comparison', 'repurchase_percentage')
    neg_data = get_chart_data('category_comparison', 'negative_review_pct')
    
    if not rep_data.empty and not neg_data.empty:
        # Gabungkan data
        comparison = pd.merge(
            rep_data,
            neg_data,
            on='x',
            suffixes=('_rep', '_neg')
        )
        
        fig, ax = plt.subplots(figsize=(14, 9))
        
        # Gunakan warna yang jelas dan mudah dibedakan
        repurchase_color = '#4285F4'  # Biru Google
        negative_color = '#EA4335'    # Merah Google
        
        # Buat plot batang horizontal untuk repurchase percentage
        bars = ax.barh(
            y=comparison['x'],
            width=comparison['value_rep'],
            height=0.6,  # Bar lebih tebal
            color=repurchase_color,
            alpha=0.8,
            label='Pembelian Ulang'
        )
        
        # Tambahkan nilai pada setiap bar
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(
                width + 0.5,
                bar.get_y() + bar.get_height()/2,
                f'{width:.1f}%',
                va='center',
                fontsize=11,
                color='black',
                fontweight='bold'
            )
        
        # Tambahkan grid horizontal untuk memudahkan pembacaan
        ax.grid(axis='x', linestyle='--', alpha=0.3)
        
        # Buat sumbu kedua untuk persentase review negatif
        ax2 = ax.twiny()
        
        # Plot persentase review negatif sebagai titik merah dengan ukuran lebih besar
        for i, (_, row) in enumerate(comparison.iterrows()):
            # Khusus untuk watches_gift, sesuaikan posisi y agar tidak tumpang tindih
            y_offset = 0
            if row['x'] == 'watches_gifts':
                y_offset = 0.25  # Geser ke atas
            
            ax2.scatter(
                row['value_neg'], 
                i + y_offset,  # Tambahkan offset untuk watches_gift
                color=negative_color,
                s=150,  # Ukuran titik lebih besar
                marker='o',
                edgecolor='white',
                linewidth=1.5,
                alpha=0.9,
                label='Review Negatif' if i == 0 else ""
            )
            
            # Tambahkan label nilai di dekat titik
            ax2.text(
                row['value_neg'] + 2,
                i + y_offset,
                f'{row["value_neg"]:.1f}%',
                va='center',
                fontsize=11,
                color='black',
                fontweight='bold'
            )
        
        # Atur batas sumbu x untuk kedua sumbu
        max_repurchase = comparison['value_rep'].max()
        ax.set_xlim(0, max_repurchase * 1.2)
        
        max_negative = comparison['value_neg'].max()
        ax2.set_xlim(0, max(50, max_negative * 1.2))  # Batasi maksimum 50% untuk fokus pada data
        
        # Tambahkan label sumbu yang jelas dengan font lebih besar
        ax.set_xlabel('Persentase Pelanggan yang Kembali Berbelanja (%)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Kategori Produk', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Persentase Review Negatif (%)', fontsize=14, fontweight='bold', color=negative_color)
        
        # Perbesar ukuran font pada sumbu y
        ax.tick_params(axis='y', labelsize=12)
        ax.tick_params(axis='x', labelsize=12)
        ax2.tick_params(axis='x', labelsize=12, colors=negative_color)
        
        # Tambahkan judul yang informatif dan sederhana
        plt.suptitle('Pelanggan yang Kembali Berbelanja vs Review Negatif', fontsize=18, y=0.98, fontweight='bold')
        plt.title('Berdasarkan Kategori Produk (30 Hari Terakhir)', fontsize=14)
        
        # Tambahkan legenda
        handles = [
            plt.Rectangle((0,0), 1, 1, color=repurchase_color, alpha=0.8),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=negative_color, markersize=12)
        ]
        labels = ['Persentase Pelanggan yang Kembali Berbelanja', 'Persentase Review Negatif']
        
        # Posisikan legenda di bawah grafik
        legend = ax.legend(handles, labels, 
                          loc='upper center', 
                          bbox_to_anchor=(0.5, -0.15),  # Posisi di bawah grafik
                          frameon=True, 
                          framealpha=0.9, 
                          fontsize=12,
                          ncol=2)  # Tampilkan dalam 2 kolom
        legend.get_frame().set_edgecolor('lightgray')
        
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        
        st.pyplot(fig)
    
    # 13. Proyeksi peningkatan repurchase sebesar 25%
    st.header("6. Proyeksi Peningkatan Repurchase 25% (Next Quarter)")
    proj_data = get_chart_data('repurchase_projection')
    
    if not proj_data.empty:
        current_data = proj_data[proj_data['x'] == 'current']
        target_data = proj_data[proj_data['x'] == 'target']
        
        if not current_data.empty and not target_data.empty:
            current_repurchase_rate = current_data['value'].values[0]
            target_repurchase_rate = target_data['value'].values[0]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Data untuk visualisasi
            quarters = ['Current', 'Target (Next Quarter)']
            rates = [current_repurchase_rate, target_repurchase_rate]
            
            # Plot bar chart
            bars = ax.bar(quarters, rates)
            
            # Tambahkan nilai di atas bar dengan offset ke atas
            for i, p in enumerate(bars):
                height = p.get_height()
                note = proj_data.iloc[i]['note']
                
                # Tambahkan offset ke atas
                y_offset = target_repurchase_rate * 0.05
                
                ax.annotate(f'{height:.2f}%\n{note}', 
                            (p.get_x() + p.get_width() / 2., height + y_offset),
                            ha='center', va='bottom', fontsize=11)
            
            # Tambahkan panah dan teks untuk menunjukkan peningkatan
            plt.annotate('', xy=(1, target_repurchase_rate), xytext=(0, current_repurchase_rate),
                         arrowprops=dict(arrowstyle='->', color='red', lw=2))
            
            # Posisikan teks peningkatan
            mid_y = (current_repurchase_rate + target_repurchase_rate)/2
            y_offset_original = (target_repurchase_rate - current_repurchase_rate) * 0.05
            additional_y_offset = (target_repurchase_rate - current_repurchase_rate) * 0.05
            x_adjustment = 0.07
            
            plt.text(0.5 - 0.2 + x_adjustment, mid_y + y_offset_original + additional_y_offset, 
                     f'+25%\n(+{int(total_negative_reviews * current_repurchase_rate * 0.25 / 100):,} pelanggan)', 
                     color='green', ha='center', fontsize=12, fontweight='bold')
            
            plt.title('Target Peningkatan Tingkat Pembelian Ulang Sebesar 25% dalam Kuartal Berikutnya', fontsize=14)
            plt.xlabel('Periode', fontsize=12)
            plt.ylabel('Persentase Pembelian Ulang (%)', fontsize=12)
            plt.ylim(0, target_repurchase_rate * 1.3)  # Berikan ruang untuk anotasi
            plt.grid(axis='y', linestyle='--', alpha=0.3)
            
            st.pyplot(fig)
            
            st.markdown("""
            **Strategi untuk Meningkatkan Tingkat Pembelian Ulang 25% dalam Kuartal Berikutnya:**
            
            1. **Follow-up Personal**: Hubungi pelanggan yang memberikan review negatif untuk menyelesaikan masalah mereka.
            
            2. **Program Insentif**: Tawarkan voucher atau diskon khusus kepada pelanggan yang memberikan review negatif.
            
            3. **Perbaikan Kategori Bermasalah**: Fokus pada kategori produk dengan tingkat review negatif tinggi dan repurchase rendah.
            
            4. **Pelatihan Seller**: Edukasi seller tentang pentingnya layanan pelanggan dan penanganan keluhan.
            
            5. **Sistem Penanganan Keluhan**: Tingkatkan kecepatan dan kualitas respons terhadap keluhan pelanggan.
            
            6. **Program Loyalitas**: Implementasikan program loyalitas khusus untuk pelanggan yang pernah kecewa.
            
            7. **Monitoring Berkala**: Pantau dan evaluasi hasil secara bulanan untuk memastikan target peningkatan tercapai.
            """)

# Footer
st.markdown("---")
st.markdown("Dashboard created by Hammam Alfarisy | E-Commerce Public Dataset Analysis")