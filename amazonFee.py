# 변수 클래스
import amazonFeeClass

# 외부 라이브러리
import math
from fastapi import APIRouter

router = APIRouter()

def estimate_fba_fulfillment_fee(weight_g: float, l_cm: float, w_cm: float, h_cm: float) -> tuple[float, str]:
    """Amazon.ca 표준 크기 및 무게 구간별 FBA 풀필먼트 배송비 추정 (CAD)"""
    dims = sorted([l_cm, w_cm, h_cm], reverse=True)
    longest, median, shortest = dims[0], dims[1], dims[2]

    # 부피 무게 (kg) = (L * W * H) / 5000
    vol_weight_g = ((l_cm * w_cm * h_cm) / 5000.0) * 1000.0
    shipping_weight_g = max(weight_g, vol_weight_g)

    # 표준 크기(Standard Size) 판별: 최대변 45cm, 중간변 35cm, 최소변 20cm 이하 & 9kg 이하
    is_standard = (longest <= 45.0 and median <= 35.0 and shortest <= 20.0 and shipping_weight_g <= 9000.0)

    if is_standard:
        if shipping_weight_g <= 100:
            return 5.45, "표준 소형 (100g 이하)"
        elif shipping_weight_g <= 250:
            return 5.85, "표준 소형 (250g 이하)"
        elif shipping_weight_g <= 500:
            return 6.35, "표준 소형 (500g 이하)"
        elif shipping_weight_g <= 1000:
            return 7.45, "표준 중형 (1kg 이하)"
        elif shipping_weight_g <= 1500:
            return 8.35, "표준 중형 (1.5kg 이하)"
        elif shipping_weight_g <= 2000:
            return 9.10, "표준 중형 (2kg 이하)"
        else:
            extra_500g = math.ceil((shipping_weight_g - 2000) / 500.0)
            return round(9.10 + (extra_500g * 0.45), 2), f"표준 대형 ({round(shipping_weight_g/1000, 2)}kg)"
    else:
        # 특대형 (Oversize) 기본 $13.50 + 500g당 $0.55
        extra_500g = max(0, math.ceil((shipping_weight_g - 500) / 500.0))
        return round(13.50 + (extra_500g * 0.55), 2), f"특대형 Oversize ({round(shipping_weight_g/1000, 2)}kg)"
    

