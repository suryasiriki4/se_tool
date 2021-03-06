import re
import sys
import os
#cs18b018
from bs4 import BeautifulSoup
import requests
import googlesearch
from html2text import html2text

import random

from utils import ANSWERS_URL, QUESTIONS_URL
from utils import Question, Answer
from storage import QUESTIONS, ANSWERS, QUSTION_IDS

SO_URL = "https://stackoverflow.com"

USER_AGENTS = [
    "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Firefox/59",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
]

def souper(url):
    """ getting the beautifulSoup object from url """

    try:
        html = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Firefox/59"})
    except requests.exceptions.RequestException:
        print("unable to fetch stack overflow results")
        sys.exit(1)

    print(html.url)

    if re.search("\.com/nocaptcha", html.url): # checking if URL is captcha page
        return None
    else:
        return BeautifulSoup(html.text, "html.parser")

def get_search_results(soup):
    """ return a list of directories of containg serach resluts """
    search_results = []

    for result in soup.find_all("div", class_="question-summary search-result"):
        search_results.append(result)


def get_questions_urls(query):
    """ wrapper function for get_search_results"""    

    search_text = query + " site:stackoverflow.com"

    questions_urls = googlesearch.search(search_text)[:4]

    return questions_urls


def get_question_ids(questions_urls):
    # taking only the question ids from the urls using regular expresssions
    # parse questions id from each url path
    # re.findall will return something like '/666/' so the
    # [1:-1] slicing can remove these slashes
    question_ids = [re.findall(r"/\d+/", q)[0][1:-1] for q in questions_urls]

    return question_ids

def get_answers_to_questions(question_ids):
    """ retriving the most voted anwers and the accepted answers for the question with given ids """

    answers = []

    for question_id in question_ids:

        response = requests.get(ANSWERS_URL.replace("<id>", question_id))
        items = response.json()["items"]

        if items == []:
            continue

        most_voted_answer = items[0]

        body_of_most_voted_answer = most_voted_answer["body"]

        markdown_answer_body = html2text(body_of_most_voted_answer)

        answers.append(
            Answer(
                id=str(most_voted_answer["answer_id"]),
                accepted=most_voted_answer["is_accepted"],
                score=most_voted_answer["score"],
                body=markdown_answer_body,
                author=most_voted_answer["owner"]["display_name"],
                profile_image=most_voted_answer["owner"].get("profile_image", None),
        ))

    return answers


def store_questions(question_ids):
    questions = []

    for question_id in question_ids:

        response = requests.get(QUESTIONS_URL.replace("<id>", question_id))
        items = response.json()["items"]

        if items == []:
            continue

        question = items[0]

        question_body = question["body"]

        markdown_question_body = html2text(question_body)

        questions.append(Question(id=question_id, has_accepted=None, body=markdown_question_body))



    return questions

def print_results(QUSTION_IDS, QUESTIONS, ANSWERS):

    num_of_results = len(QUSTION_IDS)

    for i in range(num_of_results):
        print(' ')
        print("#####################################################################################################")
        print(' ')
        print('Question: ')
        print(' ')
        print(QUESTIONS[i].body)
        print(' ')
        print("-----------------------------------------------------------------------------------------------------")
        print(' ')
        print("Author: " + ANSWERS[i].author)
        print(' ')
        print(' ')
        print("Answer: ")
        print(' ')
        print(ANSWERS[i].body)

    return

def main():

    query = input("please enter your query : ")

    questions_urls = get_questions_urls(query)  # getting all the urls of the questions related to the query.

    QUSTION_IDS = get_question_ids(questions_urls)  # getting question ids from the url.

    QUESTIONS = store_questions(QUSTION_IDS)  # storing questions all the top questions with ids in a list


    ANSWERS = get_answers_to_questions(QUSTION_IDS) # getting top most answers to the question with the given ids.

    

    print_results(QUSTION_IDS, QUESTIONS, ANSWERS)  # printing all the resutled questions with answers




