import argparse
import asyncio
import ctypes
import os
import random
import sys
import traceback

from art import text2art
from imap_tools import MailboxLoginError
from termcolor import cprint

from better_proxy import Proxy

from core import Grass
from core.autoreger import AutoReger
from core.utils import logger, file_to_list
from core.utils.accounts_db import AccountsDB
from core.utils.exception import EmailApproveLinkNotFoundException, LoginException, RegistrationException
from core.utils.generate.person import Person
from data.config import ACCOUNTS_FILE_PATH, PROXIES_FILE_PATH, REGISTER_ACCOUNT_ONLY, THREADS, REGISTER_DELAY, \
    CLAIM_REWARDS_ONLY, APPROVE_EMAIL, APPROVE_WALLET_ON_EMAIL, MINING_MODE, CONNECT_WALLET, \
    WALLETS_FILE_PATH, SEND_WALLET_APPROVE_LINK_TO_EMAIL, SINGLE_IMAP_ACCOUNT, SEMI_AUTOMATIC_APPROVE_LINK, \
    PROXY_DB_PATH


def bot_info(name: str = ""):
    cprint(text2art(name), 'green')

    if sys.platform == 'win32':
        ctypes.windll.kernel32.SetConsoleTitleW(f"{name}")


async def claim_rewards_mode():
    """Режим для выполнения `CLAIM_REWARDS_ONLY`."""
    accounts = file_to_list(ACCOUNTS_FILE_PATH)

    if not accounts:
        logger.warning("No accounts found!")
        return

    for account in accounts:
        try:
            # Разделяем строку на email и пароль
            consumables = account.strip().split(":")
            if len(consumables) != 2:
                logger.error(f"Неправильный формат учетной записи: {account}")
                continue

            email, password = consumables

            # Проверка наличия email и пароля
            if not email or not password:
                logger.error(f"Отсутствуют email или пароль: {account}")
                continue

            # Создаем объект Grass
            grass = Grass(0, email, password, None, None)

            logger.info(f"Claiming rewards for {email}")
            await grass.claim_rewards()
            await grass.session.close()
            await grass.ws_session.close()

        except Exception as e:
            logger.error(f"Error during claim_rewards for {account}: {e} {traceback.format_exc()}")


async def worker_task(_id, account: str, proxy: str = None, wallet: str = None, db: AccountsDB = None):
    consumables = account.split(":")[:3]
    imap_pass = None

    if SINGLE_IMAP_ACCOUNT:
        consumables.append(SINGLE_IMAP_ACCOUNT.split(":")[1])

    if len(consumables) == 1:
        email = consumables[0]
        password = Person().random_string(8)
    elif len(consumables) == 2:
        email, password = consumables
    else:
        email, password, imap_pass = consumables

    grass = None

    try:
        grass = Grass(_id, email, password, proxy, db)

        if MINING_MODE:
            await asyncio.sleep(random.uniform(1, 2) * _id)
            logger.info(f"Starting №{_id} | {email} | {password} | {proxy}")
        else:
            await asyncio.sleep(random.uniform(*REGISTER_DELAY))
            logger.info(f"Starting №{_id} | {email} | {password} | {proxy}")

        if REGISTER_ACCOUNT_ONLY:
            await grass.create_account()
        elif APPROVE_EMAIL or CONNECT_WALLET or SEND_WALLET_APPROVE_LINK_TO_EMAIL or APPROVE_WALLET_ON_EMAIL:
            await grass.enter_account()
            user_info = await grass.retrieve_user()

            if APPROVE_EMAIL:
                if user_info['result']['data'].get("isVerified"):
                    logger.info(f"{grass.id} | {grass.email} email already verified!")
                else:
                    if SEMI_AUTOMATIC_APPROVE_LINK:
                        imap_pass = "placeholder"
                    elif imap_pass is None:
                        raise TypeError("IMAP password is not provided")
                    await grass.confirm_email(imap_pass)
            if CONNECT_WALLET:
                if user_info['result']['data'].get("walletAddress"):
                    logger.info(f"{grass.id} | {grass.email} wallet already linked!")
                else:
                    await grass.link_wallet(wallet)

            if user_info['result']['data'].get("isWalletAddressVerified"):
                logger.info(f"{grass.id} | {grass.email} wallet already verified!")
            else:
                if SEND_WALLET_APPROVE_LINK_TO_EMAIL:
                    await grass.send_approve_link(endpoint="sendWalletAddressEmailVerification")
                if APPROVE_WALLET_ON_EMAIL:
                    if SEMI_AUTOMATIC_APPROVE_LINK:
                        imap_pass = "placeholder"
                    elif imap_pass is None:
                        raise TypeError("IMAP password is not provided")
                    await grass.confirm_wallet_by_email(imap_pass)
        else:
            await grass.start()

        return True
    except (LoginException, RegistrationException) as e:
        logger.warning(f"{_id} | {e}")
    except MailboxLoginError as e:
        logger.error(f"{_id} | {e}")
    except EmailApproveLinkNotFoundException as e:
        logger.warning(e)
    except Exception as e:
        logger.error(f"{_id} | not handled exception | error: {e} {traceback.format_exc()}")
    finally:
        if grass:
            await grass.session.close()
            await grass.ws_session.close()


async def main(args):
    if args.claim_rewards:
        logger.info("Starting CLAIM_REWARDS_ONLY mode...")
        await claim_rewards_mode()
        return

    accounts = file_to_list(ACCOUNTS_FILE_PATH)
    if not accounts:
        logger.warning("No accounts found!")
        return

    autoreger = AutoReger.get_accounts(
        (ACCOUNTS_FILE_PATH, PROXIES_FILE_PATH, WALLETS_FILE_PATH),
        with_id=True,
        static_extra=(None,)
    )

    threads = THREADS
    msg = "__MINING__ MODE"
    logger.info(msg)
    await autoreger.start(worker_task, threads)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grass Auto")
    parser.add_argument("--claim-rewards", action="store_true", help="Run in CLAIM_REWARDS_ONLY mode")
    args = parser.parse_args()

    bot_info("GRASS_AUTO")

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main(args))
    else:
        asyncio.run(main(args))
