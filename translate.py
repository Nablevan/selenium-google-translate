import time
from selenium import webdriver

text = 'The invention relates to a medication container (1) having a base module (2) having multiple package \
compartments (3) for holding and dispensing medication packages, and having a medication dispensing element \
(4) having multiple medication compartments (5) for holding and dispensing unpackaged medications, in particular \
tablets, wherein the medication dispensing element (4) is or can be fixed to, preferably on, the base module \
(2), in particular by means of an nondestructively detachable medication dispensing element connecting device \
(6), wherein the base module (2) has at least one nondestructively detachable module connection device \
(7) for fixing at least one additional module (8).'

# url = 'https://translate.google.cn'
url = 'https://translate.google.cn/#view=home&op=translate&sl=zh-CN&tl=en'
browser = webdriver.Chrome()
browser.get(url)

sourse = browser.find_element_by_id('source')
sourse.send_keys(text)
time.sleep(3)
result = browser.find_element_by_css_selector('.result-shield-container>.translation>span')
print(text)
print(result.text)
# time.sleep(5)
browser.quit()
