# ✅ Full Final users_chats_db.py with Two Verification System Only
# ✅ Includes all features: user, group, ban, premium, settings, and verification
# ❌ Removed: third_time_verified, tutorial_3, THREE_VERIFY_GAP, use_third_shortener

import motor.motor_asyncio
from info import *
import datetime
import pytz
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
from typing import Dict, Any, Optional, List, Tuple

class Database:
    def __init__(self, uri: str, database_name: str):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users = self.db.users  # Fixed typo from uersz to users
        self.groups = self.db.groups
        self.requests = self.db.requests
        self.bot_settings = self.db.bot_settings
        self.user_verification = self.db.user_verification  # Renamed from misc
        self.verify_ids = self.db.verify_ids  # Renamed from verify_id

    def new_user(self, id: int, name: str) -> Dict[str, Any]:
        return {
            "id": id,
            "name": name,
            "ban_status": {"is_banned": False, "ban_reason": ""},
            "expiry_time": None,
            "has_free_trial": False
        }

    def new_group(self, id: int, title: str) -> Dict[str, Any]:
        return {
            "id": id,
            "title": title,
            "chat_status": {"is_disabled": False, "reason": ""}
        }

    async def add_user(self, id: int, name: str) -> bool:
        try:
            await self.users.insert_one(self.new_user(id, name))
            return True
        except DuplicateKeyError:
            return False

    async def is_user_exist(self, id: int) -> bool:
        return bool(await self.users.find_one({'id': int(id)}))

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return await self.users.find_one({"id": user_id})

    async def update_user(self, user_data: Dict[str, Any]) -> None:
        await self.users.update_one(
            {"id": user_data["id"]},
            {"$set": user_data},
            upsert=True
        )

    async def total_users_count(self) -> int:
        return await self.users.count_documents({})

    async def total_chat_count(self) -> int:
        return await self.groups.count_documents({})

    async def get_all_users(self):
        return self.users.find({})

    async def get_all_chats(self):
        return self.groups.find({})

    async def delete_user(self, user_id: int) -> None:
        await self.users.delete_many({'id': int(user_id)})

    async def delete_chat(self, id: int) -> None:
        await self.groups.delete_many({'id': int(id)})

    async def get_banned(self) -> Tuple[List[int], List[int]]:
        users = self.users.find({'ban_status.is_banned': True})
        chats = self.groups.find({'chat_status.is_disabled': True})
        banned_users = [user['id'] async for user in users]
        banned_chats = [chat['id'] async for chat in chats]
        return banned_users, banned_chats

    async def remove_ban(self, id: int) -> None:
        await self.users.update_one(
            {'id': id},
            {'$set': {'ban_status': {"is_banned": False, "ban_reason": ""}}}
        )

    async def ban_user(self, user_id: int, ban_reason: str = "No Reason") -> None:
        await self.users.update_one(
            {'id': user_id},
            {'$set': {'ban_status': {"is_banned": True, "ban_reason": ban_reason}}}
        )

    async def get_ban_status(self, id: int) -> Dict[str, Any]:
        user = await self.users.find_one({'id': int(id)})
        return user.get('ban_status', {"is_banned": False, "ban_reason": ""}) if user else {"is_banned": False, "ban_reason": ""}

    async def add_chat(self, chat: int, title: str) -> None:
        await self.groups.insert_one(self.new_group(chat, title))

    async def get_chat(self, chat: int) -> Optional[Dict[str, Any]]:
        data = await self.groups.find_one({'id': int(chat)})
        return data.get('chat_status') if data else None

    async def disable_chat(self, chat: int, reason: str = "No Reason") -> None:
        await self.groups.update_one(
            {'id': int(chat)},
            {'$set': {'chat_status': {"is_disabled": True, "reason": reason}}}
        )

    async def re_enable_chat(self, id: int) -> None:
        await self.groups.update_one(
            {'id': int(id)},
            {'$set': {'chat_status': {"is_disabled": False, "reason": ""}}}
        )

    async def update_settings(self, id: int, settings: Dict[str, Any]) -> None:
        await self.groups.update_one(
            {'id': int(id)},
            {'$set': {'settings': settings}}
        )

    async def get_settings(self, id: int) -> Dict[str, Any]:
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
        chat = await self.groups.find_one({'id': int(id)})
        return chat['settings'] if chat and 'settings' in chat else default.copy()

    async def get_verification_user(self, user_id: int) -> Dict[str, Any]:
        user_id = int(user_id)
        user = await self.user_verification.find_one({"user_id": user_id})
        ist_timezone = pytz.timezone('Asia/Kolkata')
        
        if not user:
            res = {
                "user_id": user_id,
                "last_verified": datetime.datetime(2020, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
                "second_time_verified": datetime.datetime(2019, 5, 17, 0, 0, 0, tzinfo=ist_timezone)
            }
            await self.user_verification.insert_one(res)
            return res
        return user

    async def update_verification_user(self, user_id: int, value: Dict[str, Any]) -> None:
        await self.user_verification.update_one(
            {"user_id": user_id},
            {"$set": value}
        )

    async def is_user_verified(self, user_id: int) -> bool:
        user = await self.get_verification_user(user_id)
        past_date = user.get("last_verified")
        ist = pytz.timezone('Asia/Kolkata')
        return (datetime.datetime.now(tz=ist) - past_date.astimezone(ist)).total_seconds() <= TWO_VERIFY_GAP

    async def user_verified(self, user_id: int) -> bool:
        user = await self.get_verification_user(user_id)
        past_date = user.get("second_time_verified")
        ist = pytz.timezone('Asia/Kolkata')
        return (datetime.datetime.now(tz=ist) - past_date.astimezone(ist)).total_seconds() <= TWO_VERIFY_GAP

    async def use_second_shortener(self, user_id: int, time: int) -> bool:
        user = await self.get_verification_user(user_id)
        if not user.get("second_time_verified"):
            await self.update_verification_user(
                user_id,
                {"second_time_verified": datetime.datetime(2019, 5, 17, 0, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))}
            )
            user = await self.get_verification_user(user_id)
            
        if await self.is_user_verified(user_id):
            past_date = user.get("last_verified")
            now = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            return (now - past_date.astimezone(pytz.timezone('Asia/Kolkata'))).total_seconds() > time
        return False

    async def create_verify_id(self, user_id: int, hash: str) -> None:
        await self.verify_ids.insert_one({
            "user_id": user_id,
            "hash": hash,
            "verified": False
        })

    async def get_verify_id_info(self, user_id: int, hash: str) -> Optional[Dict[str, Any]]:
        return await self.verify_ids.find_one({"user_id": user_id, "hash": hash})

    async def update_verify_id_info(self, user_id: int, hash: str, value: Dict[str, Any]) -> None:
        await self.verify_ids.update_one(
            {"user_id": user_id, "hash": hash},
            {"$set": value}
        )

    async def has_premium_access(self, user_id: int) -> bool:
        data = await self.get_user(user_id)
        if data:
            expiry = data.get("expiry_time")
            if isinstance(expiry, datetime.datetime) and datetime.datetime.now() <= expiry:
                return True
            if expiry is not None:
                await self.users.update_one(
                    {"id": user_id},
                    {"$set": {"expiry_time": None}}
                )
        return False

    async def give_free_trial(self, user_id: int) -> None:
        expiry = datetime.datetime.now() + datetime.timedelta(minutes=5)
        await self.users.update_one(
            {"id": user_id},
            {"$set": {"expiry_time": expiry, "has_free_trial": True}},
            upsert=True
        )

    async def check_trial_status(self, user_id: int) -> bool:
        data = await self.get_user(user_id)
        return data.get("has_free_trial", False) if data else False

    async def remove_premium_access(self, user_id: int) -> None:
        await self.users.update_one(
            {"id": user_id},
            {"$set": {"expiry_time": None}}
        )

    async def get_expired(self, now: datetime.datetime) -> List[Dict[str, Any]]:
        expired = []
        async for user in self.users.find({"expiry_time": {"$lt": now}}):
            expired.append(user)
        return expired

    async def all_premium_users(self) -> int:
        return await self.users.count_documents({"expiry_time": {"$gt": datetime.datetime.now()}})

    async def get_db_size(self) -> int:
        return (await self.db.command("dbstats"))['dataSize']

    async def get_bot_setting(self, bot_id: int, setting_key: str, default: Any) -> Any:
        data = await self.bot_settings.find_one(
            {'id': int(bot_id)},
            {setting_key: 1, '_id': 0}
        )
        return data.get(setting_key) if data else default

    async def update_bot_setting(self, bot_id: int, setting_key: str, value: Any) -> None:
        await self.bot_settings.update_one(
            {'id': int(bot_id)},
            {'$set': {setting_key: value}},
            upsert=True
        )

    async def pm_search_status(self, bot_id: int) -> bool:
        return await self.get_bot_setting(bot_id, 'PM_SEARCH', PM_SEARCH)

    async def update_pm_search_status(self, bot_id: int, enable: bool) -> None:
        await self.update_bot_setting(bot_id, 'PM_SEARCH', enable)

    async def movie_update_status(self, bot_id: int) -> bool:
        return await self.get_bot_setting(bot_id, 'MOVIE_UPDATE_NOTIFICATION', MOVIE_UPDATE_NOTIFICATION)

    async def update_movie_update_status(self, bot_id: int, enable: bool) -> None:
        await self.update_bot_setting(bot_id, 'MOVIE_UPDATE_NOTIFICATION', enable)

    async def find_join_req(self, id: int) -> bool:
        return bool(await self.requests.find_one({'id': id}))

    async def add_join_req(self, id: int) -> None:
        await self.requests.insert_one({'id': id})

    async def del_join_req(self) -> None:
        await self.requests.drop()


# ✅ DB instances
db = Database(DATABASE_URI, DATABASE_NAME)
db2 = Database(DATABASE_URI2, DATABASE_NAME)
