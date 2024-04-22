from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

def generateXPATH(element: WebElement, current: str):
    child_tag = element.tag_name
    if child_tag == "html":
        return "/html[1]" + current
    
    parent_element = element.find_element(By.XPATH, "..")
    children_elements = parent_element.find_elements(By.XPATH, "*")
    count = 0
    for index, child_element in enumerate(children_elements):
        if child_tag == child_element.tag_name:
            count+=1
        if element == child_element:
            return generateXPATH(parent_element, f"/{child_tag}[{count}]{current}")
    return None