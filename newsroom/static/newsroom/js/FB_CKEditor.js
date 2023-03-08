let counter = 0;

function extractPath(fileUrl) {
    let dir = fileUrl.match(/(.*)[\/\\]/)[1]||'';
    const lenMedia = "/media/".length - 1;
    const versions = "/_versions/";
    const lenVer = "/_versions/".length;
    const lenUpload = "uploads/".length;

    dir = dir.substring(lenMedia);
    if (dir.substring(0, lenVer) === versions) {
        dir = dir.substring(lenVer - 1);
    }
    dir = dir.substring(1);
    dir = decodeURI(dir);
    if (dir.substr(0, lenUpload) === "uploads/") {
        dir = dir.substr(lenUpload);
    }
    return dir;
}

jQuery(document).ready(function ($) {
    // First make sure we're dealing with images
    let dir;
    let urlSearchParams = new URLSearchParams(window.location.search);
    let params = Object.fromEntries(urlSearchParams.entries());

    if (!("dir" in params) || !(params["dir"].includes("images"))) return;
    let fileUrl;
    if ('summary' in params) {
        fileUrl = window.opener.getSummaryImage();
    } else if ('audio' in params){
        fileUrl = window.opener.getAudioSummary();
    }else {
        fileUrl = window.opener.CKEDITOR.document.$.
            getElementsByClassName('cke_dialog_image_url')[0].
            querySelector('input').value;
    }

    if (fileUrl) {
        dir = decodeURI(extractPath(fileUrl));
    } else {
        dir = localStorage.getItem('fb_dir');
        const ms = localStorage.getItem('fb_dir_ms');
        if(dir && ms && ((Date.now() - ms) < 3600000)) {
            dir = decodeURI(dir);
        } else {
            dir = "images";
        }
    }

    if (dir && !("attempted" in params)) {
        params["dir"] = dir
        params["attempted"] = true;
        urlSearchParams = new URLSearchParams(params);
        url = window.location.pathname + "?" + urlSearchParams.toString();
        window.location = url;
    }
});

function ProtectPath(path) {
    path = path.replace( /\\/g,'\\\\');
    path = path.replace( /'/g,'\\\'');
    return path ;
}

function gup( name ) {
  name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp(regexS);
  var results = regex.exec(window.location.href);
  if(results == null)
    return "";
  else
    return results[1];
}

function OpenFile(fileUrl) {
    let CKEditorFuncNum = gup('CKEditorFuncNum');
    if (fileUrl.includes("images")) {
        localStorage.setItem('fb_dir', extractPath(fileUrl));
        localStorage.setItem('fb_dir_ms', Date.now());
    }
    const params = new URLSearchParams(location.search);
    if (params.get('summary')) {
        if (window.opener && window.opener.document &&
            window.opener.document.getElementById("id_summary_image")) {
            window.opener.receiveSummaryImage(fileUrl);
            window.top.close();
            window.top.opener.focus();
        }
    } else if (params.get('audio')) {
        if (window.opener && window.opener.document &&
            window.opener.document.getElementById("id_audio_summary")) {
            window.opener.receiveAudioSummary(fileUrl);
            window.top.close();
            window.top.opener.focus();
        }
    }else {
        window.top.opener.CKEDITOR.tools.callFunction(CKEditorFuncNum, fileUrl);
    }
    window.top.close();
    window.top.opener.focus();
}
