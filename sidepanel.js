document.getElementById("calcBtn").addEventListener("click", async () => {
    const inputVal = parseFloat(document.getElementById("numInput").value);
    const resultArea = document.getElementById("resultArea");
  
    if (isNaN(inputVal)) {
      resultArea.innerText = "올바른 숫자를 입력해 주세요.";
      return;
    }
  
    resultArea.innerText = "Python 서버에서 계산 중...";
  
    try {
      // 1단계에서 실행한 Python FastAPI 서버로 데이터 전송
      const response = await fetch("http://127.0.0.1:8000/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ number: inputVal })
      });
  
      const data = await response.json();
      resultArea.innerText = `결과: ${data.result} (10% 추가됨)`;
    } catch (error) {
      resultArea.innerText = "연결 실패: Python 서버(uvicorn)가 실행 중인지 확인하세요.";
    }
  });
  