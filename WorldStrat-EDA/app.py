
import streamlit as st
import pandas as pd
import pydeck as pdk
from PIL import Image
from pathlib import Path
import kagglehub

# 📥 KaggleHub 데이터 다운로드
DATA_PATH = kagglehub.dataset_download("jucor1/worldstrat")
HR_IMAGE_BASE = Path(DATA_PATH) / "hr_dataset" / "12bit"
METADATA_PATH = Path(DATA_PATH) / "metadata.csv"

# 📄 메타데이터 불러오기
df = pd.read_csv(METADATA_PATH)
df = df.dropna(subset=["lat", "lon"])

# ☁️ 클라우드 커버 필터
st.set_page_config(layout="wide")
st.title("🗺️ WorldStrat 시각화 및 이미지 탐색기")
cloud_max = st.slider("☁️ 최대 클라우드 커버 (%)", 0, 100, 20)
filtered_df = df[df["cloud_cover"] <= cloud_max]

# 🌍 지도 시각화
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/satellite-streets-v11",
    initial_view_state=pdk.ViewState(
        latitude=filtered_df["lat"].mean(),
        longitude=filtered_df["lon"].mean(),
        zoom=3.5,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position="[lon, lat]",
            get_radius=30000,
            get_color=[255, 140, 0],
            pickable=True,
        )
    ]
))

# 🔍 tile_id 선택
tile_id = st.selectbox("📌 tile_id 선택", filtered_df["Unnamed: 0"].unique())
tile_dir = HR_IMAGE_BASE / tile_id

if tile_dir.exists():
    st.markdown(f"**디렉토리:** `{tile_dir}`")
    files = list(tile_dir.glob(f"{tile_id}_*"))
    if files:
        cols = st.columns(2)
        for i, path in enumerate(files):
            if path.suffix.lower() in [".png", ".jpg", ".jpeg", ".tif", ".tiff"]:
                try:
                    with cols[i % 2]:
                        st.image(Image.open(path), caption=path.name)
                except Exception as e:
                    st.warning(f"⚠️ {path.name} 로딩 실패: {e}")
    else:
        st.info("ℹ️ 해당 타일에 파일이 없습니다.")
else:
    st.error("❌ 해당 tile_id의 디렉토리를 찾을 수 없습니다.")
