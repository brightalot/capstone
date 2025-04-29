# utils/response_generator.py

import os

def generate_single_listcard(stock_list, total_assets, total_profit_amt, total_profit_rate):
    items = []
    for name, qty, eval_amt, profit_amt, profit_rate in stock_list:
        sign = "+" if profit_amt >= 0 else "-"
        items.append({
            "title": name,
            "description": (
                f"{qty:,}주\n  |  "
                f"평가금액: {eval_amt:,}원({sign}{abs(profit_rate):.2f}%)"
                # f"손익: {sign}{abs(profit_amt):,}원 ({sign}{abs(profit_rate):.2f}%)"
            ),
            "action": "message",
            "messageText": name
        })

    # 총 요약
    total_sign = "+" if total_profit_amt >= 0 else "-"
    total_summary = (
        f"📊 전체 자산\n"
        f"총 평가금액: {total_assets:,}원\n"
        f"총 손익: {total_sign}{abs(total_profit_amt):,}원 "
        f"({total_sign}{abs(total_profit_rate):.2f}%)"
    )

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "listCard": {
                        "header": {
                            "title": f"📈 보유 종목"
                        },
                        "items": items,
                        "buttons": [
                            {
                                "label": "처음으로",
                                "action": "block",
                                "blockId": os.getenv("HOME_BLOCK_ID")
                            },
                            {
                                "label": "매수/매도",
                                "action": "block",
                                "blockId": os.getenv("MOCK_ORDER_ID")
                            }
                        ]
                    }
                },
                {
                    "simpleText": {
                        "text": total_summary
                    }
                }
            ]
        }
    }

def generate_carousel(stock_list, total_assets):
    list_cards = []
    for idx in range(0, len(stock_list), 5):
        chunk = stock_list[idx:idx + 5]
        items = []
        for name, qty in chunk:
            items.append({
                "title": name,
                "description": f"{qty:,}주 보유"
            })
        
        list_cards.append({
            "header": {
                "title": f"📈 보유 종목 (Page {idx//5 + 1})"
            },
            "items": items,
            "buttons": [
                {
                    "label": "처음으로",
                    "action": "block",
                    "blockId": os.getenv("HOME_BLOCK_ID")
                }
            ]
        })

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "carousel": {
                        "type": "listCard",
                        "items": list_cards
                    }
                }
            ]
        }
    }

def generate_stock_response(stock_list, total_assets, total_profit_amt, total_profit_rate):
    if len(stock_list) <= 5:
        return generate_single_listcard(stock_list, total_assets, total_profit_amt, total_profit_rate)
    else:
        return generate_carousel(stock_list, total_assets)