# test_selenium.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_selenium():
    # Optional: specify Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # if you want to run without opening a visible browser

    # If chromedriver.exe is not in your PATH, specify its location like this:
    # driver = webdriver.Chrome(executable_path="C:/path/to/chromedriver.exe", options=chrome_options)
    # Otherwise, if it's on PATH, you can just do:
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.google.com")
        print("Navigated to Google")
        print("Page title is:", driver.title)
    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":
    test_selenium()