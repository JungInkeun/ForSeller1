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


// --- 3. 새로 추가된 관세 & 판매세 계산기 기능 ---
async function runTaxDuty() {
  const originCountry = document.getElementById("originCountry").value;
  const province = document.getElementById("canadaProvince").value;
  const category = document.getElementById("itemCategory").value;
  const priceCad = parseFloat(document.getElementById("cadPriceInput").value);
  const quantity = parseInt(document.getElementById("quantityInput").value, 10) || 1;
  const useFta = document.getElementById("useFtaCheck").checked;
  const isGstReg = document.getElementById("gstRegCheck").checked;
  const taxDutyResultArea = document.getElementById("taxDutyResultArea");

  if (isNaN(priceCad) || priceCad <= 0) {
    taxDutyResultArea.innerText = "올바른 CAD 단가를 입력해 주세요.";
    return;
  }

  taxDutyResultArea.innerText = "관세 및 세금 계산 중...";

  try {
    const response = await fetch("http://localhost:8000/tax-duty", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        price_cad: priceCad,
        quantity: quantity,
        origin_country: originCountry,
        province: province,
        category: category,
        use_fta: useFta,
        is_gst_registered: isGstReg
      })
    });

    if (!response.ok) {
      throw new Error("서버 응답 오류");
    }

    const data = await response.json();
    const noticeHtml = data.notice
      ? `<div style="color:#d93025; font-size:12px; font-weight:bold; margin-top:6px;">${data.notice}</div>`
      : "";

    taxDutyResultArea.innerHTML = `
      <div>• 물품 총액 (${data.quantity}개): <strong>$${data.total_goods_cad} CAD</strong></div>
      <div>• 관세 (${data.duty_rate_percent}%): <strong>$${data.duty_cad} CAD</strong> ${data.fta_applied ? "(FTA 면세)" : ""}</div>
      <div>• 판매세 (${data.province}): <strong>$${data.net_tax_cost_cad} CAD</strong></div>
      <div class="big-price">세후 총합계: $${data.total_subtotal_cad} CAD</div>
      <div style="font-size:12px; color:#5f6368;">(개당 세후 원가: $${data.unit_subtotal_cad} CAD)</div>
      ${noticeHtml}
    `;
  } catch (error) {
    taxDutyResultArea.innerText = "연결 실패: Python 서버(uvicorn)가 실행 중인지 확인하세요.";
  }
}

document.getElementById("taxDutyBtn").addEventListener("click", runTaxDuty);

document.getElementById("cadPriceInput").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    runTaxDuty();
  }
});

document.getElementById("quantityInput").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    runTaxDuty();
  }
});