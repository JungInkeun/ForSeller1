const extpay = ExtPay("for-amazon-sellers");
const MAX_FREE_USES = 10; // 무료 사용 10회

// 유료 구매자인지 확인하고, 무료 사용자면 10회까지만 허용하는 함수
async function checkFreeOrPaidUsage() {
  try {
    const user = await extpay.getUser();

    // 1. 유료 결제자(월간 구독 또는 평생 구매)는 무제한 통과
    if (user.paid) {
      return true;
    }

    // 2. 무료 사용자는 현재까지 사용한 횟수 조회
    const storageData = await chrome.storage.local.get(["freeUsageCount"]);
    const currentCount = storageData.freeUsageCount || 0;

    // 3. 10회 미만이면 횟수 +1 증가시키고 통과
    if (currentCount < MAX_FREE_USES) {
      const nextCount = currentCount + 1;
      await chrome.storage.local.set({ freeUsageCount: nextCount });
      console.log(`무료 체험 사용 중: ${nextCount} / ${MAX_FREE_USES}회`);
      return true;
    }

    // 4. 10회 초과 시 결제 안내 후 ExtensionPay 결제창 오픈
    alert(`무료 계산 ${MAX_FREE_USES}회를 모두 사용하셨습니다.\n계속 이용하시려면 구독 또는 평생 소장 플랜을 선택해 주세요!`);
    extpay.openPaymentPage();
    return false;
  } catch (error) {
    console.error("결제 상태 확인 오류:", error);
    return true; // 네트워크 일시 오류 시 사용자 불편 방지
  }
}



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
