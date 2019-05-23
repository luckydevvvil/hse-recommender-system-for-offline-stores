import csv
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, ConversationHandler, RegexHandler, CallbackQueryHandler

ID, LOGGED_IN, CHECKOUT = range(3)

ids = {}
recommendations = {}
bonuses = {}
menu_keyboard_markup = ReplyKeyboardMarkup([[KeyboardButton("/Я-на-кассе")], [KeyboardButton("/Я-в-магазине"), KeyboardButton("/История-покупок"), KeyboardButton("/Поиск-на-карте")]])


def start(bot, update):
    update.message.reply_text(
        "Для активации бота введите номер карты лояльности:")
    return ID


def id(bot, update):
    if not update.message.text.isdigit():
        update.message.reply_text("Введите число. Идентификационный номер состоит только из цифр")
        return ID

    customer_id = int(update.message.text)

    if not customer_id in recommendations:
        update.message.reply_text("Ваш идентификационный номер отстутствует в нашей базе данных. Введите корректный ид. номер либо приобретите нашу карту лояльности")
        return ID

    ids[update.message.from_user.id] = customer_id

    update.message.reply_text("Здравствуйте, {}! Теперь всю информацию по вашей карте можно узнать здесь. Для продолжения выберите один из пунктов меню ниже".format(update.message.from_user.first_name), reply_markup=menu_keyboard_markup)

    return LOGGED_IN


def get_recommendations(bot, update):
    update.message.reply_text(recommendations[ids[update.message.from_user.id]], reply_markup=menu_keyboard_markup)

    return LOGGED_IN


def checkout(bot, update):
    update.message.reply_text("Покажите этот QR-код сотруднику на кассе, чтобы использовать карту лояльности")
    update.message.reply_photo(photo="http://qr-code-generator.online/img/qrcode1558444907.png")

    return LOGGED_IN


def in_shop(bot, update):
    update.message.reply_text("Количество бонусов, доступных для списывания:\n"
                              + bonuses[ids[update.message.from_user.id]] + " рублей.\n\n"
                              + "Ваши перснальные скидки до конца этой недели:\n"
                              + recommendations[ids[update.message.from_user.id]])

#     update.message.reply_text("Ваши перснальные скидки до конца этой недели:\n"
#                               + recommendations[ids[update.message.from_user.id]])

    return LOGGED_IN


history_inline_keyboard_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Оценить продукты", callback_data="1")], [InlineKeyboardButton("Оценить сервис", callback_data="2")], [InlineKeyboardButton("Выслать чек по почте", callback_data="3")]])


def history(bot, update):
    update.message.reply_text("Список ваших последних покупок:")
    update.message.reply_text("Покупка 1", reply_markup=history_inline_keyboard_markup)
    update.message.reply_text("Покупка 2", reply_markup=history_inline_keyboard_markup)

    return LOGGED_IN


def menu(bot, update):
    update.message.reply_text.InputTextMessageContent("Вы в главном меню", reply_markup=menu_keyboard_markup)

    return LOGGED_IN


menu_command_handler = CommandHandler("menu", menu)


def main():
    with open("./recommender_output.csv", newline="") as csvfile:
        recommendations_reader = csv.reader(
            csvfile, delimiter=",", quotechar="|")
        for row in recommendations_reader:
            customer_id = row[0]
            if customer_id.isdigit():
                recommendations[int(customer_id)] = row[2]
                bonuses[int(customer_id)] = row[3]
    updater = Updater("")

    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ID: [RegexHandler(".", id)],
            LOGGED_IN: [CommandHandler("рекомендации", get_recommendations), CommandHandler("Я-на-кассе", checkout), CommandHandler("в-магазине", in_shop), CommandHandler("история-покупок", history)],
        },
        fallbacks=[]
    ))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
