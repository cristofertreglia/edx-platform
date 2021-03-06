#pylint: disable=C0111
#pylint: disable=W0621

from lettuce import world
import time
from urllib import quote_plus
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from lettuce.django import django_url


@world.absorb
def wait(seconds):
    time.sleep(float(seconds))


@world.absorb
def wait_for(func):
    WebDriverWait(world.browser.driver, 5).until(func)


@world.absorb
def visit(url):
    world.browser.visit(django_url(url))


@world.absorb
def url_equals(url):
    return world.browser.url == django_url(url)


@world.absorb
def is_css_present(css_selector, wait_time=5):
    return world.browser.is_element_present_by_css(css_selector, wait_time=wait_time)


@world.absorb
def is_css_not_present(css_selector, wait_time=5):
    return world.browser.is_element_not_present_by_css(css_selector, wait_time=wait_time)


@world.absorb
def css_has_text(css_selector, text):
    return world.css_text(css_selector) == text


@world.absorb
def css_find(css, wait_time=5):
    def is_visible(driver):
        return EC.visibility_of_element_located((By.CSS_SELECTOR, css,))

    world.browser.is_element_present_by_css(css, wait_time=wait_time)
    wait_for(is_visible)
    return world.browser.find_by_css(css)


@world.absorb
def css_click(css_selector):
    """
    Perform a click on a CSS selector, retrying if it initially fails
    """
    assert is_css_present(css_selector)
    try:
        world.browser.find_by_css(css_selector).click()

    except WebDriverException:
        # Occassionally, MathJax or other JavaScript can cover up
        # an element  temporarily.
        # If this happens, wait a second, then try again
        world.wait(1)
        world.browser.find_by_css(css_selector).click()


@world.absorb
def css_click_at(css, x=10, y=10):
    '''
    A method to click at x,y coordinates of the element
    rather than in the center of the element
    '''
    e = css_find(css).first
    e.action_chains.move_to_element_with_offset(e._element, x, y)
    e.action_chains.click()
    e.action_chains.perform()


@world.absorb
def id_click(elem_id):
    """
    Perform a click on an element as specified by its id
    """
    world.css_click('#%s' % elem_id)


@world.absorb
def css_fill(css_selector, text):
    assert is_css_present(css_selector)
    world.browser.find_by_css(css_selector).first.fill(text)


@world.absorb
def click_link(partial_text):
    world.browser.find_link_by_partial_text(partial_text).first.click()


@world.absorb
def css_text(css_selector):

    # Wait for the css selector to appear
    if world.is_css_present(css_selector):
        try:
            return world.browser.find_by_css(css_selector).first.text
        except StaleElementReferenceException:
            # The DOM was still redrawing. Wait a second and try again.
            world.wait(1)
            return world.browser.find_by_css(css_selector).first.text
    else:
        return ""


@world.absorb
def css_visible(css_selector):
    assert is_css_present(css_selector)
    return world.browser.find_by_css(css_selector).visible


@world.absorb
def dialogs_closed():
    def are_dialogs_closed(driver):
        '''
        Return True when no modal dialogs are visible
        '''
        return not css_visible('.modal')
    wait_for(are_dialogs_closed)
    return not css_visible('.modal')


@world.absorb
def save_the_html(path='/tmp'):
    u = world.browser.url
    html = world.browser.html.encode('ascii', 'ignore')
    filename = '%s.html' % quote_plus(u)
    f = open('%s/%s' % (path, filename), 'w')
    f.write(html)
    f.close()


@world.absorb
def click_course_settings():
    course_settings_css = 'li.nav-course-settings'
    if world.browser.is_element_present_by_css(course_settings_css):
        world.css_click(course_settings_css)


@world.absorb
def click_tools():
    tools_css = 'li.nav-course-tools'
    if world.browser.is_element_present_by_css(tools_css):
        world.css_click(tools_css)
