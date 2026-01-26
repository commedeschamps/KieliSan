from aiogram.fsm.state import StatesGroup, State


class QuizStates(StatesGroup):
    in_quiz = State()


class CompareQuizStates(StatesGroup):
    in_quiz = State()


class FeedbackStates(StatesGroup):
    waiting = State()
