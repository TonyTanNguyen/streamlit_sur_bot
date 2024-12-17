from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

import shutil

import time
import streamlit as st
import re
import os
import datetime
import json
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from concurrent.futures import ThreadPoolExecutor
import random

def find_question(browser):
    question_css_list = [
    '[for="profilequestion-value"]',
    '[class="questionPreview__text recruitment__questionText MuiBox-root css-0"]',
    '[class="control-label has-star"]'
    ]
    for selector in question_css_list:
        try:
            # Try finding the element with the current selector
            element = browser.find_element(By.CSS_SELECTOR, selector)
            return element
        except NoSuchElementException:
            continue
    # If no element is found, return None
    return None



def isRadio(browser):
    #Check if radio button
    radios = browser.find_elements(By.CSS_SELECTOR,'[type="radio"]')
    if len(radios) > 0:
        return radios
    return False
def next_button_available(browser):
    #check button state if clickable
    try:
        next = WebDriverWait(browser, 20).until(lambda d: d.find_element(By.CSS_SELECTOR, '[class="btn btn-primary form-control recruitment-btn btnPreviewNext questionPreview__btn_right"]').get_attribute("disabled") is None)
        next_button = browser.find_elements(By.CSS_SELECTOR,'[class="btn btn-primary form-control recruitment-btn btnPreviewNext questionPreview__btn_right"]')
    except:
        next = WebDriverWait(browser, 20).until(lambda d: d.find_element(By.CSS_SELECTOR, '[class="btn btn-primary form-control recruitment-btn"]').get_attribute("disabled") is None)
        next_button = browser.find_elements(By.CSS_SELECTOR,'[class="btn btn-primary form-control recruitment-btn"]')
    if len(next_button) > 0:
        return next_button[0]
    return False

def isCheckbox(browser):
    #Check if radio button
    checkboxes = browser.find_elements(By.CSS_SELECTOR,'[type="checkbox"]')
    if len(checkboxes) > 0:
        return checkboxes
    return False

def isAnswerText(browser):
    #Check if radio button
    textFields = browser.find_elements(By.CSS_SELECTOR,'[class="form-control"]')
    inputTFs = [i for i in textFields if i.get_attribute("type")=="text"]
    if len(inputTFs) == 1:
        print("Single Text Field")
        return inputTFs[0]
    return False

def isMultipleTextField(browser):
    fields = browser.find_elements(By.CSS_SELECTOR,'[class="form-control"]')
    if len(fields) > 1:
        return fields
    return False

def isRankingBlock(browser):
    
    blocks = browser.find_elements(By.CSS_SELECTOR,'[class="fa fa-square-o "]')
    if len(blocks) > 0:
        return blocks
    return False

def isThereTextField(browser):
    inputField = browser.find_elements(By.CSS_SELECTOR,'[class="form-control"]')
    if len(inputField) > 1:
        return inputField[0]
    return False
    
def answer_radio(browser,radios,next_button):
    textField =  isThereTextField(browser)
    random_option = random.choice(radios)
    random_option.click()

    #check if last option might be asked for input text field
    if random_option == radios[-1]:
        #check if text Field
        if textField:
            answer_input(browser, textField, next_button)
    next_button.click()


def answer_checkbox(browser, checkboxes ,next_button, ranking = False):
    if ranking:
        remove_selection = browser.find_element(By.CSS_SELECTOR, '[class="btn btn-primary form-control recruitment-btn"]')
        remove_selection.click()
        
    textField = isThereTextField(browser)
    #random how many options to choose
    quant = random.randrange(1, len(checkboxes))
    choices = random.choices(checkboxes,k=quant)
    #uncheck all checkbox:
    for i in checkboxes:
        if i.is_selected():
            i.click()
    for i in choices:
        i.click()
        if i == choices[-1]:
            if textField:
                answer_input(browser, textField, next_button)
    next_button.click()


def isTextInputError(pre_question_text , browser):
    #is next button available?
    next_button_available(browser)

    #Get current question
    cur_quesiton = find_question(browser)
    cur_question_text = cur_question.text
    
    print("Pre quest: ",pre_question_text)
    print("Current quest: ",cur_question_text)
    if pre_question_text == cur_question_text:
        return True
    return False

def isError(browser):
    # next_button_available(browser)
    error = browser.find_elements(By.CSS_SELECTOR,'[class="help-block"]')
    content = ""
    for i in error:
        content += i.text
    if content != '':
        
        print(f'Error! {content}')
        return True
    # print("No error")
    return False
    
