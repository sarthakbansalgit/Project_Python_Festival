"""Step 03, on the side: one function per job, and commands from the terminal.

uv run python B2/side/e03_shopping.py              the whole list
uv run python B2/side/e03_shopping.py total        the price of everything
uv run python B2/side/e03_shopping.py aisle fruit  what to take in one aisle
"""

import sys

ITEMS = [
    {"name": "apples", "aisle": "fruit", "price": 2.40},
    {"name": "bread", "aisle": "bakery", "price": 1.10},
    {"name": "pears", "aisle": "fruit", "price": 3.05},
]


                                                                         
                                                                   
def total_price(items: list[dict]) -> float:
    total = 0.0
    for item in items:
        total += item["price"]
    return total


def items_in_aisle(items: list[dict], aisle: str) -> list[dict]:
    result = []
    for item in items:
        if item["aisle"] == aisle:
            result.append(item)
    return result


                                                                           
def show(items: list[dict]) -> None:
    for item in items:
        print(f"{item['name']:<8} {item['price']:>5.2f} EUR")


def main() -> None:
                                                                             
    arguments = sys.argv[1:]
    if len(arguments) == 0:
        show(ITEMS)
    elif arguments == ["total"]:
        print(f"{total_price(ITEMS):.2f} EUR")
    elif arguments[0] == "aisle" and len(arguments) == 2:
        show(items_in_aisle(ITEMS, arguments[1]))
    else:
        print(__doc__)


main()
