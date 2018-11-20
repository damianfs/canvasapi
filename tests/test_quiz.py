from __future__ import absolute_import, division, print_function, unicode_literals
import unittest

import requests_mock

from canvasapi import Canvas
from canvasapi.exceptions import RequiredFieldMissing
from canvasapi.quiz import Quiz, QuizSubmission, QuizQuestion, QuizExtension
from canvasapi.quiz_group import QuizGroup
from tests import settings
from tests.util import register_uris


@requests_mock.Mocker()
class TestQuiz(unittest.TestCase):

    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with requests_mock.Mocker() as m:
            register_uris({'course': ['get_by_id'], 'quiz': ['get_by_id']}, m)

            self.course = self.canvas.get_course(1)
            self.quiz = self.course.get_quiz(1)

    # __str__()
    def test__str__(self, m):
        string = str(self.quiz)
        self.assertIsInstance(string, str)

    # edit()
    def test_edit(self, m):
        register_uris({'quiz': ['edit']}, m)

        title = 'New Title'
        edited_quiz = self.quiz.edit(quiz={'title': title})

        self.assertIsInstance(edited_quiz, Quiz)
        self.assertTrue(hasattr(edited_quiz, 'title'))
        self.assertEqual(edited_quiz.title, title)
        self.assertTrue(hasattr(edited_quiz, 'course_id'))
        self.assertEqual(edited_quiz.course_id, self.course.id)

    # delete()
    def test_delete(self, m):
        register_uris({'quiz': ['delete']}, m)

        title = "Great Title"
        deleted_quiz = self.quiz.delete(quiz={'title': title})

        self.assertIsInstance(deleted_quiz, Quiz)
        self.assertTrue(hasattr(deleted_quiz, 'title'))
        self.assertEqual(deleted_quiz.title, title)
        self.assertTrue(hasattr(deleted_quiz, 'course_id'))
        self.assertEqual(deleted_quiz.course_id, self.course.id)

    # get_quiz_group()
    def test_get_quiz_group(self, m):
        register_uris({'quiz': ['get_quiz_group']}, m)

        result = self.quiz.get_quiz_group(1)
        self.assertIsInstance(result, QuizGroup)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.quiz_id, 1)

    # create_question_group()
    def test_create_question_group(self, m):
        register_uris({'quiz': ['create_question_group']}, m)

        quiz_group = [{'name': 'Test Group', 'pick_count': 1,
                      'question_points': 2, 'assessment_question_bank_id': 3}]
        result = self.quiz.create_question_group(quiz_group)

        self.assertIsInstance(result, QuizGroup)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.quiz_id, 1)
        self.assertEqual(result.name, quiz_group[0].get('name'))
        self.assertEqual(result.pick_count, quiz_group[0].get('pick_count'))
        self.assertEqual(result.question_points, quiz_group[0].get('question_points'))
        self.assertEqual(result.assessment_question_bank_id,
                         quiz_group[0].get('assessment_question_bank_id'))

    def test_create_question_group_empty_list(self, m):
        register_uris({'quiz': ['create_question_group']}, m)

        quiz_group = []

        with self.assertRaises(ValueError):
            self.quiz.create_question_group(quiz_group)

    def test_create_question_group_incorrect_param(self, m):
        register_uris({'quiz': ['create_question_group']}, m)

        quiz_group = [1]

        with self.assertRaises(ValueError):
            self.quiz.create_question_group(quiz_group)

    def test_create_question_group_incorrect_dict(self, m):
        register_uris({'quiz': ['create_question_group']}, m)

        quiz_group = [{}]

        with self.assertRaises(RequiredFieldMissing):
            self.quiz.create_question_group(quiz_group)

    # create_question()
    def test_create_question(self, m):
        register_uris({'quiz': ['create_question']}, m)

        question_dict = {
            'question_name': 'Pick Correct Answer',
            'question_type': 'multiple_choice_question',
            'question_text': 'What is the right answer?',
            'points_possible': 10,
            'correct_comments': 'That\'s correct!',
            'incorrect_comments': 'That\'s wrong!',
        }
        question = self.quiz.create_question(question=question_dict)

        self.assertIsInstance(question, QuizQuestion)
        self.assertTrue(hasattr(question, 'question_name'))
        self.assertEqual(question.question_name, question_dict['question_name'])

    # get_question()
    def test_get_question(self, m):
        register_uris({'quiz': ['get_question']}, m)

        question_id = 1
        question = self.quiz.get_question(question_id)

        self.assertIsInstance(question, QuizQuestion)
        self.assertTrue(hasattr(question, 'id'))
        self.assertEqual(question.id, question_id)
        self.assertTrue(hasattr(question, 'question_name'))
        self.assertEqual(question.question_name, 'Pick Correct Answer')

    # get_questions()
    def test_get_questions(self, m):
        register_uris({'quiz': ['get_questions']}, m)

        questions = self.quiz.get_questions()
        question_list = [q for q in questions]

        self.assertEqual(len(question_list), 2)
        self.assertIsInstance(question_list[0], QuizQuestion)
        self.assertTrue(hasattr(question_list[0], 'id'))
        self.assertEqual(question_list[0].id, 1)
        self.assertIsInstance(question_list[1], QuizQuestion)
        self.assertTrue(hasattr(question_list[1], 'id'))
        self.assertEqual(question_list[1].id, 2)

    # set_extensions()
    def test_set_extensions(self, m):
        register_uris({'quiz': ['set_extensions']}, m)

        extension = self.quiz.set_extensions([
            {
                'user_id': 1,
                'extra_time': 60
            },
            {
                'user_id': 2,
                'extra_attempts': 3
            }
        ])

        self.assertIsInstance(extension, list)
        self.assertEqual(len(extension), 2)

        self.assertIsInstance(extension[0], QuizExtension)
        self.assertEqual(extension[0].user_id, "1")
        self.assertTrue(hasattr(extension[0], 'extra_time'))
        self.assertEqual(extension[0].extra_time, 60)

        self.assertIsInstance(extension[1], QuizExtension)
        self.assertEqual(extension[1].user_id, "2")
        self.assertTrue(hasattr(extension[1], 'extra_attempts'))
        self.assertEqual(extension[1].extra_attempts, 3)

    def test_set_extensions_not_list(self, m):
        with self.assertRaises(ValueError):
            self.quiz.set_extensions({'user_id': 1, 'extra_time': 60})

    def test_set_extensions_empty_list(self, m):
        with self.assertRaises(ValueError):
            self.quiz.set_extensions([])

    def test_set_extensions_non_dicts(self, m):
        with self.assertRaises(ValueError):
            self.quiz.set_extensions([('user_id', 1), ('extra_time', 60)])

    def test_set_extensions_missing_key(self, m):
        with self.assertRaises(RequiredFieldMissing):
            self.quiz.set_extensions([{'extra_time': 60, 'extra_attempts': 3}])

    # get_all_quiz_submissions()
    def test_get_all_quiz_submissions(self, m):
        register_uris({'quiz': ['get_all_quiz_submissions']}, m)
        submission = self.quiz.get_all_quiz_submissions()

        self.assertIsInstance(submission, list)
        self.assertEqual(len(submission), 2)

        self.assertIsInstance(submission[0], QuizSubmission)
        self.assertEqual(submission[0].id, 1)
        self.assertTrue(hasattr(submission[0], 'attempt'))
        self.assertEqual(submission[0].attempt, 3)

        self.assertIsInstance(submission[1], QuizSubmission)
        self.assertEqual(submission[1].id, 2)
        self.assertTrue(hasattr(submission[1], 'score'))
        self.assertEqual(submission[1].score, 5)

    # get_quiz_submission
    def test_get_quiz_submission(self, m):
        register_uris({'quiz': ['get_quiz_submission']}, m)

        quiz_id = 1
        submission = self.quiz.get_quiz_submission(quiz_id)

        self.assertIsInstance(submission, QuizSubmission)
        self.assertTrue(hasattr(submission, 'id'))
        self.assertEqual(submission.quiz_id, quiz_id)
        self.assertTrue(hasattr(submission, 'quiz_version'))
        self.assertEqual(submission.quiz_version, 1)
        self.assertTrue(hasattr(submission, 'user_id'))
        self.assertEqual(submission.user_id, 1)
        self.assertTrue(hasattr(submission, 'validation_token'))
        self.assertEqual(submission.validation_token, 'this is a validation token')
        self.assertTrue(hasattr(submission, 'score'))
        self.assertEqual(submission.score, 0)

    # create_submission
    def test_create_submission(self, m):
        register_uris({'quiz': ['create_submission']}, m)

        submission = self.quiz.create_submission()

        self.assertIsInstance(submission, QuizSubmission)


