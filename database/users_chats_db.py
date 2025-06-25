# ✅ Full Final users_chats_db.py with Two Verification System Only
# ✅ Includes all features: user, group, ban, premium, settings, and verification
# ❌ Removed: third_time_verified, tutorial_3, THREE_VERIFY_GAP, use_third_shortener

import motor.motor_asyncio
from info import *
import datetime
import pytz
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.users = self.db.uersz
        self.req = self.db.requests
        self.botcol = self.db.bot_settings
        self.misc = self.db.misc
        self.verify_id = self.db.verify_id

    def new_user(self, id, name):
        return dict(id=id, name=name, ban_status={"is_banned": False, "ban_reason": ""})

    def new_group(self, id, title):
        return dict(id=id, title=title, chat_status={"is_disabled": False, "reason": ""})

    async def add_user(self, id, name):
        await self.col.insert_one(self.new_user(id, name))

    async def is_user_exist(self, id):
        return bool(await self.col.find_one({'id': int(id)}))

    async def get_user(self, user_id):
        return await self.users.find_one({"id": user_id})

    async def update_user(self, user_data):
        await self.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)

    async def total_users_count(self):
        return await self.col.count_documents({})

    async def total_chat_count(self):
        return await self.grp.count_documents({})

    async def get_all_users(self):
        return self.col.find({})

    async def get_all_chats(self):
        return self.grp.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def delete_chat(self, id):
        await self.grp.delete_many({'id': int(id)})

    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        return [user['id'] async for user in users], [chat['id'] async for chat in chats]

    async def remove_ban(self, id):
        await self.col.update_one({'id': id}, {'$set': {'ban_status': {"is_banned": False, "ban_reason": ""}}})

    async def ban_user(self, user_id, ban_reason="No Reason"):
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': {"is_banned": True, "ban_reason": ban_reason}}})

    async def get_ban_status(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('ban_status', {"is_banned": False, "ban_reason": ""}) if user else {"is_banned": False, "ban_reason": ""}

    async def add_chat(self, chat, title):
        await self.grp.insert_one(self.new_group(chat, title))

    async def get_chat(self, chat):
        data = await self.grp.find_one({'id': int(chat)})
        return data.get('chat_status') if data else False

    async def disable_chat(self, chat, reason="No Reason"):
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': {"is_disabled": True, "reason": reason}}})

    async def re_enable_chat(self, id):
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': {"is_disabled": False, "reason": ""}}})

    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})

    async def get_settings(self, id):
        default = {
            'button': SINGLE_BUTTON,
            'botpm': P_TTI_SHOW_OFF,
            'file_secure': PROTECT_CONTENT,
            'imdb': IMDB,
            'spell_check': SPELL_CHECK_REPLY,
            'welcome': MELCOW_NEW_USERS,
            'auto_delete': AUTO_DELETE,
            'auto_ffilter': AUTO_FFILTER,
            'max_btn': MAX_BTN,
            'template': IMDB_TEMPLATE,
            'log': LOG_VR_CHANNEL,
            'tutorial': TUTORIAL,
            'tutorial_2': TUTORIAL_2,
            'shortner': SHORTENER_WEBSITE,
            'api': SHORTENER_API,
            'shortner_two': SHORTENER_WEBSITE2,
            'api_two': SHORTENER_API2,
            'is_verify': IS_VERIFY,
            'verify_time': TWO_VERIFY_GAP,
            'caption': CUSTOM_FILE_CAPTION,
            'fsub_id': AUTH_CHANNEL
        }
        chat = await self.grp.find_one({'id': int(id)})
        return chat['settings'] if chat and 'settings' in chat else default.copy()

    async def get_notcopy_user(self, user_id):
        user_id = int(user_id)
        user = await self.misc.find_one({"user_id": user_id})
        ist_timezone = pytz.timezone('Asia/Kolkata')
        if not user:
            res = {
                "user_id": user_id,
                "last_verified": datetime.datetime(2020, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
                "second_time_verified": datetime.datetime(2019, 5, 17, 0, 0, 0, tzinfo=ist_timezone)
            }
            await self.misc.insert_one(res)
            return res
        return user

    async def update_notcopy_user(self, user_id, value: dict):
        return await self.misc.update_one({"user_id": user_id}, {"$set": value})

    async def is_user_verified(self, user_id):
        user = await self.get_notcopy_user(user_id)
        pastDate = user.get("last_verified")
        ist = pytz.timezone('Asia/Kolkata')
        return (datetime.datetime.now(tz=ist) - pastDate.astimezone(ist)).total_seconds() <= TWO_VERIFY_GAP

    async def user_verified(self, user_id):
        user = await self.get_notcopy_user(user_id)
        pastDate = user.get("second_time_verified")
        ist = pytz.timezone('Asia/Kolkata')
        return (datetime.datetime.now(tz=ist) - pastDate.astimezone(ist)).total_seconds() <= TWO_VERIFY_GAP

    async def use_second_shortener(self, user_id, time):
        user = await self.get_notcopy_user(user_id)
        if not user.get("second_time_verified"):
            await self.update_notcopy_user(user_id, {"second_time_verified": datetime.datetime(2019, 5, 17, 0, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))})
            user = await self.get_notcopy_user(user_id)
        if await self.is_user_verified(user_id):
            pastDate = user.get("last_verified")
            now = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            return (now - pastDate.astimezone(pytz.timezone('Asia/Kolkata'))).total_seconds() > time
        return False

    async def create_verify_id(self, user_id: int, hash):
        return await self.verify_id.insert_one({"user_id": user_id, "hash": hash, "verified": False})

    async def get_verify_id_info(self, user_id: int, hash):
        return await self.verify_id.find_one({"user_id": user_id, "hash": hash})

    async def update_verify_id_info(self, user_id, hash, value: dict):
        return await self.verify_id.update_one({"user_id": user_id, "hash": hash}, {"$set": value})

    async def has_premium_access(self, user_id):
        data = await self.get_user(user_id)
        if data:
            expiry = data.get("expiry_time")
            if isinstance(expiry, datetime.datetime) and datetime.datetime.now() <= expiry:
                return True
            if expiry is not None:
                await self.users.update_one({"id": user_id}, {"$set": {"expiry_time": None}})
        return False

    async def give_free_trial(self, user_id):
        expiry = datetime.datetime.now() + datetime.timedelta(minutes=5)
        await self.users.update_one({"id": user_id}, {"$set": {"expiry_time": expiry, "has_free_trial": True}}, upsert=True)

    async def check_trial_status(self, user_id):
        data = await self.get_user(user_id)
        return data.get("has_free_trial", False) if data else False

    async def remove_premium_access(self, user_id):
        return await self.users.update_one({"id": user_id}, {"$set": {"expiry_time": None}})

    async def get_expired(self, now):
        expired = []
        async for user in self.users.find({"expiry_time": {"$lt": now}}):
            expired.append(user)
        return expired

    async def all_premium_users(self):
        return await self.users.count_documents({"expiry_time": {"$gt": datetime.datetime.now()}})

    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']

    async def get_bot_setting(self, bot_id, setting_key, default):
        data = await self.botcol.find_one({'id': int(bot_id)}, {setting_key: 1, '_id': 0})
        return data.get(setting_key) if data else default

    async def update_bot_setting(self, bot_id, setting_key, value):
        await self.botcol.update_one({'id': int(bot_id)}, {'$set': {setting_key: value}}, upsert=True)

    async def pm_search_status(self, bot_id):
        return await self.get_bot_setting(bot_id, 'PM_SEARCH', PM_SEARCH)

    async def update_pm_search_status(self, bot_id, enable):
        await self.update_bot_setting(bot_id, 'PM_SEARCH', enable)

    async def movie_update_status(self, bot_id):
        return await self.get_bot_setting(bot_id, 'MOVIE_UPDATE_NOTIFICATION', MOVIE_UPDATE_NOTIFICATION)

    async def update_movie_update_status(self, bot_id, enable):
        await self.update_bot_setting(bot_id, 'MOVIE_UPDATE_NOTIFICATION', enable)

    async def find_join_req(self, id):
        return bool(await self.req.find_one({'id': id}))

    async def add_join_req(self, id):
        await self.req.insert_one({'id': id})

    async def del_join_req(self):
        await self.req.drop()


# ✅ DB instances

db = Database(DATABASE_URI, DATABASE_NAME)
db2 = Database(DATABASE_URI2, DATABASE_NAME)
