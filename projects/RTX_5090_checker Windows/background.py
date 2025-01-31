import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import os
import datetime
from dotenv import load_dotenv
import winsound  # For the beep on Windows
from urllib.parse import urlparse, parse_qs  # Parse domain, skuId from URL

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Load environment variables (optional)
load_dotenv()

# List of product URLs to check
ITEM_URLS = [
    "https://www.bestbuy.com/site/nvidia-geforce-rtx-5090-32gb-gddr7-graphics-card-dark-gun-metal/6614151.p?skuId=6614151",
    "https://www.bestbuy.com/site/asus-rog-astral-nvidia-geforce-rtx-5080-16gb-gddr7-pci-express-5-0-graphics-card-black/6613334.p?skuId=6613334",
    "https://www.amazon.com/MSI-Graphics-DisplayPort-Blackwell-Architecture/dp/B0DT7L98J1",
    "https://www.amazon.com/ASUS-Graphics-3-8-Slot-Axial-tech-Phase-Change/dp/B0DQSD7YQC",
    "https://www.newegg.com/asus-rog-astral-rog-astral-rtx5090-o32g-gaming-nvidia-geforce-rtx-5090-32gb-gddr7/p/N82E16814126751?Item=N82E16814126751",
    "https://www.newegg.com/gigabyte-gv-n5090aorus-m-32gd-nvidia-geforce-rtx-5090-32gb-gddr7/p/N82E16814932760?Item=N82E16814932760",
]

def check_in_stock(url):
    """
    Master function that:
      - Determines which domain we're dealing with
      - Applies site-specific logic
      - Returns True if the item is in stock, False otherwise
    """
    domain = urlparse(url).netloc.lower()  # e.g., "www.bestbuy.com", "www.amazon.com", "www.newegg.com"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(15)  # 15-second limit for page loads

    try:
        driver.get(url)
        time.sleep(2)  # Give the page time to render JavaScript

        if "bestbuy.com" in domain:
            return bestbuy_in_stock(driver, url)
        elif "amazon.com" in domain:
            return amazon_in_stock(driver)
        elif "newegg.com" in domain:
            return newegg_in_stock(driver)
        else:
            # Fallback check: look for "Add to Cart" text in page source
            return fallback_in_stock(driver)
    except TimeoutException:
        # If page took too long to load, assume not in stock or site error
        return False
    finally:
        driver.quit()

def bestbuy_in_stock(driver, url):
    """
    Find the specific "Add to Cart" button for the SKU from the URL's query param (skuId).
    Then check 'data-button-state' and whether the button is disabled.
    """
    # Extract skuId from the query string (e.g., "?skuId=6614151")
    parsed = urlparse(url)
    sku_id = parse_qs(parsed.query).get('skuId', [None])[0]
    
    # If there's no skuId in the URL, fallback to a simpler approach
    if not sku_id:
        return fallback_in_stock(driver)

    try:
        # Look specifically for a button matching this SKU
        # Example: button.add-to-cart-button[data-sku-id="6614151"]
        selector = f'button.add-to-cart-button[data-sku-id="{sku_id}"]'
        button = driver.find_element(By.CSS_SELECTOR, selector)

        # Check the data-button-state attribute
        button_state = button.get_attribute("data-button-state")  # e.g., "SOLD_OUT", "ADD_TO_CART", etc.
        # Also check if the "disabled" attribute is present (button is greyed out)
        disabled_attr = button.get_attribute("disabled")

        # If the state is "SOLD_OUT" or the button is disabled, not in stock
        if button_state == "SOLD_OUT" or disabled_attr is not None:
            return False
        return True
    except NoSuchElementException:
        # If we can't find the specific button, assume out of stock
        return False

def amazon_in_stock(driver):
    """
    For Amazon, there's often an 'add-to-cart-button' with id="add-to-cart-button".
    Another possibility is a 'Buy Now' button.
    """
    try:
        # Check for Add to Cart
        atc_button = driver.find_element(By.ID, "add-to-cart-button")
        if atc_button.is_enabled():
            return True
    except NoSuchElementException:
        pass
    
    # Sometimes it's a "Buy Now" button
    try:
        buy_now_button = driver.find_element(By.ID, "buy-now-button")
        if buy_now_button.is_enabled():
            return True
    except NoSuchElementException:
        pass
    
    return False

def newegg_in_stock(driver):
    try:
        # Grab the product title
        product_title_el = driver.find_element(By.XPATH, "//h1[contains(@class, 'product-title')]")
        product_title = product_title_el.text.strip()

        # Button whose title attribute contains 'Add to cart' + the product title
        xpath = (
            f"//button[contains(translate(@title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart') "
            f"and contains(@title, '{product_title}')]"
        )
        atc_button = driver.find_element(By.XPATH, xpath)

        # Check if disabled
        disabled_attr = atc_button.get_attribute("disabled")
        return disabled_attr is None

    except Exception:
        return False

def fallback_in_stock(driver):
    """
    A generic fallback if we don't have site-specific logic.
    Looks for "add to cart" in the page source.
    """
    page_source = driver.page_source.lower()
    return "add to cart" in page_source

class StockCheckApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RTX 5090 Checker")

        # A text area to show logs
        self.log_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=70, height=20)
        self.log_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Start and Stop buttons
        self.start_button = tk.Button(self, text="Start Bot", command=self.start_bot)
        self.start_button.grid(row=1, column=0, padx=10, pady=5, sticky='ew')

        self.stop_button = tk.Button(self, text="Stop Bot", command=self.stop_bot, state='disabled')
        self.stop_button.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        # Control variables
        self.running = False
        self.check_thread = None
        self.check_interval = 20  # 20 seconds

    def log(self, message):
        """Helper method to log a message to the GUI with a timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)  # auto-scroll

    def start_bot(self):
        """Start the background check in a separate thread."""
        self.log("Starting the bot...")
        self.running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.check_thread = threading.Thread(target=self.run_checks, daemon=True)
        self.check_thread.start()

    def stop_bot(self):
        """Signal the thread to stop."""
        self.log("Stopping the bot...")
        self.running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def run_checks(self):
        """Background loop that checks stock for each URL, then sleeps."""
        while self.running:
            for url in ITEM_URLS:
                if not self.running:
                    break

                self.log(f"Checking stock for: {url}")
                try:
                    if check_in_stock(url):
                        self.log(f"IN STOCK! {url}")
                        self.play_sound_alert()
                    else:
                        self.log("Not in stock.")
                except Exception as e:
                    self.log(f"Error checking {url}: {e}")

            # Sleep for the specified interval after checking all URLs
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)

        self.log("Bot has stopped checking.")

    def play_sound_alert(self):
        """
        Simple audible alert using winsound.
        Adjust frequencies/durations as you'd like.
        """
        winsound.Beep(1000, 400)
        time.sleep(0.1)
        winsound.Beep(1200, 400)
        time.sleep(0.1)
        winsound.Beep(1400, 400)


if __name__ == "__main__":
    app = StockCheckApp()
    app.mainloop()
