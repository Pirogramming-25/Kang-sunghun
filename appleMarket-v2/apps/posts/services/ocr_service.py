import cv2
import numpy as np
import re
import easyocr

# 인식기는 한 번만 생성 (매번 만들면 느림)
_reader = None


def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['ko', 'en'])
    return _reader


def preprocess(image_path):
    """이미지 전처리: 확대 + 흑백 (한글 경로 대응)"""
    # 한글 경로 대응: numpy로 읽어서 디코딩
    img_array = np.fromfile(image_path, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray


def extract_nutrition(image_path):
    """영양성분표 이미지에서 칼로리/탄단지 추출"""
    reader = get_reader()
    processed = preprocess(image_path)
    result = reader.readtext(processed)

    # 인식된 모든 텍스트를 한 줄로 합침
    full_text = " ".join([text for _, text, _ in result])

    # 숫자 파싱
    nutrition = {
        'calories': _find_calories(full_text),
        'carbohydrate': _find_value(full_text, ['탄수화물', '단수화물', '탄수화']),
        'protein': _find_value(full_text, ['단백질']),
        'fat': _find_value(full_text, ['지방']),
    }
    return nutrition


def _find_calories(text):
    """kcal 앞의 숫자 찾기"""
    match = re.search(r'(\d+)\s*k?cal', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _find_value(text, keywords):
    """키워드 뒤에 나오는 첫 숫자 찾기 (g 단위)"""
    for kw in keywords:
        idx = text.find(kw)
        if idx != -1:
            # 키워드 뒤 20글자 안에서 숫자 찾기
            after = text[idx:idx + 20]
            match = re.search(r'(\d+\.?\d*)', after)
            if match:
                return float(match.group(1))
    return None