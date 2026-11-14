
// 숫자를 3자리마다 쉼표가 찍힌 문자열로 변환 (예: 440000 -> "440,000" / 53.2 -> "53.20")
function formatPrice(num) {
  if (isNaN(num) || num === null) return "0";
  return Number(num).toLocaleString("en-US", {
    minimumFractionDigits: Number.isInteger(Number(num)) ? 0 : 2,
    maximumFractionDigits: 2
  });
}


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
