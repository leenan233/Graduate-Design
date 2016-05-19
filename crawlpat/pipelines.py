# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from store import PatentDB
import MySQLdb
import re




class CrawlpatPipeline(object):
        
    def process_item(self, item, spider):
        print "CrawlpatPipeline"
        if spider.name != "patSpider":  return item
        # conn = MySQLdb.connect('localhost','root','123456','Patent' )
        conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='Patent',
                                   unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock', port=8889)

        if item:
            try:
                print item['patent_url']
                cur = conn.cursor()
                sql = 'insert into tab_patent (patent_no,patent_date,patent_title,patent_abstract,patent_familyId,patent_applyNo,patent_fieldDate,patent_claims,patent_description,patent_url,patent_references,patent_otherref, patent_keyword)\
                 values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                if "patent_familyId" in item.keys():
                    if "patent_references" in item.keys():
                        param = (
                            item['patent_no'], item['patent_date'], item['patent_title'], item['patent_abstract'], item['patent_familyId'],
                            item['patent_applyNo'], item['patent_fieldDate'], item['patent_claims'],
                            item['patent_description'], item['patent_url'], item['patent_references'], item['patent_otherref'], item['patent_keyword']
                        )
                    else:
                        param = (
                            item['patent_no'], item['patent_date'], item['patent_title'], item['patent_abstract'], item['patent_familyId'],
                            item['patent_applyNo'], item['patent_fieldDate'], item['patent_claims'],
                            item['patent_description'], item['patent_url'], "", item['patent_otherref'], item['patent_keyword']
                        )
                else :
                    if "patent_references" in item.keys():
                        param = (
                            item['patent_no'], item['patent_date'], item['patent_title'], item['patent_abstract'], "",
                            item['patent_applyNo'], item['patent_fieldDate'], item['patent_claims'],
                            item['patent_description'], item['patent_url'], item['patent_references'], item['patent_otherref'], item['patent_keyword']
                        )
                    else:
                        param = (
                            item['patent_no'], item['patent_date'], item['patent_title'], item['patent_abstract'], "",
                            item['patent_applyNo'], item['patent_fieldDate'], item['patent_claims'],
                            item['patent_description'], item['patent_url'], "", item['patent_otherref'], item['patent_keyword']
                                 )
                #cur.execute(sql,param)
                try:  
                    cur.execute(sql,param)
                    # cur.execute("insert into tab_patent (patent_references) values(%s)",[(patent_references,) for patent_references in item['patent_references']])
                except (AttributeError, MySQLdb.OperationalError):  
                    conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='Patent',
                                   unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock', port=8889 )
                    cur = conn.cursor()  
                    cur.execute(sql,param)

                if 'patent_inventors' in item.keys():
                    invent_sql = 'insert into tab_inventor (patent_no,patent_inventors,patent_inventors_city,patent_inventors_country)  values(%s,%s,%s,%s)'
                    for inv in item['patent_inventors']:
                        f_pattern = re.compile(r'\([^)]*\)')
                        #匹配括号外面的inventor name
                        inventor_name = f_pattern.sub('',inv)
                        #print str(inventor_name)
                        pattern = re.compile(r"\((.*?)\)", re.I|re.X)
                        temp = pattern.findall(inv)
                        templist = temp[0].split(",")
                        inv_param = (item['patent_no'],inventor_name.strip(),templist[0].strip(),templist[1].strip())
                        #cur.execute(invent_sql,inv_param)
                        try:  
                            cur.execute(invent_sql,inv_param)  
                        except (AttributeError, MySQLdb.OperationalError):  
                            conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='Patent',
                                   unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock', port=8889 )
                            cur = conn.cursor()  
                            cur.execute(invent_sql,inv_param)

                if 'patent_refurl' in item.keys():
                    reference_sql = 'insert into tab_refurl (patent_no, patent_reference, patent_refurl)  value(%s,%s,%s)'
                    r = len(item['patent_refurl'])
                    print 'patent_refurl', len(item['patent_refurl'])
                    if r != 0:
                        for url in item['patent_refurl']:
                            ref_param = (item['patent_no'], url[1], url[0])
                            try:
                                cur.execute(reference_sql, ref_param)
                            except (AttributeError, MySQLdb.OperationalError):
                                conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='Patent',
                                    unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock', port=8889)
                                cur = conn.cursor()
                                cur.execute(reference_sql, ref_param)

                if 'patent_assignee' in item.keys():
                    assign_sql = 'insert into tab_assignee (patent_no,patent_assignee,patent_assignee_city,patent_assignee_country)  values(%s,%s,%s,%s)'
                    for assign in item['patent_assignee']:
                        if assign:
                            f_pattern = re.compile(r'\([^)]*\)')
                            #匹配括号外面的inventor name
                            assign_name = f_pattern.sub('',assign)
                            #print str(inventor_name)
                            pattern = re.compile(r"\((.*?)\)", re.I | re.X)
                            temp = pattern.findall(assign)
                            templist = temp[0].split(",")
                            if(len(templist)>1):
                                assign_param = (item['patent_no'], assign_name.strip(), templist[0].strip(), templist[1].strip())
                            else:
                                assign_param = (item['patent_no'], assign_name.strip(), "", templist[0].strip())
                            #cur.execute(assign_sql,assign_param)
                            try:  
                                cur.execute(assign_sql, assign_param)
                            except (AttributeError, MySQLdb.OperationalError):  
                                conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='Patent',
                                   unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock', port=8889 )
                                cur = conn.cursor()  
                                cur.execute(assign_sql,assign_param)

                if 'patent_applicant_Name' in item.keys():
                    applicant_sql = "insert into tab_applicant (patent_no,patent_applicant_Name,patent_applicant_State,patent_applicant_City,patent_applicant_Country)\
                     values(%s,%s,%s,%s,%s)"
                    count = 0
                    for name in item['patent_applicant_Name']:
                        applicant_param =(item['patent_no'],name,item['patent_applicant_State'][count],item['patent_applicant_City'][count],item['patent_applicant_Country'][count])
                        count = count+1
                        #cur.execute(applicant_sql,applicant_param)
                        try:  
                            cur.execute(applicant_sql,applicant_param)  
                        except (AttributeError, MySQLdb.OperationalError):  
                            conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='Patent',
                                   unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock', port=8889)
                            cur = conn.cursor()  
                            cur.execute(applicant_sql,applicant_param)

            except MySQLdb.Error,e:
                print "Mysql Error %d: %s" % (e.args[0], e.args[1])  
            conn.commit()
            #cur.close()
            #conn.close()
        return item
