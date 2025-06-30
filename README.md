# Addr2CoordHangjeongdong

**Convert Korean addresses to coordinates and administrative dong (행정동) information**

---

## Features

- **엑셀 파일 업로드**
- **주소 → 위경도 변환** (Kakao Local API)
- **위경도 → 행정동 정보 변환** (VWorld Address API)
- **변환결과 엑셀 다운로드**

---

## Demo

<img src="https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png" width="150"/>

> Coming soon! (Streamlit Cloud or your own server)

---

## Installation

```bash
git clone https://github.com/your-username/addr2coord-hangjeongdong.git
cd addr2coord-hangjeongdong
pip install -r requirements.txt
```

---

## Setup (API Keys)

1. Create a file: .streamlit/secrets.toml
```
[kakao]
api_key = "YOUR_KAKAO_REST_API_KEY"
[vworld]
api_key = "YOUR_VWORLD_API_KEY"
```

2. Make sure .streamlit/secrets.toml is in your .gitignore (included by default).

---

##  Usage
```
streamlit run app.py
```
