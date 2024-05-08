#爬取資料
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import csv
import time

# 104 關鍵字: Python Engineer (共 11070 筆，150 頁) #抓出來只有3008筆
url_base = 'https://www.104.com.tw/jobs/search/?ro=0&keyword=Python%20Engineer&expansionType=area,spec,com,job,wf,wktm&jobsource=index_s&langFlag=0&langStatus=0&recommendJob=1&hotJob=1&page={}'

# 偽裝表頭
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# chromedriver 路徑
#driver_path = r'C:\Users\user\OneDrive\桌面\chromedriver-win64\chromedriver.exe'
driver_path = r'C:\Users\student\Desktop\chromedriver-win64\chromedriver.exe'
# 建立瀏覽器物件
driver = webdriver.Chrome()

# 建立 CSV 檔案
with open('job_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    # 設定欄位名稱
    fieldnames = ['職稱', '公司', '地區', '年資', '學歷', '薪資']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # 寫入 CSV 
    writer.writeheader()

    # 抓取全部所需資料共 150 頁
    for page in range(1, 151):
        url = url_base.format(page)
        driver.get(url)

        try:
            # 等待網頁元素加載完成
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'js-next-page')))
        except Exception as e:
            print(f"頁面載入失敗: {str(e)}")
            continue
        
        # 模擬向下滾動
        actions = ActionChains(driver)
        actions.send_keys(Keys.END).perform()
        time.sleep(3)
        
        # 解析 html 原始碼
        content = BeautifulSoup(driver.page_source, 'html.parser')
        # 找 104 職缺元素
        info = content.find_all('article', class_='js-job-item')
        
        #搜尋職位、公司、地區、產業、年資、學歷、薪資
        for job_item in info:
            job_name = job_item.find('a', class_='js-job-link')
            company_name = job_item.find('div', class_='b-block__left').find_all('ul')[0]('li')[1]
            #使用select_one指定，ul的class b-list-inline下的li標籤css選擇器nth-child(2)下的a標籤 
            #company_name = job_item.select_one('ul.b-list-inline > li:nth-child(2) > a')
            #industry_name = job_item.find('div', class_='b-block__left').find_all('ul')[0]('li')[2]
            location_name = job_item.find('ul', class_='job-list-intro').find_all('li')[0]
            qualifications_name = job_item.find('ul', class_='job-list-intro').find_all('li')[1]
            educational_name = job_item.find('ul', class_='job-list-intro').find_all('li')[2]
            
            #薪資: 年薪、月薪<a>、待遇面議<span>，從<div>抓取第一個
            salary_name = job_item.find('div', class_='job-list-tag')
            if salary_name:
                first = salary_name.find(True) #找到第一個子元素
                
                #如果 first=a、span
                if first and (first.name == 'a' or first.name == 'span'):
                    salary = first.text.strip()
                else:
                    salary = None
            else:
                salary = None
            
            #取出文字
            if job_name and company_name and location_name and qualifications_name and educational_name:
                title = job_name.text.strip() #strip()用來刪除文字前面和後面多餘的空白
                company = company_name.text.strip()
                location = location_name.text.strip()
                qualifications = qualifications_name.text.strip()
                #industry = industry_name.text.strip()
                educational = educational_name.text.strip()

                # 寫入 CSV
                writer.writerow({
                    '職稱': title,
                    '公司': company,
                    '地區': location,
                    #'產業': industry,
                    '年資': qualifications,
                    '學歷': educational,
                    '薪資': salary
                })
        
driver.quit()          


#%%

#資料清理
import pandas as pd
df=pd.read_csv('job_data_final.csv',encoding='ansi')
df=df[df['地區'].str.contains('台北市|新北市')]
df=df[~df['薪資'].str.contains('時薪')]