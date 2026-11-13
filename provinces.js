const PROVINCE_LIST = [
    { code: "BC", label: "British Columbia" },
    { code: "AB", label: "Alberta" },
    { code: "SK", label: "Saskatchewan" },
    { code: "MB", label: "Manitoba" },
    { code: "ON", label: "Ontario" },
    { code: "QC", label: "Quebec" },
    { code: "NB", label: "New Brunswick" },
    { code: "NS", label: "Nova Scotia" },
    { code: "PE", label: "Prince Edward Island" },
    { code: "NL", label: "Newfoundland and Labrador" }
  ];

// 드롭다운(select)에 옵션을 자동으로 채워주는 함수
function canadaProvinceDropdowns() {
    const pronvice = document.getElementById("canadaProvince");
    if (!provinceSelect) return;
  
    PROVINCE_LIST.forEach((item) => {
      // From 드롭다운 옵션 생성 (기본값: ON)
      const fromOption = new Option(item.label, item.code, false, item.code === "ON");
      pronvice.add(fromOption);
  
    });
  }
  
  // 화면이 열리면 즉시 실행
  canadaProvinceDropdowns();