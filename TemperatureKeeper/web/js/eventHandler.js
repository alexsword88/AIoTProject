eel.expose(onTempUpdate);
function onTempUpdate(temp) {
  document.getElementById("temp").innerText = temp;
}

eel.expose(onTriggerUpdate);
function onTriggerUpdate(temp) {
  document.getElementById("trigger").innerText = temp;
}
