
// --- 1. 새로운 실시간 환율 계산기 기능 ---
// sidepanelCurrency.js 에서 불러옴


// --- 2. 관세 + 판매세 + 국제 배송비 통합 계산기 기능 ---
// sidepanelShipping.js 에서 불러옴


// --- 3. Amazon.ca 판매가 & 마진 계산기 기능 ---
// sidepanelAmazon.js 에서 불러옴

// 모든 숫자 입력칸에서 마우스 휠 / 트랙패드 스크롤로 숫자가 바뀌는 현상 차단
document.querySelectorAll('input[type="number"]').forEach((input) => {
  input.addEventListener("wheel", (event) => {
    event.preventDefault();
  }, { passive: false });
});
