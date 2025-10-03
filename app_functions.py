import pandas as pd
import numpy as np
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from io import StringIO



# Functions used:
# Function to create the dictionary of all the reviews. Later can be used to pass this as an argument to other functions
def get_data():
    df = pd.read_excel('uploads/stored_excel_file.xlsx')
    # Extract the 'text' column and convert to a dictionary
    text_column = df['Text']
    text_dict = text_column.to_dict()
    return text_dict

def csv_text_to_dataframe(csv_text):
    # Use StringIO to treat the text like a file
    csv_data = StringIO(csv_text)
    # Define the column names manually
    df = pd.read_csv(csv_data) #, header=None, names=["ID", "Review", "Rating", "Sentiment"])
    return df

def actual_rating():
    df = pd.read_excel('uploads/stored_excel_file.xlsx')
    act_rating_mean = round(df['Rating'].mean(), 1)
    return act_rating_mean

# def actual_rating(rating_series):
#     return rating_series.mean()

def count_sentiments(df):
    positive_count = (df['Sentiment'] == 'Positive').sum()
    negative_count = (df['Sentiment'] == 'Negative').sum()
    neutral_count = (df['Sentiment'] == 'Neutral').sum()
    return positive_count, negative_count, neutral_count

def clean_and_mean(df):
    if df.shape[1] < 3:
        raise ValueError("DataFrame has fewer than 3 columns.")

    # Extract 3rd column (index 2)
    col = df.iloc[:, 2]

    # Convert to numeric, coercing errors to NaN
    col_numeric = pd.to_numeric(col, errors='coerce')

    # Drop NaNs
    col_numeric = col_numeric.dropna()

    # Return mean if there are valid numbers
    return round(col_numeric.mean(), 2) if not col_numeric.empty else 0

def summarize(text_dict):

    summarize_key = os.getenv('summarize_key')
    summarize_model = os.getenv('summarize_model', 'llama-3.3-70b-versatile')

    # Initialize the ChatGroq model
    chat = ChatGroq(temperature=0, groq_api_key=summarize_key, model_name=summarize_model)

    # Define the system message with additional requirements
    system = system = """You are an AI system designed to process and summarize text.
    You will receive a Python dictionary where each key represents an index, and its value is a detailed review.
    Your task is to process this dictionary and return the output as CSV text (no files, only plain text).
    CSV Requirements:
    - The header must be exactly: Index,Review,Rating,Sentiment (spellings must match exactly).
    - Each row should have:
        - "Index": same as the dictionary key (no quotes around the index),
        - "Review": a very concise summary of the review (enclosed in double quotes),
        - "Satisfaction Score": an integer from 1 to 100 based on the review, that indicates how much is the customer satisfied,
        - "Sentiment": either Positive, Negative, or Neutral (no quotes around the sentiment).
    Strict Instructions:
    - Respond ONLY with raw CSV text.
    - Do NOT add any explanations, titles, or extra formatting.
    - Ensure the column names match exactly: Index,Review,Satisfaction Score,Sentiment.
    - Do NOT put Satisfaction Score in quotes "".
    The summaries must be objective, unbiased, and free from emotional language."""
    # Join the reviews into one string
    human_reviews = "\n".join(f"{key + 1}: {value}" for key, value in text_dict.items())
    human = "{text}"

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    # Invoke the chain with the required input
    chain = prompt | chat
    response = chain.invoke({"text": f"Here are the client reviews:\n{human_reviews}"})
    res = response.content

    return res


def tag_it(text_dict):

    tag_key = os.getenv('tag_key')
    tag_model = os.getenv('tag_model', 'llama-3.3-70b-versatile')

    # Initialize the ChatGroq model
    chat = ChatGroq(temperature=0, groq_api_key=tag_key,
                    model_name=tag_model)

    # Define the system and human messages
    system = """You are an AI-powered review classification assistant. Your task is to analyze a given dictionary of client reviews and classify each review into one or more relevant categories.  

    ### Instructions:
    {{1}} Analyze the reviews to identify key themes (e.g., product quality, pricing, delivery, customer experience).  
    {{2}} Generate a concise set of 5–10 categories that broadly cover most of the reviews.  
       - Categories should be **general enough** to apply to multiple reviews.  
       - Avoid creating redundant or highly specific categories.  
    {{3}} Classify each review into one or more relevant categories.  
       - A review can belong to **multiple categories** if it discusses different aspects.  
       - If a review does not fit any clear category, assign it to `"Other"`.  
    {{4}} Return the output as a CSV text (no files, only plain text):  
        Each row should have:
        - "Index": same as the dictionary key and an integer value,  
        - "Tags": containing the assigned categories, separated by commas and in double quotes"".
    Strict Instructions:
    - Respond ONLY with raw CSV text.
    - Do NOT add any explanations, titles, or extra formatting.
    - Do NOT put the index numbers in quotes "".
    - Ensure the column names match exactly: Index,Tags. And do NOT put them in quotes "".
    Do **not** provide explanations, extra text, or formatting—just return the csv text only, not even the text like "here is the required information or something like that".
    """
    human_reviews = "\n".join(f"{key + 1}: {value}" for key, value in text_dict.items())
    human = "{text}"

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    # Invoke the chain with the required input
    chain = prompt | chat
    response = chain.invoke({"text": f"Here are the client reviews:\n{human_reviews}"})
    res = response.content
    return res

# Function to analyse the summaries and provide a single summarized report of all the reviews
def analysis_report(text_dict):

    analysis_key = os.getenv('analysis_key')
    analysis_model = os.getenv('analysis_model', 'qwen/qwen3-32b')

    # Initialize the ChatGroq model
    chat = ChatGroq(temperature=0, groq_api_key=analysis_key, model_name=analysis_model)

    # Define the system and human messages
    system = "You are a business analyst. Based on the given reviews, write a summary report highlighting the key points. If you feel like the data which you get is not at all related to reviews, just return this statement - 'PLEASE CROSS CHECK THE FILE YOU UPLOADED'"
    human_reviews = "\n".join(text_dict.values())  # Join the dictionary values
    human = "{text}"

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    # Invoke the chain with the required input
    chain = prompt | chat
    response = chain.invoke({"text": f"Here are the client reviews:\n{human_reviews}"})
    result = response.content
    return result


# Function to suggest improvements based on the customer feedback
def suggested_improvements(text_dict):

    improvements_key = os.getenv('improvements_key')
    improvements_model = os.getenv('improvements_model', 'qwen/qwen3-32b')

# Initialize the ChatGroq model
    chat = ChatGroq(temperature=0, groq_api_key=improvements_key, model_name=improvements_model)

    # Define the system and human messages
    system = "You are a quality assurance consultant. Based on the given client reviews, pinpoint the key areas that require improvement. Focus on identifying issues and suggesting strategies to enhance overall customer satisfaction and product quality. If you feel like the data which you get is not at all related to reviews, just return this statement - 'PLEASE CROSS CHECK THE FILE YOU UPLOADED'"
    human_reviews = "\n".join(text_dict.values())  # Join the dictionary values
    human = "{text}"

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    # Invoke the chain with the required input
    chain = prompt | chat
    response = chain.invoke({"text": f"Here are the client reviews:\n{human_reviews}"})
    result = response.content
    return result
    