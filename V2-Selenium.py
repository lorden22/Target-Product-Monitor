#V2-Selenium.py
#By:Bryan Lorden
#Version - 2.0

"""" A python script made for personal use to monitor for sports card resocks on
target.com since they are sold out often. When a restock occurs or a product page
is loaded, it will send a message through the terminal, and also through a discord
webhook. Tagert doesnt offer a free eduactional api acesss product data so a
in-house script is need to load refresh product page during suspected restock
times based on patterns. My V2 version stimulates a chrome webdriver and renders the html
and JS. This solves the problem from V1 with BeautifulSoup not able to render JS. """

#Imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dhooks import Webhook,Embed
import datetime
import time

print("Imports done...")

#Setting up settings for monitor
base_url = "https://www.target.com/p/-/A-"
hook = Webhook(" <Enter Discord Webhook URL Here>  ")
target_img_url = "http://abullseyeview.s3.amazonaws.com/wp-content/uploads/2014/04/targetlogo-6.jpeg"
PATH = " <Enter Path For Chrome Driver Here> "
options = Options()
options.headless = True
driver = webdriver.Chrome(PATH,options=options)

#Lists of skus and boolean values if product page is loaded or not
skus = [" <Enter SKUs In Strings Here> "]
loaded = []
stock = []

for index in range(len(skus)):
    loaded.append(False)
    stock.append(False)
    

#Staring up loop for monitor 
while True:
    start_time = time.time()
    for sku in skus:
        
        #Webdriver will try pinging product page for current sku
        driver.get(base_url+sku)
        time.sleep(1.25)

        #checking if sku was already loaded or not
        if loaded[skus.index(sku)] == False:

            #Try-Expect to catch any erros with trying to get prodcut name, 
            try:
                product_name = driver.find_element_by_xpath('//*[@id="viewport"]/div[4]/div/div[1]/div[2]/h1').text
                print(product_name + " - Product Page Loaded...")
                loaded[skus.index(sku)] = True

                product_img_url = driver.find_element_by_xpath('/html/body/div[1]/div/div[4]/div/div[2]/div[1]/div/div/div/div/div/div/div/div[1]/div/div[5]/a/div/div/div/div/img').get_attribute('src')
                    
                embed = Embed(
                description= product_name + " - Product Page Is Now Laded",
                timestamp=str(datetime.datetime.now())
                )
                embed.set_author(name='Target Monitor', icon_url = target_img_url)
                embed.add_field(name="Sku",value=sku)
                embed.add_field(name="Link",value="https://www.target.com/p/-/A-" +sku)
                embed.set_thumbnail(product_img_url)
                embed.set_footer(str(datetime.datetime.now()))
                hook.send(embed=embed)
            #If found looking for that element, product page is not live
            except:
                print(sku + " - Not Loaded Yet...")

        #Product page is live, checking for stock
        else:
            #Checks if produt page is still live by looking for product name
            try:
                product_name = driver.find_element_by_xpath('//*[@id="viewport"]/div[4]/div/div[1]/div[2]/h1').text

            #If not found, set loaded back false and contine back to sku loop
            except:
                loaded[skus.index(sku)] = False
                print(sku + "- Product Page Is No Longer Loaded...")
                continue

            #If product title is found, you will be able to find inner HTML to find stock level
            innerHTML = driver.find_element_by_xpath('//*[@id="viewport"]/div[4]/script')
            string_HTML = str(innerHTML.get_attribute('innerHTML'))
            stock_level_index = string_HTML.find('InStock')

            #Checking if stock is found or not
            if stock_level_index > -1:

                #Checking if fresh restock or not
                if stock[skus.index(sku)] == False:
                    
                    #Pulling product name, bulding discord wehbook, and sening notication
                    stock[skus.index(sku)] = True
                    print(product_name + " - IS LIVE...")

                    product_img_url = driver.find_element_by_xpath('/html/body/div[1]/div/div[4]/div/div[2]/div[1]/div/div/div/div/div/div/div/div[1]/div/div[5]/a/div/div/div/div/img').get_attribute('src')
                    
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
            
                else:
                    print(product_name + " - IS LIVE...")

                                        
            #Setting stock levels back to false
            else:
                stock[skus.index(sku)] = False
                print(product_name - "Is No Longer In Stock...")
                

    #print how much time it takes to loop through all skus        
    print("Total time to loop - ", time.time() - start_time)
                
            
            
        
                
                
