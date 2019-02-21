
  var _paq = window._paq || [];
  /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
  _paq.push(["setDocumentTitle", document.domain + "/" + document.title]);
  _paq.push(["setCookieDomain", "*.fabscan.org"]);
  _paq.push(["setDomains", ["*.fabscan.org","*.www.fabscan.org"]]);
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {
    var u="//analytics.mariolukas.de/";
    _paq.push(['setTrackerUrl', u+'matomo.php']);
    _paq.push(['setSiteId', '3']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.type='text/javascript'; g.async=true; g.defer=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
  })();
    
$.get('https://api.github.com/repos/mariolukas/FabScanPi-Build-Raspbian/releases/latest', function (data) {
   var asset = data.assets[0];
     var downloadCount = 0;
     for (var i = 0; i < data.assets.length; i++) {
         downloadCount += data.assets[i].download_count;
     }
     var oneHour = 60 * 60 * 1000;
     var oneDay = 24 * oneHour;
     var dateDiff = new Date() - new Date(asset.updated_at);
     var timeAgo;
     if (dateDiff < oneDay)
     {
         timeAgo = Math.ceil((dateDiff / oneHour).toFixed(1)) + " hours ago";
     }
     else
     {
         timeAgo = Math.ceil((dateDiff / oneDay).toFixed(1)) + " days ago";
     }
  $('#latest_release').attr('href', data.assets[0].browser_download_url);
  $('#latest_release').text(data.assets[0].browser_download_url.split("/").pop());
  $('#latest_release_info').text( " download size is "+parseInt(data.assets[0].size/1000/1000)+"  MB was updated "+timeAgo+" and downloaded "+data.assets[0].download_count+" times" );


  console.log(data)
});
