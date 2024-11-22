import os.path

THREADS = 5  # for register account / claim rewards mode / approve email mode
MIN_PROXY_SCORE = 50  # Put MIN_PROXY_SCORE = 0 not to check proxy score (if site is down)

#########################################
APPROVE_EMAIL = False  # approve email (NEEDED IMAP AND ACCESS TO EMAIL)
CONNECT_WALLET = False  # connect wallet (put private keys in wallets.txt)
SEND_WALLET_APPROVE_LINK_TO_EMAIL = False  # send approve link to email
APPROVE_WALLET_ON_EMAIL = False  # get approve link from email (NEEDED IMAP AND ACCESS TO EMAIL)
SEMI_AUTOMATIC_APPROVE_LINK = False  # if True - allow to manual paste approve link from email to CLI
SINGLE_IMAP_ACCOUNT = False  # usage "name@domain.com:password"

IMAPS = {
    "gmail.com": "imap.gmail.com",
    "outlook.com": "outlook.office365.com",
    "yahoo.com": "imap.mail.yahoo.com",
    "aol.com": "imap.aol.com",
    "zoho.com": "imap.zoho.com",
    "icloud.com": "imap.mail.me.com",
    "mail.com": "imap.mail.com",
    "gmx.com": "imap.gmx.com",
    "protonmail.com": "imap.proton.me",
    "dfirstmail.com": "imap.firstmail.ltd"  # Firstmail домен
}

CAPTCHA_PARAMS = {
    "captcha_type": "v2",
    "invisible_captcha": False,
    "sitekey": "6LeeT-0pAAAAAFJ5JnCpNcbYCBcAerNHlkK4nm6y",
    "captcha_url": "https://app.getgrass.io/register"
}
def get_imap_from_email(email):
    domain = email.split("@")[1]

    if "firstmail" in domain:
        return "imap.firstmail.ltd"
    elif domain in IMAPS:
        return IMAPS[domain]
        print(f"IMAP для домена {domain} не найден.")
        return input("Введите IMAP-домен вручную: ")

def load_accounts(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл {filepath} не найден!")
    accounts = []
    with open(filepath, "r") as file:
        for line in file:
            if ":" in line.strip():
                email, password = line.strip().split(":", 1)
                imap_server = get_imap_from_email(email)
                accounts.append({"email": email, "password": password, "imap": imap_server})
            else:
                print(f"Неверный формат строки: {line.strip()}")
    return accounts

def select_imap(accounts):
    if accounts:
        return accounts[0]["imap"]
    else:
        print("Список аккаунтов пуст. Укажите IMAP вручную.")
        return input("Введите IMAP-домен вручную: ")

#########################################
CLAIM_REWARDS_ONLY = False  # claim tiers rewards only (https://app.getgrass.io/dashboard/referral-program)

STOP_ACCOUNTS_WHEN_SITE_IS_DOWN = True  # stop account for 20 minutes, to reduce proxy traffic usage
CHECK_POINTS = True  # show point for each account every nearly 10 minutes
SHOW_LOGS_RARELY = False  # not always show info about actions to decrease pc influence

# Mining mode
MINING_MODE = True  # False - not mine grass, True - mine grass | Remove all True on approve \ register section

# REGISTER PARAMETERS ONLY
REGISTER_ACCOUNT_ONLY = True
REGISTER_DELAY = (3, 7)

TWO_CAPTCHA_API_KEY = "d91cde282734ac715b2cc39150c75458"
ANTICAPTCHA_API_KEY = ""
CAPMONSTER_API_KEY = ""
CAPSOLVER_API_KEY = ""
CAPTCHAAI_API_KEY = ""

# Use proxy also for mail handling
USE_PROXY_FOR_IMAP = False

########################################
ACCOUNTS_FILE_PATH = "data/accounts.txt"
PROXIES_FILE_PATH = "data/proxies.txt"
WALLETS_FILE_PATH = "data/wallets.txt"
PROXY_DB_PATH = 'data/proxies_stats.db'


try:
    accounts = load_accounts(ACCOUNTS_FILE_PATH)
    IMAP_DOMAIN = select_imap(accounts)
    print(f"Используемый IMAP-домен: {IMAP_DOMAIN}")
except Exception as e:
    print(f"Ошибка: {e}")
