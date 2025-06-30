import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st

# --- 좌표 가져오는 함수
def get_coords_from_address(address, kakao_key):
    url = 'https://dapi.kakao.com/v2/local/search/address.json'
    headers = {'Authorization': f'KakaoAK {kakao_key}'}
    params = {"query": address}
    logs = []

    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        res.raise_for_status()
        data = res.json()
        if data.get('documents'):
            doc = data['documents'][0]
            x, y = float(doc['x']), float(doc['y'])
            logs.append(f"[Coords Success] {address} → x:{x}, y:{y}")
            return x, y, logs
        else:
            logs.append(f"[Coords Empty] {address}")
    except Exception as e:
        logs.append(f"[Coords Error] {address} | {e}")

    return None, None, logs

# --- 좌표 → 행정동 코드/명
def get_region_code_from_coords(x, y, vworld_key):
    url = "https://api.vworld.kr/req/address"
    params = {
        "service": "address",
        "request": "getAddress",
        "point": f"{x},{y}",
        "crs": "EPSG:4326",
        "format": "json",
        "type": "both",
        "key": vworld_key
    }
    logs = []

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data['response']['status'] == 'OK':
            result = data['response']['result'][1]
            structure = result.get('structure', {})
            dong_name = structure.get('level4A') or structure.get('level4L')
            dong_code = structure.get('level4AC') or structure.get('level4LC')
            logs.append(f"[Dong Success] x:{x}, y:{y} → {dong_name}, {dong_code}")
            return dong_name, dong_code, logs
        else:
            logs.append(f"[Dong Empty] x:{x}, y:{y}")
    except Exception as e:
        logs.append(f"[Dong Error] x:{x}, y:{y} | {e}")

    return None, None, logs

# --- 주소 리스트를 받아 행정동 정보 반환
def get_dong_info_parallel(addresses, kakao_key, vworld_key, max_workers=10):
    results = []

    def worker(address):
        x, y, coord_logs = get_coords_from_address(address, kakao_key)
        all_logs = coord_logs.copy()
        if x is not None and y is not None:
            dong_name, dong_code, dong_logs = get_region_code_from_coords(x, y, vworld_key)
            all_logs.extend(dong_logs)
        else:
            dong_name, dong_code = None, None
        return {'주소': address, '경도': x, '위도': y, '행정동_명': dong_name, '행정동_코드': dong_code, 'logs': all_logs}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(worker, addr): addr for addr in addresses}
        for future in as_completed(futures):
            result = future.result()

            # 👉 메인 스레드에서 로그 출력
            for log_msg in result["logs"]:
                print(log_msg)        # Cloud Logs에 출력
                st.write(log_msg)     # Streamlit 화면에 출력

            results.append(result)

    # logs는 DataFrame에 포함시키지 않고, 결과 데이터만 반환
    return pd.DataFrame([{k: v for k, v in res.items() if k != "logs"} for res in results])