def answer_input(browser , element , next_button):
    #is next button available?
    next_button = next_button_available(browser)
    answers = ["Blah Blah","20","nptan111@gmail.com"]


    pre_question = find_question(browser)
    print(pre_question.text)
    pre_question_text = pre_question.text
    for answer in answers:
        print(f"Aswer: {answer}")
        element.clear()
        element.send_keys(answer)

        #Click next
        next_button.click()
        
        #check button state if clickable
        next_button_available(browser)
        
        #Check if there is error, the new loaded page if current question is the same with previous => error
        error = isError(browser)
        if error:
            continue
        break
        

#define a dict of options based on the error message
def answer_multi_field(browser):
    # next_button = browser.find_element(By.CSS_SELECTOR, '[class="btn btn-primary form-control recruitment-btn btnPreviewNext questionPreview__btn_right"]')
    next_button = next_button_available(browser)
    text_options = {
        "text": "Blahblah",
        "number": "1",
        "email":"nptan111@gmail.com"
    }
    def correct_input_type(error_text):
        if "email" in error_text:
            return "email"
        elif "number" in error_text:
            return "number"
        else:
            return 'email'
    
    
    
    #Get the parent body of all fields
    fields_container = browser.find_element(By.CSS_SELECTOR,'[class="questionPreview__answer recruitment__answerWrap "')
    #Get all rows inside the parent body
    rows = fields_container.find_elements(By.CSS_SELECTOR,'[class="row"]')
    #create dic of {Field name: Selenium ele} of only text input fields
    fields_dic = {value.text:value for idx,value in enumerate(rows) if len(value.find_elements(By.CSS_SELECTOR,'[class="form-control"]')) > 0 }
    
    #Send initial values
    for i in fields_dic.keys():
        inputField = fields_dic[i].find_element(By.CSS_SELECTOR,'[class="form-control"]')
        inputField.clear()
        inputField.send_keys('blahblah')
    
    #Press next and see if error
    next_button.click()
    next_button_available(browser)
    
                
    #Now run the loop to fill all error (if any)
    while True:
        #Now get the error message if any
        error = browser.find_elements(By.CSS_SELECTOR,'[class="help-block"]')
        if len(error) > 0:
            #If there is error then get the text
            error_text = error[0].text
            error_field = re.sub(":.+$","",error_text)
            
            #Now detect the error then pick the correct value
            correct_type = correct_input_type(error_text)
            new_value = text_options[correct_type]
    
            #Get the field that needed to correct, then fill with new value
            corrected_field = fields_dic[error_field].find_element(By.CSS_SELECTOR,'[class="form-control"]')
            corrected_field.clear()
            corrected_field.send_keys(new_value)
            next_button.click()
            next_button_available(browser)
        else:
            break

def answer(browser):
    next_button = next_button_available(browser)
    question = find_question(browser)
    print(question.text)
    st.write(question.text)
    
    radios = isRadio(browser)
    checkboxes = isCheckbox(browser)
    answerText = isAnswerText(browser)
    multiField = isMultipleTextField(browser)
    rankingBlock = isRankingBlock(browser)
    if radios:
        print("Input type: Radio")
        answer_radio(browser,radios, next_button)
    elif checkboxes:
        print("Input type: Checkbox")
        answer_checkbox(browser,checkboxes,next_button)


    elif answerText:
        print("Input type: Text")
        answer_input(browser, answerText, next_button)

    elif rankingBlock:
        ranking = True
        print("Input type: Ranking Block")
        answer_checkbox(browser,rankingBlock,next_button,ranking)
    elif multiField:
        answer_multi_field(browser)
        
    elif next_button:
        print("Input type not detected")
        print("Clicking Next Button")
        next_button.click()
    
    else:
        print("End of Survey")
        return
    print("=========================================")
    # next_button.click()


@st.cache_resource(show_spinner=False)
def get_chromedriver_path() -> str:
    return shutil.which('chromedriver')


# @st.cache_resource
def get_webdriver_service(logpath) -> Service:
    service = Service(
        executable_path=get_chromedriver_path(),
        log_output=logpath,
    )
    return service

def get_logpath() -> str:
    return os.path.join(os.getcwd(), 'selenium.log')

# def get_driver():
#     options = webdriver.ChromeOptions()
    
#     options.add_argument('--disable-gpu')
#     options.add_argument('--headless')
#     # options.add_argument(f"--window-size={width}x{height}")
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     # service = Service()
#     service = get_webdriver_service(logpath=logpath)
#     browser = webdriver.Chrome(service = service,options=options)
    
#     return browser
@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    # service = service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    service = Service()
    return webdriver.Chrome(
        service=service,
        options=options,
    )

def run_all():

    browser = get_driver()
    browser.get('https://tgm.mobi/sa/XQ276?surveytest=1')

    st.write('Opening URL...')
    time.sleep(10)
    next = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[id="btn-next"]')))
    st.write('Finding next button...')
    next.click()
    st.write("Next button clicked.")
    while True:
        answer(browser)