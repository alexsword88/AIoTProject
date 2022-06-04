eel.expose(onTempUpdate);
function onTempUpdate(temp) {
  document.getElementById("temp").innerText = temp;
}

eel.expose(onTriggerUpdate);
function onTriggerUpdate(temp) {
  document.getElementById("trigger").innerText = temp;
}

eel.expose(onTriggerRaise);
function onTriggerRaise() {
  document.getElementById("trigger").style.color = "#F00";
}

eel.expose(onTriggerOff);
function onTriggerOff() {
  document.getElementById("trigger").style.color = "#000";
}
