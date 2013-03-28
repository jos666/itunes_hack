#encoding=utf-8
import urllib2
import httplib
import urllib
import cookielib
import urllib2
import socket
import json
import ssl
from xml.dom.minidom import parseString
import time
from sgmllib import SGMLParser
import re


timeout = 40
socket.setdefaulttimeout(timeout)
sleep_download_time=  10
time.sleep(sleep_download_time)

def link_server(host):
    """ link server
    
    Args:
        host: host name 
    
    Returns:
        None
    """
    try:
        httpClient = httplib.HTTPSConnection(host, 443, timeout = 60)
    except Exception, e:
        print e
    
def request_server(httpClient, url, body, headers, method):
    """ request server
        
        Args:
            httpClien : HTTPSConnection
            url       : a str indicating host_url
            body      : a str indicating send content
            headers   : a dict object
            return    : a response object indicating response from server
        
        Return:
            response: reponse object
        
    """
    try:
        httpClient.request(method, url, body, headers)
    except Exception, e:
        print e
    return httpClient.getresponse()
    
def auth_check(response, hostName, isServerRight, isLoginSuccess):
    """ check whether login is successful
    
        when server responses the right xml file, it indicates the successful login operation
        
        Args:
            response: response objects saving the data from server and other params
            hostNmae: a str indicatinghost name
            isServerRight: a boolean data indicating whether host name is right for this id to login
            isLoginSuccess: a boolean data indicating whetheh login is successful
        
        Return:
            hostNmae: a str indicatinghost name
            isServerRight: a boolean data indicating whether host name is right for this id to login
            isLoginSuccess: a boolean data indicating whetheh login is successful
        
        Raise:
            None
            
    """
    resp_content = response.read()
    xml_obj = parseString(resp_content)
    login_info = xml_obj.getElementsByTagName('key')
    value = login_info[0].childNodes[0].data
    #login the wrong server, turn to the right one
    if cmp(value, "appleId") == 0:
        location = response.getheader("location")
        #location:https://p*-buy.itunes.apple.com//WebObjects/MZFinance.woa/wa/authenticat?Pod=59&PRH=59
        hostName = location.split('/')[2]
        print 'linking to the correct server:', location.split('/')[2]
        isServerRight = False
    #login failed
    elif cmp(value, "accountInfo") != 0:
        fail_info = xml_obj.getElementsByTagName('string')[1].childNodes[0].data
        print fail_info
    #login success
    else:
        isLoginSuccess = True
    file = open("login_file.xml", "w")
    file.write(resp_content)
    file.close()
    return isLoginSuccess, isServerRight, hostName

def get_user_information(response, appleId):
    """ get user information
        
        Args:
            response: response objects saving the data from server and other params
            appleId: a int indicating the login id
        
        Return:
            cookie: a str indicating cookies
            token:  a str indicating token
            id: a int indicating id
        
        Raise:
            XML Exception
            
    """
    m_cookie = response.getheader("Set-Cookie")
    content = open("login_file.xml").read()
    try:
        xmldoc = parseString(content)
    except Exception, e:
        print e
    document_list = xmldoc.getElementsByTagName('string')
    token = document_list[4].childNodes[0].data
    personId = document_list[6].childNodes[0].data
    #print person information
    print '***********************************************************'
    print '    appleId: ',appleId
    print '   personId: ',personId
    print 'accountKind: ',document_list[1].childNodes[0].data
    print '  firstName: ',document_list[2].childNodes[0].data
    print '   lastName: ',document_list[3].childNodes[0].data
    print '************************************************************'
    return m_cookie, token, personId

def get_app_information(response):
    """ get app information
        
        Args:
            response: response objects saving the data from server and other params
        Return:
            None
    
    """
    app_json = json.loads(response.read())
    print '************************************************************'
    print 'name                 version               style            '
    print '------------------------------------------------------------'
    for app_item in app_json:
        name = app_item['name']
        version = app_item['versionString']
        style = app_item['genreName']
        print name, '\t', version, '\t', style
        print '------------------------------------------------------------'

