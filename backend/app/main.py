import json
import os 
import openai
from bertopic import BERTopic
from gensim.utils import simple_preprocess
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
stop=set(stopwords.words('english'))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://www.alexdomain.xyz:8000",
    "https://www.alexdomain.xyz"
    "https://0.0.0.0:8000",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

key = os.environ['openai_api']
openai.api_key = key
ALEX = "davinci:ft-brainmonkey-foundation-2021-12-01-09-02-32"
ROBERT = "davinci:ft-brainmonkey-foundation-2021-12-01-10-22-50"

TEMP = 0.2
MAX_TOKENS = 512
PRES_PEN = 1
FRE_PEN = 1

SIMILARITY_THRESHOLD_QUESTION_ALEX = 0.35
SIMILARITY_THRESHOLD_ANSWER_QA_ALEX = 0.30
SIMILARITY_THRESHOLD_ANSWER_COMPLETION_ALEX = 0.25


with open("classification_examples_w_labels.txt", "r") as fp:
  examples = json.load(fp)


def get_model():
    """
    Retrieve BERTopic model from EC2
    """
    load_bert = BERTopic.load('bertopic_trained_alex_1026')
    return load_bert


def topic_similarity(question):
    """
    Use the trained BERTopic to find out whether the user's question belongs 
    to the train data topic distribution. 
    """
    topic_model = get_model()
    question_token = simple_preprocess(question, deacc=True, max_len=512)
    question_whole = " ".join([kept for kept in question_token if not kept in stop])
    similar_topics, similarity = topic_model.find_topics(question_whole, top_n=5)
    top_score = similarity[0]
    return top_score


def completion(question, character):
    """
    Generate completion given the question using the params
    """
    answer_parse = openai.Completion.create(
            model = character,
            prompt = question,
            temperature=TEMP,
            max_tokens=MAX_TOKENS,
            frequency_penalty=FRE_PEN,
            presence_penalty=PRES_PEN,
            echo=True,
            stop=[" \###"])
    answer = answer_parse['choices'][0]['text']
    return answer


def content_filtering(answer):
    """
    Filter GPT-3 completion before returning to user
    If content is sensitive or unsafe, regenerate completion 
    0 = safe, 1 = senstive, 2 = unsafe
    """
    content_filter = openai.Completion.create(
        engine="content-filter-alpha",
        prompt= "<|endoftext|>"+answer+"\n--\nLabel:",
        temperature=0,
        max_tokens=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        logprobs=10
    )
    content_rate = content_filter['choices'][0]["text"]
    return content_rate


def classify_question(question):
  question_type = openai.Classification.create(
      search_model="babbage", 
      model="davinci",
      examples=examples,
      query=question,
      labels = ["Factual","Non-factual"],    
      max_examples=len(examples))
  question_type = question_type["label"]
  return question_type


def question_answer_alex(question):
  try:
    qa_answer = openai.Answer.create(
        search_model="curie", 
        model="davinci", 
        question=question, 
        file="file-mcgwAkzglsZSibNyeFuuGjcH",
        examples_context="In 2017, U.S. life expectancy was 78.6 years.", 
        examples=[["What is human life expectancy in the United States?", "78 years."]], 
        max_rerank=200,
        max_tokens=25,
        temperature=0.05,
        stop=["\n", "<|endoftext|>"]
    )
    qa_answer_parse = qa_answer['answers'][0]
    print(qa_answer_parse)
    # Acccounting for incomplete answer
    if not qa_answer_parse.endswith("."):
        qa_answer_x = qa_answer_parse.split(".")
        return qa_answer_x[0]+'.'
    else: 
      return qa_answer_parse.split(".")[0]+'.'
  except:
    return "This is not within my training data, I don't have an answer. Sorry."


def question_answer_robert(question):
  try:
    qa_answer = openai.Answer.create(
        search_model="curie", 
        model="davinci", 
        question=question, 
        file="file-pDRf8IM6fij00OKY6kOODzfl",
        examples_context="In 2017, U.S. life expectancy was 78.6 years.", 
        examples=[["What is human life expectancy in the United States?", "78 years."]], 
        max_rerank=200,
        max_tokens=25,
        temperature=0.05,
        stop=["\n", "<|endoftext|>"]
    )
    qa_answer_parse = qa_answer['answers'][0]
    print(qa_answer_parse)
    # Acccounting for incomplete answer
    if not qa_answer_parse.endswith("."):
        qa_answer_x = qa_answer_parse.split(".")
        return qa_answer_x[0]+'.'
    else: 
      return qa_answer_parse.split(".")[0]+'.'
  except:
    return "This is not within my training data, I don't have an answer. Sorry."


@app.get("/alex_gpt/")
def ask_question():
    return {"answer": "Ask a question that you'd like to know how Alex would answer."}


