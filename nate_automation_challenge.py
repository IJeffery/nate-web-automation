import asyncio
import random
import logging
from pyppeteer import launch

EXAMPLE_DATA = {
    "city": "london",
    "name": "nate",
    "password": "07000000000",
    "email": "nate@nate.tech",
    "gender": "female"
}


async def update_all_visible_elements(page):
    logging.info("Updating page with visible element attributes")
    await page.evaluate('''
        var all = document.getElementsByTagName("*");
        for (var i = 0, max = all.length; i < max; i++) {
            if (!isHidden(all[i])){
                all[i].setAttribute('nate-visible', 'true')
            }
        }
        function isHidden(el) {
            var style = window.getComputedStyle(el);
            return ((style.display === 'none') || (style.visibility === 'hidden'))
        }
    ''')


async def save_file(data, name):
    logging.info("Saving file: " + name)
    file = open(name, "w")
    file.write(data)
    file.close()


async def save_page_source(page, name):
    await update_all_visible_elements(page)
    page_source = await page.content()
    await save_file(page_source, name)


def generate_random_phone_number():
    return '07' + str(random.randint(100000000, 999999999))


async def page_1(page):
    await page.goto(
        'https://nate-eu-west-1-prediction-test-webpages.s3-eu-west-1.amazonaws.com/tech-challenge/page1.html')
    element = await page.querySelector("input[type=button]")
    await page.evaluate("(element) => element.setAttribute('nate-action-type', 'click')", element)
    await save_page_source(page, "page_1.html")
    await page.evaluate("(element) => element.click()", element)


async def page_2(page):
    await page.waitForNavigation()
    elements = await page.querySelectorAll(".custom-option")
    for element in elements:
        element_inner = await element.getProperty("innerHTML")
        element_inner_text = await element_inner.jsonValue()
        if element_inner_text.lower() == EXAMPLE_DATA['city'].lower():
            await page.evaluate("(element) => element.classList.add('selection')", element)
            await page.evaluate("(element) => element.setAttribute('nate-dict-key', 'city')", element)
            await page.evaluate("(element) => element.setAttribute('nate-action-type', 'select')", element)
            break

    elements = await page.querySelectorAll("input[type=button]")
    await page.evaluate("(element) => element.setAttribute('nate-action-type', 'click')", elements[0])
    await page.evaluate("(element) => element.removeAttribute('disabled')", elements[0])
    await save_page_source(page, "page_2.html")
    await page.evaluate("(element) => element.click()", elements[0])


async def page_3(page):
    await page.waitForNavigation()
    elements = await page.querySelectorAll("input")
    for element in elements:

        element_id = await element.getProperty("id")
        element_id_value = await element_id.jsonValue()

        element_type = await element.getProperty("type")
        element_type_value = await element_type.jsonValue()

        if element_id_value == "name":
            await page.evaluate("(element) => element.setAttribute('value', '%s')" % (EXAMPLE_DATA['name']), element)
            await page.evaluate("(element) => element.setAttribute('nate-dict-key', 'name')", element)
            await page.evaluate("(element) => element.setAttribute('nate-action-type', 'input')", element)
        elif element_id_value == "pwd":
            await page.evaluate("(element) => element.setAttribute('value', '%s')" % (EXAMPLE_DATA['password']),
                                element)
            await page.evaluate("(element) => element.setAttribute('nate-dict-key', 'password')", element)
            await page.evaluate("(element) => element.setAttribute('nate-dict-key', 'input')", element)
        elif element_id_value == "phone":
            await page.evaluate("(element) => element.setAttribute('value', '%s')" % generate_random_phone_number(),
                                element)
            await page.evaluate("(element) => element.setAttribute('nate-action-type', 'input')", element)
        elif element_id_value == "email":
            await page.evaluate("(element) => element.setAttribute('value', '%s')" % (EXAMPLE_DATA['email']), element)
            await page.evaluate("(element) => element.setAttribute('nate-dict-key', 'email')", element)
            await page.evaluate("(element) => element.setAttribute('nate-action-type', 'input')", element)
        elif element_type_value == "checkbox":
            element_value = await element.getProperty("value")
            element_value_text = await element_value.jsonValue()
            if element_value_text.lower() == EXAMPLE_DATA['gender'].lower():
                await page.click("input[id=%s]" % element_id_value)
                await page.evaluate("(element) => element.setAttribute('nate-dict-key', 'gender')", element)
                await page.evaluate("(element) => element.setAttribute('nate-action-type', 'check')", element)

    elements = await page.querySelectorAll("button[type=submit]")
    await page.evaluate("(element) => element.setAttribute('nate-action-type', 'click')", elements[0])
    await save_page_source(page, "page_3.html")
    await page.evaluate("(element) => element.click()", elements[0])
    await page.waitForNavigation()


async def intercept_css(response):
    if response.url.endswith('.css'):
        data = await response.text()
        file_name = response.url.split("/")[-1]
        await save_file(data, file_name)


async def log_navigation(request):
    if request.url.endswith('.html'):
        logging.info("Navigating to: " + request.url)


async def main():
    logging.basicConfig(encoding='utf-8', level=logging.INFO)
    logging.info("Starting browser")
    browser = await launch()
    page = await browser.newPage()
    page.on('response', lambda res: asyncio.ensure_future(intercept_css(res)))
    page.on('request', lambda req: asyncio.ensure_future(log_navigation(req)))
    await page_1(page)
    await page_2(page)
    await page_3(page)
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
