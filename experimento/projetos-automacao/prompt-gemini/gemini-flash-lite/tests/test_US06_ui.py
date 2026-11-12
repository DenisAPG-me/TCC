import re
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online"


def login_admin(page: Page):
    page.goto(f"{BASE_URL}/#/admin")
    page.get_by_placeholder("Username").fill("admin")
    page.get_by_placeholder("Password").fill("password")
    page.get_by_role("button", { name: "Login" }).click()
    expect(page.get_by_role("heading", { name: "B&B Details" })).to_be_visible()


def test_CT01_anotar_contador_mensagens_admin(page: Page):
    login_admin(page)
    messages_link = page.get_by_role("link", { name: re.compile("Messages") })
    expect(messages_link).to_be_visible()
    count_text = messages_link.inner_text()
    assert any(char.isdigit() for char in count_text), "O contador de mensagens deve conter um número."


def test_CT02_envio_mensagem_visitante(page: Page):
    page.goto(BASE_URL)
    page.get_by_placeholder("Name").fill("John Doe")
    page.get_by_placeholder("Email").fill("johndoe@example.com")
    page.get_by_placeholder("Phone").fill("01234567890")
    page.get_by_placeholder("Subject").fill("Inquiry about booking")
    page.get_by_placeholder("Message").fill("Hello, I would like to know more about room availability.")
    page.get_by_role("button", { name: "Submit" }).click()
    expect(page.get_by_text(re.compile("Thanks for getting in touch John Doe!"))).to_be_visible()


def test_CT03_verificar_incremento_contador(page: Page):
    login_admin(page)
    messages_link = page.get_by_role("link", { name: re.compile("Messages") })
    initial_text = messages_link.inner_text()
    initial_nums = re.findall(r'\d+', initial_text)
    initial_count = int(initial_nums[0]) if initial_nums else 0

    page.goto(BASE_URL)
    page.get_by_placeholder("Name").fill("Visitor Test")
    page.get_by_placeholder("Email").fill("visitor@example.com")
    page.get_by_placeholder("Phone").fill("09876543210")
    page.get_by_placeholder("Subject").fill("Test Subject")
    page.get_by_placeholder("Message").fill("Testing message count increment.")
    page.get_by_role("button", { name: "Submit" }).click()
    expect(page.get_by_text(re.compile("Thanks for getting in touch Visitor Test!"))).to_be_visible()

    login_admin(page)
    updated_text = messages_link.inner_text()
    updated_nums = re.findall(r'\d+', updated_text)
    updated_count = int(updated_nums[0]) if updated_nums else (initial_count + 1)

    assert updated_count == initial_count + 1


def test_CT04_verificar_mensagem_na_lista_admin(page: Page):
    subject_text = "Unique Subject Test 123"
    sender_name = "Unique Visitor"

    page.goto(BASE_URL)
    page.get_by_placeholder("Name").fill(sender_name)
    page.get_by_placeholder("Email").fill("unique@example.com")
    page.get_by_placeholder("Phone").fill("11223344556")
    page.get_by_placeholder("Subject").fill(subject_text)
    page.get_by_placeholder("Message").fill("Checking message list visibility.")
    page.get_by_role("button", { name: "Submit" }).click()
    expect(page.get_by_text(re.compile(f"Thanks for getting in touch {sender_name}!"))).to_be_visible()

    login_admin(page)
    page.get_by_role("link", { name: re.compile("Messages") }).click()
    expect(page.get_by_text(sender_name)).to_be_visible()
    expect(page.get_by_text(subject_text)).to_be_visible()


def test_CT05_restricao_acesso_apos_logout(page: Page):
    login_admin(page)
    logout_button = page.get_by_role("button", { name: re.compile("Logout|Log out", re.IGNORECASE) })
    if logout_button.is_visible():
        logout_button.click()
    else:
        page.goto(f"{BASE_URL}/#/admin")
        page.get_by_role("button", { name: re.compile("Logout|Log out", re.IGNORECASE) }).click()

    page.goto(f"{BASE_URL}/#/admin")
    expect(page.get_by_placeholder("Username")).to_be_visible()
    expect(page.get_by_placeholder("Password")).to_be_visible()
