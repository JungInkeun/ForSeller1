from pydantic import BaseModel

#1. Amazon.ca 카테고리별 추천 수수료율 (Referral Fee)
AMAZON_CA_REFERRAL_FEES = {
    "cosmetics": {"name": "뷰티/화장품 (Beauty)", "rate": 0.15, "low_price_rate": 0.08, "threshold": 10.0},
    "food":      {"name": "식품/간식 (Grocery)", "rate": 0.15, "low_price_rate": 0.08, "threshold": 15.0},
    "computer":  {"name": "컴퓨터/전자 (Computers)", "rate": 0.08, "low_price_rate": 0.08, "threshold": 0.0},
    "apparel":   {"name": "의류/잡화 (Apparel)", "rate": 0.17, "low_price_rate": 0.17, "threshold": 0.0},
    "tools":     {"name": "공구/홈개선 (Tools)", "rate": 0.15, "low_price_rate": 0.15, "threshold": 0.0},
    "general":   {"name": "기타 일반 (General)", "rate": 0.15, "low_price_rate": 0.15, "threshold": 0.0},
}

# 2. Amazon.ca FBA 월 창고 보관료 (CAD per cubic foot / month)
STORAGE_RATE_OFF_PEAK = 0.87   # 1월 ~ 9월 (비수기)
STORAGE_RATE_PEAK = 2.40       # 10월 ~ 12월 (연말 성수기)

class AmazonFeeRequest(BaseModel):
    unit_landed_cost_cad: float      # 개당 최종 수입원가 (관세+세금+국제배송비 포함)
    category: str = "cosmetics"      # 품목 코드
    unit_weight_g: float = 200       # 제품 1개 무게 (g)
    length_cm: float = 15            # 제품 1개 포장 가로 (cm)
    width_cm: float = 10             # 제품 1개 포장 세로 (cm)
    height_cm: float = 5             # 제품 1개 포장 높이 (cm)
    fulfillment_type: str = "FBA"    # "FBA" (아마존 창고) 또는 "FBM" (직접 배송)
    fbm_local_shipping_cad: float = 0.0  # FBM 선택 시 캐나다 내 로컬 배송비 (CAD)
    storage_months: float = 1.0      # 평균 창고 보관 개월 수 (기본 1개월)
    is_peak_season: bool = False     # 10~12월 성수기 보관료 적용 여부
    is_individual_plan: bool = False # 개인 셀러 플랜(건당 $1.49 CAD 추가) 여부
    target_margin_rate: float = 0.30 # 목표 순마진율 (예: 0.30 -> 30%)