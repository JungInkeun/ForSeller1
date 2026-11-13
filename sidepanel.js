document.getElementById("calcBtn").addEventListener("click", async () => {
    const inputVal = parseFloat(document.getElementById("numInput").value);
    const resultArea = document.getElementById("resultArea");
  
    if (isNaN(inputVal)) {
      resultArea.innerText = "올바른 숫자를 입력해 주세요.";
      return;
    }
  
    resultArea.innerText = "Python 서버에서 계산 중...";
  
    try {
      // 1단계에서 실행한 Python FastAPI 서버로 데이터 전송
      const response = await fetch("http://127.0.0.1:8000/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ number: inputVal })
      });
  
      const data = await response.json();
      resultArea.innerText = `결과: ${data.result} (10% 추가됨)`;
    } catch (error) {
      resultArea.innerText = "연결 실패: Python 서버(uvicorn)가 실행 중인지 확인하세요.";
    }
  });
  

// --- 2. 새로운 실시간 환율 계산기 기능 ---
async function runConvert() {
    const fromCurr = document.getElementById("fromCurrency").value;
    const toCurr = document.getElementById("toCurrency").value;
    const amountVal = parseFloat(document.getElementById("amountInput").value);
    const convertResultArea = document.getElementById("convertResultArea");
  
    if (isNaN(amountVal) || amountVal <= 0) {
      convertResultArea.innerText = "올바른 금액을 입력해 주세요.";
      return;
    }
  
    convertResultArea.innerText = "실시간 환율 계산 중...";
  
    try {
      const response = await fetch("http://127.0.0.1:8000/convert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          price: amountVal,
          from_currency: fromCurr,
          to_currency: toCurr
        })
      });
  
      if (!response.ok) {
        throw new Error("서버 응답 오류");
      }
  
      const data = await response.json();
      convertResultArea.innerHTML = `
        <div>적용 환율: 1 ${data.from_currency} = ${data.rate} ${data.to_currency}</div>
        <div class="big-price">결과: ${data.converted_price} ${data.to_currency}</div>
      `;
    } catch (error) {
      convertResultArea.innerText = "연결 실패: Python 서버(uvicorn)가 실행 중인지 확인하세요.";
    }
  }
  
  document.getElementById("convertBtn").addEventListener("click", runConvert);
  
  document.getElementById("amountInput").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      runConvert();
    }
  });