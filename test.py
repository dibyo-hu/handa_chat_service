import asyncio
import aiohttp
import json

user_context = {
    "Vikas": {
        "acc1_latest_balance": 29728.6,
        "acc2_latest_balance": 318866,
        "acco_latest_balance": 162667,
        "age": 45,
        "amt_credit_txn_m0": 84992.6,
        "amt_credit_txn_m1": 1026386,
        "amt_credit_txn_m2": 586631,
        "amt_credit_txn_m3": 704890,
        "amt_debit_txn_m0": 913722,
        "amt_debit_txn_m1": 462670,
        "amt_debit_txn_m2": 1411763,
        "amt_debit_txn_m3": 951275,
        "auto_debit_bounce_m0": False,
        "auto_debit_bounce_m1": False,
        "auto_debit_bounce_m2": False,
        "auto_debit_bounce_m3": False,
        "bounce_flag": 0,
        "brand": "OnePlus",
        "cc_utilisation": 0.28,
        "cheque_bounce_c30": False,
        "cheque_bounce_m0": False,
        "cheque_bounce_m1": False,
        "cheque_bounce_m2": False,
        "cheque_bounce_m3": False,
        "cnt_apps_sub_genre_lending_c30": 0,
        "cnt_apps_sub_genre_lending_c60": 0,
        "cnt_apps_sub_genre_lending_c90": 0,
        "cnt_apps_sub_genre_lending_v2": 1,
        "cnt_apps_sub_segment_betting_games_c30": 0,
        "cnt_bounce_senders_c90": 0,
        "cnt_delinquency_broadband": None,
        "cnt_delinquncy_bnpl_c15": 0,
        "cnt_delinquncy_bnpl_c30": 0,
        "cnt_delinquncy_bnpl_c90": 0,
        "cnt_delinquncy_cc_c15": 0,
        "cnt_delinquncy_cc_c30": 0,
        "cnt_delinquncy_cc_c60": 0,
        "cnt_delinquncy_cc_c90": 0,
        "cnt_loan_accounts": None,
        "cnt_savings_accounts": 12,
        "credit_card_user_flag": True,
        "debit_card_user_flag": True,
        "ecs_bounce_m0": False,
        "ecs_bounce_m1": False,
        "ecs_bounce_m2": False,
        "ecs_bounce_m3": False,
        "fis_affordability_v1": 71200.7,
        "insurance_flag": True,
        "investor_flag": True,
        "mf_trx_recency": 28,
        "mobile_model": "CPH2585",
        "net_banking_flag": True,
        "obligations": 0,
        "postpaid_flag": True,
        "si_bounce_m0": False,
        "si_bounce_m1": False,
        "si_bounce_m2": False,
        "si_bounce_m3": False,
        "upi_user_flag": False,
        "wallet_user_flag": False
    }
}

async def test_stream():
    async with aiohttp.ClientSession() as session:
        data = {
            "message": "How would you categorize my financial behavior?",
            "rag_docs": json.dumps(["Recent reports indicate moderate financial activity."]),
            "user_id": "Vikas"
        }
        async with session.post("http://127.0.0.1:8000/chat/stream", data=data) as resp:
            async for line in resp.content:
                print(line.decode().strip())

asyncio.run(test_stream())
