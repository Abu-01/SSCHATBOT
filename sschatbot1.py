import logging
import random
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

logging.basicConfig(level=logging.INFO)

# Questions and answers
questions = [
    # Easy questions
    ("What is the capital of France?", "Paris"),
    ("What is the square root of 144?", "12"),
    ("What is the chemical symbol for water?", "H2O"),
    ("Who painted the Mona Lisa?", "Leonardo da Vinci"),
    ("What year was the electric guitar invented?", "1931"),
    # Add more difficult questions here
    
    # Python questions
    ("What is the keyword used to define a function in Python?", "def"),
    ("Which keyword is used to create a class in Python?", "class"),
    ("What is the output of the following code: print('Hello, World!'.lower())", "hello, world!"),
    ("What is the output of the following code: print('Hello, World!'.upper())", "HELLO, WORLD!"),
    ("What is the output of the following code: print(len('Hello, World!'))", "13"),
    ("What is the output of the following code: print('Hello, World!'[0])", "H"),
    ("What is the output of the following code: print('Hello, World!'[-1])", "!"),
    ("What is the output of the following code: print('Hello, World!'[7:12])", "World"),
    ("What is the output of the following code: print('Hello, World!'.replace('World', 'Python'))", "Hello, Python!"),
    ("What is the output of the following code: print('Hello, World!'.split(', '))", "['Hello', 'World!']"),
    ("What is the output of the following code: print('Hello, World!'.startswith('Hello'))", "True"),
    ("What is the output of the following code: print('Hello, World!'.endswith('World!'))", "True"),
    ("What is the output of the following code: print('Hello, World!'.count('l'))", "3"),
    ("What is the output of the following code: print('Hello, World!'.find('World'))", "7"),
    ("What is the output of the following code: print('Hello, World!'.isalnum())", "False"),
    # Python questions
    ("Which Python library is used for web scraping?", "BeautifulSoup"),
    ("Which Python library is used for scientific computing?", "NumPy"),
    ("Which Python library is used for data manipulation and analysis?", "pandas"),
    ("Which Python library is used for machine learning?", "scikit-learn"),
    ("Which Python library is used for deep learning?", "TensorFlow"),

    # Programming questions
    ("What does the acronym 'OOP' stand for in programming?", "Object-Oriented Programming"),
    ("What does the acronym 'IDE' stand for in programming?", "Integrated Development Environment"),
    ("What does the acronym 'API' stand for in programming?", "Application Programming Interface"),
    ("What does the acronym 'SQL' stand for in programming?", "Structured Query Language"),
    ("What does the acronym 'HTML' stand for in programming?", "HyperText Markup Language"),

    # General knowledge questions
    ("What is the largest planet in our solar system?", "Jupiter"),
    ("What is the smallest planet in our solar system?", "Mercury"),
    ("What is the largest ocean on Earth?", "Pacific Ocean"),
    ("What is the smallest ocean on Earth?", "Arctic Ocean"),
    ("What is the largest country in the world by land area?", "Russia"),
    ("What is the smallest country in the world by land area?", "Vatican City"),
    ("What is the highest mountain on Earth?", "Mount Everest"),
    ("What is the longest river on Earth?", "Nile River"),
    ("What is the largest desert on Earth?", "Antarctic Desert"),
    ("What is the smallest continent on Earth?", "Australia"),

]

leaderboard = []

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Please enter your username.")
    return "username"

def username(update: Update, context: CallbackContext):
    context.user_data["username"] = update.message.text
    update.message.reply_text("Please enter your password.")
    return "password"

def password(update: Update, context: CallbackContext):
    context.user_data["password"] = update.message.text
    update.message.reply_text("Please enter your age.")
    return "age"

def age(update: Update, context: CallbackContext):
    try:
        context.user_data["age"] = int(update.message.text)
    except ValueError:
        update.message.reply_text("Invalid input. Please enter your age as a number.")
        return "age"

    if context.user_data["age"] < 15:
        update.message.reply_text("You must be at least 15 years old to play.")
        return ConversationHandler.END
    else:
        context.user_data["retries"] = 3
        return start_game(update, context)

def start_game(update: Update, context: CallbackContext):
    update.message.reply_text("Great! You will receive 5 questions. You have {} chances to answer all questions correctly. Good luck!".format(context.user_data["retries"]))
    context.user_data["questions_asked"] = 0
    context.user_data["questions_correct"] = 0
    context.user_data["used_questions"] = set()
    context.user_data["start_time"] = time.time()
    return ask_question(update, context)

def ask_question(update: Update, context: CallbackContext):
    if context.user_data["questions_asked"] < 5:
        question, answer = random.choice(questions)
        while question in context.user_data["used_questions"]:
            question, answer = random.choice(questions)
        context.user_data["used_questions"].add(question)
        context.user_data["current_question"] = question
        context.user_data["current_answer"] = answer
        update.message.reply_text(context.user_data["current_question"])
        context.user_data["questions_asked"] += 1
        return "answer"
    else:
        end_time = time.time()
        time_taken = end_time - context.user_data["start_time"]
        leaderboard.append((context.user_data["username"], time_taken))
        leaderboard.sort(key=lambda x: x[1])

        update.message.reply_text("You answered {} out of 5 questions correctly.".format(context.user_data["questions_correct"]))

        with open("user_data.txt", "a") as f:
            f.write("{}:{}:{}\n".format(context.user_data["username"], context.user_data["password"], context.user_data["questions_correct"]))

        if context.user_data["retries"] > 1:
            context.user_data["retries"] -= 1
            update.message.reply_text("You have {} retries left. Type /retry to try again or /cancel to end the game.".format(context.user_data["retries"]))
            return "retry"
        else:
            update.message.reply_text("You have answered all 5 questions and used all your retries. Thank you for playing! for any feedback : @sstutor_bot")
            return ConversationHandler.END

def check_answer(update: Update, context: CallbackContext):
    user_answer = update.message.text.strip().lower()
    if user_answer == context.user_data["current_answer"].lower():
        update.message.reply_text("Correct!")
        context.user_data["questions_correct"] += 1
    else:
        update.message.reply_text("Incorrect. The correct answer is: " + context.user_data["current_answer"])
    return ask_question(update, context)

def retry(update: Update, context: CallbackContext):
    return start_game(update, context)

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Conversation cancelled.")
    return ConversationHandler.END

updater = Updater("6129528190:AAGbQRt8JriXNeBKsUdU0579y-vuJY0aKBk", use_context=True)

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        "username": [MessageHandler(Filters.text, username)],
        "password": [MessageHandler(Filters.text, password)],
        "age": [MessageHandler(Filters.text, age)],
        "answer": [MessageHandler(Filters.text, check_answer)],
        "retry": [CommandHandler('retry', retry)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

updater.dispatcher.add_handler(conv_handler)

updater.start_polling()

updater.idle()
