from pydantic import BaseModel


# 1. 특송사(DHL/FedEx) 매월 변동 유류할증료 및 통관 대행 수수료 (CAD)
EXPRESS_FUEL_SURCHARGE = 0.25   # 유류할증료 25% (필요시 숫자만 수정)
EXPRESS_BROKERAGE_FEE = 15.0    # 특송 통관 대행 수수료 ($15 CAD)

# 2. 출발국별 기본 운송 요율 데이터 (캐나다 도착 기준, CAD 환산 추정치)
ORIGIN_SHIPPING_RATES = {
    "KR": {
        "name": "한국 (South Korea)",
        "kpacket": {"base": 10.5, "per_500g": 4.5, "max_kg": 2.0, "days": "7~14일"},
        "ems":     {"base": 28.0, "per_500g": 6.8, "max_kg": 30.0, "days": "4~7일"},
        "express": {"base": 32.0, "per_500g": 7.5, "max_kg": 70.0, "days": "3~5일"},
        "ocean":   {"min_cbm": 0.5, "per_cbm": 220.0, "per_kg_min": 2.8, "days": "25~35일"}
    },
    "JP": {
        "name": "일본 (Japan)",
        "kpacket": {"base": 11.0, "per_500g": 4.8, "max_kg": 2.0, "days": "7~14일"},
        "ems":     {"base": 30.0, "per_500g": 7.2, "max_kg": 30.0, "days": "4~7일"},
        "express": {"base": 34.0, "per_500g": 7.8, "max_kg": 70.0, "days": "3~5일"},
        "ocean":   {"min_cbm": 0.5, "per_cbm": 240.0, "per_kg_min": 3.0, "days": "25~35일"}
    },
    "TW": {
        "name": "대만 (Taiwan)",
        "kpacket": {"base": 10.0, "per_500g": 4.3, "max_kg": 2.0, "days": "8~15일"},
        "ems":     {"base": 27.0, "per_500g": 6.5, "max_kg": 30.0, "days": "5~8일"},
        "express": {"base": 31.0, "per_500g": 7.2, "max_kg": 70.0, "days": "3~5일"},
        "ocean":   {"min_cbm": 0.5, "per_cbm": 210.0, "per_kg_min": 2.7, "days": "25~35일"}
    },
    "US": {
        "name": "미국 (United States)",
        "kpacket": {"base": 12.0, "per_500g": 3.5, "max_kg": 2.0, "days": "5~10일"},
        "ems":     {"base": 24.0, "per_500g": 5.0, "max_kg": 30.0, "days": "3~6일"},
        "express": {"base": 26.0, "per_500g": 5.5, "max_kg": 70.0, "days": "2~4일"},
        "ocean":   {"min_cbm": 0.5, "per_cbm": 150.0, "per_kg_min": 1.8, "days": "5~10일 (육로/화물)"}
    }
}

class ShippingRequest(BaseModel):
    origin_country: str = "KR"       # 출발국 (KR, JP, TW, US)
    unit_weight_g: float             # 제품 1개당 실제 무게 (g)
    length_cm: float                 # 박스 가로 (cm)
    width_cm: float                  # 박스 세로 (cm)
    height_cm: float                 # 박스 높이 (cm)
    quantity: int = 1                # 총 발송 수량 (개)
    method: str = "kpacket"          # 배송 방식: kpacket, ems, express, ocean