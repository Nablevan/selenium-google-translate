import asyncio
import time
import xml
import os
import pyperclip
import selenium
import traceback
import logging
import warnings
import threading
import multiprocessing
from sys import argv
from multiprocessing import Process
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from xml.dom.minidom import parse


def translate(bw: webdriver.Chrome, txt: str):
    re = bw.find_element_by_css_selector('.result-shield-container')

    js = "element = document.getElementById('source');" \
         "element.value = '" + txt + "';"
    # print('*******************js********************\n' + js)

    bw.execute_script(js)    # 通过js输入，提高速度

    WebDriverWait(bw, 30, poll_frequency=0.01).until(EC.staleness_of(re))

    locator = (By.CSS_SELECTOR, '.result-shield-container')
    WebDriverWait(bw, 30, poll_frequency=0.01).until(EC.presence_of_element_located(locator))
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
        while file[-1] is not '>':     # 去除末尾的空格
            file = file[:-1]

    temp = os.path.join(path, 'temp-%s.xml' % threading.current_thread().name)
    with open(temp, 'w', encoding='utf-8') as w:        # 创建临时文件
        w.write(file)
    tree = parse(temp)

    os.remove(temp)       # 删除临时文件
    root = tree.documentElement   # 根节点
    txt_list = xml_to_list(tree)
    result_list = translate_list(txt_list, bw)  # 翻译列表
    set_node_text(root, result_list)  # 写入翻译结果

    file_name = os.path.split(xml_file)[-1]
    file_name = os.path.join(result_path, file_name)

    # with open(file_name, 'w', encoding='utf-8')as f:
    #     tree.writexml(f, encoding='utf-8')
    return [file_name, tree]


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
        temp_txt = str(temp_txt).replace('"', '\\"').replace("'", "\\'")
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


