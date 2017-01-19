var timeHandle;
var s;
var id;

function showLoginError(login){
    if (login == null || login == undefined || login.match("^[a-zA-Z]{1}[0-9]{4}$") == null){
        document.getElementById("textde1").className = "input-text error";
        return true;
    } else{
        document.getElementById("textde1").className = "input-text";
        return false;
    }
}

function showPhoneError(phone){
    if (phone == null || phone == undefined || phone.match("^[1]{1}[0-9]{10}$")== null){
	    document.getElementById("textde3").className = "input-no error";
	    return true;
	} else {
	    document.getElementById("textde3").className = "input-no";
	    return false;
	}
}

function showMailError(mail){
    if (mail == null || mail == undefined || mail.match("@dtdream[\.]com$")== null){
        document.getElementById("textde4").className = "input-no error";
        return true;
    } else{
        document.getElementById("textde4").className = "input-no";
        return false;
    }

}

function showSNError(sn) {
    if ( sn == null || sn == undefined || sn == "" ) {
        document.getElementById("textde5").className = "input-text error";
        return true;
    } else{
        document.getElementById("textde5").className = "input-text";
        return false;
    }
}

function showPasswordError(passwd,passwd2){
    if (passwd == null || passwd == undefined || passwd == ""){
        document.getElementById("textde6").className = "input-text error";
        return true;
    } else if (passwd != passwd2){
        document.getElementById("textde6").className = "input-text"
        document.getElementById("textde7").className = "input-text error";
        return true;
    } else{
        document.getElementById("textde6").className = "input-text"
        document.getElementById("textde7").className = "input-text"
    }
}

function getCodeByMail(){

    var username = document.getElementById("textde1").value;
    var mail = document.getElementById("textde4").value;

    if (showLoginError(username) || showMailError(mail)){
        return;
    }

	var data ={
		"login":username,
		"mail":mail
	};

	$.ajax({
          type: 'POST',
          url: "/web/ad/ms/mail",
          contentType: "application/json; charset=utf-8",
          data: JSON.stringify(data),
          dataType: "json",
          success: function(data){
            console.log(data.result);
            if (data.result.code == 10000){
                s=data.result.timeout;
                id="yxbtn";
                waitTimeout();
                timeHandle = setInterval(waitTimeout,1000);
            } else{
                alert(data.result.message)
            }
          },
          error:function(data){
            console.log(data);
          }
        });
};

function getCodeByPhone(){
	var username = document.getElementById("textde1").value;
	var phone = document.getElementById("textde3").value;

	if (showLoginError(username) || showPhoneError(phone)){
	    return;
	}

	var data ={
		"login":username,
		"phone":phone
	};

	$.ajax({
          type: 'POST',
          url: "/web/ad/ms/phone",
          contentType: "application/json; charset=utf-8",
          data: JSON.stringify(data),
          dataType: "json",
          success: function(data){
            console.log(data.result);
            if (data.result.code == 10000){
                s=data.result.timeout;
                id="sjbtn";
                waitTimeout();
                timeHandle = setInterval(waitTimeout,1000);
            } else{
                alert(data.result.message)
            }
          },
          error:function(data){
            console.log(data);
          }
        });
};

function waitTimeout(){
    if(s<0){
        document.getElementById(id).disabled=false;
        document.getElementById(id).value = '获取验证码';
        clearInterval(timeHandle);
        return false;
    }else{
      document.getElementById(id).disabled=true;
      document.getElementById(id).value = s+'秒';
      s--;
    }
}

function save(){

	var username = document.getElementById("textde1").value;
	var sn = document.getElementById("textde5").value;

	var passwd = document.getElementById("textde6").value;
	var passwd2 = document.getElementById("textde7").value;

	if ( showLoginError(username) || showSNError(sn) || showPasswordError(passwd, passwd2)){
	    return;
	}

	var data ={
		"login":username,
		"sn":sn,
		"passwd":passwd,
		"passwd2":passwd2
	}

	$.ajax({
          type: 'POST',
          url: "/web/ad/reset",
          contentType: "application/json; charset=utf-8",
          data: JSON.stringify(data),
          dataType: "json",
          success: function(data){
            console.log(data.result);
            if (data.result.code == 10000){
                alert(data.result.message)
                self.location = "/web/login"
            } else{
                alert(data.result.message)
            }
          },
          error:function(data){
            console.log(data.result);
            alert(data.result.message)
          }
        });
}

//------------------placeholder
var doc=document,
inputs=doc.getElementsByTagName('input'),
supportPlaceholder='placeholder'in doc.createElement('input'),

placeholder=function(input){
    var text = input.getAttribute('placeholder'),
    defaultValue = input.defaultValue;
    if(defaultValue=='') {
        input.value=text;
        input.style.color="#b2b2b2";
    }
    input.onfocus = function() {
        if(input.value===text)
        {
            this.value='';
            input.style.color="black";
        }
    };

    input.onblur=function() {
        if(input.value==='') {
            this.value=text;
            input.style.color="#b2b2b2";
        }
    };
};

if(!supportPlaceholder) {
    for(var i=0,len=inputs.length;i<len;i++) {
        var input=inputs[i],
        text=input.getAttribute('placeholder');
        if(input.type==='text'&&text){
            placeholder(input);
        }
    }
}

//--------------dropdown menu

function choose(value){
   document.getElementById("textde2").value=value;
   document.getElementById("myOption").style.display="none";
}

function choosePhone(value){
    choose("手机");
    document.getElementById("myMail").style.display="none";
    document.getElementById("myMobile").style.display="block";
}

function chooseMail(value){
    choose("邮箱");
    document.getElementById("myMail").style.display="block";
    document.getElementById("myMobile").style.display="none";
}