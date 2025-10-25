import re
import io
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas

# Get Bot Token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==============================
# Regex for message pattern
# ==============================
pattern = re.compile(
    r"✅សូមបងពិនិត្យ.*?\n\n"
    r"👤 អតិថិជន: (.*?)\n"
    r"📞 លេខទូរស័ព្ទ: (.*?)\n"
    r"📍 ទីតាំង: (.*?)\n"
    r"🏠 អាសយដ្ឋាន: (.*?)\n"
    r".*?សរុបចុងក្រោយ: \$([0-9.,]+)\n"
    r" ?(🟥 .*?|🟩 .*?)\n\n"
    r"🚚 វិធីសាស្រ្តដឹកជញ្ជូន: (.*?)\n",
    re.S
)

# ==============================
# Message Handler
# ==============================
@dp.message()
async def check_messages(message: types.Message):
    # Only act on messages sent by this bot
    if not message.from_user or not message.from_user.is_bot:
        return

    text = message.text or ""
    match = pattern.search(text)
    if match:
        customerName, phone, location, address, total, payment, shipping = match.groups()

        # Create button
        kb = InlineKeyboardBuilder()
        kb.button(
            text="🖨 Print Label",
            callback_data=f"print|{customerName}|{phone}|{location}|{address}|{total}|{payment}|{shipping}"
        )

        try:
            await bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=kb.as_markup()
            )
        except Exception as e:
            print("Edit error:", e)

# ==============================
# Callback for printing
# ==============================
@dp.callback_query()
async def print_label(callback: types.CallbackQuery):
    if not callback.data.startswith("print|"):
        return

    _, name, phone, location, address, total, payment, shipping = callback.data.split("|")

    # Generate 78x50mm PDF label
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(78*mm, 50*mm))
    c.setFont("Helvetica", 10)

    c.drawString(5*mm, 45*mm, f"👤 អតិថិជន: {name}")
    c.drawString(5*mm, 40*mm, f"📞 លេខទូរស័ព្ទ: {phone}")
    c.drawString(5*mm, 35*mm, f"📍 ទីតាំង: {location}")

    if address.strip() != "(មិនបានបញ្ជាក់)":
        c.drawString(5*mm, 30*mm, f"🏠 អាសយដ្ឋាន: {address}")

    c.line(5*mm, 28*mm, 73*mm, 28*mm)
    c.drawString(5*mm, 23*mm, f"💰 សរុបចុងក្រោយ: ${total}")
    c.drawString(5*mm, 18*mm, f"{payment}")
    c.drawString(5*mm, 13*mm, f"🚚 ដឹកជញ្ជូន: {shipping}")

    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    await callback.message.answer_document(
        document=types.BufferedInputFile(pdf_buffer.read(), filename="label.pdf"),
        caption="📦 Label generated successfully!"
    )
    await callback.answer("✅ Label ready to print!")

# ==============================
# Start Bot
# ==============================
async def main():
    print("🚀 Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
