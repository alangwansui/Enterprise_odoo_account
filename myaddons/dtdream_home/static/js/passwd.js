$(function () {
    function redirect (url, wait) {
        var old = "" + window.location;
        var old_no_hash = old.split("#")[0];
        var url_no_hash = url.split("#")[0];
        location.assign(url);
        if (old_no_hash === url_no_hash) {
            location.reload(true);
        }
    }

    var $button = $(".o_dtdream_home_reset_passwd").on('click', function (e){
//        console.log('aaaa')
        var data ={
		"old_pwd":$('#old_pwd').val(),
		"new_pwd":$('#new_pwd').val(),
		"confirm_password":$('#confirm_password').val()
        }

        $.ajax({
              type: 'POST',
              url: "/dtdream_home/resetpasswd",
              contentType: "application/json; charset=utf-8",
              data: JSON.stringify(data),
              dataType: "json",
              success: function(data){
                console.log(data.result);
                if (data.result.code == 0){
                    redirect('/web/session/logout');
                } else{
                    $('.error-text').text(data.result.error).show()
                }
              },
              error:function(data){
                $('.error-text').text(data.result.error).show()
              }
            });
        });
});