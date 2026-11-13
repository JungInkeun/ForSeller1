const PRODUCT_CATEGORY_LIST = [
    { code: "cosmetics", label: "화장품 (Cosmetics)" },
    { code: "food", label: "가공식품/간식 (Food)" },
    { code: "computer", label: "컴퓨터/전자부품 (Computer)" },
    { code: "apparel", label: "의류/잡화 (Apparel)" },
    { code: "tools", label: "수공구/장비 (Tools)" },
    { code: "general", label: "기타 일반품목 (General)" }
  ];

// 드롭다운(select)에 옵션을 자동으로 채워주는 함수
function productCategoryDropdowns() {
    const categorySelect = document.getElementById("itemCategory");
    if (!categorySelect) return;
  
    PRODUCT_CATEGORY_LIST.forEach((item) => {
      // From 드롭다운 옵션 생성 (기본값: ON)
      const fromOption = new Option(item.label, item.code, false, item.code === "cosmetics");
      categorySelect.add(fromOption);
  
    });
  }
  
  // 화면이 열리면 즉시 실행
  productCategoryDropdowns();

