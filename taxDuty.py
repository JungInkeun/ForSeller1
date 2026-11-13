# 클래스
import provicesTax

#외부라이브러리
from fastapi import APIRouter

router = APIRouter()

@router.post("/tax-duty")
def calculate_tax_and_duty(data: provicesTax.TaxDutyRequest):
    print("====================================")
    print("세금+관세 계산 요청:", data)

    prov_code = data.province.upper()
    if prov_code not in provicesTax.CN_PROVINCE_TAX_RATES:
        raise ValueError(f"지원하지 않는 주 코드입니다: {prov_code}")
    tax_info = provicesTax.CN_PROVINCE_TAX_RATES[prov_code]

    origin_code = data.origin_country.upper()
    cat_code = data.category.lower()
    cat_info = provicesTax.CN_KR_CATEGORY_DUTY_RATES.get(cat_code, provicesTax.CN_KR_CATEGORY_DUTY_RATES["general"])

    # 전체 물품 신고 가액 (단가 * 수량)
    total_goods_cad = round(data.price_cad * data.quantity, 2)

    # 관세 계산
    is_fta_applied = (origin_code in provicesTax.FTA_ELIGIBLE_ORIGINS) and data.use_fta and cat_info["fta_exempt"]
    applied_duty_rate = 0.0 if is_fta_applied else cat_info["mfn_rate"]
    total_duty_cad = round(total_goods_cad * applied_duty_rate, 2)

    # 세금 계산 (물품총액 + 관세 기준)
    taxable_value = total_goods_cad + total_duty_cad
    gst_hst_cad = round(taxable_value * tax_info["gst_hst"], 2)
    pst_cad = round(taxable_value * tax_info["pst"], 2)
    total_tax_paid = round(gst_hst_cad + pst_cad, 2)

    # 실제 원가 반영 세금 (사업자 GST/HST 등록 시 PST만 원가 반영)
    net_tax_cost = pst_cad if data.is_gst_registered else total_tax_paid

    total_duty_and_tax = round(total_duty_cad + net_tax_cost, 2)
    total_subtotal_cad = round(total_goods_cad + total_duty_and_tax, 2)
    unit_subtotal_cad = round(total_subtotal_cad / data.quantity, 2)

    # $3,300 CAD 초과 정식 통관 안내 메시지
    notice = ""
    if is_fta_applied and total_goods_cad > 3300:
        notice = "⚠️ 총 수입액이 $3,300 CAD를 초과하여 정식 FTA 원산지 증명서 제출이 필수입니다."
    
    print(f"출발국: {origin_code} | FTA 적용됨: {is_fta_applied} | 관세({applied_duty_rate*100}%): ${total_duty_and_tax} CAD")
    print(f"통관 시 납부 세금: ${total_tax_paid} CAD (실제 원가 반영 세금: ${net_tax_cost} CAD)")
    print(f"제품가+관세+세금 소계: ${total_subtotal_cad} CAD")
    print("====================================")

    return {
        "origin_country": origin_code, #•  물건이 출발하는 소싱 국가 코드입니다. ("KR", "JP", "TW", "US" 등)
        "province": prov_code,
        "category": cat_info["name"],
        "fta_applied": is_fta_applied,
        "quantity": data.quantity, #한 번에 수입하는 전체 제품 수량(개수)입니다.
        "total_goods_cad": total_goods_cad, #• 세금과 관세가 붙기 전의 순수 물품 총액(개당 단가 × 수량)입니다. 세관 신고 기준 금액이 됩니다. 
        "duty_rate_percent": round(applied_duty_rate * 100, 2), #최종 적용된 관세율(%)입니다. fta_applied가 true이면 0.0이고, 면제 대상이 아니면 품목별 일반 관세율(예: 6.5)이 나옵니다.
        "duty_cad": total_duty_cad, #전체 물품 총액(total_goods_cad)에 관세율을 곱해 산출된 총 관세 금액(CAD)입니다.
        "net_tax_cost_cad": net_tax_cost, #셀러가 최종적으로 부담하는 순수 판매세 비용(CAD)입니다. 사업자 GST 환급 체크를 끄면 전체 세금(GST+PST/HST)이 들어가고, 환급 체크를 켜면 돌려받지 못하는 주세(PST)만 계산됩니다.
        "total_duty_and_tax_cad": total_duty_and_tax, #전체 수량에 대해 셀러가 부담하는 총 관세 + 순수 판매세 합계(duty_cad + net_tax_cost_cad)입니다.
        "total_subtotal_cad": total_subtotal_cad, #전체 물품 총액에 관세와 세금을 모두 더한 전체 수입 중간 합계 (total_goods_cad + total_duty_and_tax_cad)입니다.
        "unit_subtotal_cad": unit_subtotal_cad, # 위 전체 중간 합계를 수량(quantity)으로 나눈 제품 1개당 세후 원가(CAD)입니다.
        "notice": notice #통관 시 주의해야 할 안내 메시지입니다. 평소에는 빈 글자("")로 나오다가, 총 수입액(total_goods_cad)이 $3,300 CAD를 초과할 때만 *"정식 FTA 원산지 증명서 제출이 필수입니다"*라는 경고 문구가 담겨 나옵니다.
    }
