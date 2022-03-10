'''A tool to collect research papers for you.
   This is a draft version of a Python tool which can search papers,
   download PDF versions, and perform a simple text processing on 
   the abstracts of the papers.
   The paper search is performed through Springer Open Access API. 
   You may go to Springer API website to obtain your key:
   https://dev.springernature.com/  And FOR TESTING PURPOSE ONLY: 
   You may enter "testing" when you are prompted to enter a key.
   Name:    papers_SpringerOA.py
   Author:  Nan LI (nankli@berkeley.edu)
   Date:    Oct 29, 2021
   Version: 1.0
'''

import requests
import json
import csv
import os
from urllib import parse
from bs4 import BeautifulSoup
from gensim.summarization import summarize
from gensim.parsing.preprocessing import remove_stopwords

class Search():
    '''base class for construct searching URL string'''
    def __init__(self, urlbase, APIkey, keywords):
        self.urlbase = urlbase
        self.APIkey = APIkey
        self.keywords = keywords
        
class Search_Springer(Search):
    '''construct URL string and get the Json metadata'''
    def __init__(self, urlbase, APIkey, keywords, paper_num):
        super().__init__(urlbase, APIkey, keywords)
        #formating the Springer openaccess API search parameters
        self.paper_num = paper_num
        self.url_params = {}
        self.url_params['api_key'] = self.APIkey
        #The maximum number of results returned per query is 100.
        self.url_params['p'] = self.paper_num   
        self.url = self.urlbase + self.keywords + '&'+ \
                   parse.urlencode(self.url_params)
        
    def search_papers(self):
        '''Get metadata through API 
        https://dev.springer.com/example-metadata-response 
        Although the examples format does not match with the real
        reponses'''
        response = requests.get(self.url)
        #sf is a flag for API key failure
        sf = False
        try:
            response.raise_for_status()
            res = response.json()
        except requests.exceptions.HTTPError as e:
            # if response is not a 200
            print('Error: ' + str(e))
            if "Client Error" in str(e):
                sf = True
                res = {}
        return(res, sf)  

class Get_Article_Info():
    '''convert article info from Json format'''
    def __init__(self, records={}):
        self.records = records
        self.title = records['title']    
        self.journal = records['publicationName'] 
        self.date = records['publicationDate'] 
        self.url = records['url'][0]['value'] 
        #some abstracts are missing in Json
        if records['abstract'] == '':
            self.abstract = ''
        #abstracts are strings as 'value' in a dict    
        elif type(records['abstract']['p']) == str:
            self.abstract = records['abstract']['p']
        #abstracts are lists as 'value' in a dict
        else:
            ablist = records['abstract']['p']
            self.abstract = ' '.join(ablist)
        
    def author(self):
        '''combine mutiple authors' names as a string'''
        name_list = [i['creator']  for i in self.records['creators']]
        combine_name = ','
        combine_name = combine_name.join(name_list)
        return combine_name 

class Dl_Papers():
    '''downloading PDF versions to the local directory with journal \
    name as the folder name'''
    def __init__(self, weburl, title, journal):
        self.weburl = weburl
        self.title = title
        self.journal = journal
   
    def downloading(self):
        '''making folders using the journals as folder names; find the 
        PDF url in the hyperlinks of the webpage using BeautifulSoup;
        download PDFs using Response lib'''
        #remove special char in the title and journal
        self.title = self.title.replace(':','').replace('?','')
        self.journal = self.journal.replace(':','').replace('?','')
        #making folders using the journals as folder names if not existed
        if not os.path.isdir(self.journal):
            os.mkdir(self.journal)
        try:
            response = requests.get(self.weburl)
            #find the base of the webpage
            urlbase = response.url
            soup = BeautifulSoup(response.text, 'html.parser')
            #finds all <a> elements 
            links = soup.find_all('a')
            #soup.find_all('a', attrs={'href': re.compile("^http://")})
            #find .pdf url in all hyperlinks
            for link in links:
                if ('.pdf' in link.get('href')):
                    print('\nDownloading file: ', self.title)
                    pdf_templink = link.get('href')
                    # Get response object for link
                    if pdf_templink[0:7] == "http://" or \
                       pdf_templink[0:8] == "https://":
                        pdflink = pdf_templink
                    elif pdf_templink[:2] == '//':
                        pdflink = 'http:' + pdf_templink
                    elif pdf_templink[:2] == '/a':
                        pdflink = 'https://www.nature.com' + pdf_templink
                    else:
                        pdflink = urlbase + pdf_templink
                    response = requests.get(pdflink)
                    # Write content in pdf file
                    pdf = open('./'+self.journal+'/'+self.title+'.pdf', \
                               'wb')
                    pdf.write(response.content)
                    pdf.close()
                    print('\n'+self.title+'.pdf downloaded')
                    #shutil.move(self.title+'.pdf', './'+self.journal+'/')
                    break
        except requests.exceptions.HTTPError as e:
            # if response is not a 200
            print('Error: ' + str(e))
            pass
        except IOError as e1:
            print('Error: ' + str(e1))
            pass
        
