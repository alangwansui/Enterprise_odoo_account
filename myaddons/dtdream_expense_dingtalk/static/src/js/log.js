
if(sessionStorage.logBuf == "" || sessionStorage.logBuf == undefined){
sessionStorage.logBuf=[];
}
var debug_arr = window.location.search.substr(1).match(new RegExp("debug=([^&]*)"));
if (debug_arr){
    DEBUG=true;
} else {
    DEBUG=false;
}

var Util = {
    log: function (type, msg) {
        if (!DEBUG){
            return;
        }
        var sLog = type + ': ' + msg
        if (sLog.length > 100) {
            sLog = sLog.substring(0, 80) + '...'
        }
        sLog = (new Date()).getTime() + ' ' + sLog +";"
        sessionStorage.logBuf += sLog;
    },
    clear: function(){
        sessionStorage.logBuf.length = 0;
    }
};
var cui_buf = [];
var view_image = false;
var isAlert = false;