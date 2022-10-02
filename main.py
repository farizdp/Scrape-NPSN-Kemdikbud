import requests, unicodedata, re, csv
from bs4 import BeautifulSoup
from html_table_parser.parser import HTMLTableParser

def link(url):
    web = requests.get(url)
    soup = BeautifulSoup(web.text, 'lxml')
    table = soup.find('table', id="box-table-a")
    if table is None:
        table = soup.find('table', id="example")
        link = table.findAll('a')
        links = [unicodedata.normalize("NFKD", x.text).strip() for x in link]
    else:
        link = table.findAll('a')
        links = ['https://referensi.data.kemdikbud.go.id/' + i['href'] for i in link if 'kode' in i['href']]
    return links

def detail_sekolah(id, prov, kota, kec):
    url = 'https://referensi.data.kemdikbud.go.id/tabs.php?npsn=' + id
    page = requests.get(url)
    s = BeautifulSoup(page.text, 'lxml')
    p1, p2 = HTMLTableParser(), HTMLTableParser() 
    p1.feed(str(s.find('div', id="tabs-1")))
    p2.feed(str(s.find('div', id="tabs-2")))
    script = s.select_one("script:contains('map')")
    [latitude, longitude] = re.search('L.marker\(\[(.+?)\]\).addTo', str(script)).group(1).split(",")
    detail = [p1.tables[0][1][3],
                p1.tables[0][0][3],
                p1.tables[0][8][3].replace("Prov. ", ""),
                re.search('kode=(.+?)&level', str(prov)).group(1),
                p1.tables[0][7][3].replace("Kab. ", ""),
                re.search('kode=(.+?)&level', str(kota)).group(1),
                p1.tables[0][6][3].replace("Kec. ", ""),
                re.search('kode=(.+?)&level', str(kec)).group(1),
                p1.tables[0][5][3],
                p1.tables[0][2][3],
                p1.tables[0][9][3],
                p1.tables[0][13][3],
                p2.tables[1][0][3],
                p2.tables[1][1][3],
                p2.tables[1][2][3],
                p2.tables[1][4][3],
                p2.tables[1][5][3],
                p2.tables[1][6][3],
                p2.tables[1][11][3],
                p2.tables[1][12][3],
                p2.tables[1][9][3],
                p2.tables[1][14][3],
                latitude,
                longitude]
    return detail

header = ["NPSN",
            "Sekolah",
            "Provinsi",
            "Kode Provinsi",
            "Kabupaten",
            "Kode Kabupaten",
            "Kecamatan",
            "Kode Kecamatan",
            "Kelurahan",
            "Alamat",
            "Status",
            "Jenjang",
            "Naungan",
            "SK Pendirian",
            "Tgl SK Pendirian",
            "SK Operasional",
            "Tgl Mulai SK Operasional",
            "Tgl Akhir SK Operasional",
            "SK Akreditasi",
            "Tgl SK Akreditasi",
            "Akreditasi",
            "SK ISO",
            "Latitude",
            "Longitude"]

referensi = ['https://referensi.data.kemdikbud.go.id/index11.php'
            ,'https://referensi.data.kemdikbud.go.id/index21.php'
            ,'https://referensi.data.kemdikbud.go.id/index31.php'
            ,'https://referensi.data.kemdikbud.go.id/index41.php'
            ,'https://referensi.data.kemdikbud.go.id/index51.php']

with open('npsn.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='|', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    for ref in referensi:
        for prov in link(ref):
            for kota in link(prov):
                for kec in link(kota):
                    for id in link(kec):
                        writer.writerow(detail_sekolah(id, prov, kota, kec))