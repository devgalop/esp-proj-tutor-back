import json

from itmentorsoft_persistence.repositories import (
    QuestionAssessmentRepository,
)
from itmentorsoft_persistence.dto import (
    EvaluativeQuestion,
    QuestionDifficulty,
)

from src.features.shared.cache_service import CacheEntry, CacheService


class EvaluativeQuestionsCache:
    def __init__(self, questions: list[EvaluativeQuestion], expiration_time: int):
        self.questions = questions
        self.expiration_time = expiration_time


class QuestionsCacheRepository(QuestionAssessmentRepository):

    PREFIX: str = "questions"
    CACHE_EXPIRATION_TIME_SECONDS = 3600

    def __init__(
        self,
        assessment_repository: QuestionAssessmentRepository,
        cache_service: CacheService,
    ):
        self.assessment_repository = assessment_repository
        self.cache_service = cache_service

    async def get_question_by_level(
        self, difficulty: QuestionDifficulty
    ) -> list[EvaluativeQuestion]:
        key = f"{self.PREFIX}:{difficulty.name}"
        value_cached = await self.cache_service.get(key)
        if not value_cached:
            questions = await self.assessment_repository.get_question_by_level(
                difficulty
            )
            await self.cache_service.set(
                key,
                CacheEntry(
                    self._generate_serialized_value(questions),
                    self.CACHE_EXPIRATION_TIME_SECONDS,
                ),
            )
            return questions
        questions_result = [
            EvaluativeQuestion(**question)
            for question in json.loads(value_cached.value)
        ]
        return questions_result

    async def get_questions_by_category(
        self, category: str
    ) -> list[EvaluativeQuestion]:
        key = f"{self.PREFIX}:{category}"
        value_cached = await self.cache_service.get(key)
        if not value_cached:
            questions = await self.assessment_repository.get_questions_by_category(
                category
            )
            await self.cache_service.set(
                key,
                CacheEntry(
                    self._generate_serialized_value(questions),
                    self.CACHE_EXPIRATION_TIME_SECONDS,
                ),
            )
            return questions

        questions_result = [
            EvaluativeQuestion(**question)
            for question in json.loads(value_cached.value)
        ]
        return questions_result

    async def get_questions_by_topic(
        self, topic: str, difficulty: QuestionDifficulty
    ) -> list[EvaluativeQuestion]:
        key = f"{self.PREFIX}:{topic}:{difficulty.name}"
        value_cached = await self.cache_service.get(key)
        if not value_cached:
            questions = await self.assessment_repository.get_questions_by_topic(
                topic, difficulty
            )
            await self.cache_service.set(
                key,
                CacheEntry(
                    self._generate_serialized_value(questions),
                    self.CACHE_EXPIRATION_TIME_SECONDS,
                ),
            )
            return questions

        questions_result = [
            EvaluativeQuestion(**question)
            for question in json.loads(value_cached.value)
        ]
        return questions_result

    def _generate_serialized_value(self, questions: list[EvaluativeQuestion]) -> str:
        return json.dumps(questions, default=lambda o: o.__dict__)
