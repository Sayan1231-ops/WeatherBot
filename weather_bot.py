import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = "7700902657:AAH9U1xrcJCfQjVwMULOfLLziJSoRRH7dw0"
WEATHER_API_KEY = "8bcc0ec44a434225ba885852252105"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Send /weather <city> to get the current weather.\n"
        "Send /help to see all commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/start - Welcome message\n"
        "/weather <city> - Get current weather for a city\n"
        "/help - Show this help message"
    )

async def fetch_weather(city: str):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=1&aqi=no&alerts=no"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return None, f"API returned status code {resp.status}"
                data = await resp.json()
                return data, None
        except Exception as e:
            return None, str(e)

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /weather <city>")
        return

    city = ' '.join(context.args)
    data, error = await fetch_weather(city)

    if error:
        await update.message.reply_text(f"Error fetching weather: {error}")
        return

    if "error" in data:
        await update.message.reply_text(f"City '{city}' not found. Please check the name and try again.")
        return

    location = data["location"]["name"]
    country = data["location"]["country"]
    current = data["current"]
    condition = current["condition"]["text"]
    temp_c = current["temp_c"]
    humidity = current["humidity"]
    wind_kph = current["wind_kph"]

    msg = (
        f"🌤 Weather in {location}, {country}:\n"
        f"Condition: {condition}\n"
        f"Temperature: {temp_c}°C\n"
        f"Humidity: {humidity}%\n"
        f"Wind Speed: {wind_kph} km/h"
    )
    await update.message.reply_text(msg)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("weather", weather))

    print("Bot is running...")
    app.run_polling()
