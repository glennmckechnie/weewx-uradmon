# scrape http://93.202.138.90:8080/

import requests
res = requests.get('http://93.202.138.90:8080/')
print(res.text)

print(res.status_code)
exit()

from bs4 import BeautifulSoup
page = requests.get('http://93.202.138.90:8080/')
soup = BeautifulSoup(page.content, 'html.parser')
print(soup.prettify())


all_td_tags = []
for element in soup.select('td'):
    all_td_tags.append(element.text)
print(all_td_tags)

second_td_text = soup.select('td')[1].text
print(second_td_text)

second_t_text = soup.select('td')[1].contents


"""
>>> second_t_text = soup.select('td')[1].text
>>> print(second_t_text)
S1 ZE03-O3 :0.165ppmS2 ZE03-NO2:0.103ppmS3 ZE03-SO2:0.006ppmS4 ZE03-CO :0.940ppm
>>> second_t_contents = soup.select('td')[1].contents
>>> print(second_t_contents)
[<b>S1 ZE03-O3 :</b>, '0.165ppm', <br/>, <b>S2 ZE03-NO2:</b>, '0.103ppm', <br/>, <b>S3 ZE03-SO2:</b>, '0.006ppm', <br/>, <b>S4 ZE03-CO :</b>, '0.940ppm']
"""
print(second_t_text[0])
print(second_t_text[1])
print(second_t_text[2])
print(second_t_text[3])

"""
>>> print(second_t_text[0],second_t_text[3],second_t_text[6],second_t_text[9])
<b>S1 ZE03-O3 :</b> <b>S2 ZE03-NO2:</b> <b>S3 ZE03-SO2:</b> <b>S4 ZE03-CO :</b>
>>>
"""

for element in soup.select('b'):
    all_b_tags.append(element.text)

print(all_b_tags)
OR
second_t_text = soup.select('td')[1].text
print(second_t_text)

# -------------------

for element in soup.select('b'):
    if "ZE" in element:
        print(element)
    else:
        print("not in %s" % element.text)

not in Temperature:
not in Pressure:
not in Humidity:
not in VOC:
not in S1 ZE03-O3 :
not in S2 ZE03-NO2:
not in S3 ZE03-SO2:
not in S4 ZE03-CO :
not in PM1.0:
not in PM2.5:
not in PM10:
not in Noise:
not in Warmup:
not in Time:
not in WDT:
not in Autoreboot:
not in USB:
not in WiFi:
not in IP:
not in Interval:
not in HTTP:
not in Stats:
not in Disable AP:

# -------------------

for element in soup.select('b'):
    ZET=str(element)
    ZE="ZE03"
    if ZE in ZET:
        print("found %s in %s" % (ZE, ZET))

found ZE03 in <b>S1 ZE03-O3 :</b>
found ZE03 in <b>S2 ZE03-NO2:</b>
found ZE03 in <b>S3 ZE03-SO2:</b>
found ZE03 in <b>S4 ZE03-CO :</b>
>>>

>>> for element in soup.select('b'):
    ZET=str(element.text)
    ZE="ZE03"
    if ZE in ZET:
        print("found %s in %s" % (ZE, ZET))

found ZE03 in S1 ZE03-O3 :
found ZE03 in S2 ZE03-NO2:
found ZE03 in S3 ZE03-SO2:
found ZE03 in S4 ZE03-CO :



for element in soup.select('b'):
    ZET=str(element.text)
    ZE="ZE03"
    if ZE in ZET:
        ZET=ZET.replace(':','')
        ZET=ZET.strip()
        print("found %s in %s" % (ZE, ZET))

found ZE03 in S1 ZE03-O3
found ZE03 in S2 ZE03-NO2
found ZE03 in S3 ZE03-SO2
found ZE03 in S4 ZE03-CO


for element in soup.select('b'):
    ZET=str(element.text)
    ZE="ZE03"
    if ZE in ZET:
        ZET=ZET.replace(':','')
        ZET=ZET.replace('-','')
        ZET=ZET.strip()
        print("found %s in %s" % (ZE, ZET))

found ZE03 in S1 ZE03O3
found ZE03 in S2 ZE03NO2
found ZE03 in S3 ZE03SO2
found ZE03 in S4 ZE03CO


for element in soup.select('b'):
    ZET=str(element.text)
    ZE="ZE03"
    if ZE in ZET:
        ZET=ZET.replace(':','')
        ZET=ZET.replace('-','')
        ZET=ZET.strip()
        print("found %s in %s" % (ZE, ZET))
        NZET=ZET.split()
        print("New ZET is %s" % (NZET))

found ZE03 in S1 ZE03O3
New ZET is ['S1', 'ZE03O3']
found ZE03 in S2 ZE03NO2
New ZET is ['S2', 'ZE03NO2']
found ZE03 in S3 ZE03SO2
New ZET is ['S3', 'ZE03SO2']
found ZE03 in S4 ZE03CO
New ZET is ['S4', 'ZE03CO']



*******************

ZET_map = []
for element in soup.select('b'):
    ZET=str(element.text)
    ZE="ZE03"
    if ZE in ZET:
        ZET=ZET.replace(':','')
        ZET=ZET.replace('-','')
        NZET=ZET.split()
        print("found %s in %s" % (ZE, ZET))
        NZET=ZET.split()
        print("New ZET is %s" % (NZET))
        ZET_map.append(NZET)
        print("ZET_Map is now %s" % ZET_map)

found ZE03 in S1 ZE03O3
New ZET is ['S1', 'ZE03O3']
ZET_Map is now [['S1', 'ZE03O3']]
found ZE03 in S2 ZE03NO2
New ZET is ['S2', 'ZE03NO2']
ZET_Map is now [['S1', 'ZE03O3'], ['S2', 'ZE03NO2']]
found ZE03 in S3 ZE03SO2
New ZET is ['S3', 'ZE03SO2']
ZET_Map is now [['S1', 'ZE03O3'], ['S2', 'ZE03NO2'], ['S3', 'ZE03SO2']]
found ZE03 in S4 ZE03CO
New ZET is ['S4', 'ZE03CO']
ZET_Map is now [['S1', 'ZE03O3'], ['S2', 'ZE03NO2'], ['S3', 'ZE03SO2'], ['S4', 'ZE03CO']]


type(ZET_map)
<class 'list'>

*******************

