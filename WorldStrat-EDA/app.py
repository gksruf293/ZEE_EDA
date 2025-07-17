import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("🌍 WorldStrat EDA - 풍부한 메타데이터 탐색 대시보드")

# 데이터 로드
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

metadata_path = st.sidebar.text_input("📁 metadata.csv 경로", "dataset_download/metadata.csv")
try:
    df = load_data(metadata_path)
    st.success("✅ metadata.csv 로드 완료")
except Exception as e:
    st.error(f"❌ 불러오기 실패: {e}")
    st.stop()

# 기본 정보
st.header("🔎 데이터 개요")
st.dataframe(df.head())
st.write(df.describe(include="all"))

# 위치 시각화
st.header("🗺️ 이미지 위치 시각화")
lat_col = st.sidebar.selectbox("위도 컬럼 선택", options=df.columns, index=df.columns.get_loc("lat"))
lon_col = st.sidebar.selectbox("경도 컬럼 선택", options=df.columns, index=df.columns.get_loc("lon"))

if lat_col and lon_col:
    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=2)
    cluster = MarkerCluster().add_to(m)
    for _, row in df.iterrows():
        popup = f"POI: {row['Unnamed: 0']}<br>Area: {row['area']} km²"
        folium.Marker([row[lat_col], row[lon_col]], popup=popup).add_to(cluster)
    st_folium(m, width=1000, height=500)

# 날짜 정보 분석
st.header("📅 이미지 날짜 분포")
df["lowres_date"] = pd.to_datetime(df["lowres_date"], errors='coerce')
df["highres_date"] = pd.to_datetime(df["highres_date"], errors='coerce')
fig, ax = plt.subplots(figsize=(10, 4))
df["lowres_date"].dt.year.value_counts().sort_index().plot(kind='bar', ax=ax, color='skyblue', label='Low-Res')
df["highres_date"].dt.year.value_counts().sort_index().plot(kind='bar', ax=ax, color='orange', alpha=0.7, label='High-Res')
plt.legend()
st.pyplot(fig)

# 클라우드 커버 히스토그램
st.header("☁️ 클라우드 커버 분포")
fig2, ax2 = plt.subplots()
sns.histplot(df["cloud_cover"].dropna(), bins=50, ax=ax2, kde=True)
st.pyplot(fig2)

# IPCC, LCCS, SMOD 클래스별 분포
st.header("📊 토지 피복 및 정착지 유형 통계")

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("IPCC Class")
    st.bar_chart(df["IPCC Class"].value_counts())

with col2:
    st.subheader("LCCS Class (상위 10)")
    st.bar_chart(df["LCCS class"].value_counts().head(10))

with col3:
    st.subheader("SMOD Class")
    st.bar_chart(df["SMOD Class"].value_counts())

# delta 값 분석
st.header("📉 해상도 차이 (Delta) 통계")
fig3, ax3 = plt.subplots()
sns.histplot(df["delta"], bins=50, kde=True, ax=ax3)
st.pyplot(fig3)
