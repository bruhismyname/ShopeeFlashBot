"""
Bot service for executing Shopee flash sale tasks
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import time
import undetected_chromedriver as uc
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BotService:
    """Service for managing bot instances"""
    
    def __init__(self):
        self.active_bots: Dict[int, Any] = {}
    
    def create_driver(self, user_agent: Optional[str] = None, 
                     user_data_dir: Optional[str] = None) -> webdriver.Chrome:
        """Create a Chrome driver instance with specified options"""
        chrome_options = Options()
        
        if user_agent:
            chrome_options.add_argument(f"user-agent={user_agent}")
        
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--window-size=1280,720")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--headless")  # Run in headless mode for SaaS
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        if user_data_dir:
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        driver = uc.Chrome(options=chrome_options)
        return driver
    
    def wait_until_target_time(self, target_time: str) -> None:
        """Wait until the specified target time"""
        logger.info(f"Waiting until target time: {target_time}")
        while True:
            now = datetime.now().strftime("%H:%M:%S")
            if now == target_time:
                logger.info("Target time reached")
                break
            time.sleep(1)
    
    def execute_purchase_flow(self, driver: webdriver.Chrome, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the purchase flow based on configuration"""
        result = {
            "success": False,
            "steps_completed": [],
            "error": None
        }
        
        try:
            # Refresh page at target time
            driver.refresh()
            result["steps_completed"].append("page_refreshed")
            logger.info("Page refreshed")
            
            # Select product options if configured
            if config.get("product_option"):
                try:
                    button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//button[@aria-label='{config['product_option']}']"))
                    )
                    button.click()
                    result["steps_completed"].append("product_option_selected")
                    logger.info(f"Selected product option: {config['product_option']}")
                except TimeoutException:
                    logger.warning(f"Product option button not found: {config['product_option']}")
            
            # Click buy with voucher or buy now
            # Note: Button text and selectors are Shopee-specific and may need localization
            try:
                buy_button_xpath = config.get("buy_button_xpath")
                if not buy_button_xpath:
                    # Default selectors for Indonesian Shopee site
                    if config.get("use_voucher", False):
                        buy_button_xpath = "//button[contains(text(), 'Beli Dengan Voucher')]"
                    else:
                        buy_button_xpath = "//button[contains(text(), 'beli sekarang')]"
                
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, buy_button_xpath))
                )
                button.click()
                result["steps_completed"].append("buy_button_clicked")
                logger.info("Buy button clicked")
            except TimeoutException:
                raise Exception("Buy button not found")
            
            # Click checkout
            try:
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'shopee-button-solid') and .//span[text()='checkout']]"))
                )
                button.click()
                result["steps_completed"].append("checkout_clicked")
                logger.info("Checkout clicked")
            except TimeoutException:
                logger.warning("Checkout button not found")
            
            # Select payment method
            payment_method = config.get("payment_method", "ShopeePay")
            try:
                if payment_method == "ShopeePay":
                    button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='ShopeePay']]"))
                    )
                    button.click()
                elif payment_method == "COD":
                    button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='COD' and @aria-disabled='false']"))
                    )
                    button.click()
                elif payment_method == "Bank Transfer":
                    button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Transfer Bank')]"))
                    )
                    button.click()
                    
                    if config.get("bank_name"):
                        bank_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'checkout-bank-transfer-item__title') and text()='{config['bank_name']}']"))
                        )
                        bank_button.click()
                
                result["steps_completed"].append("payment_method_selected")
                logger.info(f"Payment method selected: {payment_method}")
            except TimeoutException:
                logger.warning(f"Payment method button not found: {payment_method}")
            
            # Complete order (only if auto_confirm is enabled)
            if config.get("auto_confirm", False):
                try:
                    button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.stardust-button.stardust-button--primary.stardust-button--large"))
                    )
                    button.click()
                    result["steps_completed"].append("order_placed")
                    logger.info("Order placed")
                except TimeoutException:
                    logger.warning("Order confirmation button not found")
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error during purchase flow: {e}")
        
        return result
    
    def run_task(self, task_id: int, url: str, target_time: str, 
                 config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a bot task"""
        driver = None
        try:
            # Create driver
            driver = self.create_driver(
                user_agent=config.get("user_agent"),
                user_data_dir=config.get("user_data_dir")
            )
            
            self.active_bots[task_id] = driver
            
            # Navigate to URL
            driver.get(url)
            logger.info(f"Navigated to URL: {url}")
            
            # Wait for target time
            self.wait_until_target_time(target_time)
            
            # Execute purchase flow
            result = self.execute_purchase_flow(driver, config)
            
            return result
            
        except Exception as e:
            logger.error(f"Error running task {task_id}: {e}")
            return {
                "success": False,
                "steps_completed": [],
                "error": str(e)
            }
        finally:
            if driver:
                driver.quit()
            if task_id in self.active_bots:
                del self.active_bots[task_id]
    
    def stop_task(self, task_id: int) -> bool:
        """Stop a running bot task"""
        if task_id in self.active_bots:
            try:
                self.active_bots[task_id].quit()
                del self.active_bots[task_id]
                return True
            except Exception as e:
                logger.error(f"Error stopping task {task_id}: {e}")
                return False
        return False

bot_service = BotService()
