# selenium 4
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.select import Select
from webdriver_manager.firefox import GeckoDriverManager


def init(driver):
    driver.get("https://www.hcilondon.gov.in/appointment/")
    return


def ensure_service_selected(driver):
    service_selector = Select(driver.find_element(by=By.ID, value="serviceid"))
    # if service_selector.first_selected_option.text != 'Surrender of Indian Passport':
    # service_selector.select_by_index(1)
    if service_selector.first_selected_option.text != "VISA":
        service_selector.select_by_index(4)
    return


def find_available_appointment(driver, location_idx):
    ensure_service_selected(driver)
    loc_selector = Select(driver.find_element(by=By.ID, value="locationid"))
    loc_selector.select_by_index(location_idx)
    dates = (
        driver.find_element(By.ID, "calendar")
        .find_element(By.CLASS_NAME, "dates")
        .find_elements(By.TAG_NAME, "li")
    )
    available_date = next(
        (
            e.get_attribute("id")[3:]
            for e in dates
            if e.value_of_css_property("color") == "rgb(40, 185, 19)"
        ),
        "None",
    )
    return available_date


if __name__ == "__main__":
    gecko_driver = GeckoDriverManager().install()
    driver = webdriver.Firefox(service=FirefoxService(gecko_driver))
    init(driver)
    ensure_service_selected(driver)
    loc_selector = Select(driver.find_element(by=By.ID, value="locationid"))
    locations = [e.text for e in loc_selector.options]

    i = 1  # Skip '--select--'
    results = {}
    while i < len(locations):
        try:
            results[i] = find_available_appointment(driver, i)
            print(locations[i], results[i], sep="\t")
            i += 1
        except NoSuchElementException:
            print(driver.find_element(By.TAG_NAME, "body").text)
            init(driver)

    driver.quit()
