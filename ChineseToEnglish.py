import time
import xml
import os
import pyperclip
import selenium
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from xml.dom.minidom import parse


def translate(bw: webdriver.Chrome, txt: str):
    re = bw.find_element_by_css_selector('.result-shield-container')

    js = "element = document.getElementById('source');" \
         "element.value = '" + txt + "';"
    bw.execute_script(js)    # 通过js输入，提高速度

    WebDriverWait(bw, 10, poll_frequency=0.01).until(EC.staleness_of(re))

    locator = (By.CSS_SELECTOR, '.result-shield-container')
    WebDriverWait(bw, 10, poll_frequency=0.01).until(EC.presence_of_element_located(locator))
    try:
        r = bw.find_element_by_css_selector('.result-shield-container>.translation>span')
    except selenium.common.exceptions.NoSuchElementException:
        r = bw.find_element_by_css_selector('.result-shield-container>.translation')
    print('in: ' + txt)
    print(r.text)
    return r.text


def translate_xml(xml_file: str, bw: webdriver.Chrome):
    tree = parse(xml_file)
    root = tree.documentElement
    translate_node(root, bw)
    file_name = os.path.split(xml_file)[-1]
    file_name = file_name.split('.')[0] + '-trans.xml'
    with open(file_name, 'w')as f:
        tree.writexml(f, encoding='utf-8')


def translate_node(node: xml.dom.minidom.Node, bw: webdriver.Chrome):
    try:
        name = node.getAttribute('name')
        if name is not '':
            node.setAttribute('name', translate(bw, name))
    except AttributeError:
        pass
    if node.hasChildNodes():
        for n in node.childNodes:
            translate_node(n, bw)
    try:
        txt = node.data
        txt = txt.strip()
    except AttributeError:
        txt = ''
    if not (txt is '\n' or txt is ''):
        node.data = translate(bw, txt)


# text = '天王盖地虎，宝塔镇河妖'
#
# domTree = parse(r"D:\lkx\Python-code\seleniumtest\22170\0 - 副本.xml")
# rootNode = domTree.documentElement


# url = 'https://translate.google.cn'
url = 'https://translate.google.cn/#view=home&op=translate&sl=zh-CN&tl=en'
browser = webdriver.Chrome()
browser.implicitly_wait(3)
browser.get(url)
s = browser.find_element_by_id('source')
s.send_keys('开始')

start_time = time.time()
file_path = r"D:\lkx\Python-code\seleniumtest\22170\0 - 副本.xml"
translate_xml(file_path, browser)

end_time = time.time()
# print(text)
# print(translate(browser, text))
# time.sleep(5)
print('use %s seconds' % (end_time-start_time))
browser.quit()




