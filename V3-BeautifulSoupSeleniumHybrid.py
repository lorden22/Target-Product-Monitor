#V3-BeautifulSoupSeleniumHybrid.py
#By:Bryan Lorden
#Version - 3.0

""" A python script made for personal use to monitor for sports card resocks on
target.com since they are sold out often. When a restock occurs or a product page
is loaded, it will send a message through the terminal, and also through a discord
webhook. Tagert doesnt offer a free eduactional api acesss product data so a
in-house script is need to load refresh product page during suspected restock
times based on patterns. My V3 version is hybrid mixed of BeautifulSoup and
Selenium due to the fact BeautifulSoup can only process HTML (some product info is in JS),
therefore a mix is needed to grab all infomation while trying to maintain maximum speed. """

#Imports
import requests as req
from bs4 import BeautifulSoup as BSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from dhooks import Webhook, Embed
import datetime
import time

print("Imports done...")

#Defining settings for BeautifulSoup/requests
user_Agents = {
   " <Enter User Agent Here> "
}

#Defining settings for Selenium
PATH = " <Enter Path For Chrome Driver Here> 
options = Options()
options.headless = True
driver = webdriver.Chrome(PATH,options=options)

#Defining wehbook address (Change as needed)
hook = Webhook(" <Enter Discord Webhook URL Here> ")
target_img_url = "http://abullseyeview.s3.amazonaws.com/wp-content/uploads/2014/04/targetlogo-6.jpeg"


#Base url for target products and SKUs for wanted prodcuts (Chaange as needed)
base_url = "https://www.target.com/p/-/A-"
skus = ["<Enter SKUs In Strings Here> "]

#Lists of skus and boolean values if product page is loaded or not
if_loaded = []
if_instock = []
for index in range(len(skus)):
    if_loaded.append(False)
    if_instock.append(False)

#Staring up loop for monitor 
while True:
    start_time = time.time()
    for sku in skus:
        
        #Pinging the site and rendering html
        product_url = base_url + sku
        responce = req.get(product_url, headers=user_Agents)

        #Searching the html code for product title and product image
        soup = BSoup(responce.text, 'html.parser')
        product_title = soup.find('h1')
        prodcut_picture_tag= soup.find('picture')
        prodcut_img_tag = soup.find('img')
        product_img_url = prodcut_img_tag['src']

        #Checking if sku was already loaded or not
        if if_loaded[skus.index(sku)] == False:

            #Checking if a product title section was found or not
            if product_title != None:

                #Pulling product name, bulding discord wehbook, and sening notications
                product_name = product_title.find('span').get_text()
                print(product_name + " - is now loaded")

                embed = Embed(
                    description= product_name + " - Product Page Is Now Loaded",
                    timestamp=str(datetime.datetime.now())
                )
                embed.set_author(name='Target Monitor', icon_url = target_img_url)
                embed.add_field(name="Sku",value=sku)
                embed.add_field(name="Link",value="https://www.target.com/p/-/A-" +sku)
                embed.set_thumbnail(product_img_url)
                embed.set_footer(str(datetime.datetime.now()))
                hook.send(embed=embed)
                
                #Updating loaded skus list
                if_loaded[skus.index(sku)] = True
                
            #If not loaded, prints current sku isnt loaded
            else:
                print("SKU " + sku + ": Is not loaded")

        #Process is product page was still loaded
        else:
            #Webdriver pinging product url
            driver.get(product_url)
            time.sleep(1.25)
            
            #Checking if a product title section was found or not
            if product_title != None:

                #Find inner HTML to find stock level
                innerHTML = driver.find_element_by_xpath('//*[@id="viewport"]/div[4]/script')
                string_HTML = str(innerHTML.get_attribute('innerHTML'))
                stock_level_index = string_HTML.find('InStock')

                #Checking if stock is found or not printing if live
                if stock_level_index > -1:
                    print(product_name + " - IS LIVE...")

                    #Checking if fresh restock or not
                    if if_instock[skus.index(sku)] == False:

                        #Pulling product name, bulding discord wehbook, and sening notication
                        if_instock[skus.index(sku)] = True
                        
                        embed = Embed(
                        description= product_name + " - Is Now Live",
                        timestamp=str(datetime.datetime.now())
                        )
                        embed.set_author(name='Target Monitor', icon_url = target_img_url)
                        embed.add_field(name="Sku",value=sku)
                        embed.add_field(name="Link",value="https://www.target.com/p/-/A-" +sku)
                        embed.set_thumbnail(product_img_url)
                        embed.set_footer(str(datetime.datetime.now()))
                        hook.send(embed=embed)

                    #Still printing if stock is not fresh
                    else:
                        continue
                    
                #Setting stock levels back to false           
                else:
                    print(product_name + " - Product Page Loaded...")
                    if_instock[skus.index(sku)] = False

            #Product Page is no loaded loaded
            else:
                print(sku, " - Is No Longer Loaded...")
                if_loaded[skus.index(sku)] = False
                if_instock[skus.index(sku)] = False

    #Total time to loop through all skus
    print("Total Time to loop - ", (time.time() - start_time))
                
