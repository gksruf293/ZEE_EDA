import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import os
from PIL import Image
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🌍 WorldStrat 위성 이미지 EDA 대시보드")

# 데이터 불러오기
st.sidebar.header("📁 데이터 로드")
metadata_path = st.sidebar.text_input("metadata.csv 경로", "WorldStrat-EDA/dataset_download/metadata.csv")
split_path = st.sidebar.text_input("데이터 분할 CSV 경로 (선택)", "dataset_download/stratified_train_val_test_split.csv")

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

try:
    df = load_data(metadata_path)
    st.success("✅ metadata.csv 로드 완료")
except Exception as e:
    st.error(f"❌ metadata.csv 불러오기 실패: {e}")
    st.stop()

# 기본 통계
st.header("📊 기본 통계 및 구조")
st.dataframe(df.head())
st.markdown("컬럼별 요약 통계")
st.write(df.describe(include='all'))

# 지도 시각화
st.header("🗺️ 위성 이미지 위치 시각화")

lat_col = 'latitude' if 'latitude' in df.columns else 'lat'
lon_col = 'longitude' if 'longitude' in df.columns else 'lon'

if lat_col in df.columns and lon_col in df.columns:
    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=2)
    cluster = MarkerCluster().add_to(m)
    for _, row in df.iterrows():
        popup = f"ID: {row.get('id', 'N/A')}<br>Date: {row.get('date', 'N/A')}"
        folium.Marker([row[lat_col], row[lon_col]], popup=popup).add_to(cluster)
    st_folium(m, width=1000, height=500)
else:
    st.warning("⚠️ 위도/경도 컬럼이 존재하지 않습니다.")

# 분할 정보 표시
if os.path.exists(split_path):
    st.header("🔀 Train/Val/Test 분할 정보")
    try:
        split_df = load_data(split_path)
        st.dataframe(split_df['split'].value_counts())
    except Exception as e:
        st.error(f"split CSV 불러오기 오류: {e}")

# 이미지 확인
st.header("🖼️ HR / LR 이미지 비교 보기")

hr_path = st.text_input("HR 이미지 폴더 경로", "dataset_download/hr_dataset_raw")
lr_path = st.text_input("LR 이미지 폴더 경로", "dataset_download/lr_dataset_l2a")
image_id = st.text_input("확인할 이미지 ID (확장자 제외)", "")

def load_img(path):
    try:
        return Image.open(path)
    except:
        return None

if image_id:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("HR 이미지")
        img = load_img(os.path.join(hr_path, f"{image_id}.tif"))
        if img: st.image(img)
        else: st.warning("이미지를 불러올 수 없습니다.")

    with col2:
        st.subheader("LR 이미지")
        img = load_img(os.path.join(lr_path, f"{image_id}.tif"))
        if img: st.image(img)
        else: st.warning("이미지를 불러올 수 없습니다.")
