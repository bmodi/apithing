from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Set up Selenium WebDriver options
options = Options()
options.headless = True  # Run in headless mode for faster execution

# Initialize the WebDriver
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# URL of the website
url = "https://www.financialjuice.com/home"

# Load the page
driver.get(url)

# Wait for JavaScript to load content
time.sleep(5)  # Adjust the sleep time as necessary

# Get the full page HTML
html = driver.page_source

# Close the WebDriver
driver.quit()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Find all matching div elements
matching_divs = soup.find_all('div', {'data-id': True, 'data-time': True})

timelyNews = []

englishImportance = {"dot-1": "Red dot", "dot-2": "Orange dot", "dot-3": "Yellow dot", "dot-4": "Blue dot", "fas fa-bolt imp-1": "Red lightning bolt", "fas fa-bolt imp-2": "Orange lightning bolt", "fas fa-bolt imp-3": "Yellow lightning bolt"}

for div in matching_divs[:len(matching_divs)]:
    eventTime = div.find('div', class_='div-table-col event-time').get_text(strip=True)
    eventHour = int(eventTime[0:2])
    eventMinute = int(eventTime[3:])
    eventSpanDiv = div.find('div', class_='div-table-col event-imp')
    # print("THE THING", eventSpanDiv)
    eventSpan = eventSpanDiv.find('span')
    if eventSpan == None:
        eventSpan = eventSpanDiv.find('i')
    eventImp = eventSpan['class'][0]
    if eventHour >= 9 and eventHour <= 11:
        timelyNews.append([eventTime, eventImp])
    if eventHour > 11:
        break


print("\n\n\nHERE IS YOUR DATA\n")

for news in timelyNews:
    print("There is a " + englishImportance[news[1]] + " at " + news[0])

print()