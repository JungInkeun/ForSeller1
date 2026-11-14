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

    const canUse = await checkFreeOrPaidUsage(); //10회 무료
    if (!canUse) return; // 10회 무료   
  
    if (isNaN(priceCad) || priceCad <= 0) {
      resultArea.innerText = "올바른 CAD 단가를 입력해 주세요.";
      return;
    }
  
    resultArea.innerText = "관세, 세금 및 국제 배송비 계산 중...";
  
    try {
      // 1) 관세+세금 API와 2) 배송비 API를 동시에 호출
      const [taxRes, shipRes] = await Promise.all([
        // fetch("http://localhost:8000/tax-duty", {
          fetch(`${API_BASE_URL}/tax-duty`, {
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
        // fetch("http://localhost:8000/shipping", {
          fetch(`${API_BASE_URL}/shipping`, {
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
        <div>• 물품 총액 (${quantity}개): <strong>$${formatPrice(taxData.total_goods_cad)} CAD</strong></div>
        <div>• 관세 (${taxData.duty_rate_percent}%): <strong>$${taxData.duty_cad} CAD</strong> | 세금(${taxData.province}): <strong>$${taxData.net_tax_cost_cad} CAD</strong></div>
        <div>• 국제 배송비 (${shipData.method}, ${shipData.estimated_days}): <strong>$${formatPrice(shipData.total_shipping_cad)} CAD</strong></div>
              <div style="font-size:12px; color:#5f6368;">  └ 청구중량: ${shipData.chargeable_kg}kg (${shipData.weight_basis})</div>
        ${quantity > 1 ? `<div style="font-size:12px; color:#5f6368;">  └ ${quantity}개 합산 배송비 $${formatPrice(shipData.total_shipping_cad)} CAD → 1개당 $${formatPrice(shipData.unit_shipping_cad)} CAD</div>` : ""}
        <div class="big-price" style="margin-top:8px;">최종 수입원가: $${formatPrice(totalLandedCost)} CAD</div>
        <div style="font-size:13px; font-weight:bold; color:#174ea6;">(개당 최종원가: $${formatPrice(unitLandedCost)} CAD)</div>
        ${noticeHtml}
      `;
      const amzInput = document.getElementById("amzLandedCostInput");
      if (amzInput) amzInput.value = unitLandedCost;
  
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
  