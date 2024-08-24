from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import Polynomial
import matplotlib.animation as animation
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Set up Selenium WebDriver options
options = Options()
options.headless = True  # Run in headless mode for faster execution

# Initialize the WebDriver
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# URL of the website
url = "https://trader.tradovate.com/welcome"

with open('username.txt', 'r') as usernameFile:
    username = usernameFile.read()

with open("password.txt", 'r') as passwordFile:
    password = passwordFile.read()

# Load the page
driver.get(url)

# Wait for JavaScript to load content
# time.sleep(3)  # Adjust the sleep time as necessary
WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '#name-input'))
)




# LOG IN TO TRADOVATE -----------------------------------

username_field = driver.find_element(By.CSS_SELECTOR, "#name-input")
password_field = driver.find_element(By.CSS_SELECTOR, "#password-input")
loginButton = driver.find_element(By.CSS_SELECTOR, ".MuiButtonBase-root.MuiButton-root.MuiButton-contained.fat-button.full-width-button.mb-20.MuiButton-containedPrimary")

username_field.send_keys(username)
time.sleep(0.5)
password_field.send_keys(password)
time.sleep(0.5)
loginButton.click()


WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "button.MuiButtonBase-root.MuiButton-root.jss10.MuiButton-contained.fat-button.full-width-button.mt-2.mb-2.tm"))
)


# START SIMULATION -----------------------------------------
simulationButton = driver.find_element(By.CSS_SELECTOR, "button.MuiButtonBase-root.MuiButton-root.jss10.MuiButton-contained.fat-button.full-width-button.mt-2.mb-2.tm")
simulationButton.click()


# GET DATA --------------------------------------------------

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '.app-modules'))
)
print("PAGE LOADED")

time.sleep(5)

viewport_width = driver.execute_script("return window.innerWidth;")
viewport_height = driver.execute_script("return window.innerHeight;")

actions = ActionChains(driver)
# actions.move_by_offset(100, 200).perform()
# actions.move_by_offset(900, 400).perform()
# actions.move_by_offset(-800, 0).perform()

actions.move_by_offset(50, 50).perform()
actions.move_by_offset(0, 300).perform()
actions.move_by_offset(350, 0).perform()
actions.move_by_offset(800, 0).perform()

nqData = []
esData = []
xValues = []
esVolume = 0
nqVolume = 0

nqBuyLevels = sorted([19800, 19880, 19900])
nqSellLevels = sorted([19550, 19000, 19500])
esBuyLevels = sorted([5681, 5685, 5690])
esSellLevels = sorted([5577, 5570, 5560])

firstDerivativeTrackerEs = []
secondDerivativeTrackerEs = []

firstDerivativeTrackerNq = []
secondDerivativeTrackerNq = []

nqBreakingUp = []
nqBreakingDown = []
esBreakingUp = []
esBreakingDown = []

derivativePercentGoal = 0.8
numSamples = 60

pastLevelMarginES = 3
closeToLevelES = 0.5

scaleFactor = 10

def volumeQuality(volume):
    if volume < 3000:
        return "Garbage"
    elif volume < 6000:
        return "Bad"
    elif volume < 10000:
        return "Decent"
    elif volume < 15000:
        return "Good"
    else:
        return "Great"

def handleLevelsBuy(levels, data, scale):
    if len(levels) == 0:
        print("GIVE ME BETTER LEVELS YOU FOOL")
        return 0

    level = levels[0]

    if data[-1] - level > pastLevelMarginES*scale:
        del levels[0]
    
    if data[-1] - level > closeToLevelES*scale:
        return 1
    
    return 0

def handleLevelsSell(levels, data, scale):
    if len(levels) == 0:
        print("GIVE ME BETTER LEVELS YOU FOOL")
        return 0
    if levels[0] - data[-1] > pastLevelMarginES*scale:
        del levels[0]
    
    if levels[0] - data[0] > closeToLevelES*scale:
        return 1
    
    return 0

def trackDerivative(data, firstDerivativeTracker, secondDerivativeTracker):
    # degree = int(len(xValues)/10)
    degree = 10

    # print("Length of data:", len(xValues), len(data))
    # print("xValues:", xValues[-numSamples:])
    # print("data:", data[-numSamples:])
    coefficients = np.polyfit(xValues, data, degree)
    polynomial = np.poly1d(coefficients)

    derivative = np.polyder(polynomial)
    second_derivative = np.polyder(derivative)

    firstDerivativeValue = np.polyval(derivative, xValues[-1])
    secondDerivativeValue = np.polyval(second_derivative, xValues[-1])

    firstDerivativeTracker.append(firstDerivativeValue)
    secondDerivativeTracker.append(secondDerivativeValue)

def checkForDirection(firstDerivativeTracker, secondDerivativeTracker):
    firstDerivativeCounter = 0
    secondDerivativeCounter = 0

    for j in range(numSamples-1):
        firstDerivativeCounter += int(firstDerivativeTracker[-1-j] > 0)
        secondDerivativeCounter += int(secondDerivativeTracker[-1-j] > 0)

    if firstDerivativeCounter > derivativePercentGoal*numSamples and secondDerivativeCounter > derivativePercentGoal*numSamples:
        return "UP"
    elif firstDerivativeCounter < 1-derivativePercentGoal*numSamples and secondDerivativeCounter < 1-derivativePercentGoal*numSamples:
        return "Down"
    else:
        return "SIDEWAYS"

