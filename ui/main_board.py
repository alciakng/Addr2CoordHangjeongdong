import pandas as pd
import streamlit as st
import io

from controller.transform_cntrol import get_dong_info_parallel

def main_board():

    st.markdown("""
        <h1 style='font-weight: 700;'>🚀 주소 → 위경도 · 행정동 매핑 서비스 </h1>

        <p style='line-height: 2em; font-weight: 500;'>
        본 프로젝트는 <strong style="color: lightgreen">주소를 포함한 엑셀 파일을 입력</strong>받고,<br>
        해당 주소를 기반으로 <strong style="color: lightgreen">위경도 · 행정동을 매핑 후 엑셀파일로 제공</strong>하는 서비스입니다.            
        </p>
        """, unsafe_allow_html=True)

    # secrets.toml에서 API 키 읽기
    kakao_key = st.secrets["kakao"]["api_key"]
    vworld_key = st.secrets["vworld"]["api_key"]

    st.markdown("kakao_key" + kakao_key)
    st.markdown("vworld_key"+ vworld_key)

    st.markdown("### 📄 엑셀 파일 업로드")
    uploaded_file = st.file_uploader("주소가 포함된 엑셀 파일 업로드", type=['xlsx', 'xls'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("업로드된 데이터 예시:")
        st.dataframe(df.head())

        address_col = st.selectbox("주소가 포함된 컬럼을 선택하세요", df.columns)

        if st.button("행정동 정보 매핑 시작"):
            addresses = df[address_col].dropna().tolist()

            with st.spinner("주소 → 좌표 변환 및 행정동 매핑 중..."):
                result_df = get_dong_info_parallel(addresses, kakao_key, vworld_key)

            st.success("매핑 완료!")
            st.write("결과 데이터:")
            st.dataframe(result_df)

            # 엑셀 다운로드
            output = io.BytesIO()

            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                result_df.to_excel(writer, index=False, sheet_name='Result')
            processed_data = output.getvalue()

            st.download_button(
                label="결과 다운로드 (Excel)",
                data=processed_data,
                file_name='주소_행정동_매핑결과.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )