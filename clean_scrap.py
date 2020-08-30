import sqlite3
import urllib.error
import time
import ssl
import json
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn1 = sqlite3.connect('recipe.sqlite')
cur1 = conn1.cursor()

conn2 = sqlite3.connect('clean_recipe.sqlite')
cur2 = conn2.cursor()

cur2.execute('''CREATE TABLE IF NOT EXISTS food_recipe
    (id INTEGER PRIMARY KEY, url TEXT UNIQUE, food_name TEXT UNIQUE, food_description TEXT, preparation_time TEXT, food_ingredient TEXT, 
    food_direction TEXT, recipe_category TEXT, food_nutrition TEXT)''')

food_link = list()
count = 0

print("Program is warming up...........")

##Select all row from recipe.sqlite
cur1.execute('SELECT url, id FROM Pages ORDER BY id')
link_list = cur1.fetchall()

##Select last row from recipe.sqlite
try:
    cur2.execute("SELECT * FROM food_recipe ORDER BY id DESC LIMIT 1")
    last_row = cur2.fetchone()
    x = True
    print("Last stop at", last_row[1], "Delete clean_recipe.sqlite for new scraping")
except:
    print("Starting fresh scraping.....")
    x = False

for row in link_list:
    ##Convert Tuple to List
    link = list(row)

    ##Continue from previous scraping
    if x == True:
        if last_row[1] == link[0]:
            x = False
    else:
        ##Filter links
        if not link[0].startswith("https://www.allrecipes.com/recipe/") or link[0].find("?") > 0:
            continue
        else:
            ##Append filtered food link into list
            food_link.append(link[0])

##Scrap data from each link
for link in food_link:
    ##Open URL and parse the JSON
    print("Retriving", link, end=" ")
    document = urlopen(link, context=ctx)
    html = document.read()
    soup = BeautifulSoup(html, "html.parser")
    js_data = soup.find("script")
    
    ##Try convert to JSON
    try:
        ori_json = json.loads(js_data.string)
    except:
        continue

    ##Food Name
    food_name = ori_json[1]["name"]

    ##Description
    food_description = ori_json[1]["description"]

    ##Food Preparation Time
    preparation_time = dict()
    preparation_time["prepare_time"] = ori_json[1]["prepTime"]
    preparation_time["cook_time"] = ori_json[1]["cookTime"]
    preparation_time["total_time"] = ori_json[1]["totalTime"]

    ##Ingredient
    food_ingredient = list()
    for item in ori_json[1]["recipeIngredient"]:
        food_ingredient.append(item)

    ##Instruction
    food_instruction = dict()
    num = 1
    for item in ori_json[1]["recipeInstructions"]:
        food_instruction[num] = item["text"]
        num += 1

    ##Recipe Caterogy
    recipe_caterogy = list()
    for item in ori_json[1]["recipeCategory"]:
        recipe_caterogy.append(item)

    ##Food Nutrition
    food_nutrition = dict()
    food_nutrition["Recipe Yield"] = ori_json[1]["recipeYield"]
    food_nutrition["Calories"] = ori_json[1]["nutrition"]["calories"]
    food_nutrition["Carbohydrate"] = ori_json[1]["nutrition"]["carbohydrateContent"]
    food_nutrition["Cholesterol"] = ori_json[1]["nutrition"]["cholesterolContent"]
    food_nutrition["Fat"] = ori_json[1]["nutrition"]["fatContent"]
    food_nutrition["Fiber"] = ori_json[1]["nutrition"]["fiberContent"]
    food_nutrition["Protein"] = ori_json[1]["nutrition"]["proteinContent"]
    food_nutrition["Saturated Fat"] = ori_json[1]["nutrition"]["saturatedFatContent"]
    food_nutrition["Serving Size"] = ori_json[1]["nutrition"]["servingSize"]
    food_nutrition["Sodium"] = ori_json[1]["nutrition"]["sodiumContent"]
    food_nutrition["Sugar"] = ori_json[1]["nutrition"]["sugarContent"]
    food_nutrition["Trans Fat"] = ori_json[1]["nutrition"]["transFatContent"]
    food_nutrition["Unsaturated Fat"] = ori_json[1]["nutrition"]["unsaturatedFatContent"]

    ##Insert data into database
    cur2.execute('''INSERT OR IGNORE INTO food_recipe (url, food_name, food_description, preparation_time, food_ingredient, food_direction, 
                recipe_category, food_nutrition) VALUES 
                ( ?, ?, ?, ?, ?, ?, ?, ? )''', (link,food_name,food_description,str(preparation_time),str(food_ingredient),str(food_instruction),str(recipe_caterogy),str(food_nutrition),))

    conn2.commit()
    print("Inserted into Database")

    count += 1

    ##Sleep 5 second for every 10 links retrived
    if count == 10:
        print("Take a rest for 5 seconds")
        time.sleep(5)
        count = 0




