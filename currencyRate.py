from pydantic import BaseModel
from fastapi import APIRouter
import requests

# 라우터 생성 (server.py에서 한 줄로 불러오기 위한 객체)
router = APIRouter()

# 입력받을 데이터 형식 정의
class CalcRequest(BaseModel):
    number: float

class CurrencyRequest(BaseModel): #환율
    price: float
    from_currency: str  # 예: KRW, JPY, EUR, USD, CAD
    to_currency: str    # 예: CAD, USD


@router.post("/calculate")
def calculate_ten_percent(data: CalcRequest):
    # 입력받은 숫자에 10%를 더함
    result = round(data.number * 1.10, 2)
    return {"input": data.number, "result": result}


@router.post("/convert")
def convert_currency(data: CurrencyRequest):
    print("====================================")
    print("받은 데이터:", data)

    # 같은 통화끼리는 환율 1.0 적용
    if data.from_currency == data.to_currency:
        rate = 1.0
    else:
        url = f"https://open.er-api.com/v6/latest/{data.from_currency}"
        res = requests.get(url, timeout=5).json()
        rate = res["rates"][data.to_currency]

    converted = round(data.price * rate, 2)

    print(f"환율: 1 {data.from_currency} = {rate} {data.to_currency}")
    print(f"변환 결과: {converted} {data.to_currency}")
    print("====================================")

    return {
        "from_currency": data.from_currency,
        "to_currency": data.to_currency,
        "rate": rate,
        "converted_price": converted
    }