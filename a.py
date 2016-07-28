# -*-coding:utf-8-*-


import requests
import json
import time
#from subprocess import Popen
from HTMLParser import HTMLParser


class ZhihuClient(object):
    #captchaFile = os.path.join(sys.path[0], "captcha.gif")  
    def __init__(self):
        object.__init__(self)

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
                   }
        self.session = requests.session()
        self.session.headers.update(headers)
        self.xsrf = None

    def login(self, username, password):
        url = 'http://www.zhihu.com/#signin'

        r = self.session.get(url)
        captcha_type, self.xsrf = _get_captcha(r.content)

        url = 'http://www.zhihu.com/login/phone_num'
        data = {'phone_num': username, 'password': password}
        
        #captcha_url = 'http://www.zhihu.com/captcha.gif?r=%s&type=login&lang=cn' % int(time.time()*1000)
        #while True:
        #    capatcha = self.session.get('http://www.zhihu.com/captcha.gif').content
        #    with open('code.gif', 'wb') as output:
        #        output.write(capatcha)
            #Popen('code.gif', shell=True)
        #    captcha = raw_input(u"请输入验证码:")
        #    data['captcha'] = captcha
        data['captcha_type'] = captcha_type
        data['remember_me'] = 'false'

        headers = {'X-Xsrftoken': self.xsrf,
                    }
        self.session.headers.update(headers)
            #print self.session.headers
        r = self.session.post(url, data=data)
        print json.loads(r.content).get('msg','')
        #print self.session.cookies.items()

    def edit_signature(self, description):
        url = 'http://www.zhihu.com/node/ProfileHeaderV2'
        data = {'method': 'save', 'params': json.dumps({"data":{"description": description}})}
        headers = {'Origin': 'http://www.zhihu.com',
                   'Host': 'www.zhihu.com',
                   'Referer': 'http://www.zhihu.com/people/jinshuz',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   }
        self.session.headers.update(headers)
        print self.session.headers
        r = self.session.post(url, data=data)
        print '---------------->',(r.content)


def _attr(attrs, attrname):
    for attr in attrs:
        if attr[0] == attrname:
            return attr[1]
    return None


def _get_captcha(content):
    class CaptchaParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.captcha_type = None
            self.captcha_url = None
            self._xsrf = None

        def handle_starttag(self, tag, attrs):
            if tag == 'input' and _attr(attrs, 'type') == 'hidden' and _attr(attrs, 'name') == 'captcha_type':
                self.captcha_type = _attr(attrs, 'value')

            if tag == 'input' and _attr(attrs, 'type') == 'hidden' and _attr(attrs, 'name') == '_xsrf':
                self._xsrf = _attr(attrs, 'value')

    p = CaptchaParser()
    p.feed(content)
    return p.captcha_type, p._xsrf


if __name__ == '__main__':
    c = ZhihuClient()
    username = '15088618784'
    password = 'jinshuz18784'
    c.login(username, password)
    #c.edit_signature('dasdada')





