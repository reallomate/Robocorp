from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_parts_from_website():
    open_website()
    close_annoying_popup()
    orders = get_orders()

    for order in orders:
        fill_the_form(order)

    archive_receipts()

def open_website():
    browser.configure(
        slowmo=100,
    )
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_popup():
    page = browser.page()
    page.click("text=I guess so...")

def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

    library = Tables()
    orders = library.read_table_from_csv("orders.csv", column_unknown=True)
    return orders

def fill_the_form(order):
    page = browser.page()

    page.select_option("#head", str(order["Head"]))
    page.click(f'label[for="id-body-{str(order["Body"])}"]')
    page.fill("input[type='number']", str(order["Legs"]))
    page.fill("input[type='text']", order["Address"])
    page.click("#order")

    while page.is_visible("div[class*='alert-danger']"):
        page.click("#order")

    store_receipt_as_pdf(order["Order number"])

    page.click("#order-another")
    close_annoying_popup()

def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt_html, f"output/receipts/receipt-{str(order_number)}.pdf")
    embed_screenshot_to_receipt(screenshot_robot(order_number), f"output/receipts/receipt-{str(order_number)}.pdf")

def screenshot_robot(order_number):
    page = browser.page()
    path = f"output/screenshots/screenshot-{str(order_number)}.png"
    page.screenshot(path=path)
    return path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "output/receipts.zip")
