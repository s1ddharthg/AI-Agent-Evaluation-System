from langchain.tools import tool
from data import user_data
from dotenv import load_dotenv
import logging
from objects import PurchaseItem
from datetime import date

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

@tool
def get_user_purchase_history(user:str) -> dict:
    '''
    this tool take user username and returns dictionary of purchase history if exists
    '''
    logging.info(f"using get_user_purchase_history tool on user: { user }")
    if user_data.get(user):
        return user_data[user]
    return { "status" : "username not found" }

@tool
def calculate_refund_amount(user:str, items:list[PurchaseItem]) -> str:
    '''
    takes list of items to be returned and username and will return refund amount
    '''
    logging.info(f"using calculate_refund_amount tool on user: { user }")

    if user_data.get(user):
        total_refund = 0
        for item in items:
            if user_data[user].get(item.name):
                total_refund+=user_data[user][item.name]["price"]
        return f'value of refund is : {total_refund}'
    return { "status" : "username not found" }

@tool
def issue_refund_ticket(user: str, refundAmount: float) -> str:
    '''
    this tool will send a ticket to the right teams to return right refund
    '''
    logging.info(f"using issue_refund_ticket tool for user: { user }")

    return f'A refund ticket has been issued successfully for the amount : {refundAmount}'

@tool
def get_today_date(user: str) -> str:
    '''
    this tool will return today's date
    '''
    logging.info(f"using get_today_date tool for user: { user }")

    return date.today()