import os
from datetime import datetime, timedelta
import openai
import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, Message, CallbackQuery
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler, MessageHandler, CallbackContext, Filters, ConversationHandler
import time

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY") # Initialize OpenAI API
MODEL_ENGINE = "gpt-3.5-turbo"

TOKEN_TELEGRAM_BOT = os.getenv("TELEGRAM_BOT_KEY") # Initialize Telegram Bot

def show_time_now(): # Function to show the time at the moment
    time_offset = timedelta(hours=3) # Time fit to GMT+3
    current_time = (datetime.now() + time_offset).strftime("%H:%M:%S %d-%m-%Y")
    return current_time

def write_log_to_file_txt(file_name: str, msg: str): # Function to open error_log.txt and write the error message
    with open(file_name, "a") as file:
        file.write(msg)

def reset_data(arr: list):
    del arr[:-2]

CONVERSATIONS = [] # History conversation
def get_response_from_openai(user_input: str): # Define the function to get the response from the chat bot
    def get_response():
        global CONVERSATIONS
        try: #Try to get the response from chatbot GPT-3.5-turbo
            CONVERSATIONS.append({'role':'user', 'content':user_input})
            response = openai.ChatCompletion.create(model=MODEL_ENGINE, messages=CONVERSATIONS, temperature=1.2, max_tokens=2596, top_p=0.8)
            reset_data(CONVERSATIONS) # The chatbot remembers its last 5 questions and 5 answers and then just the last question and answer 
            # raise openai.error.APIConnectionError("Connect to openai failed!")
        except Exception as error:
            CONVERSATIONS.clear() # Clear cache data
            current_time = show_time_now()
            error_msg = f"An error occurred while generating a response from OpenAI - at {current_time}: {error}\n"
            write_log_to_file_txt("error_log.txt", error_msg)
            return "system", "I'm sorry, I was unable to generate a response. Please try again later!"
        
        try:
            choices_from_response_openai = response["choices"]
        except KeyError: # The KeyError occurs when a key specified in a dictionary is not found in the dictionary.
            current_time = show_time_now()
            write_log_to_file_txt("error_log.txt", f"An error occurred while 'extracting' the response from OpenAI, not found key 'choices' - at {current_time}: {response}\n")
            return "system", "I'm sorry, I was unable to extract a response from the OpenAI API. Please try again later!"
            
        role_reply = choices_from_response_openai[0].message.role.strip()
        content_reply = choices_from_response_openai[0].message.content.strip()
        CONVERSATIONS.append({'role':role_reply, 'content':content_reply})
        return content_reply
    
    return get_response
 
def chat_handler(update: Update, context: CallbackContext): # Define the chat message handler
    message_text_from_user = update.message.text.strip()
    get_reply_from_openai = get_response_from_openai(message_text_from_user)
    reply_msg_from_openai = get_reply_from_openai()
    update.message.reply_text(reply_msg_from_openai) # Send the response to the user
    new_conversation_to_write_to_file_text = f"User '@{update.message.from_user.username}': {message_text_from_user}\nChatbot GPT-3: {reply_msg_from_openai}\n"
    write_log_to_file_txt("history_conversation.txt", new_conversation_to_write_to_file_text)  # Appending new conversation to the file history conversation

def start_command(update: Update, context: CallbackContext): # Define the start command
    update.message.reply_text("Hi, I am a simple A.I chat bot! How can I help you today? '/help' for more info!")
    
def help_command(update: Update, context: CallbackContext): # Define the help command
    update.message.reply_text("I am a bot that can help you with the following commands: \n /start - Start the bot \n /help - Get this message :))) \n /end - End talking with the bot \nYou just need to write your message and I'll give you a response!")
    
def end_command(update: Update, context: CallbackContext): # Define the end command to end the conversation
    update.message.reply_text("Bye! I hope we can talk again soon!")
    return ConversationHandler.END
    
def error_handler(update: Update, context: CallbackContext): # Define the error handler
    current_time = show_time_now()
    error_msg = f"ERROR: {context.error} caused by {update} - at {current_time}"
    write_log_to_file_txt("error_log.txt", error_msg)
    
# Define the main function
def main():
    updater: Updater = Updater(token=TOKEN_TELEGRAM_BOT, use_context=True) # Create the Updater and pass it the bot's token

    dispatcher = updater.dispatcher # Get the dispatcher to register handlers

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
    chat_msg_handler = MessageHandler(Filters.text, chat_handler)
    dispatcher.add_handler(handler = chat_msg_handler)

    # Add the error handler to the dispatcher
    dispatcher.add_error_handler(error_handler)
    
    updater.start_polling() # Start the bot
    
    updater.idle() # Keep the bot running until being interrupted

if __name__ == "__main__":
    main()
    