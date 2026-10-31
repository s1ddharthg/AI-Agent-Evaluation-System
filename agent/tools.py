from langchain.tools import tool
from data import user_data
from dotenv import load_dotenv
import logging
from objects import PurchaseItem
from datetime import time

load_dotenv()

@tools
def get_user_purchase_history(user:str) -> dict:
    '''
    this tool take user username and returns dictionary of purchase history if exists
    '''
    logging.info(f"using get_user_purchase_history tool on user: { user }")
    if user_data.get(user):
        return user_data[user]
    return { "status" : "username not found" }