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
            attribute_blocks: list[dict] = None,
            image_url: str | None = None
    ) -> None:
        self.attribute_blocks = attribute_blocks
        self.image_url = image_url

    @staticmethod
    def _get_driver() -> WebDriver:
        """
        Returns: WebDriver with Enable CDP (Chrome DevTools Protocol) support
        """
        options = Options()
        options.add_argument('--headless')  # comment to enable graphics mode
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--kiosk-printing')

        # Enable CDP (Chrome DevTools Protocol) support
        return webdriver.Chrome(options=options)

    def __get_html_image(self) -> str:
        """
        Returns: an HTML string containing the image block.
        """
        image = self.image_url

        image_html_block = f"""
        <div class="info">
            <div class="image-box">
                <img src="{image}" alt="Tile preview">
            </div>
        </div>
        """

        return image_html_block

    def __get_html_attribute_blocks(self) -> str:
        """
        Returns: an HTML string of all attribute blocks.
        """

        attribute_blocks = []
        for block_idx, attribute_block in enumerate(self.attribute_blocks[1:]):

            if block_idx == 0 and self.image_url:
                name = f"<h1>{list(self.attribute_blocks[0].values())[0]}</h1>"
            else:
                name = ""

            rows = ""
            for attribute, value in attribute_block.items():
                rows += f'''
                <div class="row">
                    <div class="label">{attribute}:</div> 
                    <div class="value">{value}</div>
                </div>
                '''

            attributes_block = f"""
            <div class="info">
                {name}
                <div class="main-info">
                    {rows}
                </div>
            </div>
            """

            attribute_blocks.append(attributes_block)

        return "".join(attribute_blocks)

    @staticmethod
    def __get_html_footer() -> str:
        """
        Returns: an HTML string containing the footer.
        """
        footer = """
            <div class="footer">
                We utilize information gleaned from manufacturer websites to compile data and images to create a custom
                Project Binder for you.<br />
                Please note that acceptance of this Project Binder, visiting our website, or utilizing our related services
                explicitly waives <a>Spec-ID</a> of ALL liability pursuant to our <a>Terms and Conditions</a>
            </div>
        """

        return footer

    def __get_html(self) -> str:
        """
        Returns: full HTML string (document) with styles for converting to pdf
        """
        styles = """
        @page {
            size: Letter;
            margin: 0px;
        }
        * {
            box-sizing: border-box;
            font-family: 'Inter', Arial, sans-serif;
        }
        body {
            margin: 0;
            padding: 0;
            background: #fff;
        }
        .image-box {
            width: 92mm;
            height: 92mm;
            border: 1px solid #ddd;
        }
        .image-box img {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        .info {
            font-size: 16px;
        }
        .row {
            align-items: center;
        }
        .label {
            flex: 0 0 auto;
            color: #666;
            word-break: break-word;
            word-wrap: break-word;
            overflow-wrap: break-word;
            width: 55%;
            color: #504840;
            font-weight: 400;
            font-size: 14px
        }
        .value {
            flex: 1 1 auto;
            white-space: nowrap;
            line-height: 1.2;
            font-size: 16px
        }
        a {
            color: #C05B28;
            line-height: 1.5;
        }
        .main-info {
            display: flex;
            flex-direction: column;
            gap: 4.5mm;
        }
        .page {
            width: 8.5in;
            min-height: 11in;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .info-wrapper {
            display: grid;
            grid-template-columns: 92mm 84mm;
            margin: 53px;
            gap: 16mm 10mm;
        }
        """

        if self.image_url:
            image = self.__get_html_image()
            name = ""
            styles += """
            h1 {
                margin: 0 0 10px 0;
                font-size: 33px;
                color: #332E28;
            }
            .footer {
                font-size: 11px;
                line-height: 1.6;
                color: #332E28;
                border-top: 1px solid #C05B28;
                background-color: #FBFAF9;
                padding-top: 5mm;
                padding: 14px 40.5px;
            }
            """
        else:
            image = ""
            name = f"<h1>{list(self.attribute_blocks[0].values())[0]}</h1>"
            styles += """
            h1 {
                margin: 40px 0px -40px 50px;
                font-size: 33px;
                color: #332E28;
            }
            .footer {
                font-size: 11px;
                line-height: 1.6;
                color: #332E28;
                border-top: 1px solid #C05B28;
                background-color: #FBFAF9;
                padding-top: 5mm;
                padding: 14px 40.5px;
                margin-top: auto;
            }
            """

        attribute_blocks = self.__get_html_attribute_blocks()
        footer = self.__get_html_footer()

        html_code = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <title>Product Sheet</title>
            <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
            <style>
                {styles}
            </style>
        </head>
        <body>
            <div class="page">
                {name}
                <!-- MAIN CONTENT -->
                <div class="info-wrapper">
                    {image}
                    {attribute_blocks}
                </div>
                <!-- FOOTER -->
                {footer}
            </div>
        </body>
        </html>
        """

        return html_code

    def get_pdf(self) -> dict:
        """
        Use selenium to convert html to pdf
        Returns: pdf dict
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
                'preferCSSPageSize': True,
            }

            pdf = driver.execute_cdp_cmd("Page.printToPDF", print_options)
        finally:
            driver.quit()

        return pdf


if __name__ == "__main__":

    attribute_blocks = [
        # Name (title) block must always be first
        {
            None: "Product Name"
        },
        # next attributes block
        {
            "Manufacturer": "Tilebar",
            "Collection": "BG992-223.6",
            "Color": "Blue",
            "Size": "15 x 15",
            "Edge": "Some Edge",
            "Material": "Ceramic",
        },
        # next attributes block
        {
            "Manufacturer": "Tilebar",
            "Collection": "BG992-223.6",
            "Color": "Blue",
            "Size": "15 x 15",
            "Edge": "Some Edge",
            "Material": "Ceramic",
        },
        # next attributes block
        {
            "Manufacturer": "Tilebar",
            "Collection": "BG992-223.6",
            "Color": "Blue",
            "Size": "15 x 15",
            "Edge": "Some Edge",
            "Material": "Ceramic",
        },
    ]

    url = "https://image_url_example.jpg"
    file_path = "created_pdf.pdf"

    pdf_creator = PdfCreator(attribute_blocks=attribute_blocks, image_url=None)
    pdf = pdf_creator.get_pdf()
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(pdf['data']))