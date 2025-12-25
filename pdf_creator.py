# PdfCreator imports
import base64
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# PdfCreator imports for the type annotations
from selenium.webdriver.chrome.webdriver import WebDriver


class PdfCreator:
    """
    PdfCreator: use selenium for creating custom pdf file
    """
    def __init__(
            self,
            attributes: dict = None,
            image_url: str = None
    ) -> None:
        self.attributes = attributes
        self.image_url = image_url

    @staticmethod
    def _get_driver() -> WebDriver:
        """
        Returns: WebDriver with Enable CDP (Chrome DevTools Protocol) support
        """
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--kiosk-printing')

        # Enable CDP (Chrome DevTools Protocol) support
        return webdriver.Chrome(options=options)

    def __get_html_image(self) -> str:
        """
        Returns: an HTML with styles for image
        """
        image = self.image_url
        styled_image = f"""
            <div style="margin: 20px auto; padding: 10px; border: 1px solid #ccc; text-align: center;">
                <img src="{image}" style="max-width: 300px; height: auto;" />
            </div>
            """
        return styled_image

    def __get_html_attributes(self) -> str:
        """
        Returns: an HTML table with styles for attributes
        """
        styles = """
        <style>
            table.specs {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            table.specs th, table.specs td {
                border: 1px solid #ccc;
                padding: 8px 12px;
                text-align: left;
            }
            table.specs th {
                background-color: #f4f4f4;
                font-weight: bold;
            }
        </style>
        """

        table = "<h1>Specifications</h1>\n"
        table += "<table class='specs'>"

        for attribute, value in self.attributes.items():
            table += f"<tr><td>{attribute}</td><td>{value}</td></tr>"

        table += "</tbody></table>"

        return styles + table

    def __get_html(self):
        """
        Returns: full HTML for converting to pdf
        """
        styles = """
        <style>
            .collection-uses, .collection-uses * {

                max-width: 100% !important;
                box-sizing: border-box !important;
                margin: 0 !important;
            }
        </style>
        """

        image = self.__get_html_image()
        attributes = self.__get_html_attributes()

        html_code = f"""
        <!DOCTYPE html>
        <html>
        {styles}
        <body>
        {image}
        {attributes}
        </body>
        </html>
        """

        return html_code

    def get_pdf(self) -> dict:
        """
        Returns: pdf dict
        use selenium to convert html to pdf
        """
        html_code = self.__get_html()

        # selenium block
        driver = self._get_driver()
        try:
            # Loading HTML via data URI
            driver.get("data:text/html;charset=utf-8," + quote(html_code))

            # waiting for entire page load
            WebDriverWait(driver, 5).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )

            # Using DevTools Protocol to Save to PDF
            print_options = {
                'landscape': False,
                'displayHeaderFooter': False,
                'printBackground': True,
                'preferCSSPageSize': False,
                'paperWidth': 8.27,  # A4 format
                'paperHeight': 11.69  # A4 format
            }

            pdf = driver.execute_cdp_cmd("Page.printToPDF", print_options)
        finally:
            driver.quit()

        return pdf


if __name__ == "__main__":
    attributes = {
        "Name": "Some Name",
        "Size": "15 x 15",
        "Edge": "Some Edge"
    }

    url = "image_url"

    pdf_creator = PdfCreator(attributes=attributes, image_url=url)
    pdf = pdf_creator.get_pdf()
    with open("created_pdf.pdf", "wb") as f:
        f.write(base64.b64decode(pdf['data']))
