from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from config import Config     # 信息保存在config.py里
import time
import random


# 这个函数用来判断是否有预订按钮是非常快的，自己尝试的其他方法都很慢~(^T^)~
# 判断是否有预订按钮非常影响速度，如果有人感觉自己写的代码慢，大概率是因为这个
def check_available_tickets():
    # 使用 JavaScript 直接获取符合条件的车次信息
    tickets_info = driver.execute_script("""
        const tickets = [];
        const rows = document.querySelectorAll('#queryLeftTable tr:not([style*="display: none"])');
        
        for (const row of rows) {
            const trainNumber = row.querySelector('.number')?.textContent;
            const bookingBtn = row.querySelector('.btn72');
            const ywStatus = row.querySelector('td:nth-child(8)')?.textContent;
            
            if (bookingBtn && trainNumber && ywStatus) {
                tickets.push({
                    trainNumber: trainNumber,
                    hasButton: true,
                    status: ywStatus
                });
            }
        }
        return tickets;
    """)
    return tickets_info


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
 
    start = time.time()

    while True:
        current_time = time.time()

        # 如果查询按钮可用，点击查询
        if query_tag.get_attribute('class') == "btn92s":
            driver.execute_script("arguments[0].click();", query_tag)
      
        # 使用新的车票查询方法
        available_tickets = check_available_tickets()
        
        if not available_tickets:
            print("未找到预订按钮，继续等待...")
            time.sleep(random.uniform(0.097, 0.345))
            continue
            
        print("找到可预订车次！")
        
        # 直接在 JavaScript 返回的数据中查找目标车次
        target_ticket = next((ticket for ticket in available_tickets 
                            if ticket['trainNumber'] == conf.trainnumber 
                            and "候补" not in ticket['status']), None)
        
        if target_ticket:
            # 使用 JavaScript 直接点击对应车次的预订按钮
            driver.execute_script("""
                const rows = document.querySelectorAll('#queryLeftTable tr:not([style*="display: none"])');
                for (const row of rows) {
                    if (row.querySelector('.number')?.textContent === arguments[0]) {
                        row.querySelector('.btn72').click();
                        break;
                    }
                }
            """, conf.trainnumber)
            
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