async def main(list_temp: list):

    # url = 'https://translate.google.cn'
    url = 'https://translate.google.cn/#view=home&op=translate&sl=zh-CN&tl=en'
    browser = webdriver.Chrome()
    browser.implicitly_wait(3)
    browser.get(url)
    s = browser.find_element_by_id('source')
    s.send_keys('开始')    # 初始化浏览器

    if not os.path.exists(result_path):   # 创建result文件夹用于存放结果
        os.mkdir(result_path)

    logging.basicConfig(filename=os.path.join(result_path, 'log.txt'), level=logging.ERROR,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    xml_list = os.listdir(path)
    result_list = os.listdir(result_path)
    begin_time = time.time()
    num = 0
    failed = open(os.path.join(result_path, 'failed.txt'), 'w', encoding='utf-8')
    list_to_write = list_temp
    for name in xml_list:
        if name in result_list:  # 跳过已经翻译的文件
            continue
        if not os.path.isfile(os.path.join(path, name)):  # 跳过文件夹
            continue
        if name.split('.')[-1] != 'xml':  # 跳过非xml文件
            continue
        start_time = time.time()
        try:
            target = translate_xml(os.path.join(path, name), browser)

            while True:
                await asyncio.sleep(1)
                if list_to_write.__len__() < 100:
                    list_to_write.append(target)
                    break

        except Exception:     # 记录错误文件和信息
            if os.path.exists(os.path.join(result_path, name)):
                os.remove(os.path.join(result_path, name))
            failed.write(os.path.join(path, name) + '\n')
            warnings.warn(name + ' error', RuntimeWarning)
            logging.error(os.path.join(path, name))
            logging.error(traceback.format_exc())
            continue
        num += 1
        end_time = time.time()
        average = (end_time - begin_time) / num
        print(name + ' use %.2f seconds ' % float(end_time - start_time) + 'average: %.2f seconds' % average)
    failed.close()
    browser.quit()


async def write_xml(list_temp: list):
    count = 0
    while True:
        await asyncio.sleep(1)
        count += 1
        while list_temp.__len__() > 0:
            start = time.time()
            count = 0
            temp = list_temp.pop(0)
            with open(temp[0], 'w', encoding='utf-8')as f:
                temp[1].writexml(f, encoding='utf-8')
            print('done writing', temp[0], 'in {:.5f} secs'.format(time.time() - start))
        if count > 5:
            # event_loop = asyncio.get_running_loop()
            # event_loop.stop()
            return


def write_xml(list_temp: list):
    while threads.__len__() > 0:    # 当有爬虫进程还活着
        time.sleep(1)
        while list_temp.__len__() > 0:
            # start = time.time()
            temp = list_temp.pop(0)
            with open(temp[0], 'w', encoding='utf-8')as f:
                temp[1].writexml(f, encoding='utf-8')
            # print('done writing', temp[0], 'in {:.5f} secs'.format(time.time() - start))
    # 死光以后
    while list_temp.__len__() > 0:
        # start = time.time()
        temp = list_temp.pop(0)
        with open(temp[0], 'w', encoding='utf-8')as f:
            temp[1].writexml(f, encoding='utf-8')
        # print('done writing', temp[0], 'in {:.5f} secs'.format(time.time() - start))


def main_multi_thread(sub_xml_list, list_temp: list):
    # url = 'https://translate.google.cn'
    url = 'https://translate.google.cn/#view=home&op=translate&sl=zh-CN&tl=en'
    browser = webdriver.Chrome()
    browser.implicitly_wait(3)
    browser.get(url)
    browser.minimize_window()

    s = browser.find_element_by_id('source')
    s.send_keys('开始')  # 初始化浏览器

    logging.basicConfig(filename=os.path.join(result_path, 'log.txt'), level=logging.ERROR,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    result_list = os.listdir(result_path)
    begin_time = time.time()
    num = 0
    with open(os.path.join(result_path, 'failed.txt'), 'a', encoding='utf-8') as failed:
        for name in sub_xml_list:
            if name in result_list:  # 跳过已经翻译的文件
                continue
            if not os.path.isfile(os.path.join(path, name)):  # 跳过文件夹
                continue
            if name.split('.')[-1] != 'xml':  # 跳过非xml文件
                continue
            start_time = time.time()
            try:
                result = translate_xml(os.path.join(path, name), browser)
                list_temp.append(result)
            except Exception:     # 记录错误文件和信息
                if os.path.exists(os.path.join(result_path, name)):
                    os.remove(os.path.join(result_path, name))
                failed.write(os.path.join(path, name) + '\n')
                warnings.warn(name + ' error', RuntimeWarning)
                logging.error(os.path.join(path, name))
                logging.error(traceback.format_exc())
                continue
            num += 1
            end_time = time.time()
            average = (end_time - begin_time) / num
            print(threading.current_thread().name + ' ' + name + ' use %.2f seconds ' % float(end_time - start_time)
                  + 'average: %.2f seconds' % average)
    threads.remove(threading.current_thread().getName())
    browser.quit()


if __name__ == '__main__':
    # 单线程
    # path = argv[1]
    # fold = os.path.split(path)[-1]
    # result_path = os.path.join('', '{}-result'.format(fold))
    # l: list = []
    # task1 = main(l)
    # task2 = write_xml(l)
    #
    # loop = asyncio.get_event_loop()
    #
    # asyncio.get_event_loop().run_until_complete(asyncio.gather(task1, task2))
    #
    # print('done')

    # 多线程

    path = argv[1]
    fold = os.path.split(path)[-1]
    result_path = os.path.join('', '{}-result'.format(fold))
    if not os.path.exists(result_path):   # 创建result文件夹用于存放结果
        os.mkdir(result_path)

    xml_list = os.listdir(path)
    num_thread = 7
    num_xml = xml_list.__len__()//num_thread
    n = 0
    temp_list = []
    threads = []
    while n < num_thread - 1:
        sub_list = []
        for x in range(num_xml):
            sub_list.append(xml_list.pop(0))

        t = threading.Thread(target=main_multi_thread, name='thread-%d' % n, args=(sub_list, temp_list))
        t.start()
        threads.append(t.getName())
        n += 1
    t = threading.Thread(target=main_multi_thread, name='thread-%d' % n, args=(xml_list, temp_list))
    t.start()
    threads.append(t.getName())
    t = threading.Thread(target=write_xml, name='thread-write', args=(temp_list,))
    t.start()
    t.join()
    print('done')

