import os
import re
import math
import ast
import operator as op
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN env ထည့်ပါ")

USDT_RATE = 83.5
PROFIT = 2.0
ROUND_VALUE = 50

ANTI_SPAM = True
ANTI_LINK = True

OPEN_MSG = "🌅 ပြန်ဖွင့်ပါပြီ\nOwner အားပါပြီ။ လိုတာများအကုန် အစုံ ရပါမယ်ရှင့် 🤗"
CLOSE_MSG = "🌙 Owner အလုပ်ရှုပ်နေလို့ ခဏပိတ်ထားပါတယ်ရှင့်။"

WELCOME_MSG = """👋 ကြိုဆိုပါတယ်ရှင့်

💎 Diamond / Bundle / Pass များ မေးမြန်းနိုင်ပါတယ်ရှင့်
✅ Bot Ready ပါပြီ"""

LEFT_MSG = "👋 Goodbye ပါရှင့်"

BAD_WORDS = ["spam", "scam", "xxx", "fuck", "http://", "https://", "t.me/", "www."]

PACKS = {
    "86wp": 137.50, "86wp2": 213.50, "172wp": 198.00, "257wp": 253.50,
    "wp": 76.00, "86": 61.50, "110": 76.00, "172": 122.00,
    "257": 177.50, "343": 239.00, "344": 244.00, "429": 299.50,
    "514": 355.00, "600": 416.50, "706": 480.00, "792": 541.50,
    "878": 602.00, "963": 657.50, "1049": 719.00, "1135": 779.50,
    "1220": 835.00, "1412": 960.00, "1584": 1082.00, "1755": 1199.00,
    "2195": 1453.00, "2901": 1940.00, "3688": 2424.00,
    "4390": 2906.00, "5532": 3660.00, "9288": 6079.00,
    "11483": 7532.00,
    "50+50": 39.00, "150+150": 116.90, "250+250": 187.50, "500+500": 385.00,
    "twillight pass": 402.50, "twilight pass": 402.50,
    "web": 39.00, "meb": 196.50,
}

KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📋 Pack List", "💎 Price List"],
        ["🌅 ဆိုင်ဖွင့်", "🌙 ဆိုင်ပိတ်"],
        ["🧮 Calculator Help", "ℹ️ Help"],
    ],
    resize_keyboard=True
)

def round_50(amount: float) -> int:
    return int(math.ceil(amount / ROUND_VALUE) * ROUND_VALUE)

def diamond_mmk(usdt: float) -> int:
    return round_50(usdt * USDT_RATE * (1 + PROFIT / 100))

# safe normal calculator
OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: op.neg
}

def safe_calc(expr: str):
    def eval_node(node):
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp):
            return OPS[type(node.op)](eval_node(node.left), eval_node(node.right))
        if isinstance(node, ast.UnaryOp):
            return OPS[type(node.op)](eval_node(node.operand))
        raise ValueError("bad expression")
    return eval_node(ast.parse(expr, mode="eval").body)

def pack_list_text():
    return """╔════〔 𝗣𝗨𝗕𝗟𝗜𝗖 𝗣𝗔𝗖𝗞 𝗟𝗜𝗦𝗧 〕════╗

🌟 Normal Pack
• 86wp - 137.50 USDT
• 86wp2 - 213.50 USDT
• 172wp - 198.00 USDT
• 257wp - 253.50 USDT
• wp - 76.00 USDT
• 86 - 61.50 USDT
• 110 - 76.00 USDT
• 172 - 122.00 USDT
• 257 - 177.50 USDT
• 343 - 239.00 USDT
• 344 - 244.00 USDT
• 429 - 299.50 USDT
• 514 - 355.00 USDT
• 600 - 416.50 USDT
• 706 - 480.00 USDT
• 792 - 541.50 USDT
• 878 - 602.00 USDT
• 963 - 657.50 USDT
• 1049 - 719.00 USDT
• 1135 - 779.50 USDT
• 1220 - 835.00 USDT
• 1412 - 960.00 USDT
• 1584 - 1082.00 USDT
• 1755 - 1199.00 USDT
• 2195 - 1453.00 USDT
• 2901 - 1940.00 USDT
• 3688 - 2424.00 USDT
• 4390 - 2906.00 USDT
• 5532 - 3660.00 USDT
• 9288 - 6079.00 USDT
• 11483 - 7532.00 USDT

🔥 Double Pack
• 50+50 - 39.00 USDT
• 150+150 - 116.90 USDT
• 250+250 - 187.50 USDT
• 500+500 - 385.00 USDT

🎟 Pass / Bundle
• Twillight Pass - 402.50 USDT
• web - 39.00 USDT
• meb - 196.50 USDT

╚════════════════════╝"""

