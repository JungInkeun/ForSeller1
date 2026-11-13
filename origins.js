// 소싱 국가(출발국) 목록 데이터
const ORIGIN_LIST = [
    { code: "KR", label: "한국 (South Korea)", defaultCurrency: "KRW" },
    { code: "JP", label: "일본 (Japan)", defaultCurrency: "JPY" },
    { code: "TW", label: "대만 (Taiwan)", defaultCurrency: "TWD" },
    { code: "US", label: "미국 (United States)", defaultCurrency: "USD" }
  ];
  
  // 드롭다운(select)에 소싱 국가 옵션을 자동으로 채워주는 함수
  function populateOriginDropdown() {
    const originSelect = document.getElementById("originCountry");
    if (!originSelect) return;
  
    ORIGIN_LIST.forEach((item) => {
      // 기본값: 한국 (KR)
      const option = new Option(item.label, item.code, false, item.code === "KR");
      originSelect.add(option);
    });
  }
  
  // 화면이 열리면 즉시 실행
  populateOriginDropdown();
  