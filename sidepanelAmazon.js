async function runAmazonCalc() {
    const unitLandedCost = parseFloat(document.getElementById("amzLandedCostInput").value);
    const targetMarginPercent = parseFloat(document.getElementById("targetMarginInput").value);
    const fulfillmentType = document.getElementById("fulfillmentType").value;
    const storageMonths = parseFloat(document.getElementById("storageMonthsInput").value) || 1.0;
    const fbmShipping = parseFloat(document.getElementById("fbmShippingInput").value) || 0.0;
    const isPeak = document.getElementById("peakSeasonCheck").checked;
    const isIndiv = document.getElementById("indivPlanCheck").checked;
  
    // 2번 카드에 입력된 카테고리·무게·크기 값을 그대로 재활용
    const category = document.getElementById("itemCategory").value;
    const weightG = parseFloat(document.getElementById("weightInput").value) || 200;
    const lengthCm = parseFloat(document.getElementById("lengthInput").value) || 15;
    const widthCm = parseFloat(document.getElementById("widthInput").value) || 10;
    const heightCm = parseFloat(document.getElementById("heightInput").value) || 5;
  
    const amzResultArea = document.getElementById("amazonResultArea");
  
    if (isNaN(unitLandedCost) || unitLandedCost <= 0) {
      amzResultArea.innerText = "올바른 개당 수입원가(CAD)를 입력해 주세요.";
      return;
    }
  
    if (isNaN(targetMarginPercent) || targetMarginPercent <= 0 || targetMarginPercent >= 80) {
      amzResultArea.innerText = "목표 순마진은 1% ~ 79% 사이로 입력해 주세요.";
      return;
    }
  
    amzResultArea.innerText = "아마존 수수료 및 권장 판매가 계산 중...";
  
    try {
      const response = await fetch("http://localhost:8000/amazon-fee", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          unit_landed_cost_cad: unitLandedCost,
          category: category,
          unit_weight_g: weightG,
          length_cm: lengthCm,
          width_cm: widthCm,
          height_cm: heightCm,
          fulfillment_type: fulfillmentType,
          fbm_local_shipping_cad: fbmShipping,
          storage_months: storageMonths,
          is_peak_season: isPeak,
          is_individual_plan: isIndiv,
          target_margin_rate: targetMarginPercent / 100.0
        })
      });
  
      if (!response.ok) throw new Error("서버 응답 오류");
  
      const data = await response.json();
  
      amzResultArea.innerHTML = `
        <div>• 규격 등급: <strong>${data.size_tier}</strong></div>
        <div>• 추천 수수료 (${data.referral_rate_percent}%): <strong>$${data.referral_fee_cad} CAD</strong></div>
        <div>• FBA/배송비: <strong>$${data.fulfillment_fee_cad} CAD</strong> | 보관료: <strong>$${data.storage_fee_cad} CAD</strong></div>
        <div style="font-size:12px; color:#5f6368;">  └ 손익분기 최소 판매가: $${data.breakeven_price_cad} CAD</div>
        <div class="big-price" style="margin-top:8px;">권장 판매가: $${data.recommended_price_cad} CAD</div>
        <div style="font-size:13px; font-weight:bold; color:#137333;">개당 예상 순수익: +$${data.net_profit_cad} CAD (${data.target_margin_percent}%)</div>
      `;
    } catch (error) {
      amzResultArea.innerText = "연결 실패: Python 서버(uvicorn)가 실행 중인지 확인하세요.";
    }
  }
  
  document.getElementById("amazonFeeBtn").addEventListener("click", runAmazonCalc);
  
  ["amzLandedCostInput", "targetMarginInput", "storageMonthsInput", "fbmShippingInput"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("keydown", (event) => {
        if (event.key === "Enter") runAmazonCalc();
      });
    }
  });
  