def price_list_text():
    lines = [
        "╔══〔 𝗗𝗜𝗔𝗠𝗢𝗡𝗗 𝗣𝗥𝗜𝗖𝗘 𝗟𝗜𝗦𝗧 〕══╗",
        f"💱 Rate: {USDT_RATE}",
        f"📈 Profit: {PROFIT}%",
        f"🔁 Round: {ROUND_VALUE}",
        ""
    ]

    shown = set()
    for name, usdt in PACKS.items():
        if name == "twilight pass" or name in shown:
            continue
        shown.add(name)
        display = "Twillight Pass" if name == "twillight pass" else name
        lines.append(f"💎 {display} ➜ {diamond_mmk(usdt):,} MMK")

    lines.append("╚════════════════════╝")
    return "\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Public Bot Ready ပါပြီရှင့်", reply_markup=KEYBOARD)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """📌 အသုံးပြုပုံ

📋 Pack List - USDT pack list
💎 Price List - MMK price list

ဆိုင်ဖွင့်/ပိတ်:
O
C

Normal calculator:
/calc 2+3*5

Diamond calculator:
86
172
500+500
web
meb

Rate ပြောင်းရန်:
83.5+2%

Anti spam:
/antispam on
/antispam off
/antilink on
/antilink off
""",
        reply_markup=KEYBOARD
    )

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        username = f"@{user.username}" if user.username else "No username"
        await update.message.reply_text(
            f"{WELCOME_MSG}\n\n👤 Name: {user.first_name}\n🆔 ID: {user.id}\n🔗 Username: {username}"
        )

async def left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.left_chat_member
    await update.message.reply_text(f"{LEFT_MSG}\n👤 Name: {user.first_name}")

async def pack_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(pack_list_text())

async def price_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(price_list_text())

async def open_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(OPEN_MSG)

async def close_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(CLOSE_MSG)

async def calc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /calc 2+3*5")
    expr = " ".join(context.args)
    try:
        result = safe_calc(expr)
        await update.message.reply_text(f"🧮 {expr} = {result}")
    except Exception:
        await update.message.reply_text("❌ Calculator error") 

async def antispam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ANTI_SPAM
    if not context.args or context.args[0].lower() not in ["on", "off"]:
        return await update.message.reply_text("Usage: /antispam on OR /antispam off")
    ANTI_SPAM = context.args[0].lower() == "on"
    await update.message.reply_text(f"🛡 Anti Spam: {'ON' if ANTI_SPAM else 'OFF'}")

async def antilink_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ANTI_LINK
    if not context.args or context.args[0].lower() not in ["on", "off"]:
        return await update.message.reply_text("Usage: /antilink on OR /antilink off")
    ANTI_LINK = context.args[0].lower() == "on"
    await update.message.reply_text(f"🔗 Anti Link: {'ON' if ANTI_LINK else 'OFF'}")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global USDT_RATE, PROFIT

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    lower = text.lower()

    if lower == "c":
        return await update.message.reply_text(CLOSE_MSG)

    if lower == "o":
        return await update.message.reply_text(OPEN_MSG)

    if text == "📋 Pack List":
        return await pack_list(update, context)

    if text == "💎 Price List":
        return await price_list(update, context)

    if text == "🌅 ဆိုင်ဖွင့်":
        return await open_shop(update, context)

    if text == "🌙 ဆိုင်ပိတ်":
        return await close_shop(update, context)

    if text == "ℹ️ Help":
        return await help_cmd(update, context)

    if text == "🧮 Calculator Help":
        return await update.message.reply_text("🧮 Normal calculator သုံးရန်\n/calc 2+3*5")

    if ANTI_SPAM:
        if ANTI_LINK and re.search(r"(https?://|t\.me/|telegram\.me/|www\.)", lower):
            try:
                await update.message.delete()
            except Exception:
                pass
            return

        if any(word in lower for word in BAD_WORDS):
            try:
                await update.message.delete()
            except Exception:
                pass
            return

    rate_match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)%", text)
    if rate_match:
        rate = float(rate_match.group(1))
        profit = float(rate_match.group(2))

        if not 65 <= rate <= 90:
            return await update.message.reply_text("❌ Rate ကို 65 ကနေ 90 ကြားပဲ ထည့်ပါ")
        if not 1 <= profit <= 10:
            return await update.message.reply_text("❌ Profit ကို 1% ကနေ 10% ကြားပဲ ထည့်ပါ")

        USDT_RATE = rate
        PROFIT = profit
        return await update.message.reply_text(price_list_text())

    if lower in PACKS:
        display = "Twillight Pass" if lower in ["twillight pass", "twilight pass"] else text
        usdt = PACKS[lower]
        return await update.message.reply_text(
            f"💎 {display}\n"
            f"USDT: {usdt:.2f}\n"
            f"Rate: {USDT_RATE}\n"
            f"Profit: {PROFIT}%\n"
            f"➡️ {diamond_mmk(usdt):,} MMK"
        )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("list", pack_list))
    app.add_handler(CommandHandler("price", price_list))
    app.add_handler(CommandHandler("open", open_shop))
    app.add_handler(CommandHandler("close", close_shop))
    app.add_handler(CommandHandler("calc", calc_cmd))
    app.add_handler(CommandHandler("antispam", antispam_cmd))
    app.add_handler(CommandHandler("antilink", antilink_cmd))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🔥 PUBLIC BOT RUNNING")
    app.run_polling()

if __name__ == "__main__":
    main()
