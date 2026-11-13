# 클래스
import provicesTax

#외부라이브러리
from fastapi import APIRouter

router = APIRouter()

@router.post("/tax-duty")
def calculate_tax_and_duty(data: provicesTax.TaxDutyRequest):
    print("====================================")
    print("세금+관세 계산 요청:", data)

    # 1. 주 코드 검증 및 세율 조회
    prov_code = data.province.upper()
    if prov_code not in provicesTax.CN_PROVINCE_TAX_RATES:
        raise ValueError(f"지원하지 않는 주 코드입니다: {prov_code}")
    tax_info = provicesTax.CN_PROVINCE_TAX_RATES[prov_code]

    # 2. 출발국 및 품목별 관세율 판별
    origin_code = data.origin_country.upper()
    cat_code = data.category.lower()
    cat_info = provicesTax.CN_KR_CATEGORY_DUTY_RATES.get(cat_code, provicesTax.CN_KR_CATEGORY_DUTY_RATES["general"])

    # 출발국이 KR 또는 US이고, 원산지 증명(use_fta=True)을 사용할 때만 관세 면제
    is_fta_applied = (origin_code in provicesTax.FTA_ELIGIBLE_ORIGINS) and data.use_fta and cat_info["fta_exempt"]
    applied_duty_rate = 0.0 if is_fta_applied else cat_info["mfn_rate"]
    duty_amount = round(data.price_cad * applied_duty_rate, 2)

    # 3. 판매세(Tax) 계산: (제품원가 + 관세) 합계에 주별 세율 부과
    taxable_value = data.price_cad + duty_amount
    gst_hst_amount = round(taxable_value * tax_info["gst_hst"], 2)
    pst_amount = round(taxable_value * tax_info["pst"], 2)
    total_tax_paid = round(gst_hst_amount + pst_amount, 2)

    # 사업자 등록 셀러는 GST/HST를 환급받으므로 실제 매몰 세금은 PST만 남음
    net_tax_cost = pst_amount if data.is_gst_registered else total_tax_paid

    total_duty_and_tax = round(duty_amount + net_tax_cost, 2)
    subtotal_cad = round(data.price_cad + total_duty_and_tax, 2)

    print(f"출발국: {origin_code} | FTA 적용됨: {is_fta_applied} | 관세({applied_duty_rate*100}%): ${duty_amount} CAD")
    print(f"통관 시 납부 세금: ${total_tax_paid} CAD (실제 원가 반영 세금: ${net_tax_cost} CAD)")
    print(f"제품가+관세+세금 소계: ${subtotal_cad} CAD")
    print("====================================")

    return {
        "origin_country": origin_code, # 출발국(소싱 국가)의 2자리 코드
        "province": prov_code,
        "category": cat_info["name"],
        "fta_applied": is_fta_applied,
        "price_cad": data.price_cad, #환율이 적용된 순수 제품 원가(캐나다 달러 기준)입니다.
        "duty_rate_percent": round(applied_duty_rate * 100, 2), # 최종 적용된 관세율(%)입니다. fta_applied가 true이면 0.0이 되고, 면제 대상이 아니면 품목별 일반 관세율(예: 6.5)이 표시됩니다.
        "duty_cad": duty_amount, #제품 원가에 관세율을 곱해 계산된 **실제 관세 금액(CAD)**입니다.
        "gst_hst_cad": gst_hst_amount, #통관 시 내는 연방 판매세(GST 5%) 또는 통합 판매세(온타리오 13% HST 등) 금액
        "pst_cad": pst_amount, #• 매니토바(7%), BC(7%), 퀘벡(9.975%)처럼 주 정부 자체 판매세가 있는 지역에서 부과되는 주세 금액입니다.
        "total_tax_paid_cad": total_tax_paid, #• 세관을 통과할 때 당장 납부해야 하는 **총 판매세 합계(gst_hst_cad + pst_cad)**입니다.
        "net_tax_cost_cad": net_tax_cost, #셀러의 실제 매몰 원가로 잡히는 순수 세금 비용입니다
        "total_duty_and_tax_cad": total_duty_and_tax, #셀러가 최종적으로 부담하는 **관세 + 순수 세금 합계(duty_cad + net_tax_cost_cad)**입니다.
        "subtotal_after_tax_cad": subtotal_cad #순수 제품 가격에 관세와 세금을 모두 더한 **1차 중간 합계(price_cad + total_duty_and_tax_cad)**입니다. 다음 단계에서 구할 국제 배송비와 아마존 수수료가 이 금액 위에 더해집니다.
    }