function zxGetElement(){

        if (document.getElementsByName("is_handler")[0]){

            var zx_arrays = document.getElementsByClassName("o_arrow_button");
            var zx_index=-1;
            for (i=0;i<zx_arrays.length;i++){
                if (zx_arrays[i].className.indexOf("btn-primary")>0){
                    zx_index = zx_arrays[i].getAttribute("data-id");
                }
            }
            if (document.getElementsByName("is_handler")[0].checked==false || (['0','1','2','7','8','9','10'].indexOf(zx_index)>-1)){

                //alert("none");
                document.getElementsByClassName("o_chatter_button_new_message")[0].style.display="none";
                document.getElementsByClassName("o_chatter_button_log_note")[0].style.display="none";
            }
            else {
                //alert("inline");
                document.getElementsByClassName("o_chatter_button_new_message")[0].style.display="inline-block";
                document.getElementsByClassName("o_chatter_button_log_note")[0].style.display="inline-block";
            }
        }
        else{

            setTimeout(zxGetElement,500);
        }
    }
window.onhashchange=function(){

    var uurl=window.location.href
    if (uurl.indexOf("dtdream.contract")>0 && uurl.indexOf("form")>0){

        zxGetElement();
        window.onclick=function(){

            setTimeout(zxGetElement,1000)
        }
    }
}