@requests_mock.Mocker()
class TestQuizSubmission(unittest.TestCase):
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        self.submission = QuizSubmission(
            self.canvas._Canvas__requester,
            {
                'id': 1,
                'quiz_id': 1,
                'user_id': 1,
                'course_id': 1,
                'submission_id': 1,
                'attempt': 3,
                'validation_token': 'this is a validation token',
                'manually_unlocked': None,
                'score': 7
            }
        )

    # __str__()
    def test__str__(self, m):
        string = str(self.submission)
        self.assertIsInstance(string, str)

    # complete
    def test_complete(self, m):
        register_uris({'submission': ['complete']}, m)

        submission = self.submission.complete()

        with self.assertRaises(ValueError):
            self.submission.complete(attempt=1)

        with self.assertRaises(ValueError):
            self.submission.complete(validation_token='should not pass validation token here')

        self.assertIsInstance(submission, QuizSubmission)
        self.assertTrue(hasattr(submission, 'id'))
        self.assertTrue(hasattr(submission, 'quiz_id'))
        self.assertTrue(hasattr(submission, 'attempt'))
        self.assertTrue(hasattr(submission, 'validation_token'))

    # get_times
    def test_get_times(self, m):
        register_uris({'submission': ['get_times']}, m)

        submission = self.submission.get_times()

        with self.assertRaises(ValueError):
            self.submission.get_times(attempt=1)

        self.assertIsInstance(submission, dict)
        self.assertTrue('end_at' in submission)
        self.assertTrue('time_left' in submission)
        self.assertTrue(type(submission['time_left']) == int)
        self.assertTrue(type(submission['end_at']) == str)

    # update_score_and_comments
    def test_update_score_and_comments(self, m):
        register_uris({'submission': ['update_score_and_comments']}, m)

        submission = self.submission.update_score_and_comments(
            quiz_submissions=[
                {
                    "attempt": 1,
                    "fudge_points": 1,
                    "questions":
                        {
                            "question id 1":
                            {
                                "score": 1,
                                "comment": "question 1 comment"
                            },
                            "question id 2":
                            {
                                "score": 2,
                                "comment": "question 2 comment"
                            },
                            "question id 3":
                            {
                                "score": 3,
                                "comment": "question 3 comment"
                            }
                        }
                }
            ]
        )

        # import pdb; pdb.set_trace()

        self.assertIsInstance(submission, QuizSubmission)
        self.assertTrue(hasattr(submission, 'id'))
        self.assertTrue(hasattr(submission, 'attempt'))
        self.assertTrue(hasattr(submission, 'quiz_id'))
        self.assertTrue(hasattr(submission, 'validation_token'))
        self.assertEqual(submission.score, 7)


