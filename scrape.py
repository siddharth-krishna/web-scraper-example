import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService

# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.select import Select
import sendgrid
from sendgrid.helpers.mail import *

# from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager


def init(driver):
    driver.get("https://www.hcilondon.gov.in/appointment/")
    return


def try_until(driver, fn, max_retries=10):
    for _ in range(max_retries):
        try:
            result = fn()
            return result
        except NoSuchElementException:
            print(driver.find_element(By.TAG_NAME, "body").text)
            init(driver)
    print("Max retries reached. Aborting.")


def ensure_service_selected(driver):
    service_selector = Select(driver.find_element(by=By.ID, value="serviceid"))
    # if service_selector.first_selected_option.text != "Surrender of Indian Passport":
    #     service_selector.select_by_index(1)
    if service_selector.first_selected_option.text != "VISA":
        service_selector.select_by_visible_text("VISA")
    return


def find_available_appointment(driver, location_idx):
    ensure_service_selected(driver)
    loc_selector = Select(driver.find_element(by=By.ID, value="locationid"))
    loc_selector.select_by_index(location_idx)
    cal = driver.find_element(By.ID, "calendar")
    cal.screenshot(f"out_{location_idx}.png")
    dates = cal.find_element(By.CLASS_NAME, "dates").find_elements(By.TAG_NAME, "li")
    available_date = next(
        (
            e.get_attribute("id")[3:]
            for e in dates
            # if e.value_of_css_property("color") == "rgb(40, 185, 19)"
            if e.value_of_css_property("color") == "rgba(40, 185, 19, 1)"
        ),
        None,
    )
    return available_date


if __name__ == "__main__":
    options = Options()
    options.add_argument("-headless")
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )
    init(driver)
    try_until(driver, lambda: ensure_service_selected(driver))
    loc_selector = Select(driver.find_element(by=By.ID, value="locationid"))
    locations = [e.text for e in loc_selector.options]

    results = {}
    for i in range(1, len(locations)):  # Skip '--select--'
        results[i] = try_until(driver, lambda: find_available_appointment(driver, i))
        print(locations[i], results[i], sep="\t\t")

    driver.quit()

    if any(v is not None for v in results.values()):
        subject = "APPOINTMENT FOUND!"
        from_email = Email(os.environ.get("SCRAPER_FROM_ID"))
        to_emails = [To(e) for e in os.environ.get("SCRAPER_TO_ID").split(",")]
        body = "\n".join(
            (f"{locations[loc]:<70}\t{res}") for loc, res in results.items()
        )
        content = Content("text/plain", body)

        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
        mail = Mail(from_email, to_emails, subject, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)
