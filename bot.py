import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    ChatJoinRequest,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message
)
from aiogram.filters import CommandStart

# =========================
# БОТ ТОКЕНІ
# =========================
BOT_TOKEN = "8189851832:AAF9BsZKOdWoenSKlDt_hEF5Tt45P87Cdgs"

# =========================
# НЕГІЗГІ КАНАЛ ID-І
# =========================
MAIN_CHANNEL_ID = -1004457777093

# =========================
# ДЕМЕУШІ КАНАЛДАР
# =========================
SPONSOR_CHANNELS = [
    {
        "id": -1004446766831,
        "title": "1-канал",
        "link": "https://t.me/+m8p6XXEGw49hMWQy"
    },
    {
        "id": -1004456390887,
        "title": "2-канал",
        "link": "https://t.me/+UjG5FknYE0UxOTNi"
    },
]

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# =========================
# ДЕМЕУШІ КАНАЛДАР БАТЫРМАСЫ
# =========================
def sponsor_keyboard():
    buttons = []

    for channel in SPONSOR_CHANNELS:
        buttons.append([
            InlineKeyboardButton(
                text=f"📢 {channel['title']} - Тіркелу",
                url=channel["link"]
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="✅ Тексеру",
            callback_data="check_subscription"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================
# /start КОМАНДАСЫ
# =========================
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "привет! 👋\n\n"
        "Негізгі каналға кіру үшін алдымен демеуші каналдарға жазылыңыз.\n\n"
        "Барлық каналға жазылғаннан кейін «✅ Тексеру» батырмасын басыңыз.",
        reply_markup=sponsor_keyboard()
    )


# =========================
# НЕГІЗГІ КАНАЛҒА ӨТІНІМ (JOIN REQUEST)
# =========================
@dp.chat_join_request(F.chat.id == MAIN_CHANNEL_ID)
async def join_request_handler(request: ChatJoinRequest):
    user_id = request.from_user.id

    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                "Сәлем! 👋\n\n"
                "Негізгі каналға кіру өтініміңіз қабылданды.\n\n"
                "Өтінімді толық растау үшін төмендегі демеуші каналдарға тіркеліп, "
                "«✅ Тексеру» батырмасын басыңыз:"
            ),
            reply_markup=sponsor_keyboard()
        )
    except Exception as e:
        print(f"Пайдаланушыға ЛС хабарлама жіберу қатесі ({user_id}):", e)


# =========================
# ЖАЗЫЛУДЫ ТЕКСЕРУ ФУНКЦИЯСЫ
# =========================
async def check_subscription(user_id: int):
    for channel in SPONSOR_CHANNELS:
        try:
            member = await bot.get_chat_member(
                chat_id=channel["id"],
                user_id=user_id
            )

            # Егер пайдаланушы шығып кетсе немесе банға түссе
            if member.status in ["left", "kicked"]:
                return False, channel

        except Exception as e:
            print(f"Тексеру қатесі ({channel['title']}):", e)
            return False, channel

    return True, None


# =========================
# ✅ ТЕКСЕРУ БАТЫРМАСЫН БАСҚАНДА
# =========================
@dp.callback_query(F.data == "check_subscription")
async def check_button(callback: CallbackQuery):
    user_id = callback.from_user.id

    await callback.answer("Тексеріп жатырмын...", show_alert=False)

    success, missing_channel = await check_subscription(user_id)

    if not success:
        await callback.message.answer(
            "❌ Барлық каналға тіркелмегенсіз!\n\n"
            f"Алдымен «{missing_channel['title']}» каналына тіркеліңіз.\n\n"
            "Тіркеліп болған соң қайтадан «✅ Тексеру» батырмасын басыңыз.",
            reply_markup=sponsor_keyboard()
        )
        return

    # Жазылым дұрыс болса — өтінімді қабылдаймыз
    try:
        await bot.approve_chat_join_request(
            chat_id=MAIN_CHANNEL_ID,
            user_id=user_id
        )

        await callback.message.answer(
            "✅ Барлығы дұрыс!\n\n"
            "Сіз барлық демеуші каналдарға тіркелдіңіз.\n"
            "Негізгі каналға кіру өтініміңіз қабылданды! 🎉"
        )

    except Exception as e:
        print("Өтінімді қабылдау қатесі:", e)
        await callback.message.answer(
            "⚠️ Өтінімді қабылдау кезінде қате шықты.\n"
            "Сілтемені қайта басып, өтінім жібергеніңізді тексеріңіз немесе қайта байқап көріңіз."
        )


# =========================
# БОТТЫ ІСКЕ ҚОСУ
# =========================
async def main():
    print("Бот іске қосылды...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())