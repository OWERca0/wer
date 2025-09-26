# streamlit run uytam_app.py 
import streamlit as st
import pandas as pd
import requests
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import folium
from streamlit_folium import st_folium
import branca.colormap as cm

# -------------------
# Sayfa ayarları
st.set_page_config(
    page_title="🌾 Tarım Verim ve Gelir Tahmini",
    page_icon="🌱",
    layout="wide"
)

# -------------------
# Basit CSS
st.markdown("""
<style>
body {background-color: #f0f2f6; font-family: 'Arial';}
h1 {color: #2c3e50; text-align: center;}
h2 {color: #16a085;}
.card {background-color:#ffffff; padding:20px; border-radius:10px; box-shadow: 2px 2px 10px #aaaaaa;}
</style>
""", unsafe_allow_html=True)

# -------------------
# Örnek çok şehirli ve çok ürünlü veri seti
data = {
    "yil": [2024]*4,
    "sehir": ["Nevşehir","Nevşehir","Konya","Konya","Ankara","Ankara"],
    "urun": ["Buğday","Patates","Buğday","Patates"],
    "sicaklik": [25,25,27,27],
    "yagis": [280,280,300,300],
    "gubre": [120,120,130,130],
    "verim": [3.2,22.0,3.4,25.0],
    "lat": [38.6247,38.6247,37.8746,37.8746],
    "lon": [34.7126,34.7126,32.4932,32.4932]
}
df = pd.DataFrame(data)

# -------------------
st.title("🌾 Tarım Verim ve Gelir Tahmini")

# -------------------
# Kullanıcı giriş
st.subheader("Girdi Bilgileri")
col1, col2 = st.columns([1,1])

with col1:
    sehir_sec = st.selectbox("Şehir Seçiniz:", df['sehir'].unique())
    urun_sec = st.selectbox("Ürün Seçiniz:", df['urun'].unique())
    gubre_miktar = st.slider("Gübre Miktarı (kg/ha):", 50, 200, 120)
    toprak_buyuklugu = st.number_input("Toprak Büyüklüğü (ha):", 0.1, 100.0, 1.0)

# -------------------
# Random Forest ile verim tahmini
sehir_urun_veri = df[(df['sehir']==sehir_sec) & (df['urun']==urun_sec)]
X = sehir_urun_veri[["sicaklik","yagis","gubre"]]
y = sehir_urun_veri["verim"]

rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X, y)

# Kullanıcı girdisi ile tahmin
tahmini_verim = rf_model.predict([[sehir_urun_veri['sicaklik'].mean(),
                                   sehir_urun_veri['yagis'].mean(),
                                   gubre_miktar]])
toplam_urun = tahmini_verim[0] * toprak_buyuklugu

# -------------------
# Tahmini gelir (örnek sabit fiyat)
urun_fiyat = 200 if urun_sec=="Buğday" else 300
tahmini_gelir = toplam_urun * urun_fiyat

# -------------------
# Renkli kartlar
col1, col2, col3 = st.columns(3)
col1.markdown(f"<div class='card'><h3>💡 Tahmini Verim</h3><h2>{tahmini_verim[0]:.2f} ton/ha</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='card'><h3>🔹 Toplam Ürün</h3><h2>{toplam_urun:.2f} ton</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='card'><h3>💰 Tahmini Gelir</h3><h2>${tahmini_gelir:,.2f}</h2></div>", unsafe_allow_html=True)

# -------------------
# Plotly interaktif grafik
st.subheader("📊 Geçmiş Verim Karşılaştırması")
fig = px.bar(sehir_urun_veri, x='urun', y='verim', color='verim', 
             title=f"{sehir_sec} - {urun_sec} Geçmiş Verim")
fig.add_hline(y=tahmini_verim[0], line_dash="dash", line_color="red", annotation_text="Tahmini Verim")
st.plotly_chart(fig, use_container_width=True)

# -------------------
# Folium harita ile renk skalası
st.subheader("🗺 Şehir ve Verim Haritası")
verim_min = df['verim'].min()
verim_max = df['verim'].max()
colormap = cm.LinearColormap(['red','yellow','green'], vmin=verim_min, vmax=verim_max)

m = folium.Map(location=[38.0, 35.0], zoom_start=6)
for index, row in df.iterrows():
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=12,
        popup=f"{row['sehir']} - {row['urun']} Verim: {row['verim']:.2f} ton/ha",
        color=colormap(row['verim']),
        fill=True,
        fill_color=colormap(row['verim'])
    ).add_to(m)
colormap.add_to(m)
st_folium(m, width=700, height=500)

# -------------------
# Geçmiş veriler
with st.expander("Geçmiş Veriler"):

    st.dataframe(sehir_urun_veri)


