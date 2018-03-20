from bs4 import BeautifulSoup
import re
import os
import urllib.parse
import requests
import time
import random

def parse(html_cont):
    cont = []
    data = {}
    soup = BeautifulSoup(html_cont, 'html.parser')
    data['main_title'] = soup.find('dd', class_="lemmaWgt-lemmaTitle-title").find("h1").get_text()
    data['content'] = soup.find('div', class_="lemma-summary").find_all('div', class_="para")
    try:
        data['sub_title'] = soup.find('dd', class_="lemmaWgt-lemmaTitle-title").find("h2").get_text()
    except:
        pass
        #print('no sub_title')
    # 得到除了最后一个以外，所有的二级标题和正文
    ret_test = re.findall(
        r'<div class="para-title level-2" label-module="para-title">[\s\S]+?<a name="[1-9][0-9]*" class="lemma-anchor para-title" >',
        html_cont)
    #print(ret_test)
    data['second_content'] = ret_test
    temp = r'<div class="para-title level-2" label-module="para-title">[\s\S]+?</h2>'
    temp_test = re.findall(temp, html_cont)
    length = len(temp_test)
    temp_test = temp_test[
                    length - 1] + r'[\s\S]+?<div class="open-tag-title">'
    # 得到最后一个的二级标题和正文
    data['last'] = re.findall(temp_test, html_cont)
    cont.append(data)

    test = open('D:/百度百科爬取语料/'+str(word)+'.txt', 'a+', encoding='utf-8')
    for data in cont:
        test.writelines(data['main_title'])
        try:
            test.writelines(data['sub_title'])
        except:
            print('no sub_title')
        write_para_text(data['content'], test)#输入标题下的正文内容
        #test.write("<p>%s</p>"%data['content'])
        for s in data['second_content']:
            write_sec_para_text(s, test)
        for l in data['last']:
            write_sec_para_text(l, test)

def write_sec_para_text(html_cont, test):
    soup = BeautifulSoup(html_cont,'html.parser')
    pre = soup.find("h2").find("span").get_text()
    test.writelines('\n\n'+'  '+soup.find("h2").get_text()[len(pre):]+'\n')#二级标题前空2个格

    #判断是否含有三级标题
    if(len(soup.find_all('div', class_="para-title level-3")) > 0):
        first = re.findall(r'<div class="para-title level-2" label-module="para-title">[\s\S]+?<div class="para-title level-3" label-module="para-title">', str(soup))
        fsoup = BeautifulSoup(first[0],'html.parser')
        if(len(fsoup.find_all('div', class_="para")) > 0):
            #二级标题和第一个三级标题之间的正文
            write_para_text(fsoup.find_all('div', class_="para"), test)
        #得到一个个三级标题加上其下面的内容
        end = re.findall(r'<h3 class="title-text">[\s\S]+?<div class="anchor-list">', str(soup))
        write_third_para_text(end, test)
    else:
        write_para_text(soup.find_all('div', class_="para"), test)

def write_third_para_text(html_cont, test):
    for e in html_cont:
        esoup = BeautifulSoup(e,'html.parser')
        pre = esoup.find("h3").find("span").get_text()
        test.writelines('\n\n'+'    '+esoup.find("h3").get_text()[len(pre):]+'\n')#三级标题前空4个格
        write_para_text(esoup.find_all('div', class_="para"), test)

def write_para_text(paraSoup, test):
        for pSoup in paraSoup:
            test.writelines('\n'+'      '+pSoup.get_text('','/br'))#正文内容前空6个格,将换行符替换为空

headers = {
    'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
}

with open('d:\关键词汇总.txt','r',encoding='utf-8-sig') as y:
    sum1,sum2 = 0,0
    gjc = y.readlines()
    with open('d:\百度百科中没有的关键词.txt','a+',encoding='utf-8-sig') as f:
        for guanjc in gjc[:]:
            word = guanjc.strip('\n')
            a_url = 'https://baike.baidu.com/item/'+ str(word)
            print(a_url)
            try:
                sum1 += 1
                a_text = requests.get(a_url,headers = headers)
                a_text.encoding = 'utf-8'
                parse(a_text.text)
                time.sleep(random.randint(1, 3))
                print('爬取了'+str(sum1)+'篇百度百科的内容')
            except:
                sum2 += 1
                f.writelines(str(word)+'\n')
                print (str(sum2)+'个关键词百度百科无具体内容')