from bs4 import BeautifulSoup
from selenium import webdriver

# Set up Selenium WebDriver (adjust path to your WebDriver executable)
driver = webdriver.Chrome()  # or webdriver.Firefox() for Firefox

# Open the URL
url = "https://btctouchpoint.com/fr/letalon-fiat-la-recolte-de-la-nourriture-fiat/"
driver.get(url)

# Get the page source and parse it with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find the iframe tag and extract the 'src' attribute
iframe = soup.find('iframe')
podcast_url = iframe['src'] if iframe else None

# Close the browser
driver.quit()

print("Podcast URL:", podcast_url)
