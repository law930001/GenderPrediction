from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup as Soup
import time
import base64
import json
from opencc import OpenCC

from Gender_predict import GenderPredictor



class Crawler:

    def __init__(self, close_window = True):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.browser = webdriver.Chrome(options=options, executable_path='./chromedriver.exe')

        self.username = ''
        self.passwd = ''

        self.main_url = ""
        self.post_url = []
        self.post_comments = []
        self.if_login = False

        self.close_window = close_window


    # destructor, close the window
    def __del__(self):
        if self.close_window:
            self.browser.close()
        print('End.')


    # set the main url
    def set_main_url(self, url):
        self.main_url = url


    # login in the IG
    def login(self):

        if self.if_login == True:
            return

        username = base64.b64decode(self.username).decode('ascii')
        passwd = base64.b64decode(self.passwd).decode('ascii')

        self.browser.get('https://www.instagram.com/')

        WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.NAME, 'username')))

        username_input = self.browser.find_elements_by_name('username')[0]
        password_input = self.browser.find_elements_by_name('password')[0]

        username_input.send_keys(username)
        password_input.send_keys(passwd)

        # login
        WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.XPATH,
        '//*[@id="loginForm"]/div/div[3]/button/div')))

        login_click = self.browser.find_elements_by_xpath('//*[@id="loginForm"]/div/div[3]/button/div')[0]

        login_click.click()

        # store
        WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/div/div/div/button')))

        store_click = self.browser.find_elements_by_xpath('//*[@id="react-root"]/section/main/div/div/div/div/button')[0]

        store_click.click()

        # notification
        WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div/div[3]/button[2]')))

        notification_click = self.browser.find_elements_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[2]')[0]

        notification_click.click()

        self.if_login = True


    # crawl the post urls from specific page (main url)
    def crawl_post_url(self, post_num = 10):

        post_url = []
        while len(post_url) < post_num:
            scroll = 'window.scrollTo(0, document.body.scrollHeight);'
            self.browser.execute_script(scroll)
            html = self.browser.page_source
            soup = Soup(html, 'lxml')

            # 尋找所有的貼文連結
            for elem in soup.select('article div div div div a'):
                # 如果新獲得的貼文連結不在列表裡，則加入
                if elem['href'] not in post_url:
                    post_url.append(elem['href'])
            time.sleep(0.5) # 等待網頁加載

        self.post_url = post_url[:post_num]


    # save whole post urls to csv
    def save_post_url(self):

        file_name = 'data/' + self.main_url.split('/')[3] + '_post.csv'

        with open(file_name, 'w') as file:
            for p in self.post_url:
                file.write(p + ', 0\n')


    # read the post url csv file from main url
    def read_post_url(self):

        file_name = 'data/' + self.main_url.split('/')[3] + '_post.csv'

        self.post_url = []

        with open(file_name, 'r') as file:
            for line in file.readlines():
                line = line.strip()
                if line.split(', ')[1] == '1':
                    self.post_url = []
                else:
                    self.post_url.append(line.split(',')[0])


    # return post urls
    def get_post_url(self):
        return self.post_url


    # return post content from specific post url
    def get_post_comments(self, short_url, comment_num = 10):

        # browse post url
        url = 'https://www.instagram.com' + short_url
        self.browser.get(url)

        # click comment button
        while len(self.browser.find_elements_by_class_name('_6lAjh' )) < comment_num:
            try:
                # 等待直到Button出現
                WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'dCJp8')))
                # 找到Button的網頁元素(class)
                more_btn = self.browser.find_element_by_class_name('dCJp8.afkep')
                # 自動點擊Button
                more_btn.click()
            except:
                break

        # get information
        content_comment_elem = []
        person_id_elem = []
        image_elem = []

        result = []
        element_len = len(self.browser.find_elements_by_class_name('_6lAjh' ))

        # get elements
        for i in range(element_len):
            content_comment_elem.append(self.browser.find_elements_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/ul['+ str(i+1) +']/div/li/div/div[1]/div[2]/span'))
            person_id_elem.append(self.browser.find_elements_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/ul['+ str(i+1) +']/div/li/div/div[1]/div[2]/h3/div/span/a'))
            image_elem.append(self.browser.find_elements_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/ul['+ str(i+1) +']/div/li/div/div[1]/div[1]/div/a/img'))

        # get result list
        for j in range(element_len - 1) : # 這裡-1是因為抓到最後會有個空的list
            try:
                result.append([short_url, person_id_elem[j][0].text, image_elem[j][0].get_attribute("src") ,content_comment_elem[j][0].text])
            except:
                return None

        # result[post_url, person_id, image, comment_content, gender]
        return result[:comment_num]


    # crawl function, crawl and save the post url from main url
    def crawl_postlist(self, post_num):

        if self.main_url == "":
            print("Please set the main url.")
            return

        self.login()

        self.browser.get(self.main_url)

        self.crawl_post_url(post_num)

        self.save_post_url()


    # crawl function, get the information(img, comment...)
    def crawl_infolist(self, comment_num):

        self.login()

        self.read_post_url()

        self.index = 24126

        for i, url in enumerate(crawler.get_post_url()):

            print(i)

            content = crawler.get_post_comments(url, comment_num)

            if content == None:
                continue

            for line in content:
                self.post_comments.append(line)

            self.save_infolist()
            self.post_comments = []


    def save_infolist(self):

        file_name = 'data/' + self.main_url.split('/')[3] + '_comment.json'

        with open(file_name, 'a', encoding="utf-8") as file:
            for temp in self.post_comments:
                url, id, img, comment = temp
                data = {'index': self.index, 'url': url, 'id': id, 'img': img, 'comment': comment}
                json.dump(data, file, indent=4, ensure_ascii=False)
                file.write(',\n')
                self.index += 1


    def read_infolist(self):

        file_name = 'data/' + self.main_url.split('/')[3] + '_comment.json'

        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return data


    # post process function, do gender prediction and make final training list
    def post_process(self):

        info_list = self.read_infolist()

        final_list = []

        gp = GenderPredictor()

        cc = OpenCC('s2twp')

        index = 2242

        for info in info_list:

            print(info['index'], index)

            if info['index'] < 24124:
                continue

            # ignore duplicate data

            if [info['id'], info['comment']] in final_list:
                continue

            final_list.append([info['id'], info['comment']])

            comment_split = info['comment'].split()
            # comment_split = info['comment'].encode('unicode-escape').decode('ascii').split()

            # only tag and no other words, remove the whole data
            if len(comment_split) == 1 and comment_split[0][0] == '@':
                continue

            # tag with other words, remove the tags
            if len(comment_split) >= 2:
                comment_split = [word for word in comment_split if '@' not in word]

            comment_split = ' '.join(comment_split)

            # no words in comment
            if comment_split == '':
                continue

            def add_space(string, pos):
                return string[:pos] + ' ' + string[pos:]

            # add space in front of '\'
            if '\\' in comment_split:
                indices = [i for i, x in enumerate(comment_split) if x == "\\"]

                for i in reversed(indices):
                    comment_split = add_space(comment_split, i)

            # s2twp
            comment_split = cc.convert(comment_split)


            # predict gender here
            gender = gp.process(info['img'], info['index'])

            if gender == None: # no gender in image
                continue

            gender = 0 if gender == 'Male' else 1

            self.save_finallist([comment_split, gender], index)

            index += 1



    def save_finallist(self, line, index):

        file_name = 'data/' + self.main_url.split('/')[3] + '_final.csv'

        with open(file_name, 'a', encoding="utf-8") as file:

            file.write(str(index+1) + ',' + str(index+1) + ',"' + line[0] + '", ' + str(line[1]) + '\n')






if __name__ == "__main__":
    crawler = Crawler(close_window=False)

    crawler.set_main_url("https://www.instagram.com/jaychou/")

    # crawler.crawl_postlist(post_num=790)

    # crawler.crawl_infolist(comment_num=500)

    crawler.post_process()