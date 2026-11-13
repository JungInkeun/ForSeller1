
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


// --- 3. 관세 + 판매세 + 국제 배송비 통합 계산기 기능 ---
async function runTotalImportCalc() {
  const originCountry = document.getElementById("originCountry").value;
  const province = document.getElementById("canadaProvince").value;
  const category = document.getElementById("itemCategory").value;
  const method = document.getElementById("shippingMethod").value;

  const priceCad = parseFloat(document.getElementById("cadPriceInput").value);
  const quantity = parseInt(document.getElementById("quantityInput").value, 10) || 1;
  const weightG = parseFloat(document.getElementById("weightInput").value) || 200;
  const lengthCm = parseFloat(document.getElementById("lengthInput").value) || 10;
  const widthCm = parseFloat(document.getElementById("widthInput").value) || 10;
  const heightCm = parseFloat(document.getElementById("heightInput").value) || 10;

  const useFta = document.getElementById("useFtaCheck").checked;
  const isGstReg = document.getElementById("gstRegCheck").checked;
  const resultArea = document.getElementById("taxDutyResultArea");

  if (isNaN(priceCad) || priceCad <= 0) {
    resultArea.innerText = "올바른 CAD 단가를 입력해 주세요.";
    return;
  }

  resultArea.innerText = "관세, 세금 및 국제 배송비 계산 중...";

  try {
    // 1) 관세+세금 API와 2) 배송비 API를 동시에 호출
    const [taxRes, shipRes] = await Promise.all([
      fetch("http://localhost:8000/tax-duty", {
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
      }),
      fetch("http://localhost:8000/shipping", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          origin_country: originCountry,
          unit_weight_g: weightG,
          length_cm: lengthCm,
          width_cm: widthCm,
          height_cm: heightCm,
          quantity: quantity,
          method: method
        })
      })
    ]);

    if (!taxRes.ok || !shipRes.ok) {
      throw new Error("서버 응답 오류");
    }

    const taxData = await taxRes.json();
    const shipData = await shipRes.json();

    // 총 수입 원가 (Landed Cost) = 세후 물품총액 + 총 국제 배송비
    const totalLandedCost = (taxData.total_subtotal_cad + shipData.total_shipping_cad).toFixed(2);
    const unitLandedCost = (totalLandedCost / quantity).toFixed(2);

    const noticeHtml = (taxData.notice || shipData.warning)
      ? `<div style="color:#d93025; font-size:12px; font-weight:bold; margin-top:6px;">
          ${taxData.notice} ${shipData.warning}
         </div>`
      : "";

    resultArea.innerHTML = `
      <div>• 물품 총액 (${quantity}개): <strong>$${taxData.total_goods_cad} CAD</strong></div>
      <div>• 관세 (${taxData.duty_rate_percent}%): <strong>$${taxData.duty_cad} CAD</strong> | 세금(${taxData.province}): <strong>$${taxData.net_tax_cost_cad} CAD</strong></div>
      <div>• 국제 배송비 (${shipData.method}, ${shipData.estimated_days}): <strong>$${shipData.total_shipping_cad} CAD</strong></div>
            <div style="font-size:12px; color:#5f6368;">  └ 청구중량: ${shipData.chargeable_kg}kg (${shipData.weight_basis})</div>
      ${quantity > 1 ? `<div style="font-size:12px; color:#5f6368;">  └ ${quantity}개 합산 배송비 $${shipData.total_shipping_cad} CAD → 1개당 $${shipData.unit_shipping_cad} CAD</div>` : ""}
      <div class="big-price" style="margin-top:8px;">최종 수입원가: $${totalLandedCost} CAD</div>
      <div style="font-size:13px; font-weight:bold; color:#174ea6;">(개당 최종원가: $${unitLandedCost} CAD)</div>
      ${noticeHtml}
    `;
  } catch (error) {
    resultArea.innerText = "연결 실패: Python 서버(uvicorn)가 실행 중인지 확인하세요.";
  }
}

document.getElementById("taxDutyBtn").addEventListener("click", runTotalImportCalc);

// 입력칸에서 Enter 키 눌러도 즉시 계산
["cadPriceInput", "quantityInput", "weightInput", "lengthInput", "widthInput", "heightInput"].forEach((id) => {
  const el = document.getElementById(id);
  if (el) {
    el.addEventListener("keydown", (event) => {
      if (event.key === "Enter") runTotalImportCalc();
    });
  }
});