def updateData():

    global nqData, esData, xValues, esVolume, nqVolume

    mainTradePagehtml = driver.page_source
    soup = BeautifulSoup(mainTradePagehtml, 'html.parser')
    halves = soup.find_all('div', class_='contract-symbol')

    for half in halves:
        if half.find('span').get_text() == 'NQU4':
            nqValueDiv = half.find_parent('div').find_parent('div')
        elif half.find('span').get_text() == 'ESU4':
            esValueDiv = half.find_parent('div').find_parent('div')

    esInfoColumns = esValueDiv.find_all('div', class_="info-column")
    nqInfoColumns = nqValueDiv.find_all('div', class_="info-column")

    for infoColumn in esInfoColumns:
        if infoColumn.find('small').get_text() == 'ASK':
            esPrice = float(infoColumn.find('div', class_="number").get_text())
            break

    for infoColumn in nqInfoColumns:
        if infoColumn.find('small').get_text() == 'ASK':
            nqPrice = float(infoColumn.find('div', class_="number").get_text())
            break

    volumes = []
    tempValues = []

    entries = soup.find_all('ul', class_='entries')
    for entry in entries:
        divisions = entry.find_all('div', class_='desc')
        for division in divisions:
            if division.get_text().find(".") == -1:
                volumes.append(int(division.get_text()))
        tempValues.append(float(divisions[0].get_text()))

    if abs(tempValues[0] - esPrice) < abs(tempValues[0] - nqPrice):
        esVolume = volumes[0]
        nqVolume = volumes[1]
    else:
        esVolume = volumes[1]
        nqVolume = volumes[0]

    xValues.append(0.5 * len(esData))

    esData.append(float(esPrice))
    nqData.append(float(nqPrice))

    time.sleep(0.5)

buffer = 10
giveItTime = 60

# ----------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------

for i in range(360):
    updateData()
    if i < buffer:
        continue
    trackDerivative(esData, firstDerivativeTrackerEs, secondDerivativeTrackerEs)
    trackDerivative(nqData, firstDerivativeTrackerNq, secondDerivativeTrackerNq)
    if i < numSamples+buffer:
        continue
    nqDirection = checkForDirection(firstDerivativeTrackerNq, secondDerivativeTrackerNq)
    esDirection = checkForDirection(firstDerivativeTrackerEs, secondDerivativeTrackerEs)
    
    esBreakingUp.append(0)
    esBreakingDown.append(0)
    nqBreakingDown.append(0)
    nqBreakingUp.append(0)

    esBuyString = 'Nowhere close'
    esSellString = 'Nowhere close'
    nqBuyString = 'Nowhere close'
    nqSellString = 'Nowhere close'
    if handleLevelsBuy(esBuyLevels, esData, 1):
        esBuyString = "Breaking"
        esBreakingUp[-1] += 1
    if handleLevelsSell(esSellLevels, esData, 1):
        esSellString = "Breaking"
        esBreakingDown[-1] += 1
    if handleLevelsBuy(nqBuyLevels, nqData, scaleFactor):
        nqBuyString = "Breaking"
        nqBreakingUp[-1] += 1
    if handleLevelsSell(nqSellLevels, nqData, scaleFactor):
        nqSellString = "Breaking"
        nqBreakingDown[-1] += 1

    print(f"ES ({esData[-1]}) - Volume: {esVolume} ({volumeQuality(esVolume)})\tDirection: {esDirection}\tBuy Level: {esBuyString}\tSell Level: {esSellString}")
    print(f"NQ ({nqData[-1]}) - Volume: {nqVolume} ({volumeQuality(nqVolume)})\tDirection: {nqDirection}\tBuy Level: {nqBuyString}\tSell Level: {nqSellString}\n")

    if i > numSamples+buffer+giveItTime:
        if (esVolume > 12000) and (esDirection == "UP") and (sum(esBreakingUp[-giveItTime:]) > 50):
            print("BUY ES")
        if (esVolume > 12000) and (esDirection == "DOWN") and (sum(esBreakingDown[-giveItTime:]) > 50):
            print("SELL ES")
        if (nqVolume > 12000) and (nqDirection == "UP") and (sum(nqBreakingUp[-giveItTime:]) > 50):
            print("BUY NQ")
        if (nqVolume > 12000) and (nqDirection == "DOWN") and (sum(nqBreakingDown[-giveItTime:]) > 50):
            print("SELL ES")

time.sleep(2)

driver.quit()

degree = 10
coefficients = np.polyfit(xValues, nqData, degree)
polynomial = np.poly1d(coefficients)

derivative = np.polyder(polynomial)
second_derivative = np.polyder(derivative)

x_poly = np.linspace(min(xValues), max(xValues), 100)
y_poly = polynomial(x_poly)
y_derivative_poly = derivative(x_poly)
y_second_derivative_poly = second_derivative(x_poly)

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 8))

ax1.scatter(xValues, nqData, color='red', label='Data points')

ax1.plot(x_poly, y_poly, color='blue', label=f'Polynomial (degree {degree})')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_title('Polynomial Fit')
ax1.legend()

# Plot the derivative
ax2.plot(x_poly, y_derivative_poly, color='green', linestyle='--', label='Derivative')
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_title('Derivative of the Polynomial')
ax2.legend()

ax3.plot(x_poly, y_second_derivative_poly, color='orange', linestyle='-.', label='Second Derivative')
ax3.set_xlabel('X')
ax3.set_ylabel('Y')
ax3.set_title('Second Derivative of the Polynomial')
ax3.legend()

# Adjust layout and show the plot
plt.tight_layout()
plt.show()