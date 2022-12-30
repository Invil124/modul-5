import platform
from datetime import datetime, timedelta
import aiohttp
import asyncio



class CurrencyList:
    available_currency = []
    current_currency = ["EUR", "USD"]

    def add_currency(self, currency):

        if currency not in self.available_currency:
            return "Unavailable currency"
        if currency in self.current_currency:
            return "Currency already in list"

        self.current_currency.append(currency)
        return "Currency successful append"

class PBUrlMaker:
    base_url = "https://api.privatbank.ua/p24api/exchange_rates?json&date="
    current_date = datetime.now()

    def create_urls(self,days: int = 1):
        list_url = []
        date_str = self.current_date.strftime("%d.%m.%Y")
        list_url.append(f"{self.base_url}{date_str}") # додає сьогоднішній день!

        if days > 10:
            return "Not more than 10 days!"

        elif days > 1:
            for i in range(1,days):
                day = timedelta(days=i)
                new_date = self.current_date - day
                date_str = new_date.strftime("%d.%m.%Y")
                list_url.append(f"{self.base_url}{date_str}")

        return list_url




async def create_task(urls):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(make_requset(url,session))
            tasks.append(task)

        if isinstance(tasks[0],str):
            print(tasks[0])
            return tasks[0]

        result = await asyncio.gather(*tasks, return_exceptions=True)

    return result




async def make_requset(url,session):
    try:
        async with session.get(url) as response:

            if response.status == 200:
                result = await response.json()

                return result
            else:
                return "Bad connection"
    except aiohttp.ClientConnectorError as err:
        return f"Connection error:{err}"


async def make_async_request(days: int):
    urls = PBUrlMaker().create_urls(days)
    result = await create_task(urls)

    return result

def days_checker(days: str):

    if not days[0].isdigit():
        return False
    days = int(days[0])
    if days == 0:
        days = 1
    if days > 10:
        return False
    return days

def work_with_currency_list(list_currency):
    currency_list = CurrencyList()
    list_with_needed_currency = []

    for dict in list_currency:
        date = dict["date"]
        new_dict = {}
        sale_purchase = {}
        currency = {}
        for exchange_rate in dict["exchangeRate"]:
            if exchange_rate["currency"] in currency_list.current_currency:
                sale_purchase["sale"] = exchange_rate["saleRate"]
                sale_purchase["purchase"] = exchange_rate["purchaseRate"]
                currency[exchange_rate["currency"]] = sale_purchase
                new_dict[date] = currency
        list_with_needed_currency.append(new_dict)
    return list_with_needed_currency


def exchange_rate_func(*args):
    days = days_checker(args[0])
    if not days:
        return "Invalid input"
    list_currency = asyncio.run(make_async_request(days))

    if not isinstance(list_currency[0],dict):
        return list_currency[0]

    result = work_with_currency_list(list_currency)
    return result


if __name__ == "__main__":

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    user_input = input("Enter the numbers of days for request: ")
    answer = exchange_rate_func(user_input)

    print(answer)



