import unittest
import lxml.html

from pyppeteer import launch


class TestWebPageLoad(unittest.IsolatedAsyncioTestCase):

    async def test_page_valid_html(self):
        browser = await launch()
        page = await browser.newPage()
        await page.goto(
            'https://nate-eu-west-1-prediction-test-webpages.s3-eu-west-1.amazonaws.com/tech-challenge/page1.html')
        page_source = await page.content()
        await browser.close()
        assert(lxml.html.fromstring(page_source).find('.//*') is not None)


if __name__ == '__main__':
    unittest.main()
