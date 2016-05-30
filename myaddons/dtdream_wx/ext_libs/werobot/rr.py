# -*-coding:utf-8-*-

import requests

#r = requests.request(
#             method="get",
#             url="https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wxea196a3e2e4cf46f&secret=1459822bac8a036a77acd5737714c4a0",
#         )

#access_token = r.json().get("access_token")
#access_token

access_token = 'eoji02SI2Bb0CIiz1ZJni2B-sKkqqR3pyveM1FcHH8YsX0Rys3WKVzk_d95XnzI8LTltFw716ANQ1AQljhhm8l513_b5zyhs6926ZpFFIp2VhlkToVvuw8cc8duJqmm9TXNjAEAWAQ'

data = '''{
            "touser": "o6egzwcHLpVXfSkj7WG1RO4ljeNo",
            "msgtype":"text",
            "text":
            {
                 "content":"这只是测试,"
            }
        }'''

r = requests.request(
            method="post",
            url="https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" % access_token,
            data=data,
        )

print r.json()
