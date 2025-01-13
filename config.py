class Config:
    # 类不需要定义的太复杂，只需要定义一些属性即可
    
    fromstation = '北京'             # 出发地
    destination = '乌鲁木齐南'        # 目的地
    date = '2025-01-18'             # 日期   // 写成标准形式 2025-01-02 而不是 2025-1-2
    passengernum = '0'              # 乘车人 //第一个乘车人是 0  

    ## 适用于 12306pro_v2.py
    trainnumber = ['Z179','G333']    # 如果第一个车次没抢到会抢第二个车次(T_T)  
    stu_seat = 1                     # 0: 不用学生票  1：学生票   # 适用于 12306pro_v2.py
    #  Z，K开头的车次要按需求填Z_seat
    Z_seat = 4                       # 1：硬座 ， 3：硬卧， 4：软卧   // 没找到软座

    # trainnumber = 'G333'          <== 除12306pro_v2.py之外代码的应用格式

