from scrapy import Spider
from scrapy.spider  import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
import logging
import re
from crawlpat.items import CrawlpatItem
from scrapy.http import FormRequest
from scrapy.http.request import Request
from scrapy_redis.spiders import RedisSpider

data = {
    "Sect1": "PTO2",
    "Sect2": "HITOFF",
    "u": "/netahtml/PTO/search-adv.htm",
    "r": "0",
    "p": "1",
    "f": "S",
    "l": "50",
    "d": "PTXT",
    "Query": "Graphene",
}
class PatentSpider(RedisSpider):
    logging.info("start")
    name = "patSpider"
    allowed_domains = ['patft.uspto.gov']
    #start_urls =['http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=351&f=G&l=50&d=PTXT&s1=graphene&p=8&OS=graphene&RS=graphene']
    '''
    start_urls = ['http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=1&p=1&f=G&l=50&d=PTXT&S1=graphene&OS=graphene&RS=graphene']

    start_urls = ['http://tech.163.com/']
    # f = open("out.txt", "w")
    rules=(
        Rule(LinkExtractor(allow=r"/14/08\d+/\d+/*"),
        callback="parsePat",follow=True),
    )



    start_urls = [
        "http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=35&p=1&f=G&l=50&d=PTXT&S1=Graphene&OS=Graphene&RS=Graphene",]
    rules =(
            Rule(
                 LinkExtractor=(allow = ('')),
                 callback = "parse_item",
                 follow =True
                  )
            )
    '''
    start_urls = ["http://patft.uspto.gov/netahtml/PTO/search-adv.htm"]

    def parse(self, response):
        return FormRequest.from_response(
                            response,
                            formdata=data,
                            method="GET",
                            callback=self.search_result
                            )

    def search_result(self, response):
        print "response url " + response.url
        print "response status " + str(response.status)
        print "response headers " + str(response.headers)
        # print "response body "+str(response.body)
        totalitem = response.xpath("/html/body/i/strong[3]/text()").extract();
        page = int(totalitem[0]) / 50
        # page = (page if int(totalitem[0])%50 ==0 else page+1)
        count = 1
        newnum = 0
        while (count < 500):
            page = int(count) / 50 + 1
            print 't ' + str(count)
            print 'page ' + str(page)
            next_url = "http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=/netahtml/PTO/search-adv.htm?&r=" + str(count) + "&f=G&l=50&d=PTXT&s1=" + data["Query"] + "&p=" + str(page) + "&OS=" + data["Query"] + "&RS=" + data["Query"]
            print next_url
            count = count + 1
            yield Request(url=next_url, callback=self.parseurl)
            '''while(count == 500 and newnum < 1000):
                new_url = refurl[newnum]
                newnum = newnum + 1
                print new_url
                yield Request(url=new_url, callback=self.parse_item)'''

    def parseurl(self, response):
        urls = []
        for tr in response.xpath('/html/body/table[2]/tr[1]'):
            patent_no = tr.xpath('td[2]/b/text()').extract()
            if (patent_no):
                sturl = 'http://patft.uspto.gov/netacgi/nph-Parser?Sect2=PTO1&Sect2=HITOFF&p=1&u=%2Fnetahtml%2FPTO%2Fsearch-bool.html&r=1&f=G&l=50&d=PALL&RefSrch=yes&Query=PN%2F'+str(patent_no[0].replace(',', ''))
        urls.append(sturl)
        body = str(response.body)
        start_idx = body.find('<b>U.S. Patent Documents</b>')
        a = start_idx
        if (str(a) == '-1'):
            print 'No refurl in this page'
        else:
            b = a
            while (body[b:b + 4] != '<HR>'):
                b = b + 1
            end_idx = b
            slam = body[start_idx:end_idx]
            pattern = re.compile(r"<a href=\"(/.*?)\">(.*?)</a>")
            reu = re.findall(pattern, slam)
            for i in reu:
                urls.append('http://patft.uspto.gov' + i[0])
        l = len(urls)
        i = 0
        if l > 2:
            l = 2
        while (i < l):
            if (i == 0):
                print 'YES ,get it'
                yield Request(url=str(urls[i]), callback=self.parse1_item)
            else:
                yield Request(url=str(urls[i]), callback=self.parse2_item)
            i += 1

    def parse1_item(self, response):
        print "response url " + response.url
        print "response status " + str(response.status)
        print "response headers " + str(response.headers)
        # print "response body "+str(response.body)
        item = CrawlpatItem()
        item['patent_url'] = str(response.url)
        item['patent_keyword'] = str(data["Query"])
        self.get_main_table(response, item)
        self.get_patent_no(response, item)
        self.get_title(response, item)
        self.get_patent_abstract(response, item)
        self.get_patent_claims(response, item)
        self.get_patent_description(response, item)
        self.get_patent_references(response, item)
        self.get_patent_date(response, item)
        self.get_patent_otherref(response, item)
        self.get_patent_refurl(response, item)
        return item

    def parse2_item(self, response):
        print "response url " + response.url
        print "response status " + str(response.status)
        print "response headers " + str(response.headers)
        # print "response body "+str(response.body)
        item = CrawlpatItem()
        item['patent_url'] = str(response.url)
        item['patent_keyword'] = str('Be referred,'+data["Query"])
        self.get_main_table(response, item)
        self.get_patent_no(response, item)
        self.get_title(response, item)
        self.get_patent_abstract(response, item)
        self.get_patent_claims(response, item)
        self.get_patent_description(response, item)
        self.get_patent_references(response, item)
        self.get_patent_date(response, item)
        self.get_patent_otherref(response, item)
        return item

    def get_title(self,response, item):
        #title = response.xpath("/html/body/font[1]/text()").extract();
        title = response.xpath("/html/body/font").extract()
        title = str(title)[19:-9]
        m_patten = re.compile('<(b|\/b|i|\/i)>')
        title = re.sub(m_patten, "", title)
        if(title):
            print title
            item['patent_title'] = title.replace("\\n", "").strip()
            print "title "+str(item['patent_title'])
        else:
            item['patent_title'] = ' '
        return item

    def get_patent_no(self, response, item):
        for tr in response.xpath('/html/body/table[2]/tr[1]'):
            patent_no = tr.xpath('td[2]/b/text()').extract();
            if(patent_no):
                print "patent_no "+str(patent_no)
                item['patent_no'] = patent_no[0].replace(',', '')
            else:
                item['patent_no']=' '
            return item

    def get_patent_date(self, response, item):
        patent_date = response.xpath('/html/body/table[2]/tr[2]/td[2]/b/text()').extract()
        if(patent_date):
            print'patent_date'+str(patent_date)
            item['patent_date'] = str(patent_date[0]).strip()
        else:
            item['patent_date'] = ''
        return item

    def get_main_table(self, response, item):
        table1 = response.xpath('/html/body/table[3]/tr')
        if(len(table1)<2):
            table1 = response.xpath('/html/body/table[4]/tr')
        for tr in table1:
            print str(tr.xpath('th/text()').extract())
            name = str(tr.xpath('th/text()').extract()[0]).replace("\n","").strip()
            print name
            if(name=='Inventors:'):
                self.get_patent_inventors(response, item, tr)
            elif(name=='Applicant:'):
                self.get_patent_applicent(response, item, tr)
            elif(name=='Family ID:'):
                self.get_patent_familyId(response, item, tr)
            elif(name=='Appl. No.:'):
                self.get_patent_applyNo(response, item, tr)
            elif(name=='Filed:'):
                self.get_patent_fieldDate(response, item, tr)
            elif(name=='Assignee:'):
                self.get_patent_assignee(response, item, tr)

    def get_patent_abstract(self,response,item):
        abstract = response.xpath('/html/body/p').extract()
        m_patten = re.compile('<(b|\/b|i|\/i|p|\/p)>')
        abstract = re.sub(m_patten,"",str(abstract))
        if abstract:
            abstract = abstract.replace("\\n","").replace('[u\'', '').replace('\', u\' \']', '')
            print "abstract "+str(abstract)
            item['patent_abstract'] = abstract
        else:
            item['patent_abstract'] = ' '
        return item

    def get_patent_inventors(self,response,item,obj):
        #inventor_str = response.xpath('/html/body/table[3]/tr[1]/td').extract()
        inventor_str = obj.xpath('td').extract()
        inventor_str = str(inventor_str)[35:-8]
        inventor_str = inventor_str.replace('<b>,', '*')
        m_patten = re.compile('<(b|\/b)>')
        inventor_str = re.sub(m_patten,"",inventor_str)
        inventlist = inventor_str.split('*')
        if(inventlist):
            item['patent_inventors'] = inventlist
            print str(item['patent_inventors'])
        return item

    def get_patent_applicent(self,response,item,obj):
        patent_applicant_Name = []
        count = 0
        if obj.xpath('td/table/tr[2]/td'):
            for td in obj.xpath('td/table/tr[2]/td'):
                temp = []
                if(td.xpath("b/text()").extract()):
                    for name in td.xpath("b/text()").extract():
                        name = name.replace("\n", "")
                        if name != ' ':
                            patent_applicant_Name.append(name)
                    item['patent_applicant_Name'] = patent_applicant_Name
                    print str(item['patent_applicant_Name'])
                else:
                    for t in td.xpath("text()").extract():
                        t = t.replace("\n", "")
                        if t != ' ':
                            temp.append(t)
                if(count==1):
                    item['patent_applicant_City'] = temp
                elif(count==2):
                    item['patent_applicant_State'] = temp
                elif(count==3):
                    item['patent_applicant_Country'] = temp
                count = count+1
        return item

    def get_patent_assignee(self,response,item,obj):
        #assignee = response.xpath('/html/body/table[3]/tr[3]/td').extract()
        assignee = obj.xpath('td').extract()
        assignee = str(assignee)[36:-8]
        m_patten = re.compile('<(b|\/b)>')
        assign = re.sub(m_patten,"",assignee)
        assign = assign.replace("\\n", '').replace("\\", '')
        assigneelist = assign.split("<br>")
        if assigneelist:
            item['patent_assignee'] = assigneelist
            print str(item['patent_assignee'])
            return item


    def get_patent_familyId(self,response,item,obj):
        patent_familyId=obj.xpath('td/b/text()').extract()
        #patent_familyId = response.xpath('/html/body/table[3]/tr[4]/td/b/text()').extract()
        patent_familyId = patent_familyId[0].replace('\n','')
        if(patent_familyId):
            item['patent_familyId'] = patent_familyId
            
        else:
            item['patent_familyId'] = " "
        return item

    def get_patent_applyNo(self,response,item,obj):
        #patent_applyNo = response.xpath('/html/body/table[3]/tr[5]/td/b/text()').extract()
        patent_applyNo = obj.xpath('td/b/text()').extract()
        if(patent_applyNo):
            item['patent_applyNo'] = patent_applyNo[0]
        return item

    def get_patent_fieldDate(self,response,item,obj):
        #patent_fieldDate =  response.xpath('/html/body/table[3]/tr[6]/td/b/text()').extract()
        patent_fieldDate =  obj.xpath('td/b/text()').extract()
        if(patent_fieldDate):
            item['patent_fieldDate'] = patent_fieldDate[0]
            print str(item['patent_fieldDate'])
        else:
            item['patent_fieldDate'] = ' '
        return item

    def get_patent_claims(self,response,item):
        body = str(response.body)
        start_idx = body.find('<CENTER><b><i>Claims</b></i></CENTER>');
        end_idx = body.find('<CENTER><b><i>Description</b></i></CENTER>')
        claim = body[start_idx+37:end_idx].replace('<BR>', '').replace('<HR>', '')
        if claim:
            item['patent_claims'] = claim
        else:
            item['patent_claims'] = ''
        return item
                  
    def get_patent_description(self,response,item):
        body = str(response.body)
        start_idx = body.find('<CENTER><b><i>Description</b></i></CENTER>');
        end_idx = body.find('<CENTER><b>* * * * *</b></CENTER>')
        description = body[start_idx+42:end_idx].replace('<BR>', '').replace('<HR>', '')
        if description:
            item['patent_description'] = description
        else:
            item['patent_description'] = ' '
        return item

    def get_patent_references(self, response, item):
        test = response.xpath('/html/body/table[8]/tr[2]/td[1]/a/text()').extract()
        table1 = response.xpath('/html/body/table[8]/tr')
        r2 = ''
        if(test == None or test == [] ):
            table1 = response.xpath('/html/body/table[7]/tr')
            test = response.xpath('/html/body/table[7]/tr[2]/td[1]/a/text()').extract()
        if(test == None or test == [] ):
            test = response.xpath('/html/body/table[6]/tr[2]/td[1]/a/text()').extract()
            table1 = response.xpath('/html/body/table[6]/tr')
        if(test == None or test == [] ):
            table1 = response.xpath('/html/body/table[5]/tr')
        for rn in table1:
            references = str(rn.xpath('td[1]/a/text()').extract())
            if (references):
                r1 = references
                r2 = r2 + ' ' + r1
        print "patent_references" + r2
        if r2:
            item['patent_references'] = r2.replace('[','').replace(']','').replace('u\'','').replace('\'','').strip()
        else:
            item['patent_references'] = ' '
        return item

    def get_patent_otherref(self, response, item):
        body = str(response.body)
        start_idx = body.find('<b>Other References</b>')
        a = start_idx
        if (str(a) == '-1'):
            oref = ' '
        else:
            b = a
            while (body[b:b + 4] != '<HR>'):
                b = b + 1
            end_idx = b
            c = body[start_idx:end_idx]
            patten = re.compile('</?\w+[^>]*>')
            re_br = re.compile('<br\s*?/?>')
            oref = patten.sub('', c)
            oref = re_br.sub('\n', oref)
        if oref:
            print'patent_date' + oref
            item['patent_otherref'] = oref.replace('Other References', '').replace('</HTML', '').strip()
        return item

    def get_patent_refurl(self, response, item):
        body = str(response.body)
        start_idx = body.find('<b>U.S. Patent Documents</b>')
        a = start_idx
        if (str(a) == '-1'):
            print 'No refurl in this page'
        else:
            b = a
            while (body[b:b + 4] != '<HR>'):
                b = b + 1
            end_idx = b
            slam = body[start_idx:end_idx]
            pattern = re.compile(r"<a href=\"(/.*?)\">(.*?)</a>")
            reu = re.findall(pattern, slam)
            item['patent_refurl'] = []
            for i in reu:
                item['patent_refurl'].append(('http://patft.uspto.gov'+i[0], i[1]))
        return item














