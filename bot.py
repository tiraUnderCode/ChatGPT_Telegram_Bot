import os
from datetime import datetime, timedelta
import openai
import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, Message, CallbackQuery
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler, MessageHandler, CallbackContext, Filters, ConversationHandler

from dotenv import load_dotenv
load_dotenv()

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_ENGINE = "text-davinci-003"

# Initialize Telegram Bot
TOKEN_TELEGRAM_BOT = os.getenv("TELEGRAM_BOT_KEY")

# Function to show the time at the moment
def show_time_now():
    # Time fit to GMT+3
    time_offset = timedelta(hours=3)
    current_time = (datetime.now() + time_offset).strftime("%H:%M:%S %d-%m-%Y")
    return current_time

# Function to open error_log.txt and write the error message
def write_log_to_file_txt(file_name: str, msg: str):
    try:
        with open(file_name, "a") as file:
            file.write(msg)
    finally:
        file.close()
       
# Constant template for chatbot prompt paragraph
CHATBOT_PROMPT = """
<conversation_history>
User: <user input>
Chatbot:"""
# Define the function to get the response from the chat bot
def get_response(conversation_history: str, user_input: str):
    prompt = CHATBOT_PROMPT.replace(
        "<conversation_history>", conversation_history).replace("<user input>", user_input)
    
    #Try to get the response from chatbot GPT-3
    try:
        response = openai.Completion.create(engine=MODEL_ENGINE, prompt=prompt, max_tokens=2048, n=1, stop=None, temperature=0.65)
        # raise openai.error.APIConnectionError("Connect to openai failed!")
    except Exception as error:
        error_msg = f"An error occurred while generating a response from OpenAI - at {show_time_now()}: {error}\n"
        write_log_to_file_txt("error_log.txt", error_msg)
        return "I'm sorry, I was unable to generate a response. Please try again later!"
    
    # Extract the response from the response object
    response_message_from_openai = ""
    try:
        choices_from_response_openai = response["choices"]
    except KeyError:
        # The KeyError occurs when a key specified in a dictionary is not found in the dictionary.
        write_log_to_file_txt("error_log.txt", f"An error occurred while 'extracting' the response from OpenAI, not found key 'choices' - at {show_time_now()}: {response}\n")
        return "I'm sorry, I was unable to extract a response from the OpenAI API. Please try again later!"
        
    # Return the response
    response_message_from_openai = choices_from_response_openai[0]["text"].strip()
    return response_message_from_openai
    

# Create history for the conversation paragraph with chatbot
conversation_history = ""
# Define the chat message handler
def chat_msg_handler(update: Update, context: CallbackContext):
    global conversation_history
    message_text_from_user = update.message.text
    reply_msg_from_openai = get_response(conversation_history, message_text_from_user)
    # Send the response to the user
    update.message.reply_text(reply_msg_from_openai)
    new_conversation_to_write_to_file_text = f"User '@{update.message.from_user.username}': {message_text_from_user}\nChatbot GPT-3: {reply_msg_from_openai}\n"
    conversation_history += f"User: {message_text_from_user}\nChatbot: {reply_msg_from_openai}\n"
    
    # Appending new conversation to the file history conversation
    write_log_to_file_txt("history_conversation.txt", new_conversation_to_write_to_file_text)
    # Overwrite the history conversation with new history conversation
    # with open("history_conversation.txt", "w") as file:
    #     file.write(conversation_history)

# Define the start command
def start_command(update: Update, context: CallbackContext):
    update.message.reply_text("Hi, I am a simple A.I chat bot! How can I help you today? '/help' for more info!")
    
# Define the help command
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("I am a bot that can help you with the following commands: \n /start - Start the bot \n /help - Get this message :))) \n /end - End talking with the bot \nYou just need to write your message and I'll give you a response!")
    
# Define the end command to end the conversation
def end_command(update: Update, context: CallbackContext):
    update.message.reply_text("Bye! I hope we can talk again soon!")
    return ConversationHandler.END
    
# Define the error handler
def error_handler(update: Update, context: CallbackContext):
    error_msg = f"ERROR: {context.error} caused by {update} - at {show_time_now()}"
    write_log_to_file_txt("error_log.txt", error_msg)
    
# Define the main function
def main():
    # Create the Updater and pass it the bot's token
    updater: Updater = Updater(token=TOKEN_TELEGRAM_BOT, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

     # Add the start handler to the dispatcher
    start_command_handler = CommandHandler("start", start_command)
    dispatcher.add_handler(handler = start_command_handler)

    # Add the help handler to the dispatcher
    help_command_handler = CommandHandler("help", help_command)
    dispatcher.add_handler(handler = help_command_handler)
    
    # Add the end handler to the dispatcher
    end_command_handler = CommandHandler("end", end_command)
    dispatcher.add_handler(handler = end_command_handler)
    
    # Add the chat handler to the dispatcher
    chat_handler = MessageHandler(Filters.text, chat_msg_handler)
    dispatcher.add_handler(handler = chat_handler)

    # Add the error handler to the dispatcher
    dispatcher.add_error_handler(error_handler)
    
    # Start the bot
    updater.start_polling()
    
    # Keep the bot running until being interrupted
    updater.idle()

if __name__ == "__main__":
    main()