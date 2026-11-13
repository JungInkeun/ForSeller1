# 라이브러리
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 클래스
from currencyRate import CurrencyRequest
import currencyRate
import taxDuty
import shipping

app = FastAPI()

# 크롬 확장 프로그램에서 내 로컬 Python 서버에 접근할 수 있도록 허용(CORS 설정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(currencyRate.router) # 환율계산 기능
app.include_router(taxDuty.router) #세금 계산 기능
app.include_router(shipping.router) #배송기 계산 기능