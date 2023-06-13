import random
import time

import common.constant as Constant
from threading import Timer
from common.helper import sleep_for, get_random_number, ensure_wait_for_element, type_text, ensure_find_element
import common.helper as Helper
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, \
    ElementNotInteractableException
from youtube.features import *


def play_video(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, '[title^="Pause (k)"]')
    except WebDriverException:
        try:
            driver.find_element(
                By.CSS_SELECTOR, 'button.ytp-large-play-button.ytp-button').send_keys(Keys.ENTER)
        except WebDriverException:
            try:
                driver.find_element(
                    By.CSS_SELECTOR, '[title^="Play (k)"]').click()
            except WebDriverException:
                try:
                    driver.execute_script(
                        "document.querySelector('button.ytp-play-button.ytp-button').click()")
                except WebDriverException:
                    pass

    skip_again(driver)


def play_music(driver):
    try:
        driver.find_element(
            By.XPATH, '//*[@id="play-pause-button" and @title="Pause"]')
    except WebDriverException:
        try:
            driver.find_element(
                By.XPATH, '//*[@id="play-pause-button" and @title="Play"]').click()
        except WebDriverException:
            driver.execute_script(
                'document.querySelector("#play-pause-button").click()')

    skip_again(driver)


def scroll_search(driver, video_id):
    msg = None
    i = 0
    for i in range(1, 11):
        try:
            xpath = f'//ytd-item-section-renderer[{i}]'
            ensure_wait_for_element(driver, xpath)

            if driver.find_element(By.XPATH, f'//ytd-item-section-renderer[{i}]').text == 'No more results':
                msg = 'failed'
                break
            # find_video = driver.find_element(By.XPATH, xpath).find_element(
            #     By.XPATH, f'//*[@title="{video_title}"]')
            find_video = driver.execute_script(f"return document.querySelector(\"a[href='/watch?v={video_id}']\");")
            if not find_video:
                raise NoSuchElementException()
            driver.execute_script("arguments[0].scrollIntoViewIfNeeded();", find_video)
            sleep(1)
            bypass_popup(driver)
            ensure_click(driver, find_video)
            msg = 'success'
            break
        except NoSuchElementException:
            sleep(randint(2, 5))
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located(
                (By.TAG_NAME, 'body'))).send_keys(Keys.CONTROL, Keys.END)

    if i == 10:
        msg = 'failed'

    return msg


def search_video(driver, keyword, video_id):
    search_xpath = '//*[@id="search-input"]/input'
    search_icon_button = '//button[@id=\"search-icon-legacy\"]'
    try:
        type_text(driver, keyword, search_xpath, search_icon_button)
    except NoSuchElementException:
        try:
            search_xpath = '//*[@id="search"]'
            type_text(driver, keyword, search_xpath, search_icon_button)
        except WebDriverException:
            raise
    except WebDriverException:
        try:
            bypass_popup(driver)
            type_text(driver, keyword, search_xpath, search_icon_button)
        except WebDriverException:
            raise Exception(
                "Slow internet speed or Stuck at recaptcha! Can't perform search keyword")

    msg = scroll_search(driver, video_id)

    if msg == 'failed':
        bypass_popup(driver)
        Helper.click_referral(driver, f'https://www.youtube.com/watch?v={video_id}')

    return msg


def like(driver):
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located(
        (By.TAG_NAME, 'body'))).send_keys(Keys.HOME)
    # Depends on the proxy YouTube will have different UI on the like button
    try:
        button_path = '//*[@id="segmented-like-button"]/ytd-toggle-button-renderer/yt-button-shape/button'
        button_element = Helper.ensure_find_element(driver, button_path)
        pressed = button_element.get_attribute("aria-pressed")
        if pressed == 'true':
            pass
        else:
            Helper.ensure_click(driver, button_path)
    except NoSuchElementException:
        button_path = '//*[@id="top-level-buttons-computed"]/ytd-toggle-button-renderer/a/yt-icon-button/button'
        button_element = Helper.ensure_find_element(driver, button_path)
        pressed = button_element.get_attribute("aria-pressed")
        if pressed == 'true':
            pass
        else:
            Helper.ensure_click(driver, button_path)


def dislike(driver):
    WebDriverWait(driver, Constant.TRANSITION_TIMEOUT).until(EC.visibility_of_element_located(
        (By.TAG_NAME, 'body'))).send_keys(Keys.HOME)
    try:
        button_path = '//*[@id="segmented-dislike-button"]/ytd-toggle-button-renderer/yt-button-shape/button'
        button_element = Helper.ensure_find_element(driver, button_path)
        pressed = button_element.get_attribute("aria-pressed")
        if pressed == 'true':
            pass
        else:
            Helper.ensure_click(driver, button_path)
    except NoSuchElementException:
        # Depends on the proxy YouTube will have different UI on the dislike button
        pass


def like_or_dislike(driver):
    percentage = float(random.randrange(0, 100))
    if 0 <= percentage < Constant.LIKE_PERCENTAGE:
        like(driver)
    elif Constant.LIKE_PERCENTAGE <= percentage < Constant.LIKE_PERCENTAGE + Constant.DISLIKE_PERCENTAGE:
        dislike(driver)
    else:
        pass


