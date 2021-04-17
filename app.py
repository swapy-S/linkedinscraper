import pandas as pd 
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import requests
from pandas import DataFrame
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from werkzeug.utils import secure_filename
import numpy as np
import os
from datetime import datetime
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response
from flask import Flask, stream_with_context
from flask import Flask, make_response
import pyexcel as pe
from io import StringIO

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html",name="swapnil")

@app.route("/output", methods=['GET', 'POST'])
def output():
    if request.method == "POST":
        key = request.form['keywords']
        pages = request.form['pages']
        email = request.form['email']
        password = request.form['pass']
        print(password,"pass")
        print(type(password),"typepass")
        print("key",key)
        print("pages",pages)
        name,designations,content,post_link,insight_links,email = scraper(key,pages,email,password)
        # no = ['Name','designations','Content','Post Link', 'Linkedin Profile', 'Email']
        final = [['Name','designations','Content','post link','insight Links','Email']]
        for i in range(0,len(name)):
            temp = []
            # temp.append(no[i])
            temp.append(name[i])
            temp.append(designations[i])
            temp.append(content[i])
            temp.append(post_link[i])
            temp.append(insight_links[i])
            temp.append(email[i])
            final.append(temp)
            temp = []
        print(final)
        # table = df.to_html()
        sheet = pe.Sheet(final)
        io =  StringIO()
        sheet.save_to_memory("csv", io)
        output = make_response(io.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename= data.csv"
        output.headers["Content-type"] = "text/csv"
        return output
        # return table
    return render_template("home.html")

 
def scraper(keys,nopages,email,password1):
    keywords = keys
    browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    browser.get("https://www.linkedin.com/search/results/content/?keywords=AI&origin=SWITCH_SEARCH_VERTICAL")
    signin = browser.find_element_by_link_text("Sign in")
    signin.click()
    username = browser.find_element_by_id("username")
    username.send_keys(str(email))
    password = browser.find_element_by_id("password")
    password.send_keys(password1)
    login_button = browser.find_element_by_class_name("login__form_action_container").find_element_by_tag_name("button")
    login_button.click()
    time.sleep(10)
    browser.find_element_by_class_name("search-global-typeahead__input").clear()
    time.sleep(10)
    search_bar = browser.find_element_by_class_name("search-global-typeahead__input")
    search_bar.send_keys(keywords)
    search_bar.send_keys(Keys.RETURN)
    time.sleep(10)
    counter = 1
    c = []
    d = []
    k = []
    con=[]
    elink=[]
    post_link=[]
    contact = []
    print(nopages,"nopages")
    print(type(nopages))
    while (counter < int(nopages)):
        time.sleep(10)
        names = browser.find_elements_by_class_name("entity-result__title-text")
        
        for i in names:
            c.append(i.text)
            
        for i in range(0,len(c)):
            # print(c[i],type(c[i]))
            temp = c[i].split("\n",1)
            c[i] = temp[0]

        # print(c)
        # print("len-c",len(c))
        designations = browser.find_elements_by_class_name("entity-result__primary-subtitle")
        
        for i in designations:
            d.append(i.text)

        elements = browser.find_elements_by_css_selector("div.t-12 a.t-12")
        #time.sleep(3)
        for element in elements:
            ele = element.get_attribute("href")
            browser.execute_script("window.open('');")
            browser.switch_to.window(browser.window_handles[1])
            browser.get(ele)
            print("new tab....")
            post_link.append(ele)
            content_1 = browser.find_elements_by_css_selector("div.feed-shared-update-v2__description")
            for i in content_1:
                con.append(i.text)
               
            inlink = browser.find_elements_by_css_selector("div.feed-shared-article__link-container a.feed-shared-article__image-link")
            if not inlink:
                elink.append("none")
            else:
                for il in inlink:
                    ab = il.get_attribute("href")
                    elink.append(ab)
            browser.close()
            browser.switch_to.window(browser.window_handles[0])

        elements = browser.find_elements_by_css_selector("div.entity-result__content-actor a")
        # print(elements)
        for element in elements:
            
            temp_prof = element.get_attribute("href")
            browser.execute_script("window.open('');")
            browser.switch_to.window(browser.window_handles[1])
            browser.get(temp_prof)
            # print("new tab....")
            time.sleep(5)
            eles = browser.find_elements_by_class_name("pv-top-card--list-bullet")
            # print(eles)
            if not eles:
                # print("if not")
                contact.append("None")
                browser.close()
                browser.switch_to.window(browser.window_handles[0])
                # print("if finish..")
            else:
                # print("else")
                info = browser.find_element_by_link_text('Contact info')
                # print(info,"info")
                info.click()
                time.sleep(5)
                profiles = browser.find_elements_by_class_name("ci-email")
                # print(profiles,"profiles")
                if not profiles:
                    # print("if not profiles")
                    contact.append("None")
                    browser.close()
                    browser.switch_to.window(browser.window_handles[0])
                else:


                    # print("profile",profiles[0])
                    temp_det = profiles[0].text
                    contact.append(temp_det.strip('Email\n'))
                    time.sleep(5)
                    browser.close()
                    browser.switch_to.window(browser.window_handles[0])
                    # print("else finsh..")
        time.sleep(5)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        link = browser.current_url
        # print(link,"link")
        # print(type(link))
        count_link = link + "&page="+ str(counter+1)
        # print(count_link)
        browser.get(count_link)
        counter = counter + 1
        # # print(contact,"contact")
        # final_list= []
    final_list = [c,d,con,post_link,elink,contact]
    df = DataFrame (final_list).transpose()
    df.columns = ['Name','designations','Content','post link','insight Links','Email']
    print (df)
    return c,d,con,post_link,elink,contact
        # df.to_csv('file1.csv')


if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True)



