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
        <div class="big-price">결과: ${formatPrice(data.converted_price)} ${data.to_currency}</div>
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