def parse_json(response):
    """ parse json data
        
        parse json data from response
        Args:
            response: response objects saving the data from server and other params
        Return:
            ids: a string contains all the id of app
        Raise:
            json load Exception
    """
    try:
        #json_data is a dict which just like:{'Apps":{'id1',n1,'id2':n2,...}}
        json_data = json.loads(response.read())
        #app_item is app id
        ids = ','.join(app_item for app_item in json_data['Apps'])
    except Exception, e:
        print e
    return ids

def itunes_body():
    """ itunes logining main framework
        
        the main framework contains the following steps:
            1 login and get the cookie
            2 get the list(you need to send cookies and other params to server)
            3 get the information of the app(by the id of app)
            
        Args:
            none
        
        Returns:
            None
        
        Raise:
            some Exception
    """
    
    isLoginSuccess, isServerRight = False, True
    appleId, passWord, response = "", "", None
    print time.time()
    print 'login itunes page'
    print 'please input your apple id and password:'    
    #set initialise host name
    hostName = "p72-buy.itunes.apple.com"
    """ begin login """
    while isLoginSuccess == False:
        #linking the right server
        if isServerRight:
            appleId = raw_input("  id:")
            password = raw_input(" psw:")
        print 'please wait, logining ... ... ...'
        httpClient = httplib.HTTPSConnection(hostName, 443, timeout = 60)
        print 'connect server ok'
        #constrct the body and headers
        body = "<?xml version='1.0' encoding='utf-8'?><plist version='1.0'><dict><key>appleId</key><string>"
        body = body + appleId + "</string><key>attempt</key><integer>1</integer><key>createsession</key><string>true</string><key>guid</key><string>e50bd206.f858d3c7.44653f9a.a031c3f4.d8d0088e.9a65dbc9.fe8350c4</string><key>machinename</key><string>KYMO-PSC</string><key>password</key><string>"
        body = body + password + "</string><key>why</key><string>signIn</string></dict></plist>"
        headers = {
                "User-Agent":"iTunes/11.0.2 (Windows; Microsoft Windows 7 Ultimate Edition (Build 7600)) AppleWebKit/536.27.1"
            }
        response = request_server(httpClient, "/WebObjects/MZFinance.woa/wa/authenticate", body, headers, "POST")
        print 'request server ok'
        isLoginSuccess, isServerRight, hostName = auth_check(response, hostName, isServerRight, isLoginSuccess)
    """ end login """
    #begin getting user information and some params
    m_cookie, token, personId = get_user_information(response, appleId)
    #end 
    """ get app list """
    req_body = "action=POST&mt=8&vt=lockerData&restoreMode=undefined"
    head = {"User-Agent":"iTunes/11.0.2 (Windows; Microsoft Windows 7 Ultimate Edition (Build 7600)) AppleWebKit/536.27.1",
        "X-Token":token,
        "Accept-Language":"zh-cn, zh;q=0.75, en-us;q=0.50, en;q=0.25",
        "Content-Type":"application/x-www-form-urlencoded",
        "Cookie":m_cookie,
        "Host":"se.itunes.apple.com",
        "X-Dsid":str(personId)
        }
    
    purchaseClient = httplib.HTTPSConnection("se.itunes.apple.com", 443, timeout = 60)
    purchaseResponse = request_server(purchaseClient, "/WebObjects/MZStoreElements.woa/wa/purchases?cc=cn", req_body, head, "POST")
    ids = parse_json(purchaseResponse)
    #if app list exists
    if ids:
        qurDict = {
            'action': 'POST',
            'contentIds': ids,
            'pillId': 0,
            'mt': 8,
            'sortValue': 4,
            'vt': "contentData",
            'restoreMode': "undefined"
        }
        qurBody = urllib.urlencode(qurDict)
        appClient = httplib.HTTPSConnection("se.itunes.apple.com", 443, timeout = 60)
        appResponse = request_server(appClient, "/WebObjects/MZStoreElements.woa/wa/purchases?cc=cn", qurBody, head, "POST")
        get_app_information(appResponse)
        
    else:
        print "you haven't  buy any app !"
    
    """ end getting app list """
    
    """ begin purchases """
    newHead = {
        "Host"       : "itunes.apple.com",
        "User-Agent" : "iTunes/11.0.2 (Windows; Microsoft Windows 7 Ultimate Edition (Build 7600)) AppleWebKit/536.27.1",
        "Accept"     : "*/*",
        "X-Token"    : token,
        "Accept-Language" : "zh-cn, zh;q=0.75, en-us;q=0.50, en;q=0.25",
        "Cookie"    : m_cookie,
        "X-Dsid"     :  personId,
        }
   
    
    #get the appExtVrsId and salamedId
    cookie_support = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
    opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
    urllib2.install_opener(opener)
    opener.addheaders = [("User-Agent","iTunes/11.0.2 (Windows; Microsoft Windows 7 Ultimate Edition (Build 7600)) AppleWebKit/536.27.1")]
    try:
        res = opener.open("https://itunes.apple.com/cn/app/sha-shou-jiang-shi-zhi-cheng2/id533044969?mt=8")
        st = res.read()
        pattern = re.findall(r'productType.*appExtVrsId=\d*', st)
        content = pattern[0].split('&')
        #dicts save the appExtVrsId,salableAdamId and so on
        dicts = dict([(item.split('=')[0], item.split('=')[1]) for item in content]) 
    except Exception,e:
        print e
    
    """
    body = '''<?xml version="1.0" encoding="UTF-8"?>
    <plist version="1.0">
    <dict>
    <key>appExtVrsId</key>
	<string>''' + dicts['appExtVrsId'] + '''</string>
	<key>guid</key>
	<string>E50BD206.F858D3C7.44653F9A.A031C3F4.D8D0088E.9A65DBC9.FE8350C4</string>
	<key>kbsync</key>
	<data>''' + 'kbsync' + '''
	</data>
	<key>machineName</key>
	<string>KYMO-PC</string>
	<key>needDiv</key>
	<string>0</string>
	<key>origPage</key>
	<string>Software-CN-Electronic Arts-Yogify-580676053</string>
	<key>origPage2</key>
	<string>Genre-CN-Mobile Software Applications-29099</string>
	<key>origPageCh</key>
	<string>Software Pages</string>
	<key>origPageCh2</key>
	<string>Mobile Software Applications-main</string>
	<key>origPageLocation</key>
	<string>Buy</string>
	<key>origPageLocation2</key>
	<string>Tab_iphone1|Swoosh_1|Lockup_16</string>
	<key>price</key>
	<string>'''+dicts['price'] + '''</string>
	<key>pricingParameters</key>
	<string>''' + dicts['pricingParameters'] + '''</string>
	<key>productType</key>
	<string>''' + dicts['productType'] + '''</string>
	<key>salableAdamId</key>
	<string>''' + dicts['salableAdamId'] + '''</string>
    </dict>
    '''
    
    print body
    httpClient = httplib.HTTPSConnection(hostName, 443, timeout = 30)
    st = httpClient.request("POST", "/WebObjects/MZBuy.woa/wa/buyProduct",body,head)
    """
    
    """end purchase """
    
    print 'logout ?'
    print '1 yes 2 no'
    ans = int(raw_input())
    if ans == 1:
        httpClient = httplib.HTTPSConnection(hostName, 443, timeout = 30)
        st = httpClient.request("GET", "/WebObjects/MZFinance.woa/wa/logoutWithSignOutKey"," ",headers)
        resp = httpClient.getresponse()
        print resp.read()
        print 'logout success'

if __name__ == '__main__':
    itunes_body()
