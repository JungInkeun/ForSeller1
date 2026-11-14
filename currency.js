const currencyCardHtml = `
  <div class="card">
    <h3>실시간 환율 계산기</h3>
    <label>From (보유 통화 및 금액)</label>
    <div class="input-group">
      <select id="fromCurrency" style="flex: 1.2;"></select>
      <input type="number" id="amountInput" placeholder="예: 50000" style="flex: 1;" />
    </div>
    <label>To (변환할 통화)</label>
    <div class="input-group">
      <select id="toCurrency" style="width: 100%;"></select>
    </div>
    <button id="convertBtn">환율 변환하기 (Enter)</button>
    <div id="convertResultArea" class="result-box">통화를 선택하고 숫자를 입력하세요.</div>
  </div>
`;

const container = document.getElementById("currencyCardContainer");
if (container) {
  container.innerHTML = currencyCardHtml;
}


const CURRENCY_LIST = [
    { code: "CAD", label: "CAD (캐나다 달러)" },
    { code: "KRW", label: "KRW (한국 원)" },
    { code: "JPY", label: "JYP / JPY (일본 엔)" },
    { code: "CNY", label: "CHN / CNY (중국 위안)" },
    { code: "EUR", label: "EURO / EUR (유럽 유로)" },
    { code: "USD", label: "USD / USD (미국)" }
  ];

// 드롭다운(select)에 옵션을 자동으로 채워주는 함수
function populateCurrencyDropdowns() {
    const fromSelect = document.getElementById("fromCurrency");
    const toSelect = document.getElementById("toCurrency");
  
    CURRENCY_LIST.forEach((item) => {
      // From 드롭다운 옵션 생성 (기본값: KRW)
      const fromOption = new Option(item.label, item.code, false, item.code === "KRW");
      fromSelect.add(fromOption);
  
      // To 드롭다운 옵션 생성 (기본값: CAD)
      const toOption = new Option(item.label, item.code, false, item.code === "CAD");
      toSelect.add(toOption);
    });
  }
  
  // 화면이 열리면 즉시 실행
  populateCurrencyDropdowns();