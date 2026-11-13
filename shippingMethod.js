const SHIPPING_WAY = [
    { code: "kpacket", label: "소형항공 (K-Packet)" },
    { code: "ems", label: "우체국 EMS" },
    { code: "express", label: "특송 (DHL/FedEx)" },
    { code: "ocean", label: "해상화물 (대량 FBA)" }
  ];

// 드롭다운(select)에 옵션을 자동으로 채워주는 함수
function shippingWayDropdowns() {
    const shippingSelect = document.getElementById("shippingMethod");
    if (!shippingSelect) return;
  
    SHIPPING_WAY.forEach((item) => {
      // From 드롭다운 옵션 생성 (기본값: ON)
      const fromOption = new Option(item.label, item.code, false, item.code === "kpacket");
      shippingSelect.add(fromOption);
  
    });
  }
  
  // 화면이 열리면 즉시 실행
  shippingWayDropdowns();