@requests_mock.Mocker()
class TestQuizExtension(unittest.TestCase):
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        self.extension = QuizExtension(self.canvas._Canvas__requester, {
            'user_id': 1,
            'quiz_id': 1,
            'extra_time': 60,
            'extra_attempts': 3,
            'manually_unlocked': None,
            'end_at': None
        })

    # __str__()
    def test__str__(self, m):
        string = str(self.extension)
        self.assertIsInstance(string, str)


@requests_mock.Mocker()
class TestQuizQuestion(unittest.TestCase):

    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with requests_mock.Mocker() as m:
            register_uris({
                'course': ['get_by_id'],
                'quiz': ['get_by_id', 'get_question']
            }, m)

            self.course = self.canvas.get_course(1)
            self.quiz = self.course.get_quiz(1)
            self.question = self.quiz.get_question(1)

    # __str__()
    def test__str__(self, m):
        string = str(self.question)
        self.assertIsInstance(string, str)

    # delete()
    def test_delete(self, m):
        register_uris({'quiz': ['delete_question']}, m)

        response = self.question.delete()
        self.assertTrue(response)

    # edit()
    def test_edit(self, m):
        register_uris({'quiz': ['edit_question']}, m)

        question_dict = {
            'question_name': 'Updated Question',
            'question_type': 'multiple_choice_question',
            'question_text': 'This question has been updated.',
            'points_possible': 100,
            'correct_comments': 'Updated correct!',
            'incorrect_comments': 'Updated wrong!',
        }

        self.assertEqual(self.question.question_name, 'Pick Correct Answer')

        response = self.question.edit(question=question_dict)

        self.assertIsInstance(response, QuizQuestion)
        self.assertIsInstance(self.question, QuizQuestion)
        self.assertEqual(response.question_name, question_dict['question_name'])
        self.assertEqual(self.question.question_name, question_dict['question_name'])