@app.get("/alex_gpt/{question}")
def alex_gpt(question: str):
    """
    Receive the question and fine topic of it
    Go through content filtering first, if unsafe, refuse to answer
    If topic is higher than threshold then answer question
    If answer is unsafe, keep generate new answer until safe or sensitive
    Return I don't know if the question is lower than threshold"
    """
    pronouns = {
        " alex ":"",
        " Alex ":"",
        "Alex ":"",
        "alex ": "",
        "What are your ": "What are my ",
        "what are your ": "what are my ",
        " are you":" am I",
        "are you ":"am I ",
        "Are you ":"Am I ",
        "You ":"I ",
        " you ":" I ",
        " your ":" my ",
        "Your ":"My ",
        " me ":" you "}
    
    # If there's empty question
    if not question or question == "":
        return {"answer": "Ask a question that you'd like to know how Alex would answer."}

    question_parsed = " ".join(question.split("_"))

    # Don't take questions less than 3 words:
    if len(question_parsed.split()) < 3:
        return {"answer": "That's not a fully formatted question, is it?"}

    # Change pronous, a bit hacky but quick
    for key in pronouns.keys():
        question_parsed = question_parsed.replace(key, pronouns[key])

    try_times = 3
    # Content filter question
    content_rating_question = content_filtering(question_parsed)
    if content_rating_question == "2":
        return {"answer": "Sorry, can't answer that one, that's not very polite."}

    # Content is not unsafe, go ahead and classify question
    else:
        question_type = classify_question(question_parsed)
        print(f"Question type: {question_type}")

        similarity_score = topic_similarity(question_parsed)
        print(f"Question similarity score: {similarity_score}")

        # Answer Factual question
        if question_type == "Factual":
            if similarity_score <= SIMILARITY_THRESHOLD_QUESTION_ALEX:
                return {"answer": "The question topic is not in my training data, I don't have the answer. Apologies."}
            else:
                answer_factual = question_answer_alex(question_parsed)
                factual_content_rating = content_filtering(answer_factual)
                answer_factual_similarity_score = topic_similarity(answer_factual)
                print(f"Factual answer similarity score: {answer_factual_similarity_score}")
                if answer_factual_similarity_score >= SIMILARITY_THRESHOLD_ANSWER_QA_ALEX and factual_content_rating != "2":
                    return {"answer": answer_factual}
                else:
                    return {"answer": "The answer is not in my training data, I don't have the answer. Apologies."}

        if question_type == "Non-factual":
            if similarity_score < SIMILARITY_THRESHOLD_QUESTION_ALEX: 
                # Return this because the question itself is not within training data 
                return {"answer": "The question topic is not in my training data. I don't have the answer, please try another one."}
            else:
                # Answer Non-factual question
                answer_non_factual = completion(question_parsed, ALEX)
                answer_similarity_score = topic_similarity(answer_non_factual)
                print(f"Non-factual answer similarity score: {answer_similarity_score}")
                if answer_similarity_score < SIMILARITY_THRESHOLD_ANSWER_COMPLETION_ALEX:
                    return {"answer": "My training data doesn't have the answer, try another one."} 

                else:
                    answer_similarity_score >= SIMILARITY_THRESHOLD_ANSWER_COMPLETION_ALEX
                    content_rate = content_filtering(answer_non_factual)   
                    cur_rate = content_rate

                    while cur_rate == "2":
                        answer_non_factual = completion(question_parsed, ALEX)
                        new_content_rate = content_filtering(answer_non_factual)
                        cur_rate = new_content_rate
                        try_times -= 1
                        if try_times == 0:
                            return {"answer": "I have no nice way to respond to this. Try another question maybe?"}

                    # Return this because content is now safe and pass similarity threshold but could be sensitive, definitely not unsafe
                    return {"answer": answer_non_factual}  


@app.get("/robert_gpt/")
def ask_question():
    return {"answer": "Ask a question that you'd like to know how Robert would answer."}


@app.get("/robert_gpt/{question}")
def robert_gpt(question: str):
    """
    Similar to alex_gpt but with slightly different params
    """
    try_times = 3
    pronouns = {
        " robert ":"",
        " Robert ":"",
        "Robert ":"",
        "robert ": "",
        "What are your ": "What are my ",
        "what are your ": "what are my ",
        " are you":" am I",
        "are you ":"am I ",
        "Are you ":"Am I ",
        "You ":"I ",
        " you ":" I ",
        " your ":" my ",
        "Your ":"My ",
        " me ":" you "}
    
    # If there's empty question
    if not question or question == "":
        return {"answer": "Ask a question that you'd like to know how Robert would answer."}

    question_parsed = " ".join(question.split("_"))

    # Don't take questions less than 3 words:
    if len(question_parsed.split()) < 3:
        return {"answer": "That's not a fully formatted question, is it?"}

    # Change pronous, a bit hacky but quick
    for key in pronouns.keys():
        question_parsed = question_parsed.replace(key, pronouns[key])

    try_times = 3
    # Content filter question
    content_rating_question = content_filtering(question_parsed)
    if content_rating_question == "2":
        return {"answer": "Sorry, can't answer that one, that's not very polite."}

    # Content is not unsafe, go ahead and classify question
    else:
        question_type = classify_question(question_parsed)
        print(question_type)

        # Answer Factual question
        if question_type == "Factual":
            answer_factual = question_answer_robert(question_parsed)
            factual_content_rating = content_filtering(answer_factual)
            if factual_content_rating != "2":
                return {"answer": answer_factual}
            else:
                return {"answer": "I don't have the answer. Apologies."}
        
        if question_type == "Non-factual":
            # Answer Non-factual question
            answer_non_factual = completion(question_parsed, ROBERT)
            content_rate = content_filtering(answer_non_factual)   
            cur_rate = content_rate
            if cur_rate != "2":
                return {"answer": answer_non_factual} 
            elif cur_rate == "2":
                answer_non_factual = completion(question_parsed, ROBERT)
                new_content_rate = content_filtering(answer_non_factual)
                cur_rate = new_content_rate
                try_times -= 1
                if try_times == 0:
                    return {"answer": "I have no nice way to respond to this. Try another question maybe?"} 