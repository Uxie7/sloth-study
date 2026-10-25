from .schemas import QuizQuestion


def score_quiz(quiz: list[QuizQuestion], answers: list[int]) -> int:
    return sum(
        1 for question, answer in zip(quiz, answers)
        if answer == question.correct_index
    )