class Proc_Abs():
    '''process the abstracts using Gensim library
       the default ratios were set to 0.2'''
    def __init__(self, text, ratios = 0.2):
        self.text = text
        self.ratios = ratios
        #remove stop words
        self.text = remove_stopwords(self.text)
        
    def sum_sum(self, ratios = 0.2):
        return summarize(self.text, ratios)
        
class Printmsg():
    '''printer class'''
    def __init__(self):
        pass
        
    def printout(self, s):
        print(s)
   

class Main():
    '''the Main class walks through the entire work cycle: 
    Search->Collect paper info->Download PDF->Analyze the abstracts
    '''
    rm = '\n -----------by Nan Li email: nankli@berkeley.edu' + \
         '\n|-------------------------------------------------------|' + \
         '\n|This is the tool to collect research papers for you.   |' + \
         '\n|The paper search is through Springer Open Access API.  |' + \
         '\n|You may go to Springer API website to obtain your key: |' + \
         '\n|          https://dev.springernature.com/              |' + \
         '\n|FOR TESTING PURPOSE ONLY:                              |' + \
         '\n|Enter "testing" when you are prompted to enter a key.  |' + \
         '\n|-------------------------------------------------------|' 
    
    em = '\n|-------------------------------------------------------|' + \
         '\n|           Thanks for using this program!              |' + \
         '\n|-------------------------------------------------------|' 
    
    def user_interface():
        '''provide useful messages to users and prompt for input'''
        s1 = 'Please enter your search keywords.' + \
             '\nUse "+" to seperate several keywords:'
        keyword1 = input(s1)
        #prompt for input until getting non-empty input
        while not keyword1:
            keyword1 = input(s1)
        else:
            wordnum = 0 
            wordlist = keyword1.split('+')
            for i in range(len(wordlist)):
                if wordlist[i]:
                    wordnum += 1
                    #use strip() to remove trailing and leading spaces
                    #the internal spaces are preserved
                    wordlist[i] = wordlist[i].strip()
                    print('keyword no. ' + str(wordnum) + ': ' + \
                          wordlist[i])
            print('You just entered ' + str(wordnum) + ' keyword(s)')        
        #formulate serach_keyword string
        #'?q=('+'%22machine%20learning%22AND%22protein%22type:Journal)'
        search_keyword = '?q=('+ '%22'
        for word in wordlist:
                search_keyword += word.replace(' ', '%20') + '%22AND%22'
        search_keyword = search_keyword[:-6]
        search_keyword += 'type:Journal'+')'      
        s2 = '\nPlease enter your Springer API key: '
        api_key = input(s2)
        #prompt for input until getting non-empty input
        while not api_key:
            api_key = input(s2)
        else:
            APIkey = api_key
        s3 = '\nPlease enter the number of papers you want. ' + \
             '\n(The search results will be ranked by pulication ' + \
             'date from newest to oldest): ' 
        paper_num = input(s3)
        #prompt for input until getting non-empty input
        while not paper_num:
            paper_num = input(s3)
        return search_keyword, APIkey, int(paper_num)
        
    def save_metadata(articles_lists):
        '''save metadata into csv file and save abstracts into
        a text file'''
        titlelist = [i.title for i in articles_lists]
        authorlist = [i.author() for i in articles_lists]
        journallist = [i.journal for i in articles_lists]
        datelist = [i.date for i in articles_lists]
        weburllist = [i.url for i in articles_lists]
        abstractlist = [i.abstract for i in articles_lists if i.abstract]
        abstract_s = '\n'.join(abstractlist)
        file1 = open('Article_list.csv','w')
        writer=csv.writer(file1)
        writer.writerow(['title','authors','journal', 'date', 'url'])
        writer.writerows(zip(titlelist, authorlist,journallist,datelist,\
                         weburllist))
        file1.close()
        file2 = open('abstract_list.txt','w')
        file2.write(abstract_s)
        file2.close()
        return len(titlelist), len(abstractlist)

    def download_papers(articles_lists): 
        '''download PDF for each paper in the list'''
        number_dl = 0
        weburllist = [i.url for i in articles_lists]
        titlelist = [i.title for i in articles_lists]
        journallist = [i.journal for i in articles_lists]
        for i in range(len(weburllist)):
            dl = Dl_Papers(weburllist[i], titlelist[i], journallist[i])
            d = dl.downloading()
            number_dl += 1
        return number_dl    
    
    def summary_ratio():
        '''provide options to the users if they are not happy with
        the text processing results using default ratio'''
        flag = False
        ratios = 0.2
        print('\n|Do you feel the summary of the' + \
              ' abstracts suffice?|')
        s_option = str(input('Enter Y for Yes, enter N for No: ')).lower()
        legitoptions = ['s', 'l','q']
        s_operations = '\n+-----------------------------------------+' + \
                       '\n| What do you want to do? I want .........|' + \
                       '\n| s = shorter summary                     |' + \
                       '\n| l = longer summary                      |' + \
                       '\n| q = quit                                |' + \
                       '\n+-----------------------------------------+'
        if s_option == 'y':
            flag = False
        elif s_option == 'n':
            while True:
                print(s_operations)
                summary_option = input('Please enter your answer: ')
                summary_option.lower()
                if summary_option in legitoptions:
                    flag = True
                    l = 0.05
                    m = 0.5
                    #the ratios are hard-coded...  will be updated
                    #with advanced NLP in the future
                    if summary_option == 's':
                        ratios = l
                    if summary_option == 'l':
                        ratios = m
                    if summary_option == 'q':  
                        flag = False
                    break
                else:
                    print('Input is not valid')  
        else:
            print('Input is not valid')
            flag = False
        return flag, ratios
    
    def output_summary(summary):
        '''output text processing results and save results in text files'''
        print('\n|-----------------------------------------------------|')
        print('|Below are a summary extracted from' + \
              ' the abstracts.|')
        print('\n|Summary|')
        print(summary)
        file3 = open('summary.txt','wt')
        file3.write(summary)
        file3.close()
    
    # ------------------- Search for papers ------------------------- #    
    printer1 = Printmsg()
    printer1.printout(rm)   
    base_url = 'https://api.springernature.com/openaccess/json'
    keyword_string, APIkey, paper_num = user_interface()
    search_one = Search_Springer(base_url, APIkey, keyword_string, paper_num)
    #save returned Json
    #sf is request failure flag; handle API key errors
    sf = True
    while sf:
        res, sf = search_one.search_papers()
        if sf:
            print('\n|Looks like your API key is not valid.' + \
                  ' Try again with a valid API key? (Y) or Quit (Q)|')
            skey = input('Please enter Y or Q: ').lower()
            if skey == "y":
                keyword_string, APIkey, paper_num = user_interface()
                search_one = Search_Springer(base_url, APIkey, \
                                             keyword_string, paper_num)
                res, sf = search_one.search_papers()                             
            elif skey == "q":
                quit()
            else:
                print("Your input is invalid.")
                quit()
    #save each article info in a list   
    articles_lists = [Get_Article_Info(records) for records \
                      in res['records']]    
    
    # ------------------- Save papers' info ------------------------- #    
    number_of_papers, number_of_abstracts = save_metadata(articles_lists)
    if number_of_papers == 0:
        print('0 paper was found, please check your keywords and retry!')
    elif number_of_papers == 1:
        print('\n1 paper was found'.format(number_of_papers))
    else:
        #print('\nThe maximum number of results returned per query is 100')
        print('\n{} papers were found'.format(number_of_papers))
        print('Papers information is saved in Article_list.csv')
    # ------------------- Download papers ------------------------- #         
    print('\nDo you want to proceed with downloading these papers?')
    download_flag = input('Enter Y for Yes, enter N for No: ').lower() 
    if download_flag == 'y':
        number_of_downloads = download_papers(articles_lists)
        if number_of_downloads == 0:
            print('\nZero paper was downloaded, please check your ' +
                  'keywords and retry!')
        elif number_of_downloads == 1:
            print('\nOne paper downloaded'.format(number_of_downloads))
        else:
            print('\n{} papers downloaded'.format(number_of_downloads))
    elif download_flag == 'n':
        print('\nZero paper was downloaded')
    else:
        print('\nInvalid input! Zero paper was downloaded.')
    
    # ------------------- Analyze abstracts ------------------------- #     
    print('\n+--------------------------------------------------+')
    print(str(number_of_abstracts) + ' abstracts were found')
    print('\nDo you want to proceed with analyzing the abstracts?')
    print('(You need Gensim 3.8.* or older for this to work)')
    ana_flag = input('Enter Y for Yes, enter N for No: ').lower() 
    if ana_flag == 'y':    
        if os.path.exists('abstract_list.txt'):
            with open('abstract_list.txt', 'r') as f:
                abstract_text = f.read()
            process_abs_ins = Proc_Abs(abstract_text)
            output_summary(process_abs_ins.sum_sum())
            ratio_f, ratio_s = summary_ratio()
            if ratio_f:
                process_abs_ins = Proc_Abs(abstract_text, ratio_s)
                output_summary(process_abs_ins.sum_sum(ratio_s))
        else:
            pass
    printer2 = Printmsg()
    printer2.printout(em)
    
# -------- START HERE ----------- #
if __name__ == '__main__':
    main = Main()    