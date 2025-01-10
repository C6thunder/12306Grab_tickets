from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from config import Config     # 信息保存在config.py里
import random
import time

'''
    三代代码，相对于二代代码，这个代码更加迅速，可以用于抢票
    更新：测试发现，预定时若有多次列车则会因为for循环变慢
'''

# 这个函数用来判断是否有预订按钮是非常快的，自己尝试的其他方法都很慢~(^T^)~
# 判断是否有预订按钮非常影响速度，如果有人感觉自己写的代码慢，大概率是因为这个
def T_F():
    btn72_cache = driver.execute_script("""
                                        return document.querySelectorAll('td.no-br > a.btn72').length > 0;
                                        """)
    if btn72_cache:
        return True
    else:
        return False


def get_ticket(conf, driver, url):
    # 过网站检测，没加这句的话，账号密码登录时滑动验证码过不了，但二维码登录不受影响
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined})"""})
    driver.maximize_window()
    driver.get(url)

 
    # 获取并点击右上角登录按钮
    login = driver.find_element(by=By.ID, value='J-btn-login')
    login.click()
 
    # 扫码登录
    scan_QR = driver.find_element(by=By.XPATH, value='//*[@id="toolbar_Div"]/div[2]/div[2]/ul/li[2]/a')
    scan_QR.click()
    driver.implicitly_wait(10)
 
    # 点击车票预订跳转到预订车票页面
    driver.find_element(by=By.XPATH, value='//*[@id="link_for_ticket"]').click()
    driver.implicitly_wait(10)
 
    # 输入出发地和目的地信息
    # 出发地
    driver.find_element(by=By.XPATH, value='//*[@id="fromStationText"]').click()
    driver.find_element(by=By.XPATH, value='//*[@id="fromStationText"]').clear()
    driver.find_element(by=By.XPATH, value='//*[@id="fromStationText"]').send_keys(conf.fromstation)
    time.sleep(1)
    driver.find_element(by=By.XPATH, value='//*[@id="fromStationText"]').send_keys(Keys.ENTER)
 
    # 目的地
    destination_tag = driver.find_element(by=By.XPATH, value='//*[@id="toStationText"]')
    destination_tag.click()
    destination_tag.clear()
    destination_tag.send_keys(conf.destination)
    time.sleep(1)
    destination_tag.send_keys(Keys.ENTER)
    driver.implicitly_wait(5)
 
    # 出发日期
    date_tag = driver.find_element(by=By.XPATH, value='//*[@id="train_date"]')
    date_tag.click()
    date_tag.clear()
    date_tag.send_keys(conf.date)
    time.sleep(1)
    query_tag = driver.find_element(by=By.XPATH, value='//*[@id="query_ticket"]')
 


    while True:
        

        # 如果查询按钮可用，点击查询
        if query_tag.get_attribute('class') == "btn92s":   # 这个是因为有时候按钮会变成灰色，不可点击 而btn92s是可点击的
            driver.execute_script("arguments[0].click();", query_tag)
      
        # 使用缓存判断是否有预订按钮
        if not T_F():  
  
            print("未找到预订按钮，等待ing~~")
            # 随机延迟，尽量短些
            time.sleep(random.uniform(0.097, 0.345))  
            continue
        else:
            print("找到预订按钮！！！！")
        
        # 获取车票信息
        tickets = driver.find_elements(By.CSS_SELECTOR, 
                                       "#queryLeftTable tr:not([style*='display: none'])"
                                       )
        
        for ticket in tickets:
            try:
                train_number = ticket.find_element(By.CLASS_NAME, 'number').text
                if train_number == conf.trainnumber:
                    # 使用相对路径查找硬卧状态，避免使用全局XPATH  加速，加速！！！！
                    status = ticket.find_element(By.CSS_SELECTOR, 'td:nth-child(8)').text
                    if "候补" not in status:
                        # 点击预订
                        book_btn = ticket.find_element(By.CLASS_NAME, 'btn72')
                        driver.execute_script("arguments[0].click();", book_btn)
                        
                        # 选择乘车人 在这里选择乘车人，如果有多个乘车人，可以多次调用该方法
                        # 第四个乘车人
                        string = '//*[@id="normalPassenger_'+conf.passengernum+'"]'
                        driver.find_element(by=By.XPATH, value=string).click()        # '//*[@id="normalPassenger_3"]'
                        
                        # 提交订单
                        driver.find_element(by=By.XPATH, value='//*[@id="submitOrder_id"]').click()
                        
                        # 选座 F座
                        driver.find_element(by=By.XPATH, 
                                            value='//html/body/div[5]/div/div[5]/div[1]/div/div[2]/div[2]/div[3]/div[2]/div[2]/ul[2]/li[2]/a[@id="1F"]'
                                            ).click()
                        

                        element = driver.find_element(by=By.XPATH,
                                                      value='//html/body/div[5]/div/div[5]/div[1]/div/div[2]/div[2]/div[8]/a[2][@id="qr_submit_id" and @class="btn92s"]'
                                                      )   # 这个是因为btn92s是可点击的
                        element.click()
                        
                        print(f"{conf.trainnumber}次列车抢票成功，请尽快在10分钟内支付！")
                        return
            except Exception as e:
                print("处理票务时发生错误：", e)
                continue

        # 极短暂延迟，避免CPU占用过高
        time.sleep(0.001)
 
 
if __name__ == '__main__':
    # 有关车票的配置信息保存在该类里
    # 请事先在config.py里填好相关信息
    conf = Config()
 
    url = 'https://www.12306.cn/index/'

    # 用chrome浏览器打开网页
    driver = webdriver.Chrome()
    get_ticket(conf, driver, url)
    time.sleep(10)
    driver.quit()
