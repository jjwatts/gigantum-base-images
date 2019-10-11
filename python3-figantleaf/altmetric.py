import requests
from hashlib import sha1
import hmac
import configparser
from urllib.parse import urlencode, quote_plus
import twitter

altproperties_location="/home/giguser/.dimensions/dsl.ini"
api_url = "https://www.altmetric.com/explorer/api/"

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            #if dict1[option] == -1:
                #print ("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

Config = configparser.ConfigParser()
Config.read(altproperties_location)

aprops = ConfigSectionMap("altmetric")
secret=aprops['secret']
key=aprops['key']


def altmetric_auth(secret,filters):
    my_hmac = hmac.new(bytes(secret, 'UTF-8'), bytes(filters, 'UTF-8'), sha1)
    digest = my_hmac.hexdigest()
    return digest

def querystrings(afilter,base='filter'):
    digeststring = []
    urlstring = []
    for k in sorted(list(afilter.keys())):

        if type(afilter[k]) == str:
            urlstring.append("{}[{}]={}".format(base,k,afilter[k]))
            digeststring.append("{}|{}".format(k,afilter[k]))
        if type(afilter[k]) == list:
            digeststring.append("{}|{}".format(k,"|".join(sorted(afilter[k]))))
            for i in afilter[k]:
                urlstring.append("{}[{}][]={}".format(base,k,i))

    return dict(
                digest="|".join(digeststring),
                url="&".join(urlstring).replace('[','%5B').replace(']','%5D')
               )

def init_altmetric_query(afilter,endpoint, api_url=api_url, page=None):
    urlpage = ""
    if page is not None:
        urlpage = querystrings(page,base='page')['url']
        
    query = "{}{}/?digest={}&{}&key={}&{}".format(api_url,
                                endpoint,
                                altmetric_auth(secret,querystrings(afilter)['digest']),
                                querystrings(afilter)['url'],
                                key,
                                urlpage)
    
    #print(query)
    
    return requests.get(query)

# twitter
tprops = ConfigSectionMap("twitter")

consumer_key=tprops['consumer_key']
consumer_secret=tprops['consumer_secret']
access_token_key=tprops['access_token_key']
access_token_secret=tprops['access_token_secret']

twitterapi = twitter.Api(consumer_key=consumer_key,
                  consumer_secret=consumer_secret,
                  access_token_key=access_token_key,
                  access_token_secret=access_token_secret)
    






