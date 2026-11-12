from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# 크롬 확장 프로그램에서 내 로컬 Python 서버에 접근할 수 있도록 허용(CORS 설정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 입력받을 데이터 형식 정의
class CalcRequest(BaseModel):
    number: float

@app.post("/calculate")
def calculate_ten_percent(data: CalcRequest):
    # 입력받은 숫자에 10%를 더함
    result = round(data.number * 1.10, 2)
    return {"input": data.number, "result": result}