@router.post("/amazon-fee")
def calculate_amazon_price(data: amazonFeeClass.AmazonFeeRequest):
    print("====================================")
    print("아마존 최종 판매가 역산 요청:", data)

    if data.target_margin_rate >= 0.80:
        raise ValueError("목표 마진율은 80% 미만으로 설정해 주세요.")

    cat_info = amazonFeeClass.AMAZON_CA_REFERRAL_FEES.get(data.category.lower(), amazonFeeClass.AMAZON_CA_REFERRAL_FEES["general"])
    per_item_plan_fee = 1.49 if data.is_individual_plan else 0.0

    # 1. FBA 풀필먼트 배송비 & 창고 보관료 계산
    if data.fulfillment_type.upper() == "FBA":
        fulfillment_fee, size_tier = estimate_fba_fulfillment_fee(
            data.unit_weight_g, data.length_cm, data.width_cm, data.height_cm
        )
        # cm³ -> cubic feet 변환 (1 ft³ = 28,316.85 cm³)
        cubic_feet = (data.length_cm * data.width_cm * data.height_cm) / 28316.85
        monthly_rate = amazonFeeClass.STORAGE_RATE_PEAK if data.is_peak_season else amazonFeeClass.STORAGE_RATE_OFF_PEAK
        storage_fee = round(cubic_feet * monthly_rate * data.storage_months, 2)
        # 최소 보관료 보정 ($0.01)
        storage_fee = max(0.01, storage_fee)
    else:
        fulfillment_fee = round(data.fbm_local_shipping_cad, 2)
        size_tier = "FBM (셀러 직접 배송)"
        storage_fee = 0.0

    # 2. 고정 원가 합계 (수입원가 + FBA/로컬배송비 + 보관료 + 개인플랜수수료)
    fixed_cost_total = data.unit_landed_cost_cad + fulfillment_fee + storage_fee + per_item_plan_fee

    # 3. 목표 마진율 달성을 위한 권장 판매가 역산
    referral_rate = cat_info["rate"]
    denominator = 1.0 - referral_rate - data.target_margin_rate
    if denominator <= 0:
        raise ValueError("아마존 수수료율과 목표 마진율의 합이 100%를 초과합니다.")

    recommended_price = fixed_cost_total / denominator

    # 저가 상품 할인 수수료율 구간(예: 뷰티 $10 이하 8%) 해당 시 재계산
    if cat_info["threshold"] > 0 and recommended_price <= cat_info["threshold"]:
        referral_rate = cat_info["low_price_rate"]
        recommended_price = fixed_cost_total / (1.0 - referral_rate - data.target_margin_rate)

    recommended_price = round(recommended_price, 2)
    referral_fee_cad = round(recommended_price * referral_rate, 2)
    total_amazon_fees = round(referral_fee_cad + fulfillment_fee + storage_fee + per_item_plan_fee, 2)
    net_profit_cad = round(recommended_price - data.unit_landed_cost_cad - total_amazon_fees, 2)
    actual_margin_percent = round((net_profit_cad / recommended_price) * 100, 1)

    # 손익분기점 (마진 0%일 때 최소 판매가)
    breakeven_price = round(fixed_cost_total / (1.0 - referral_rate), 2)

    print(f"권장 판매가: ${recommended_price} CAD | 순수익: ${net_profit_cad} CAD ({actual_margin_percent}%)")
    print("====================================")

    return {
        "category": cat_info["name"], #선택한 Amazon.ca 판매 카테고리입니다.
        "fulfillment_type": data.fulfillment_type.upper(), #아마존 창고에 물건을 입고해 아마존이 대신 포장·배송해 주는 FBA 방식을 선택했음을 의미합니다.
        "size_tier": size_tier, #입력한 무게(200g)와 박스 크기를 바탕으로 아마존이 분류한 물류 규격 등급입니다. 이 등급에 따라 FBA 배송비가 결정됩니다.
        "unit_landed_cost_cad": round(data.unit_landed_cost_cad, 2), #• 이전 단계에서 구한 **제품 1개당 최종 수입원가($20.00 CAD)**입니다. (물품 원가 + 관세 + 판매세 + 국제 배송비가 모두 포함된 금액)
        "referral_rate_percent": round(referral_rate * 100, 1), #뷰티/화장품 카테고리(판매가 $10 초과 시)에 적용되는 아마존 기본 **추천 수수료율 15%**입니다.
        "referral_fee_cad": referral_fee_cad, #권장 판매가($47.04)의 15%에 해당하는 아마존 판매 수수료 $7.06 CAD입니다.
        "fulfillment_fee_cad": fulfillment_fee, #아마존 FBA 창고에서 캐나다 구매자 집까지 택배로 보내주는 데 드는 FBA 풀필먼트 배송비 $5.85 CAD입니다. (표준 소형 250g 이하 요율)
        "storage_fee_cad": storage_fee, #아마존 창고에 제품을 보관하는 월 창고 이용료 $0.02 CAD입니다. 화장품처럼 부피가 작은 제품은 보관료 부담이 매우 적습니다.
        "plan_fee_cad": per_item_plan_fee, #프로페셔널 셀러 플랜(월 정액제) 기준이므로 건당 추가 수수료는 $0입니다. (개인 셀러 플랜 선택 시 $1.49 표시)
        "total_amazon_fees_cad": total_amazon_fees, #• 아마존에 지불하는 모든 수수료의 총합($7.06 + $5.85 + $0.02)인 $12.93 CAD입니다.
        "breakeven_price_cad": breakeven_price, #마진을 0원으로 잡았을 때 적자를 면하는 최소 손익분기 판매가 $30.44 CAD입니다. 최소한 이 가격보다는 비싸게 팔아야 손해를 보지 않습니다.
        "recommended_price_cad": recommended_price, #수입원가($20)와 아마존 총수수료($12.93)를 모두 제하고도 목표한 순마진율(30%)을 남기기 위한 Amazon.ca 최종 권장 판매가 $47.04 CAD입니다.
        "net_profit_cad": net_profit_cad, #$47.04에 판매했을 때 셀러 통장에 실제로 남는 제품 1개당 순수익 $14.11 CAD입니다. ($47.04 - $20.00 - $12.93 = $14.11)
        "target_margin_percent": actual_margin_percent #• 판매가 대비 실제 순수익 비율($14.11 ÷ $47.04)이 목표했던 **30.0%**로 정확히 달성되었음을 보여줍니다.
    }