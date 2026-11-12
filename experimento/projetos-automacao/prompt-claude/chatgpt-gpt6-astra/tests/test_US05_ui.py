import re

from playwright.sync_api import Page, expect


BASE_URL = "https://automationintesting.online"
LOGIN_PATH = "/admin"
ROOMS_PATH = "/admin/rooms"
HOME_PATH = "/"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"
INVALID_PASSWORD = "senha_incorreta"
EMPTY_VALUE = ""

INVALID_CREDENTIALS_MESSAGE = "Invalid credentials"
ROOM_NUMBER = "101"
ROOM_TYPE = "Single"
MENU_ITEMS = ("Rooms", "Report", "Branding", "Messages")

USERNAME_LABEL = "Username"
PASSWORD_LABEL = "Password"
LOGIN_BUTTON_NAME = "Login"
LOGOUT_BUTTON_NAME = "Logout"

EXPECT_TIMEOUT_MS = 15_000
NAVIGATION_TIMEOUT_MS = 30_000


def absolute_url(path: str) -> str:
    return f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}"


def url_pattern(path: str) -> re.Pattern:
    canonical_url = absolute_url(path).rstrip("/")
    return re.compile(
        rf"^{re.escape(canonical_url)}/?(?:\?[^#]*)?(?:#.*)?$"
    )


def username_field(page: Page):
    return page.get_by_label(USERNAME_LABEL, exact=True)


def password_field(page: Page):
    return page.get_by_label(PASSWORD_LABEL, exact=True)


def login_button(page: Page):
    return page.get_by_role("button", name=LOGIN_BUTTON_NAME, exact=True)


def room_row(page: Page):
    return page.get_by_role("row").filter(
        has=page.get_by_role("cell", name=ROOM_NUMBER, exact=True)
    )


def assert_login_form_visible(page: Page) -> None:
    expect(username_field(page)).to_be_visible(timeout=EXPECT_TIMEOUT_MS)
    expect(password_field(page)).to_be_visible(timeout=EXPECT_TIMEOUT_MS)
    expect(login_button(page)).to_be_visible(timeout=EXPECT_TIMEOUT_MS)


def open_login(page: Page) -> None:
    page.goto(
        absolute_url(LOGIN_PATH),
        wait_until="domcontentloaded",
        timeout=NAVIGATION_TIMEOUT_MS,
    )
    expect(page).to_have_url(
        url_pattern(LOGIN_PATH), timeout=EXPECT_TIMEOUT_MS
    )
    assert_login_form_visible(page)


def submit_credentials(page: Page, username: str, password: str) -> None:
    username_field(page).fill(username)
    password_field(page).fill(password)
    login_button(page).click()


def login_successfully(page: Page) -> None:
    open_login(page)
    submit_credentials(page, ADMIN_USERNAME, ADMIN_PASSWORD)
    expect(page).to_have_url(
        url_pattern(ROOMS_PATH), timeout=EXPECT_TIMEOUT_MS
    )
    expect(
        page.get_by_role("button", name=LOGOUT_BUTTON_NAME, exact=True)
    ).to_be_visible(timeout=EXPECT_TIMEOUT_MS)


def logout(page: Page) -> None:
    page.get_by_role(
        "button", name=LOGOUT_BUTTON_NAME, exact=True
    ).click()
    expect(page).to_have_url(
        url_pattern(HOME_PATH), timeout=EXPECT_TIMEOUT_MS
    )


def test_ct01_enviar_credenciais_vazias(page: Page) -> None:
    open_login(page)
    submit_credentials(page, EMPTY_VALUE, EMPTY_VALUE)

    expect(
        page.get_by_text(INVALID_CREDENTIALS_MESSAGE, exact=True)
    ).to_be_visible(timeout=EXPECT_TIMEOUT_MS)
    expect(page).to_have_url(
        url_pattern(LOGIN_PATH), timeout=EXPECT_TIMEOUT_MS
    )
    assert_login_form_visible(page)


def test_ct02_enviar_senha_incorreta(page: Page) -> None:
    open_login(page)
    submit_credentials(page, ADMIN_USERNAME, INVALID_PASSWORD)

    expect(
        page.get_by_text(INVALID_CREDENTIALS_MESSAGE, exact=True)
    ).to_be_visible(timeout=EXPECT_TIMEOUT_MS)
    assert_login_form_visible(page)


def test_ct03_entrar_com_credenciais_validas(page: Page) -> None:
    login_successfully(page)

    expect(page).to_have_url(
        url_pattern(ROOMS_PATH), timeout=EXPECT_TIMEOUT_MS
    )

    row = room_row(page)
    expect(row).to_have_count(1, timeout=EXPECT_TIMEOUT_MS)
    expect(row).to_be_visible(timeout=EXPECT_TIMEOUT_MS)
    expect(
        row.get_by_role("cell", name=ROOM_NUMBER, exact=True)
    ).to_be_visible(timeout=EXPECT_TIMEOUT_MS)
    expect(
        row.get_by_role("cell", name=ROOM_TYPE, exact=True)
    ).to_be_visible(timeout=EXPECT_TIMEOUT_MS)

    navigation = page.get_by_role("navigation")
    expect(navigation).to_be_visible(timeout=EXPECT_TIMEOUT_MS)
    for item in MENU_ITEMS:
        expect(
            navigation.get_by_role("link", name=item, exact=True)
        ).to_be_visible(timeout=EXPECT_TIMEOUT_MS)


def test_ct04_sair_do_painel_administrativo(page: Page) -> None:
    login_successfully(page)
    logout(page)

    expect(page).to_have_url(
        url_pattern(HOME_PATH), timeout=EXPECT_TIMEOUT_MS
    )
    expect(username_field(page)).to_be_hidden(timeout=EXPECT_TIMEOUT_MS)
    expect(password_field(page)).to_be_hidden(timeout=EXPECT_TIMEOUT_MS)
    expect(login_button(page)).to_be_hidden(timeout=EXPECT_TIMEOUT_MS)


def test_ct05_acessar_quartos_apos_logout(page: Page) -> None:
    login_successfully(page)
    logout(page)

    # Preserva o mesmo contexto para verificar a sessão após o logout.
    page.goto(
        absolute_url(ROOMS_PATH),
        wait_until="domcontentloaded",
        timeout=NAVIGATION_TIMEOUT_MS,
    )

    expect(page).to_have_url(
        url_pattern(LOGIN_PATH), timeout=EXPECT_TIMEOUT_MS
    )
    assert_login_form_visible(page)
    expect(room_row(page)).to_be_hidden(timeout=EXPECT_TIMEOUT_MS)
