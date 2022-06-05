eel.expose(onWarningTrigger);
function onWarningTrigger() {
  document.getElementById("state").innerText = "門被打開";
  document.getElementById("info-container").style.visibility = "visible";
  document.getElementById("target").removeAttribute("src");
  document.getElementById("target-name").innerText = "搜索中。。。"
}

eel.expose(onWarningReset);
function onWarningReset() {
  document.getElementById("state").innerText = "警報重啟";
  setTimeout(() => {
    document.getElementById("info-container").style.visibility = "hidden";
    document.getElementById("state").innerText = "無事件";
  }, 5000);
}

eel.expose(onTemperatureUpdate);
function onTemperatureUpdate(temp) {
  document.getElementById("temp").innerText = temp;
}

eel.expose(onFaceFound);
function onFaceFound(name) {
  document.getElementById("target-name").innerText = name ? name: "未知";
  document.getElementById("target").setAttribute('src', `/target.jpg?r=${new Date().getTime()}` ) = "visible";
}
