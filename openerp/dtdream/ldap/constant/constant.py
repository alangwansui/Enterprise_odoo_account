# -*- coding: utf-8 -*-

__author__ = "g0335"

# AD
LDAP_HOST="dthz-adroot01.dtdream.com"
LDAP_DN='cn=dodo-admin,OU=DTALL,dc=dtdream,dc=com'
LDAP_OU='ou=DTALL'
LDAP_BASE='dc=dtdream,dc=com'
LDAP_PASS='1qaz!QAZ'
LDAP_CA_CERT_FILE='cacert/dodo-admin.pem'
LDAP_PORT = 389
LDAPS_PORT = 636

# AD constants
# SCRIPT - 将运行登录脚本
AD_USERCTRL_ACCOUNT_SCRIPT = 0x0001

# ACCOUNTDISABLE - 禁用用户帐户
AD_USERCTRL_ACCOUNT_DISABLED = 0x0002

# HOMEDIR_REQUIRED - 需要主文件夹
AD_USERCTRL_ACCOUNT_HOMEDIR_REQUIRED = 0x0008

# LOCKOUT
AD_USERCTRL_ACCOUNT_LOCKOUT = 0x0010

# PASSWD_NOTREQD - 不需要密码
AD_USERCTRL_ACCOUNT_PASSWD_NOTREQD = 0x0020

# PASSWD_CANT_CHANGE - 用户不能更改密码。可以读取此标志，但不能直接设置它
AD_USERCTRL_ACCOUNT_PASSWD_CANT_CHANGE = 0x0040

# ENCRYPTED_TEXT_PASSWORD_ALLOWED - 用户可以发送加密的密码
# AD_USERCTRL_ACCOUNT_ENCRYPTED_TEXT_PASSWORD_ALLOWED =

# TEMP_DUPLICATE_ACCOUNT - 此帐户属于其主帐户位于另一个域中的用户。此帐户为用户提供访问该域的权限，但不提供访问信任该域的任何域的权限。有时将这种帐户称为“本地用户帐户”
AD_USERCTRL_ACCOUNT_TEMP_DUPLICATE_ACCOUNT = 0x0100

# NORMAL_ACCOUNT - 这是表示典型用户的默认帐户类型
AD_USERCTRL_NORMAL_ACCOUNT = 0x0200

# INTERDOMAIN_TRUST_ACCOUNT - 对于信任其他域的系统域，此属性允许信任该系统域的帐户
AD_USERCTRL_ACCOUNT_INTERDOMAIN_TRUST_ACCOUNT = 0x0800

# WORKSTATION_TRUST_ACCOUNT - 这是运行 Microsoft Windows NT 4.0 Workstation、Microsoft Windows NT 4.0 Server、Microsoft Windows 2000 Professional
# 或 Windows 2000 Server 并且属于该域的计算机的计算机帐户
AD_USERCTRL_WORKSTATION_ACCOUNT = 0x1000

# SERVER_TRUST_ACCOUNT - 这是属于该域的域控制器的计算机帐户
AD_USERCTRL_ACCOUNT_SERVER_TRUST_ACCOUNT = 0x2000

# DONT_EXPIRE_PASSWORD - 表示在该帐户上永远不会过期的密码
AD_USERCTRL_DONT_EXPIRE_PASSWORD = 0x10000

# MNS_LOGON_ACCOUNT - 这是 MNS 登录帐户
AD_USERCTRL_ACCOUNT_MNS_LOGON_ACCOUNT = 0x20000

# SMARTCARD_REQUIRED - 设置此标志后，将强制用户使用智能卡登录
AD_USERCTRL_ACCOUNT_SMARTCARD_REQUIRED = 0x40000

# TRUSTED_FOR_DELEGATION - 设置此标志后，将信任运行服务的服务帐户（用户或计算机帐户）进行 Kerberos 委派。任何此类服务都可模拟请求该服务的客户端。
# 若要允许服务进行 Kerberos 委派，必须在服务帐户的userAccountControl 属性上设置此标志
AD_USERCTRL_ACCOUNT_TRUSTED_FOR_DELEGATION = 0x80000

# NOT_DELEGATED - 设置此标志后，即使将服务帐户设置为信任其进行 Kerberos 委派，也不会将用户的安全上下文委派给该服务
AD_USERCTRL_ACCOUNT_NOT_DELEGATED = 0x100000

# USE_DES_KEY_ONLY - (Windows 2000/Windows Server 2003) 将此用户限制为仅使用数据加密标准 (DES) 加密类型的密钥
AD_USERCTRL_ACCOUNT_USE_DES_KEY_ONLY = 0x200000

# DONT_REQ_PREAUTH - (Windows 2000/Windows Server 2003) 此帐户在登录时不需要进行 Kerberos 预先验证
AD_USERCTRL_ACCOUNT_DONT_REQ_PREAUTH = 0x400000

# PASSWORD_EXPIRED - (Windows 2000/Windows Server 2003) 用户的密码已过期
AD_USERCTRL_ACCOUNT_PASSWORD_EXPIRED = 0x800000

# TRUSTED_TO_AUTH_FOR_DELEGATION - (Windows 2000/Windows Server 2003) 允许该帐户进行委派。这是一个与安全相关的设置。应严格控制启用此选项的帐户。
# 此设置允许该帐户运行的服务冒充客户端的身份，并作为该用户接受网络上其他远程服务器的身份验证
AD_USERCTRL_ACCOUNT_TRUSTED_TO_AUTH_FOR_DELEGATION = 0x1000000
