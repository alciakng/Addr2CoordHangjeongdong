import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- 좌표 가져오는 함수
def get_coords_from_address(address, kakao_key):
    url = 'https://dapi.kakao.com/v2/local/search/address.json'
    headers = {'Authorization': f'KakaoAK {kakao_key}'}
    params = {"query": address}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        res.raise_for_status()
        data = res.json()
        if data.get('documents'):
            doc = data['documents'][0]
            return float(doc['x']), float(doc['y'])
    except:
        return None, None

    return None, None

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

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data['response']['status'] == 'OK':
            result = data['response']['result'][1]
            structure = result.get('structure', {})
            dong_name = structure.get('level4A') or structure.get('level4L')
            dong_code = structure.get('level4AC') or structure.get('level4LC')
            return dong_name, dong_code
    except:
        return None, None

    return None, None

# --- 주소 리스트를 받아 행정동 정보 반환
def get_dong_info_parallel(addresses, kakao_key, vworld_key, max_workers=10):
    results = []

    def worker(address):
        x, y = get_coords_from_address(address, kakao_key)
        if x is not None and y is not None:
            dong_name, dong_code = get_region_code_from_coords(x, y, vworld_key)
        else:
            dong_name, dong_code = None, None
        return {'주소': address, '경도': x, '위도': y, '행정동_명': dong_name, '행정동_코드': dong_code}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(worker, addr): addr for addr in addresses}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    return pd.DataFrame(results)