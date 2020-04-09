import time
import os
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
    # print('*******************js********************\n' + js)
    bw.execute_script(js)    # 通过js输入，提高速度

    WebDriverWait(bw, 10, poll_frequency=0.01).until(EC.staleness_of(re))

    locator = (By.CSS_SELECTOR, '.result-shield-container')
    WebDriverWait(bw, 10, poll_frequency=0.01).until(EC.presence_of_element_located(locator))
    try:
        r = bw.find_element_by_css_selector('.result-shield-container>.translation')
    except selenium.common.exceptions.NoSuchElementException:
        r = bw.find_element_by_css_selector('.result-shield-container>.translation>span')
    # print('in: ' + txt)
    # print(r.text)
    return r.text


def translate_xml(xml_file: str, bw: webdriver.Chrome):
    with open(xml_file, 'r', encoding='utf-8') as f:
        file = f.read()
        while file[-1] is not '>':
            file = file[:-1]

    temp = 'temp.xml'
    with open(temp, 'w', encoding='utf-8') as w:        # 创建临时文件
        w.write(file)
    tree = parse(temp)
    os.remove(temp)
    root = tree.documentElement   # 根节点
    txt_list = xml_to_list(tree)
    temp_list = txt_list.copy()
    result_list = translate_list(txt_list, bw)  # 翻译列表
    set_node_text(root, result_list)  # 写入翻译结果
    file_name = os.path.split(xml_file)[-1]
    # file_name = os.path.join(result_path, file_name)
    # file_name = file_name.split('.')[0] + '-trans.xml'
    with open(file_name, 'w', encoding='utf-8')as f:
        tree.writexml(f, encoding='utf-8')


def xml_to_list(xml_tree):   # 获取待翻译的文字列表
    source = []
    root = xml_tree.documentElement
    get_node_text(root, source)
    return source


def get_node_text(node, txt_list: list):
    try:
        name = node.getAttribute('name')
        if name is not '':
            txt_list.append(name)
    except AttributeError:
        pass
    if node.hasChildNodes():
        for n in node.childNodes:
            get_node_text(n, txt_list)
    try:
        txt = node.data
        txt = txt.strip()
    except AttributeError:
        txt = ''
    if not (txt is '\n' or txt is ''):
        txt_list.append(txt)
        # print('get: ' + txt)


def set_node_text(node, txt_list: list):
    try:
        name = node.getAttribute('name')
        if name is not '':
            node.setAttribute('name', txt_list.pop(0))
    except AttributeError:
        pass
    if node.hasChildNodes():
        for n in node.childNodes:
            set_node_text(n, txt_list)
    try:
        txt = node.data
        txt = txt.strip()
    except AttributeError:
        txt = ''
    if not (txt is '\n' or txt is ''):
        node.data = txt_list.pop(0)


def translate_list(txt_list: list, bw: webdriver.Chrome):
    result_list = []
    buffer = ''
    while txt_list.__len__() > 0:
        temp_txt = txt_list[0]
        # print('add temp:' + temp_txt)
        if buffer.__len__() + len(temp_txt) + 1 < 5000:         # 加1是因为\n也算一个字符
            buffer = buffer + temp_txt + '\\n'
            txt_list.pop(0)
        else:   # 将要超过5000时开始翻译
            # print('*******************')
            # print(buffer, end='')
            # print('*******************')
            result_txt = translate(bw, buffer.strip())
            result_list += result_txt.split('\n')
            buffer = ''  # 重置buffer
    if buffer.__len__() > 0:
        # print('last*******************')
        # print(buffer, end='')
        # print('*******************last')
        result_txt = translate(bw, buffer.strip())
        result_list += result_txt.split('\n')
    return result_list
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


# file_path = r"D:\lkx\Python-code\seleniumtest\22170\0 - 副本.xml"
file_path = r"D:\lkx\Python-code\seleniumtest\22170\2239.xml"

# path = argv[1]
# result_path = os.path.join(path, 'result')
# if not os.path.exists(result_path):
#     os.mkdir(result_path)

start_time = time.time()
translate_xml(file_path, browser)
end_time = time.time()
print('use %s seconds' % (end_time-start_time))
# xml_list = os.listdir(path)
# for name in xml_list:
#     start_time = time.time()
#     translate_xml(os.path.join(path, name), browser)
#     end_time = time.time()
#     print('use %s seconds' % (end_time-start_time))
browser.quit()




