# 입력
# Press keys one by one
await page.locator('#area').press_sequentially('Hello World!')

# Hit Enter
await page.get_by_text("Submit").press("Enter")

# Dispatch Control+Right
await page.get_by_role("textbox").press("Control+ArrowRight")

# Press $ sign on keyboard
await page.get_by_role("textbox").press("$")

'''
Backquote, Minus, Equal, Backslash, Backspace, Tab, Delete, Escape,
ArrowDown, End, Enter, Home, Insert, PageDown, PageUp, ArrowRight,
ArrowUp, F1 - F12, Digit0 - Digit9, KeyA - KeyZ, etc.
'''

# <input id=name>
await page.locator('#name').press('Shift+A')

# <input id=name>
await page.locator('#name').press('Shift+ArrowLeft')

# 업로드
async with page.expect_file_chooser() as fc_info:
    await page.get_by_label("Upload file").click()
file_chooser = await fc_info.value
await file_chooser.set_files("myfile.pdf")


# 드래그 앤 드랍
await page.locator("#item-to-be-dragged").drag_to(page.locator("#item-to-drop-at"))



# Reuse authentication state
request_context = playwright.request.new_context(http_credentials={"username": "test", "password": "test"})
request_context.get("https://api.example.com/login")
# Save storage state into a variable.
state = request_context.storage_state()

# Create a new context with the saved storage state.
context = browser.new_context(storage_state=state)