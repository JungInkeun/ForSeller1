from pydantic import BaseModel


# 1. 캐나다 주/준주별 판매세 테이블 (2026년 기준)
CN_PROVINCE_TAX_RATES = {
    "BC": {"gst_hst": 0.05, "pst": 0.07},     # 총 12%
    "AB": {"gst_hst": 0.05, "pst": 0.00},     # 총 5%
    "SK": {"gst_hst": 0.05, "pst": 0.06},     # 총 11%
    "MB": {"gst_hst": 0.05, "pst": 0.07},     # 총 12%
    "ON": {"gst_hst": 0.13, "pst": 0.00},     # 총 13% HST
    "QC": {"gst_hst": 0.05, "pst": 0.09975},  # 총 14.975% (GST + QST)
    "NB": {"gst_hst": 0.15, "pst": 0.00},     # 총 15% HST
    "NS": {"gst_hst": 0.14, "pst": 0.00},     # 총 14% HST
    "PE": {"gst_hst": 0.15, "pst": 0.00},     # 총 15% HST
    "NL": {"gst_hst": 0.15, "pst": 0.00},     # 총 15% HST
    "YT": {"gst_hst": 0.05, "pst": 0.00},     # 총 5%
    "NT": {"gst_hst": 0.05, "pst": 0.00},     # 총 5%
    "NU": {"gst_hst": 0.05, "pst": 0.00},     # 총 5%
}

# 2. 품목별 캐나다 일반 관세율(MFN) 및 FTA 면세 가능 여부
CN_KR_CATEGORY_DUTY_RATES = {
    "cosmetics": {"name": "화장품 (Cosmetics)", "mfn_rate": 0.065, "fta_exempt": True},
    "food":      {"name": "가공식품/간식 (Food)", "mfn_rate": 0.085, "fta_exempt": True},
    "computer":  {"name": "컴퓨터/전자부품 (Computer)", "mfn_rate": 0.00, "fta_exempt": True},
    "apparel":   {"name": "의류/잡화 (Apparel)", "mfn_rate": 0.18, "fta_exempt": True},
    "tools":     {"name": "수공구/장비 (Tools)", "mfn_rate": 0.065, "fta_exempt": True},
    "general":   {"name": "기타 일반품목 (General)", "mfn_rate": 0.065, "fta_exempt": False},
}

# 3. 캐나다와 양자/북미 FTA 면세 적용 국가 (한국: CKFTA, 미국: CUSMA)
FTA_ELIGIBLE_ORIGINS = {"KR", "US"}

class TaxDutyRequest(BaseModel):
    price_cad: float                 # 단품 원가 (CAD)
    quantity: int = 1                # 수입 수량 (개)
    origin_country: str = "KR"       # 출발국 (KR, JP, TW, US)
    province: str = "ON"             # 도착 주 (MB, ON, AB 등)
    category: str = "cosmetics"      # 품목 (cosmetics, food, computer 등)
    use_fta: bool = True             # FTA 원산지 증명 적용 여부
    is_gst_registered: bool = False  # 사업자 GST/HST 환급 여부