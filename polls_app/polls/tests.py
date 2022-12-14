from urllib import response
from django.urls import reverse
import datetime
from django.test import TestCase
from django.utils import timezone

from .models import Choice, Question

# TEST OF MODELS


class QuestionModelTest(TestCase):
    def setUp(self):
        self.question = Question(
            question_text="Quien es el mejor CD de Platzi?")

    def test_was_publish_recently_with_future_questions(self):
        """"was_publish_recently() retuns False for questions whose pub_date is in the future"""
        time = timezone.now() + datetime.timedelta(days=30)
        self.question.pub_date = time
        self.assertIs(self.question.was_publish_recently(), False)

    def test_was_publish_recently_with_present_questions(self):
        """"was_publish_recently() retuns True for questions whose pub_date is in the present"""
        time = timezone.now() - datetime.timedelta(hours=23)
        self.question.pub_date = time
        self.assertIs(self.question.was_publish_recently(), True)

    def test_was_publish_recently_with_past_questions(self):
        """"was_publish_recently() retuns False for questions whose pub_date is in the past"""
        time = timezone.now() - datetime.timedelta(days=1, minutes=1)
        self.question.pub_date = time
        self.assertIs(self.question.was_publish_recently(), False)


def create_question(question_text, days):
    """ Create a questions with the given 'question_text', and published the given number
       of days offset to now (negative for questions published in the past, and positive 
       for questions that have yet to be published) """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTest(TestCase):
    def test_no_questions(self):
        """If not exist, an aproppiate message is displayed"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_questions(self):
        """ Questions with a pub_date in the future are'nt displayed on the index page. """
        create_question("Future Question", days=5)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_questions(self):
        """ Questions with a pub_date in the past are displayed on the index page. """
        question = create_question("Past Question", days=-10)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"], [question])

    def test_future_and_past_question(self):
        """ Even if both past and future questions exists, only past question are displayed """
        past_question = create_question("Past Question", -5)
        future_question = create_question("Future Question", 15)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"], [past_question])

    def test_two_past_questions(self):
        """ The questions are displayed in the index view"""
        past_question1 = create_question("Past Question 1", -5)
        past_question2 = create_question("Past Question 2", -15)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"], [past_question1, past_question2])

    def test_two_future_questions(self):
        """ The questions arent displayed in the index view"""
        future_question1 = create_question("Future Question 1", 25)
        future_question2 = create_question("Future Question 2", 15)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(
            response.context["latest_question_list"], [])


class QuestionDetailViewTest(TestCase):
    def test_future_question(self):
        """ The detail view of a question with a pub_date in the future 
            returns a 404 error not found """
        future_question = create_question("Future Question", 6)
        url = reverse("polls:details", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """ The question's text of the past question are displayed in the detail view"""
        past_question = create_question("Past Question", -6)
        url = reverse("polls:details", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionResultViewTest(TestCase):
    def test_question_not_exists(self):
        """ If question not exists, returns 404  not found """
        url = reverse("polls:results", args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_exists_and_have_choices(self):
        """ If question id not exists, returns 404  not found """
        question = create_question("One Question", 0)
        question.choice_set.create(
            choice_text="One Question Choice 1", votes=0)
        question.choice_set.create(
            choice_text="One Question Choice 2", votes=0)
        url = reverse("polls:results", args=(question.id,))
        response = self.client.get(url)
        print(question.choice_set())
        self.assertContains(response, question.choice_set.all())
