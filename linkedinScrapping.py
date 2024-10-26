from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import time

# LinkedIn credentials
username = "username"
password = "password"

# Function to log in to LinkedIn
def linkedin_login(driver, username, password):
    driver.get('https://www.linkedin.com/login')
    time.sleep(3)
    
    # Enter username and password
    driver.find_element(By.ID, 'username').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)
    
    # Click on login button
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(5)

# Function to scrape connection data
def scrape_connection_data(driver, quantity):
    # Navigate to 'My Network' to see connections
    driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    time.sleep(5)
    
    connections = []
    
    # Scroll and collect data from each connection's profile
    for _ in range(quantity):
        retries = 3  # Number of times to retry fetching the connections
        while retries > 0:
            try:
                # Re-fetch the connection profile links (to avoid stale elements)
                profile_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/in/')]")
                
                for profile in profile_links:
                    profile_url = profile.get_attribute('href')
                    driver.get(profile_url)
                    time.sleep(3)
                    
                    # Scrape data from the profile using WebDriverWait
                    try:
                        name = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//h1[@class='text-heading-xlarge']"))
                        ).text
                    except:
                        name = "Name not found"
                    
                    try:
                        current_position = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@class='pv-text-details__left-panel']//span[1]"))
                        ).text
                    except:
                        current_position = "Position not found"
                    
                    # Experience Section
                    try:
                        experience_section = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//section[@id='experience-section']"))
                        ).text
                    except:
                        experience_section = "No Experience Listed"
                    
                    # Education Section
                    try:
                        education_section = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//section[@id='education-section']"))
                        ).text
                    except:
                        education_section = "No Education Listed"
                    
                    # Skills Section
                    try:
                        skills_section = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//section[@class='pv-skill-categories-section']"))
                        ).text
                    except:
                        skills_section = "No Skills Listed"
                    
                    # Contact info (if available)
                    contact_info = {}
                    try:
                        contact_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//a[@data-control-name='contact_see_more']"))
                        )
                        contact_button.click()
                        time.sleep(2)
                        
                        # Fetch contact details like phone and email
                        email = driver.find_element(By.XPATH, "//section[@class='pv-contact-info__contact-type ci-email']").text
                        contact_info['email'] = email
                    except:
                        contact_info['email'] = "No Email Available"
                    
                    # Store collected data
                    connection_data = {
                        'name': name,
                        'current_position': current_position,
                        'experience': experience_section,
                        'education': education_section,
                        'skills': skills_section,
                        'contact_info': contact_info['email']
                    }
                    
                    connections.append(connection_data)
                    print(f"Scraped data for {name}")
                    
                    # Navigate back to connections page
                    driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
                    time.sleep(5)
                break  # Exit the retry loop if successful
            except StaleElementReferenceException:
                print("Stale element detected, retrying...")
                retries -= 1
                time.sleep(2)  # Wait for a moment before retrying

    return connections

# Function to save data to Excel
def save_to_excel(connections, file_name):
    df = pd.DataFrame(connections)
    df.to_excel(file_name, index=False)  # Save the DataFrame to an Excel file

# Main function
def main(quantity):
    # Set up the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    
    try:
        linkedin_login(driver, username, password)
        connections_data = scrape_connection_data(driver, quantity)
        
        # Save the scraped data to an Excel file
        save_to_excel(connections_data, 'linkedin_connections.xlsx')
        print("Data saved to linkedin_connections.xlsx")
    
    finally:
        driver.quit()

# Example usage
if __name__ == "__main__":
    quantity = 10  # Number of connections to scrape
    main(quantity)
