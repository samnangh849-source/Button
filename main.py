import re
import io
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart, Command
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
import asyncio
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Regex to detect your message format
pattern = re.compile(
    r"✅សូមបងពិនិត្យ.*?\n\n👤 \*អតិថិជន:\* (.*?)\n📞 \*លេខទូរស័ព្ទ:\* (.*?)\n📍 \*ទីតាំង:\* (.*?)\n🏠 \*អាសយដ្ឋាន:\* (.*?)\n.*?💰 \*សរុប:.*?\n.*?\*សរុបចុងក្រោយ: \$([0-9.,]+)\*.*?\n🚚 \*វិធីសាស្រ្តដឹកជញ្ជូន:\* (.*?)\n.*?(ប្រើប្រាស់|បង់ប្រាក់|មិនទាន់បង់|paid|unpaid)",
    re.S
)

@dp.message()
async def check_messages(message: types.Message):
    if not message.from_user or not message.from_user.is_bot:
        return
    
    match = pattern.search(message.text or "")
    if match:
        # Extract fields
        customerName, phone, location, address, total, shipping, payment = match.groups()
        
        # Add button
        kb = InlineKeyboardBuilder()
        kb.button(text="🖨 Print Label", callback_data=f"print|{customerName}|{phone}|{location}|{address}|{total}|{shipping}|{payment}")
        
        try:
            await bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=kb.as_markup()
            )
        except Exception as e:
            print("Edit error:", e)

@dp.callback_query()
async def print_label(callback: types.CallbackQuery):
    if callback.data.startswith("print|"):
        _, name, phone, location, address, total, shipping, payment = callback.data.split("|")
        
        # Generate PDF label
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=(78*mm, 50*mm))
        c.setFont("Helvetica", 10)
        c.drawString(5*mm, 45*mm, f"👤 {name}")
        c.drawString(5*mm, 40*mm, f"📞 {phone}")
        c.drawString(5*mm, 35*mm, f"📍 {location}")
        if address.strip():
            c.drawString(5*mm, 30*mm, f"🏠 {address}")
        c.drawString(5*mm, 25*mm, f"💰 ${total}")
        c.drawString(5*mm, 20*mm, f"🚚 {shipping}")
        c.drawString(5*mm, 15*mm, f"💳 {payment}")
        c.showPage()
        c.save()
        pdf_buffer.seek(0)
        
        await callback.message.answer_document(document=types.BufferedInputFile(pdf_buffer.read(), filename="label.pdf"))
        await callback.answer("✅ Label generated!")

async def main():
    print("Bot running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
