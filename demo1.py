from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# s = Service(executable_path='venv/chromedriver.exe')
# driver = webdriver.Chrome(service=s)
driver = webdriver.Chrome(executable_path='venv/chromedriver.exe')
driver.get('https://tiki.vn/dien-thoai-may-tinh-bang/c1789')


# products = driver.find_elements(By.CSS_SELECTOR, '.product-item')
# driver.find_element(By.CLASS_NAME, 'product-item').click()
elements = driver.find_elements(By.CSS_SELECTOR, '#__next > div .product-item')
driver.save_screenshot('test.png')
for e in elements[:10]:
    try:
        # driver.find_element(By.CSS_SELECTOR, '.product-item').click()
        print(e.find_element(By.CSS_SELECTOR, '.name h3').text)
        print(e.find_element(By.CSS_SELECTOR, '.price-discount .price-discount__price').text)
        links = [e.get_attribute('href')]
        print(links)
    except:
        pass


# driver.get(links[0])
#
# driver.execute_script("window.scroll(0, 10000)")
# driver.implicitly_wait(5)
# driver.save_screenshot('test2.png')





# for p in products[:5]:
#     print(p.find_element(By.CSS_SELECTOR, '.name h3').text)
#     driver.find_element(By.CLASS_NAME, 'product-item').click()



driver.quit()
