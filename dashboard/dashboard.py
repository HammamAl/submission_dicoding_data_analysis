import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import geopandas as gpd
import pydeck as pdk

st.set_page_config(page_title="E-Commerce Delivery & Review Dashboard", layout="centered")

st.title("E-Commerce Delivery & Review Dashboard")
st.markdown("Insight utama pengiriman, rating, perilaku pelanggan, dan analisis geospasial")

# Load data utama
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    date_cols = [
        'order_purchase_timestamp',
        'order_delivered_customer_date',
        'order_estimated_delivery_date',
        'review_creation_date'
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed')
    return df

df = load_data()

# Sidebar filter
st.sidebar.header("Filter Data")
min_date = df['order_purchase_timestamp'].min()
max_date = df['order_purchase_timestamp'].max()
min_date = min_date.to_pydatetime()
max_date = max_date.to_pydatetime()
date_range = st.sidebar.slider(
    "Pilih rentang tanggal order",
    min_value=min_date,
    max_value=max_date,
    value=(max_date - datetime.timedelta(days=180), max_date),
    format="YYYY-MM-DD"
)
selected_rating = st.sidebar.selectbox(
    "Filter rating review",
    options=[0, 1, 2, 3, 4, 5],
    format_func=lambda x: "Semua" if x == 0 else str(x)
)

# Filter data
mask = (df['order_purchase_timestamp'] >= date_range[0]) & (df['order_purchase_timestamp'] <= date_range[1])
df_filtered = df[mask]
if selected_rating != 0:
    df_filtered = df_filtered[df_filtered['review_score'] == selected_rating]

# Hitung waktu pengiriman
df_filtered['delivery_time_days'] = (df_filtered['order_delivered_customer_date'] - df_filtered['order_purchase_timestamp']).dt.days

# 1. Korelasi Waktu Pengiriman & Rating Review
st.subheader("Korelasi Waktu Pengiriman & Rating Review")
st.markdown(
    "- Semakin lama pengiriman, rating cenderung menurun."
    "\n- Rata-rata pengiriman rating 5: {:.2f} hari, rating 1: {:.2f} hari.".format(
        df_filtered[df_filtered['review_score']==5]['delivery_time_days'].mean(),
        df_filtered[df_filtered['review_score']==1]['delivery_time_days'].mean()
    )
)

fig1, ax1 = plt.subplots(figsize=(5,3))
sns.boxplot(x='review_score', y='delivery_time_days', data=df_filtered, order=[1,2,3,4,5], ax=ax1)
ax1.set_title('Waktu Pengiriman per Rating')
ax1.set_xlabel('Rating')
ax1.set_ylabel('Hari')
st.pyplot(fig1)

# 2. Rata-rata Rating Berdasarkan Ketepatan Pengiriman
st.subheader("Rating vs Ketepatan Pengiriman")
df_filtered['delivery_accuracy_days'] = (df_filtered['order_delivered_customer_date'] - df_filtered['order_estimated_delivery_date']).dt.days
df_filtered['delivery_status'] = pd.cut(
    df_filtered['delivery_accuracy_days'],
    bins=[-1000, -3, -1, 1, 3, 1000],
    labels=['Very Early (>3d)', 'Early (1-3d)', 'On Time (±1d)', 'Late (1-3d)', 'Very Late (>3d)']
)
status_rating = df_filtered.groupby('delivery_status')['review_score'].mean().reset_index()

fig2, ax2 = plt.subplots(figsize=(5,3))
sns.barplot(x='delivery_status', y='review_score', data=status_rating, palette='coolwarm', ax=ax2)
ax2.set_title('Rating Rata-rata per Status Pengiriman')
ax2.set_xlabel('Status Pengiriman')
ax2.set_ylabel('Rating')
plt.xticks(rotation=20)
st.pyplot(fig2)

# 3. Persentase Pembelian Ulang Setelah Review Negatif
st.subheader("Pembelian Ulang Setelah Review Negatif")
neg = df[(df['review_score'].isin([1,2])) & (df['customer_unique_id'].notnull())]
repurchase = 0
if not neg.empty:
    neg = neg.sort_values(['customer_unique_id', 'order_purchase_timestamp'])
    neg['next_order_time'] = neg.groupby('customer_unique_id')['order_purchase_timestamp'].shift(-1)
    neg['days_to_repurchase'] = (neg['next_order_time'] - neg['review_creation_date']).dt.days
    repurchase = (neg['days_to_repurchase'] <= 30).sum()/len(neg) * 100
fig3, ax3 = plt.subplots(figsize=(3,3))
sizes = [100-repurchase, repurchase]
labels = ['Tidak Repurchase', 'Repurchase ≤30 hari']
ax3.pie(sizes, labels=labels, autopct='%1.2f%%', startangle=90, colors=['#ff9999','#66b3ff'])
ax3.set_title('Repurchase ≤30 Hari Setelah Review Negatif')
st.pyplot(fig3)

# 4. Tren Rating Bulanan (opsional, toggle)
show_trend = st.checkbox("Tampilkan Tren Rata-rata Rating Bulanan", value=True)
if show_trend:
    df_filtered['order_month'] = df_filtered['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly = df_filtered.groupby('order_month')['review_score'].mean().reset_index()
    fig4, ax4 = plt.subplots(figsize=(6,3))
    sns.lineplot(x='order_month', y='review_score', data=monthly, marker='o', ax=ax4)
    ax4.set_title('Tren Rating Bulanan')
    ax4.set_xlabel('Bulan')
    ax4.set_ylabel('Rata-rata Rating')
    plt.xticks(rotation=45)
    st.pyplot(fig4)

# 5. Analisis Geospasial
st.header("Analisis Geospasial")

tab1, tab2, tab3 = st.tabs(["Sebaran Pelanggan & Penjual", "Waktu Pengiriman per State", "Rating Review per State"])

with tab1:
    st.subheader("Sebaran Geospasial Pelanggan & Penjual")
    # Ambil sample agar tidak berat
    customer_sample = df_filtered[['customer_lat', 'customer_lng']].dropna().sample(min(2000, len(df_filtered)), random_state=42)
    seller_sample = df_filtered[['seller_lat', 'seller_lng']].dropna().drop_duplicates().sample(min(500, df_filtered[['seller_lat', 'seller_lng']].dropna().drop_duplicates().shape[0]), random_state=42)
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=-14.2350,
            longitude=-51.9253,
            zoom=3.5,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=customer_sample,
                get_position='[customer_lng, customer_lat]',
                get_color='[30, 144, 255, 80]',
                get_radius=2000,
                pickable=False,
            ),
            pdk.Layer(
                "ScatterplotLayer",
                data=seller_sample,
                get_position='[seller_lng, seller_lat]',
                get_color='[255, 0, 0, 160]',
                get_radius=6000,
                pickable=False,
            ),
        ],
        tooltip={"text": "Sebaran pelanggan (biru) & penjual (merah)"}
    ))
    st.caption("Pelanggan: biru, Penjual: merah")

