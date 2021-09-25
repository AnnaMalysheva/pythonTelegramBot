import unittest
import aiohttp
from unittest import IsolatedAsyncioTestCase

from database import database
from main3 import bot


class TestDatabase(IsolatedAsyncioTestCase):
    async def test_crud(self):
        await database.insert_analytics(1111, "2022-08-18")
        self.assertEqual(await database.select_analytics(1111), ("2022-08-18",))
        await database.delete_analytics(1111)
        self.assertEqual(await database.select_analytics(1111), None)


class TestBot(IsolatedAsyncioTestCase):
    async def test_bot_auth(self):
        bot._session = aiohttp.ClientSession()
        bot_info = await bot.get_me()
        await bot._session.close()

        self.assertEqual(bot_info["username"], "mws001_bot")


if __name__ == '__main__':
    unittest.main()
