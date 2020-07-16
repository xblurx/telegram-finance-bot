"""Telegram-bot itself"""
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, executor, types

import exceptions
import expenses
from categories import Categories
from middlewares import AccessMiddleware

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("TG_API_TOKEN")
ACCESS_ID = 285511498

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(AccessMiddleware(ACCESS_ID))


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Welcome a user and provide help message"""
    await message.answer(
        "Your very own accountant Nina Ivanovna👩\n\n"
        "Add expense: 250 такси\n"
        "Today's stats: /today\n"
        "Month's stats: /month\n"
        "Last 10 expenses: /expenses\n"
        "Expenses categories: /categories")


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    """Delete expense by its id"""
    row_id = int(message.text[4:])
    expenses.delete_expense(row_id)
    answer_message = "Done"
    await message.answer(answer_message)


@dp.message_handler(commands=['categories'])
async def categories_list(message: types.Message):
    """Send expense categories list"""
    categories = Categories().get_all_categories()
    answer_message = "Expense categories:\n\n* " + \
                     ("\n* ".join([c.name + ' (' + ", ".join(c.aliases) + ')' for c in categories]))
    await message.answer(answer_message)


@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    """Send today's expenses"""
    answer_message = expenses.get_today_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['month'])
async def month_statistics(message: types.Message):
    """Sends month's expenses"""
    answer_message = expenses.get_month_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['expenses'])
async def list_expenses(message: types.Message):
    """Send last 10 expenses or less"""
    last_expenses = expenses.last()
    if not last_expenses:
        await message.answer("No expenses just yet :)")
        return

    last_expenses_rows = [
        f"₽{expense.amount} on {expense.category_name} — press "
        f"/del{expense.id} to delete"
        for expense in last_expenses]
    answer_message = "Latest:\n\n* " + "\n\n* " \
        .join(last_expenses_rows)
    await message.answer(answer_message)


@dp.message_handler()
async def add_expense(message: types.Message):
    """Add a new expense"""
    try:
        expense = expenses.add_expense(message.text)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    answer_message = (
        f"Added ₽{expense.amount} on {expense.category_name}💸.\n\n"
        f"{expenses.get_today_statistics()}")
    await message.answer(answer_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
