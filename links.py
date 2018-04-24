import re, sys, numpy as np
import urllib.request,urllib.parse
from pprint import pprint
from urllib.error import URLError, HTTPError

#RETRIEVE LINKS.
def get_payload(url):
    try:
        req = urllib.request.Request(url,headers={'User-Agent' : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0)" })
        payload = urllib.request.urlopen(req).read()
        return payload
    except HTTPError as e:
        print('Error code: ', e.code, 'could not access: ',address)
        progress.failed+=1
        progress.flinks.append(url)
        return []
    except URLError as e:
        print('Reason: ', e.reason, 'could not access: ',address)
        progress.failed+=1
        progress.flinks.append(url)
        return []

#EXTRACT URLS
def extract_urls(base,payload):
    links = re.findall('(src)|(action)|(href)="([^"]*)', str(payload))
    if links == []:
        return []
    links = np.asarray(links)[:,3]
    #some sanitization
    links = links[~(links=='')]
   # import ipdb; ipdb.set_trace()
    #complete relative and anchor links
    for u in range(0,len(links)):
        if(links[u].startswith('#')):
            links[u] = base+links[u]
        else:
            links[u]= urllib.parse.urljoin(base,links[u])# works fine for two http links
    links = np.asarray([str(link) for link in links if link[:].startswith('http')])
    return links.reshape((len(links),1))


################################################################################
address = "http://www.enfieldonline.net/public-transport"
################################################################################
#Keep track of success rate
class progress:
    failed = 0
    flinks = []

payload_origin = get_payload(address)
if(payload_origin==[]):
    print("The primary site may contain no links OR an error has occurred")
    sys.exit()

urls = extract_urls(address,payload_origin)

print(address,end='\n\t')
pprint(urls)

for u in range(0,len(urls)):
    print('\n\n', urls[u][0])
    sub_payload = get_payload(urls[u][0])
    sublinks = extract_urls(urls[u][0],sub_payload)
    pprint(sublinks)
