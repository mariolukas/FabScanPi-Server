(function(){ window.i18n || (window.i18n = {}) 
var MessageFormat = { locale: {} };
MessageFormat.locale.en=function(n){return n===1?"one":"other"}

window.i18n["main"] = {}
window.i18n["main"]["FABSCAN"] = function(d){return "Fabscan"}
window.i18n["main"]["SCAN_CANCELED"] = function(d){return "Scan stoped"}
window.i18n["main"]["SCAN_STOPED"] = function(d){return "Scan stoped"}
window.i18n["main"]["SCANNING_OBJECT"] = function(d){return "Scanning Object"}
window.i18n["main"]["SCANNING_TEXTURE"] = function(d){return "Scanning Texture"}
window.i18n["main"]["NO_LASER_FOUND"] = function(d){return "No laser detected. Try other settings"}
window.i18n["main"]["SAVING_POINT_CLOUD"] = function(d){return "Saving Point Cloud please wait..."}
window.i18n["main"]["SCAN_COMPLETE"] = function(d){return "Scan complete"}
window.i18n["main"]["NO_SERIAL_CONNECTION"] = function(d){return "No connection to Arduino"}
window.i18n["main"]["NO_CAMERA_CONNECTION"] = function(d){return "Camera is not connected"}
window.i18n["main"]["CONNECTED_TO_SERVER"] = function(d){return "Connected to FabScanPi-Server"}
window.i18n["main"]["SERIAL_CONNECTION_READY"] = function(d){return "Arduino/ FabScanPI HAT connected"}
window.i18n["main"]["CAMERA_READY"] = function(d){return "Camera ready"}
})();