def comment(driver):
    comment_percentage = float(random.randrange(0, 100)) < float(Constant.COMMENT_PERCENTAGE)
    if comment_percentage:
        scroll_though_comments(driver)
        try:
            comment_click_path = "//*[@id=\"placeholder-area\"]"
            comment_click_element = ensure_find_element(driver, comment_click_path)
            scroll_to_element(driver, comment_click_element)
            Helper.ensure_click(driver, comment_click_path)
            comment_box_xpath = "//*[@id=\"contenteditable-root\"]"
            content = choice(Constant.comment_content)
            type_text(driver, content, comment_box_xpath, True)
            commit_path = '//*[@id="submit-button"]'
            Helper.ensure_click(driver, commit_path)
        except NoSuchElementException:
            # In  case when first comment need accept rule
            pass


def scroll_though_comments(driver):
    sleep_for(Constant.MEDIUM_WAIT)
    WebDriverWait(driver, get_random_number(Constant.SHORT_WAIT)).until(EC.visibility_of_element_located(
        (By.TAG_NAME, 'body'))).send_keys(Keys.ARROW_DOWN, Keys.ARROW_DOWN)
    try:
        comment_section = driver.find_element(By.ID, "comments")
        if comment_section.is_displayed():
            scroll_to_element(driver, comment_section)
    except NoSuchElementException:
        pass


def check_home_page(driver, channels):
    for j in range(randint(1, 3)):
        sleep_for(Constant.SHORT_WAIT)
        WebDriverWait(driver, get_random_number(Constant.VERY_SHORT_WAIT)).until(EC.visibility_of_element_located(
            (By.TAG_NAME, 'body'))).send_keys(Keys.CONTROL, Keys.END)

    video_list = driver.find_elements(By.ID, "dismissible")
    for i in video_list:
        channel_element = None
        try:
            channel_element = i.find_element(By.CLASS_NAME, "ytd-channel-name")
            channel_element = channel_element.find_element(By.TAG_NAME, "a")
            channel_url = channel_element.get_attribute('href')
            if list(filter(lambda x: x in f"{channel_url}", channels)):
                sleep_for(Constant.SHORT_WAIT)
                scroll_to_element(driver, channel_element)
                sleep_for(Constant.MEDIUM_WAIT)
                i.find_element(By.ID, "thumbnail").click()
                return True
        except NoSuchElementException:
            # Avoid cases where text -> a.href does not exist
            pass
        except ElementClickInterceptedException:
            sleep_for(Constant.LONG_WAIT)
            scroll_to_element(driver, channel_element)
            sleep_for(Constant.MEDIUM_WAIT)
            i.find_element(By.ID, "thumbnail").click()
    return False


def check_suggested_videos(driver, channel_names):
    for j in range(randint(4, 8)):
        sleep_for(Constant.SHORT_WAIT)
        WebDriverWait(driver, get_random_number(Constant.VERY_SHORT_WAIT)).until(EC.visibility_of_element_located(
            (By.TAG_NAME, 'body'))).send_keys(Keys.CONTROL, Keys.END)

    video_list = driver.find_elements(By.ID, "dismissible")
    for i in video_list:
        channel_element = None
        try:
            channel_element = i.find_element(By.CLASS_NAME, "ytd-channel-name")
            if list(filter(lambda x: x == f"{channel_element.text}", channel_names)):
                sleep_for(Constant.SHORT_WAIT)
                scroll_to_element(driver, channel_element)
                sleep_for(Constant.SHORT_WAIT)
                channel_element.click()
                return True
        except NoSuchElementException:
            # Avoid cases where dismissible -> text does not exist
            pass
        except ElementClickInterceptedException:
            sleep_for(Constant.LONG_WAIT)
            scroll_to_element(driver, channel_element)
            sleep_for(Constant.MEDIUM_WAIT)
            i.find_element(By.ID, "thumbnail").click()
    return False


def check_description_link(driver, url):
    # NOTE: do not try to move scroll -> sleep -> click out of try catch block
    try:
        see_more_xpath = "//*[@id=\"more\"]/yt-formatted-string"
        see_more = driver.find_elements(By.XPATH, see_more_xpath)[0]
        scroll_to_element(driver, see_more)
        sleep_for(Constant.SHORT_WAIT)
        see_more.click()
    except (IndexError, ElementNotInteractableException, Exception):
        see_more_xpath = "//*[@id=\"expand\"]"
        see_more = driver.find_element(By.XPATH, see_more_xpath)
        scroll_to_element(driver, see_more)
        sleep_for(Constant.SHORT_WAIT)
        see_more.click()

    sleep_for(Constant.SHORT_WAIT)
    try:
        xpath = "//*[@id=\"description\"]/yt-formatted-string/a[1]"
        website_link = driver.find_element(By.XPATH, xpath)
        scroll_to_element(driver, website_link)
        sleep_for(Constant.SHORT_WAIT)
        website_link.click()
    except (Exception, NoSuchElementException):
        driver.get(url)


def view(time_video):
    percentage = float(random.randrange(0, 100))
    if 0 <= percentage < 20:
        return time_video * 0.1, time_video * 0.3
    elif 20 <= percentage < 60:
        return time_video * 0.3, time_video * 0.6
    else:
        return time_video * 0.85, time_video


def schedule_take_action(driver, action, min_time, max_time):
    waiting_time = randint(int(min_time), int(max_time))
    Timer(waiting_time, action, args=[driver]).start()
    return waiting_time
