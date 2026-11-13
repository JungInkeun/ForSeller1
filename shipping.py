import math
from fastapi import APIRouter

# 라이브러리
import shippingClass

router = APIRouter()

@router.post("/shipping")
def calculate_shipping_cost(data: shippingClass.ShippingRequest):
    print("====================================")
    print("국제 배송비 계산 요청:", data)

    origin = data.origin_country.upper()
    if origin not in shippingClass.ORIGIN_SHIPPING_RATES:
        raise ValueError(f"지원하지 않는 출발국입니다: {origin}")

    method = data.method.lower()
    rates = shippingClass.ORIGIN_SHIPPING_RATES[origin]
    if method not in ["kpacket", "ems", "express", "ocean"]:
        raise ValueError(f"지원하지 않는 배송 방식입니다: {method}")

    # 1. 실제 총무게 (kg) 계산 (박스 포장재 무게 5% 여유분 가산)
    raw_actual_kg = (data.unit_weight_g * data.quantity) / 1000.0
    actual_total_kg = round(raw_actual_kg * 1.05, 3)

    # 2. 박스 총 부피(cm³) 및 운송수단별 부피 무게(kg) 계산
    # 참고: 입력받은 가로*세로*높이는 '전체 포장 박스 크기' 또는 '개당 규격' 기준
    total_volume_cm3 = data.length_cm * data.width_cm * data.height_cm

    if method == "express":
        volumetric_kg = round(total_volume_cm3 / 5000.0, 3)  # 항공 특송 기준 (÷ 5000)
    else:
        volumetric_kg = round(total_volume_cm3 / 6000.0, 3)  # 우체국/일반 항공 기준 (÷ 6000)

    # 3. 청구 중량(Chargeable Weight) 결정: 실제 무게 vs 부피 무게 중 큰 값 선택
    if method == "kpacket":
        # 소형포장물은 세변 합 90cm 이하일 때 실제 무게만 적용
        chargeable_kg = actual_total_kg
        weight_basis = "실제 무게 (소형포장 기준)"
    else:
        if volumetric_kg > actual_total_kg:
            chargeable_kg = volumetric_kg
            weight_basis = "부피 무게 적용 (박스가 큼)"
        else:
            chargeable_kg = actual_total_kg
            weight_basis = "실제 무게 적용"

    # 4. 배송 방식별 요금 계산 (0.5kg 단위 올림 처리)
    rule = rates[method]
    warning_msg = ""

    if method == "ocean":
        # 해상 운송: CBM(가로m * 세로m * 높이m) 요금 vs 최소 kg 단가 요금 비교
        cbm = max(total_volume_cm3 / 1_000_000.0, rule["min_cbm"])
        cbm_cost = cbm * rule["per_cbm"]
        weight_cost = chargeable_kg * rule["per_kg_min"]
        total_shipping_cad = round(max(cbm_cost, weight_cost), 2)
    else:
        # 항공 (K-Packet, EMS, Express): 0.5kg 단위 올림
        billed_kg = math.ceil(chargeable_kg * 2) / 2.0
        if billed_kg > rule["max_kg"]:
            warning_msg = f"⚠️ 선택한 방식({method.upper()})의 최대 한도({rule['max_kg']}kg)를 초과했습니다. 상위 배송 방식을 선택하세요."

        # 기본 0.5kg 요금 + 초과 0.5kg당 추가 요금
        extra_steps = max(0, (billed_kg - 0.5) / 0.5)
        base_freight = rule["base"] + (extra_steps * rule["per_500g"])

        if method == "express":
            # 특송은 유류할증료(25%) + 통관 대행 수수료($15 CAD) 추가
            fuel_fee = base_freight * shippingClass.EXPRESS_FUEL_SURCHARGE
            total_shipping_cad = round(base_freight + fuel_fee + shippingClass.EXPRESS_BROKERAGE_FEE, 2)
        else:
            total_shipping_cad = round(base_freight, 2)

    unit_shipping_cad = round(total_shipping_cad / data.quantity, 2)

    print(f"실제무게: {actual_total_kg}kg | 부피무게: {volumetric_kg}kg -> 청구기준: {weight_basis}")
    print(f"총 배송비: ${total_shipping_cad} CAD | 개당 배송비: ${unit_shipping_cad} CAD")
    print("====================================")

    return {
        "origin_country": origin,
        "method": method.upper(), #선택한 국제 운송 방식의 대문자 표기입니다. ("KPACKET", "EMS", "EXPRESS", "OCEAN" 중 하나)
        "estimated_days": rule["days"], #해당 운송 방식을 이용했을 때 캐나다까지 걸리는 예상 배송 기간입니다. ("4~7일", "7~14일" 등)
        "quantity": data.quantity, #한 번에 함께 포장해 발송하는 총 제품 수량(개)입니다.
        "actual_total_kg": actual_total_kg, #• 제품 순수 총무게에 포장 박스 및 완충재 무게(5% 여유분)를 더한 실제 저울 무게(kg)입니다.
        "volumetric_kg": volumetric_kg, #• 입력한 박스 크기(가로 × 세로 × 높이 cm)로 계산한 부피 무게(kg)입니다. 항공 특송(EXPRESS)은 부피를 5,000으로 나누고, 일반 항공(EMS)은 6,000으로 나누어 계산합니다.
        "chargeable_kg": chargeable_kg, #• 택배사가 실제 요금을 매기는 기준이 되는 최종 청구 중량(kg)입니다. 실제 무게(actual_total_kg)와 부피 무게(volumetric_kg) 중 더 무거운 쪽이 자동으로 선택됩니다.
        "weight_basis": weight_basis, #• 요금 계산에 어떤 무게 기준이 적용되었는지 알려주는 설명입니다. ("실제 무게 적용" 또는 "부피 무게 적용 (박스가 큼)")
        "total_shipping_cad": total_shipping_cad, #• 전체 수량을 캐나다까지 보내는 데 드는 총 국제 배송비(CAD)입니다. (EXPRESS 선택 시 유류할증료 25%와 통관 대행 수수료 $15 CAD가 모두 포함된 금액입니다.)
        "unit_shipping_cad": unit_shipping_cad, # 총 배송비를 수량(quantity)으로 나눈 제품 1개당 국제 배송비(CAD)입니다. 여러 개를 한 박스에 묶어 보낼수록 이 금액이 크게 줄어듭니다.
        "warning": warning_msg #• 무게 한도 초과 시 띄워주는 경고 문구입니다. 평소에는 빈 글자("")로 나오다가, 예를 들어 KPACKET(최대 2kg)을 선택했는데 무게가 2kg을 넘어가면 *"최대 한도를 초과했습니다. 상위 배송 방식을 선택하세요"*라는 안내가 표시됩니다.
    }