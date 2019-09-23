# Imports
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# create a pet csv file
def create_pet(location_pet_htmls,location_ids):
    # Initialize a list to hold all the pet data
    pet_data = []

    # Go through each location url and look at pets up for adoption
    for i,x in enumerate(location_pet_htmls):
        data = requests.get(x)
        html = BeautifulSoup(data.text, 'html.parser')
        pet_info = html.findAll('tr')

        # Look through each pet at the url, and get their info. Skip the first entry of the url as it is a header of none type that causes errors.
        for j,y in enumerate(pet_info):
            # Avoid none content header by skipping it with if statement
            if not j == 0:
                # Get the elements that contain the information we need
                image = y.find('td')
                name = image.findNext('td')
                breed = name.findNext('td')
                age = breed.findNext('td')
                sex = age.findNext('td')
                reference = name.find('a')['href']

                # Get values for each pet ie website, animal type, name, breed, age, sex and add to pet_data list
                row = ['https://www.adoptapet.com'+reference,re.search(r'ontario-(.*)',reference)[0].replace('ontario-',''),name.text,breed.text,age.text,sex.text,location_ids[i]]
                pet_data.append(row)

    # Create a dataframe of the pet data
    cols = ['page','animal','name','breed','age','sex','location']
    pets = pd.DataFrame(pet_data, columns=cols)
    pets.to_csv('data/ontario_raw_pets.csv')

# Create new location csv file
def create_location(location_ids):
    # Get the location data from website
    url = 'https://ontariospca.ca/contact-us/ontario-spca-animal-centre-locations/'
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')

    # Initialize empty locations list
    location_data = []

    # Look through each location from the location url table
    for i,x in enumerate(html.find('table').findAll('td')):
        # Split the data at new line character to process
        location_info = x.text.split('\n')

        # Identify the values that will be used in the location dataset
        name = location_info[0]
        id = location_ids[i]
        address = location_info[-6]+' '+location_info[-5]
        phone = location_info[-4]
        email = location_info[-2]
        website = location_info[-1]
        location_data.append([name,id,address,phone,email,website])

    # Create a dataframe of the pet data
    cols = ['name','id','address','phone','email','website']
    locales = pd.DataFrame(location_data, columns=cols)
    locales.to_csv('data/ontario_raw_locations.csv')



# Get the HTML from Ontario SPCA website for pet adoption
url = 'https://ontariospca.ca/adopt/view-pets-for-adoption/'
data = requests.get(url)
html = BeautifulSoup(data.text, 'html.parser')

# Get animal shelter names, ids, and htmls for the shelter's pets
locations = html.findAll('details')
location_pet_htmls = [x.find('iframe')['src'] for x in locations]
location_names = [x.find('summary').text for x in locations]
location_ids = [re.search(r'shelter_id=[0-9]+',x)[0].replace('shelter_id=','') for x in location_pet_htmls]

create_pet(location_pet_htmls,location_ids)
create_location(location_ids)
