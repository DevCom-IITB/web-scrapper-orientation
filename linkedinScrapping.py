from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

username = "your email id on linkedin"
password = "your password on linkedin"

# Function to log in to LinkedIn
def linkedin_login(driver, username, password):
    driver.get('https://www.linkedin.com/login')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(username)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(3)

# Function to scrape connection data
def scrape_connection_data(driver, quantity):
    driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    time.sleep(3)
    
    connections = []
    scraped_profiles = set()  # Avoid duplicates
    
    for _ in range(quantity):
        try:
            profile_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/in/')]")
            for profile in profile_links:
                profile_url = profile.get_attribute('href')
                if profile_url in scraped_profiles:
                    continue  # Skip already-scraped profiles
                
                driver.get(profile_url)
                time.sleep(3)
                
                try:
                    # Wait for the name element to appear
                    name = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, "//<tag>[contains(@class, '<class>')]"))
                    ).text
                except TimeoutException:
                    name = "Name not found"
                
                # Add more scraping as per the previous setup
                # For instance, scraping position, experience, skills, etc.

                connections.append({'name': name, 'profile_url': profile_url})
                scraped_profiles.add(profile_url)
                print(f"Scraped: {name}")
                
                driver.back()
                time.sleep(2)
        
        except StaleElementReferenceException:
            print("Encountered a stale element, retrying...")
            continue
    
    return connections

# Function to save data to Excel
def save_to_excel(connections, file_name):
    df = pd.DataFrame(connections)
    df.to_excel(file_name, index=False)

# Main function
def main(quantity):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    try:
        linkedin_login(driver, username, password)
        connections_data = scrape_connection_data(driver, quantity)
        save_to_excel(connections_data, 'linkedin_connections.xlsx')
    finally:
        driver.quit()

# Example usage
if __name__ == "__main__":
    quantity = 5  # Number of connections to scrape
    main(quantity)
