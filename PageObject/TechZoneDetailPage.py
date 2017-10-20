from Base.BaseStatistics import countSum, countInfo
from Base.BaseYaml import getYam
from Base.BaseOperate import OperateElement
import time
from Base.BaseElementEnmu import Element
from selenium.webdriver.support.ui import WebDriverWait
import selenium.common.exceptions
class TechZoneDetail:
    '''
    kwargs: WebDriver driver, String path(yaml配置参数)
    '''
    def __init__(self, **kwargs):
        self.driver = kwargs["driver"]
        self.path = kwargs["path"]
        self.operateElement = OperateElement(self.driver)
        self.isOperate = True
        test_msg = getYam(self.path)
        self.testInfo = test_msg["testinfo"]
        self.testCase = test_msg["testcase"]
        self.testcheck = test_msg["check"]
        self.getValue = ""
    '''
     logTest 日记记录器
    '''
    def operate(self, logTest):
        for item in self.testCase:
            result = self.operateElement.operate(item, self.testInfo, logTest) # 执行操作
            if not result:
                print("操作失败")
                self.testInfo[0]["msg"] = "执行过程中失败，请检查元素是否存在" + item["element_info"]
                self.isOperate = False
                break
            if item.get("swipe", "0") == "up":
                self.operateElement.swipeToUp(n=1)

            elif item.get("operate_type", "0") == Element.GET_VALUE: # 取列表中某个元素到文本
                self.getValue = result
            if item.get("is_time", "0") != "0":
                time.sleep(int(item["is_time"]))
    '''
    logTest： 日志记录
    devices 设备名
    '''
    def checkPoint(self, caseName, logTest, devices):
        result = False
        if self.isOperate:
            self.operateElement.switchToWebview()
            resp = self.operateElement.operate(self.testcheck, self.testInfo, logTest)
            if not resp:
                print("查找元素" + self.testcheck["element_info"] + "失败")
                self.isOperate = False
                self.testInfo[0]["msg"] = "请检查元素" + self.testcheck["element_info"] + "是否存在"
                result = False
            elif resp == self.getValue: # 对比列表中到一条数据和详情页数据是否相同
                result = True
            else:
                result = False
                self.testInfo[0]["msg"] = "详情页当前值为="+resp+";列表获取到值为："+self.getValue + "。两者值不相等"
        self.driver.switch_to.context("NATIVE_APP")  # 切换到native,还原
        countSum(result)
        countInfo(result=result, testInfo=self.testInfo, caseName=caseName, driver=self.driver,
                  logTest=logTest, devices=devices, testCase=self.testCase, testCheck=self.testcheck)
        return result
