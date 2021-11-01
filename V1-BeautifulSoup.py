#V1-BeautifulSoup.py
#By:Bryan Lorden
#Version - 1.0

"""" A python script made for personal use to monitor for sports card resocks on
target.com since they are sold out often. When a restock occurs or a product page
is loaded, it will send a message through the terminal, and also through a discord
webhook. Tagert doesnt offer a free eduactional api acesss product data so a
in-house script is need to load refresh product page during suspected restock
times based on patterns. My V1 version scrapes the page html. I came across the problem that
values for the stock levels of a product need to rendered in Javascrpit somehow. Later versions
will take care of this. """

#Imports
import requests as req
from bs4 import BeautifulSoup as BSoup
from dhooks import Webhook, Embed
import datetime
import time

print("Imports Done...")

#Setting up settings for monitor
user_Agents = {
    " <Enter User Agent Here> "
}
hook = Webhook(" <Enter Discord Webhook Here> ")
base_url = "https://www.target.com/p/-/A-"
target_img_url = "http://abullseyeview.s3.amazonaws.com/wp-content/uploads/2014/04/targetlogo-6.jpeg"

#Lists of sku and boolean values if product page is loaded and stock is live
skus = [" <Enter SKUs In Strings Here> "]
loaded = []
stock = []
for index in range(len(skus)):
    loaded.append(False)
    
#Start of montior loop
while True:
    start_time = time.time() 
    for sku in skus:
        product_url = base_url + sku
        
        #Pinging the site and rendering html
        responce = req.get(product_url, headers=user_Agents)
        soup = BSoup(responce.text, 'html.parser')
        
        #Searching the html code for product title and product image
        product_title = soup.find('h1')
        prodcut_picture_tag= soup.find('picture')
        prodcut_img_tag = soup.find('img')
        product_img_url = prodcut_img_tag['src']
        
        #Checking if sku was already loaded or not
        if loaded[skus.index(sku)] == False:
            #Checking if a product title section was found or not
            if product_title != None:

                #Pulling product name, bulding discord wehbook, and sening notications
                product_name = product_title.find('span').get_text()
                print(product_name + " - " + sku + " is now loaded")

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
                loaded[skus.index(sku)] = True

            #if not loaded, prints current sku isnt loaded
            else:
                print("SKU " + sku + ": Is not loaded")
                
        #Check if stock is available and if page is still loaded
        else:
            
            #If product page is not loaded, set loaded back to false
            if product_ttle != None:
                loaded[skus.index(sku)] = False

                
            #Check stock if product page is still loaded       
            else:
                
                #Cant render and scrap JS with BeautifulSoup - Solved in later versions
                continue
            
    #print how much time it takes to loop through all skus
    print("Total time to loop - ", time.time() - start_time)
                

