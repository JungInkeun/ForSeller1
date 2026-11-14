importScripts("ExtPay.js");

const extpay = ExtPay("for-amazon-sellers");
extpay.startBackground();

chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error(error));
