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
    let urlSearchParams = new URLSearchParams(window.location.search);
    let params = Object.fromEntries(urlSearchParams.entries());

    if (!("dir" in params) || !(params["dir"].includes("images"))) return;

    let fileUrl = window.opener.CKEDITOR.document.$.
        getElementsByClassName('cke_dialog_image_url')[0].
        querySelector('input').value;
    console.log("fb_dir", localStorage.getItem('fb_dir'));
    console.log("fileUrl", fileUrl);
    if (fileUrl) {
        dir = decodeURI(extractPath(fileUrl));
        console.log("dir immediately after extract", dir);
    } else {
        dir = localStorage.getItem('fb_dir');
        if(dir) {
            dir = decodeURI(dir);
        } else {
            dir = "images";
        }
    }
    console.log("dir", dir);

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
    console.log("Openfile fileUrl", extractPath(fileUrl));
    console.log("Openfile fb_dir a", localStorage.getItem('fb_dir'));
    if (fileUrl.includes("images")) {
        localStorage.setItem('fb_dir', extractPath(fileUrl));
    }
    console.log("Openfile fb_dir b", localStorage.getItem('fb_dir'));
    const params = new URLSearchParams(location.search);
    if (params.get('summary')) {
        if (window.opener && window.opener.document &&
            window.opener.document.getElementById("id_summary_image")) {
            window.opener.receiveSummaryImage(fileUrl);
            window.top.close();
            window.top.opener.focus();
        }
    } else {
        window.top.opener.CKEDITOR.tools.callFunction(CKEditorFuncNum, fileUrl);
    }
    window.top.close();
    window.top.opener.focus();
}
