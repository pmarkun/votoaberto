from lxml.html import parse, fromstring
import re
import json

base = "http://www.cmf.sc.gov.br"
soup = parse("http://www.cmf.sc.gov.br/vereadores").getroot()

vereadores = []
for v in soup.xpath("//tr/td[@valign='top'][@colspan='2']"):
	vereador = {}
	try:
		vereador['img'] = base + v.xpath(".//img")[0].get("src")
	except:
		vereador['img'] = ''
	try:
		vereador['nome'] = v.xpath(".//strong")[0].text.strip("Vereador:").strip()
	except:
		vereador['nome'] = v.xpath(".//strong/img")[0].tail.strip("Vereador:").strip()
	try:
		vereador['partido'] = v.xpath(".//strong")[0].tail.strip("Partido:").strip()
	except:
		vereador['partido'] = '??'
	vereador['email'] = fromstring(re.search(".*addy[0-9]* \= '(.*)' +", v.xpath(".//script")[0].text).group(1)).text + "@cmf.sc.gov.br"
	vereador['id'] = vereador['email'].split('@')[0]
	try:
		vereador['bio'] = v.xpath(".//p")[1].text
	except:
		vereador['bio'] = ''
	vereador['votacoes'] = {}
	vereadores.append(vereador)
 
zapt = open("vereadores-floripa.json", "w")
zapt.write(json.dumps(vereadores, sort_keys=True, indent=4, separators=(',', ': ')))
zapt.close()