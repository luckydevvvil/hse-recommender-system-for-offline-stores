import csv
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler, RegexHandler, CallbackQueryHandler

ID, LOGGED_IN = range(2)

ids = {}
recommendations = {}
keyboard_markup = ReplyKeyboardMarkup([[KeyboardButton("/recommendations")]])


def start(bot, update):
    update.message.reply_text(
        "Hello, {}! Please enter your ID as number:".format(update.message.from_user.first_name))
    return ID


def id(bot, update):
    if (not update.message.text.isdigit()):
        update.message.reply_text("Please enter only numbers!")
        return ID

    customer_id = int(update.message.text)

    if (not customer_id in recommendations):
        update.message.reply_text(
            "This user does not exist in our DB! Please enter correct ID or buy our loyalty card")
        return ID

    ids[update.message.from_user.id] = customer_id

    update.message.reply_text(
        "Now you can get your recommendations:", reply_markup=keyboard_markup)

    return LOGGED_IN


def get_recommendations(bot, update):
    update.message.reply_text("Your recommendations: {}".format(
        recommendations[ids[update.message.from_user.id]]), reply_markup=keyboard_markup)

    return LOGGED_IN


def main():
    with open("./recommender_output.csv", newline="") as csvfile:
        recommendations_reader = csv.reader(
            csvfile, delimiter=",", quotechar="|")
        for row in recommendations_reader:
            customer_id = row[0]
            if customer_id.isdigit():
                recommendations[int(customer_id)] = row[1]

    updater = Updater("844741691:AAHSYq_l3ftV_p8O9C8O5zBcODqQbJNYWfk")

    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ID: [RegexHandler(".", id)],
            LOGGED_IN: [CommandHandler("recommendations", get_recommendations)]
        },
        fallbacks=[]
    ))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()