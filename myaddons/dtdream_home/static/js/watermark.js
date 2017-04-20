odoo.define('dtdream_home.WaterMark', function (require) {
"use strict";
var Model = require('web.Model');
var session = require('web.session');
var Widget = require('web.Widget');

var userName = "";

var Main=Widget.extend({
    init: function() {
//        this._super(parent);
    },
    start:function(){
        new Model('res.users')
            .query(['name', "company_id"])
            .filter([['id','=', session.uid]])
            .all({'timeout': 3000, 'shadow': true})
            .then(function (result) {
                    console.log(result[0].name);
                    userName=result[0].name+session.username.slice(1);
                    function textToImg(canvasWidth,canvasHeight,txtX,txtY,txtFont,opacity,deg) {
                        var len = 100;
                        var i = 0;
                        var fontSize = txtFont;
                        var fontWeight = $('fontWeight').value || 'normal';
                        var txt = userName;
                        var canvas = document.createElement('canvas');
                        if (len > txt.length) {
                            len = txt.length;
                        }
                        canvas.width = canvasWidth;
                        canvas.height = canvasHeight;
                        var context = canvas.getContext('2d');
                        context.clearRect(0, 0, canvas.width, canvas.height);
//                        context.fillStyle = "rgba(240,81,51)";
                        context.fillStyle = "rgba(160,160,160,"+opacity+")";
                        context.font = fontWeight + ' ' + fontSize + 'px sans-serif';
                        context.textBaseline = 'top';
                        context.rotate(-Math.PI/deg);
                        canvas.style.display = 'none';
                        // console.log(txt.length);
                        function fillTxt(text) {
                            while (text.length > len) {
                                var txtLine = text.substring(0, len);
                                text = text.substring(len);
                                context.fillText(txtLine, 20, fontSize * (3 / 2) * i++,
                                        canvas.width);
                            }
                            context.fillText(text, txtX, txtY, canvas.width);
                        }
                        var txtArray = txt.split('\n');
                        for ( var j = 0; j < txtArray.length; j++) {
                            fillTxt(txtArray[j]);
                            context.fillText('\n', 0, fontSize * (3 / 2) * i++, canvas.width);
                        }
                        var imageData = context.getImageData(0, 0, canvas.width, canvas.height);
                        var imgSrc = canvas.toDataURL("image/png");
                        return imgSrc;
                    }
                    var img1 = textToImg(450,280,120,220,16,0.5,6);
                    var img2 = textToImg(300,100,0,0,30,0.01,0);

                    $(".o_main").css("background-image","url("+img1+")");
                }
            );
    }
})

return Main;

});