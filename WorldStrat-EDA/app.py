import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide")
st.title("🌍 WorldStrat 초고속 지도 EDA 대시보드 (pydeck 기반)")

# 데이터 불러오기
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

metadata_path = st.sidebar.text_input("📁 metadata.csv 경로", "WorldStrat-EDA/dataset_download/metadata.csv")
try:
    df = load_data(metadata_path)
    st.success("✅ metadata.csv 로드 완료")
except Exception as e:
    st.error(f"❌ 불러오기 실패: {e}")
    st.stop()

# 위도/경도 컬럼 선택
lat_col = st.sidebar.selectbox("위도 컬럼 선택", options=df.columns, index=df.columns.get_loc("lat"))
lon_col = st.sidebar.selectbox("경도 컬럼 선택", options=df.columns, index=df.columns.get_loc("lon"))

# 선택적 필터링
st.sidebar.markdown("### ☁️ 클라우드 커버 필터")
if "cloud_cover" in df.columns:
    cloud_max = st.sidebar.slider("최대 클라우드 커버 (%)", float(df["cloud_cover"].min()), float(df["cloud_cover"].max()), float(df["cloud_cover"].max()))
    df = df[df["cloud_cover"] <= cloud_max]

# pydeck 지도 시각화
st.header("🗺️ 고속 시각화 - 위성 이미지 위치 (pydeck 기반)")
if lat_col and lon_col and not df.empty:
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=df[lat_col].mean(),
            longitude=df[lon_col].mean(),
            zoom=2,
            pitch=0,
        ),
        tooltip={"text": "위치: [{lat}, {lon}]"},
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position=f"[{lon_col}, {lat_col}]",
                get_color='[200, 30, 0, 160]',
                get_radius=5000,
                pickable=True,
            ),
        ],
    ))
else:
    st.warning("위도/경도 컬럼 또는 데이터가 유효하지 않습니다.")

# 선택적: 통계 정보
if "cloud_cover" in df.columns:
    st.header("📊 클라우드 커버 요약 통계")
    st.write(df["cloud_cover"].describe())
