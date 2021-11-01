#V4-ScrapySplash.py
#By:Bryan Lorden
#Version - 4.0

"""" A python script made for personal use to monitor for sports card resocks on
target.com since they are sold out often. When a restock occurs or a product page
is loaded, it will send a message through the terminal, and also through a discord
webhook. Tagert doesnt offer a free eduactional api acesss product data so a
in-house script is need to load refresh product page during suspected restock
times based on patterns. My V4 version is very  similar to my V3 version, but
uses a different framework of scrapy-splash hybrid to scrap the start website.
Docker is needed to install splash though"""

#Imports
import time
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_splash import SplashRequest
from dhooks import Webhook, Embed
import datetime
print("Imports Done...")

#Defining Scarpy splash            
class mySpider(scrapy.Spider):

    #Defining spider name
    name = "targetSpider"

    #Defining main target homepage and product urls wanted
    start_urls = ["https://www.target.com"]
    all_urls = [
                " <Enter Product URLs Here> "
                ]

    #Defining custom settings for the spider
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        #'DUPEFILTER_CLASS' : 'scrapy_splash.SplashAwareDupeFilter',
        'SPLASH_URL' : <"Enter Splash Url Here>" ,
        'HTTPCACHE_STORAGE' : 'scrapy_splash.SplashAwareFSCacheStorage',
        'DOWNLOADER_MIDDLEWARES' : {'scrapy_splash.SplashCookiesMiddleware': 723,'scrapy_splash.SplashMiddleware': 725, 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,},
        'SPIDER_MIDDLEWARES' :  { 'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,}
    }

    #Defining the indexs of current and next prodcuts
    current_url_index = 0
    netx_url_index = 0

    #Setting a value that homepage is not loaded
    homepage_loaded = False

    #Setting first start time as 0 seconds
    start_time = 0

    #Lists of skus and boolean values if product page is loaded or not
    if_loaded = []
    if_instock = []
    for index in range(len(all_urls)):
        if_loaded.append(False)
        if_instock.append(False)

    target_img_url = "http://abullseyeview.s3.amazonaws.com/wp-content/uploads/2014/04/targetlogo-6.jpeg"

    hook = Webhook( "<Enter Discord Webhook Here> ")

    #Defining a parse method for the spider to loop and scarp
    def parse(self,responce):

        #If first ping, will ping homepage and then wont ping it again
        if not self.homepage_loaded:
            print("Homepage was loaded...")
            self.homepage_loaded = True

        #If not first ping, will loop through url list for products
        else:

            #Getting current sku
            current_sku = self.all_urls[self.current_url_index].split("-")[-1]

            #Getting product title and checking if a product name is loaded
            product_title_list = responce.xpath('//*[@id="viewport"]/div[4]/div/div[1]/div[2]/h1/span/text()').extract()
            prodcut_image_list = responce.xpath('/html/body/div/div/div[4]/div/div[2]/div[1]/div/div/div/div[2]/div/div/div/div[1]/a[1]/div/div/div/picture/img/@src').extract()
            if len(prodcut_image_list) > 0:
                product_image_url = prodcut_image_list[0]
            
            #Checking if sku was already loaded or not
            if self.if_loaded[self.current_url_index] == False:

                #Checking if a product title section was found or not
                if len(product_title_list) > 0:

                    #Pulling product name, bulding discord wehbook, and sening notications
                    product_name = product_title_list[0]
                    print(product_name + " - is now loaded")

                    embed = Embed(
                        description= product_name + " - Product Page Is Now Loaded",
                        timestamp=str(datetime.datetime.now())
                    )
                    embed.set_author(name='Target Monitor', icon_url = self.target_img_url)
                    embed.add_field(name="Sku",value=current_sku)
                    embed.add_field(name="Link",value="https://www.target.com/p/-/A-" + current_sku)
                    embed.set_thumbnail(product_image_url)
                    embed.set_footer(str(datetime.datetime.now()))
                    self.hook.send(embed=embed)
                
                    #Updating loaded skus list
                    self.if_loaded[self.current_url_index] = True
                
                #If not loaded, prints current sku isnt loaded
                else:
                    print("SKU " + current_sku + ": Is not loaded")

            #If product page is already loaded do...
            else:

                #Checking to make sure product page is still loaded
                if len(product_title_list) > -1:
                    product_name = product_title_list[0]

                    #Checking if stock is found or not printing if live
                    stock_level_list = responce.xpath('//*[@id="viewport"]/div[4]/script').extract()
                    if len(stock_level_list) > 0 and stock_level_list[0].find("InStock") > -1:    
                        print(product_title_list[0] + " - Is Now Live...")

                        #Checking if fresh restock or not    
                        if self.if_instock[self.current_url_index] == False:

                            #Pulling product name, bulding discord wehbook, and sening notication
                            self.if_instock[self.current_url_index] = True

                            embed = Embed(
                                description=product_name + "- Is Now Live...",
                                timestamp=str(datetime.datetime.now())
                            )
                            embed.set_author(name='Target Monitor', icon_url = self.target_img_url)
                            embed.add_field(name="Sku",value=current_sku)
                            embed.add_field(name="Link",value="https://www.target.com/p/-/A-" + current_sku)
                            embed.set_thumbnail(product_image_url)
                            embed.set_footer(str(datetime.datetime.now()))
                            self.hook.send(embed=embed)

                        #Still printing if stock is not fresh
                        else:
                            pass

                    #Setting stock levels back to false           
                    else:
                        print(product_name + " - Product Page Loaded...")
                        self.if_instock[self.current_url_index] = False

                #Product Page is no longer loaded
                else:
                    print(current_sku + " - Is No Longer Loaded...")
                    self.if_loaded[self.current_url_index] = False
                          
                              
        #Requesting next url
        new_url = responce.urljoin(self.all_urls[self.netx_url_index])

        #Updating current and next url index as needed
        self.current_url_index = self.netx_url_index
        self.netx_url_index += 1
        if self.netx_url_index >= len(self.all_urls):
            self.netx_url_index = 0

        #Print time to ping and resetting start time of ping  
        print("Time Ping - ", time.time()-self.start_time)
        self.start_time = time.time()

        #calling next splash request  
        yield SplashRequest(new_url, callback = self.parse)

#Starting Spider        
process = CrawlerProcess()
process.crawl(mySpider)
process.start()

#Print Exiting if an error is found
print("Exiting...")

