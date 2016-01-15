(function(){ window.i18n || (window.i18n = {}) 
var MessageFormat = { locale: {} };
MessageFormat.locale.de=function(n){return n===1?"one":"other"}

window.i18n["main"] = {}
window.i18n["main"]["FABSCAN"] = function(d){return "Fabscan"}
window.i18n["sub/folder/plural"] = {}
window.i18n["sub/folder/plural"]["test"] = function(d){return "Your "+p(d,"NUM",0,"de",{"one":"message","other":"messages"})+" go here."}
})();