with tab2:
    st.subheader("Rata-rata Waktu Pengiriman per State")
    state_delivery = df_filtered.groupby('customer_state')['delivery_time_days'].mean().reset_index()
    # Load shapefile Brazil
    brazil_states = gpd.read_file('../data/brazil_states_shapefile/brazil_states_shapefile.shp')
    uf_mapping = {
        'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas', 'BA': 'Bahia',
        'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo', 'GO': 'Goiás',
        'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'MG': 'Minas Gerais',
        'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná', 'PE': 'Pernambuco', 'PI': 'Piauí',
        'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte', 'RS': 'Rio Grande do Sul',
        'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina', 'SP': 'São Paulo',
        'SE': 'Sergipe', 'TO': 'Tocantins'
    }
    state_delivery['NM_UF'] = state_delivery['customer_state'].map(uf_mapping)
    state_delivery_map = brazil_states.merge(state_delivery, left_on='NM_UF', right_on='NM_UF', how='left')
    fig, ax = plt.subplots(figsize=(10,7))
    brazil_states.plot(ax=ax, color='whitesmoke', edgecolor='gray')
    state_delivery_map.plot(column='delivery_time_days', cmap='OrRd', legend=True, ax=ax, missing_kwds={"color": "lightgrey"})
    ax.set_title('Rata-rata Waktu Pengiriman per State (hari)')
    ax.set_axis_off()
    st.pyplot(fig)

with tab3:
    st.subheader("Rata-rata Rating Review per State")
    state_rating = df_filtered.groupby('customer_state')['review_score'].mean().reset_index()
    state_rating['NM_UF'] = state_rating['customer_state'].map(uf_mapping)
    state_rating_map = brazil_states.merge(state_rating, left_on='NM_UF', right_on='NM_UF', how='left')
    fig, ax = plt.subplots(figsize=(10,7))
    brazil_states.plot(ax=ax, color='whitesmoke', edgecolor='gray')
    state_rating_map.plot(column='review_score', cmap='YlGnBu', legend=True, ax=ax, missing_kwds={"color": "lightgrey"})
    ax.set_title('Rata-rata Rating Review per State')
    ax.set_axis_off()
    st.pyplot(fig)

# 6. Insight & Rekomendasi
st.subheader("Rekomendasi Utama")
st.markdown(
    "Fokus percepatan & ketepatan pengiriman untuk menaikkan rating.\n"
    "Lakukan follow-up personal (voucher/diskon) ke pelanggan review buruk.\n"
    "Perbaiki pengalaman pada kategori/wilayah bermasalah."
)
