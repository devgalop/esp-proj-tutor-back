from fastapi import Request
from fastapi.params import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from functools import lru_cache

from src.features.assessments.evaluate.evaluate_assessment_contract import (
    EvaluateAssessmentContract,
)
from src.features.assessments.evaluate.evaluate_assessment_service import (
    EvaluateAssessmentService,
)
from src.features.assessments.get_all_questions.get_all_questions_handler import (
    GetAllQuestionsHandler,
)
from src.features.assessments.get_assessment.get_assessment_handler import (
    GetAssessmentHandler,
)
from src.features.assessments.get_assessment_by_topic.get_assessment_by_topic_handler import (
    GetAssessmentByTopicHandler,
)
from src.features.assessments.get_assessment_result.get_assessment_result_handler import (
    GetAssessmentResultHandler,
)
from src.features.assessments.get_assessments_summary.get_assessments_summary_handler import (
    GetAssessmentsSummaryHandler,
)
from src.features.assessments.get_available_models.get_available_models_handler import (
    GetAvailableModelsHandler,
)
from src.features.assessments.get_model_selected.get_model_selected_handler import (
    GetModelSelectedHandler,
)
from src.features.assessments.get_pending_approval_questions.get_pending_approval_questions_handler import (
    GetPendingApprovalQuestionsHandler,
)
from src.features.assessments.get_qualification_status.get_qualification_status_handler import (
    GetQualificationStatusHandler,
)
from src.features.assessments.get_quantity_of_assessments.get_quantity_of_assessments_handler import (
    GetQuantityOfAssessmentsHandler,
)
from src.features.assessments.get_question_categories.get_question_categories_handler import (
    GetQuestionCategoriesHandler,
)
from src.features.assessments.get_questions_topics.get_questions_topics_handler import (
    GetQuestionsTopicsHandler,
)
from src.features.assessments.save_review_question.save_review_question_handler import (
    SaveReviewQuestionHandler,
)
from src.features.assessments.shared.classification_service import ClassificationService
from src.features.assessments.shared.get_assessment_service import (
    GetAssessmentService,
)
from src.features.assessments.get_question_by_id.get_question_by_id_handler import (
    GetQuestionByIdHandler,
)
from src.features.assessments.get_questions_by_level.get_questions_by_level_handler import (
    GetQuestionsByLevelHandler,
)
from src.features.assessments.get_questions_by_category.get_questions_by_category_handler import (
    GetQuestionsByCategoryHandler,
)
from src.features.assessments.register_question.register_question_handler import (
    RegisterQuestionHandler,
)
from src.features.assessments.save_assessments_answers.save_assessments_answers_handler import (
    SaveAssessmentsAnswersHandler,
)
from src.features.assessments.save_assessments_answers.save_assessments_answers_service import (
    SaveAssessmentsAnswersService,
)
from itmentorsoft_persistence.repositories import AssessmentRepository
from src.features.assessments.shared.qualifier_service import (
    AvailableProcesses,
    ModelExplorerService,
    ModelSelectorService,
    QualifierService,
)
from itmentorsoft_persistence.repositories import (
    QuestionAssessmentRepository,
)
from src.features.assessments.shared.question_manager_service import (
    QuestionManagerService,
)
from src.features.assessments.shared.questions_cache_repository import (
    QuestionsCacheRepository,
)
from src.features.assessments.shared.review_question_service import (
    ReviewQuestionService,
)
from src.features.assessments.update_model.update_model_handler import (
    UpdateModelHandler,
)
from src.features.assessments.update_question.update_question_handler import (
    UpdateQuestionHandler,
)
from itmentorsoft_persistence.dto import QuestionBuilder
from itmentorsoft_persistence.repositories import QuestionRepository
from src.features.assessments.update_question_status.update_question_status_handler import (
    UpdateQuestionStatusHandler,
)
from src.features.shared.cache_service import CacheService
from src.features.shared.notification_service import NotificationService
from src.features.shared.publisher_service import PublisherService
from src.features.shared.template_loader import TemplateLoader
from src.features.user_management.shared.dependencies import get_user_repository
from itmentorsoft_persistence.repositories import UserRepository
from src.infrastructure.broker.aws.services.aws_sqs_connection_factory import (
    SqsConnection,
)
from src.infrastructure.broker.aws.services.aws_sqs_manager import SqsManagerService
from src.infrastructure.broker.aws.services.aws_sqs_publisher_service import (
    EvaluateAssessmentPublishAdapter,
)
from src.infrastructure.cache.valkey_cache_service import ValkeyCacheService
from src.infrastructure.classifier.opencode_classifier_service import (
    OpenCodeClassificationService,
)
from itmentorsoft_persistence.mappers import (
    PostgresAssessmentMapper,
    PostgresQuestionMapper,
)
from src.infrastructure.database.postgresql.repository.postgres_assessment_repository import (
    PostgresAssessmentRepository,
)
from src.infrastructure.database.postgresql.repository.postgres_questions_assessment_repository import (
    PostgresQuestionsAssessmentRepository,
)
from src.infrastructure.database.postgresql.repository.postgres_questions_repository import (
    PostgresQuestionsRepository,
)
from itmentorsoft_persistence import get_db

from src.infrastructure.model_manager.opencode_model_manager_proxy import (
    OpencodeModelsManagerProxy,
)
from src.infrastructure.notification.brevo_notification_service import (
    BrevoNotificationService,
)
from src.infrastructure.qualifier.opencode_qualifier_service import (
    OpencodeQualifierService,
)


def get_question_repository(
    session_factory: Annotated[AsyncSession, Depends(get_db)],
) -> QuestionRepository:
    return PostgresQuestionsRepository(session_factory, PostgresQuestionMapper)


def get_question_assessment_repository(
    session_factory: Annotated[AsyncSession, Depends(get_db)],
) -> QuestionAssessmentRepository:
    return PostgresQuestionsAssessmentRepository(
        session_factory, PostgresQuestionMapper
    )


def get_assessment_repository(
    session_factory: Annotated[AsyncSession, Depends(get_db)],
) -> AssessmentRepository:
    return PostgresAssessmentRepository(session_factory, PostgresAssessmentMapper)


def get_cache_service(request: Request) -> CacheService:
    return ValkeyCacheService(request.app.state.valkey)


def get_questions_cache_repository(
    question_assessment_repository: Annotated[
        QuestionAssessmentRepository, Depends(get_question_assessment_repository)
    ],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
) -> QuestionAssessmentRepository:
    return QuestionsCacheRepository(
        assessment_repository=question_assessment_repository,
        cache_service=cache_service,
    )


def get_notification_service() -> NotificationService:
    return BrevoNotificationService()


def get_template_loader() -> TemplateLoader:
    return TemplateLoader()


def get_question_manager_service(
    question_repository: Annotated[
        QuestionRepository, Depends(get_question_repository)
    ],
    notification_service: Annotated[
        NotificationService,
        Depends(get_notification_service),
    ],
    template_loader: Annotated[
        TemplateLoader,
        Depends(get_template_loader),
    ],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> QuestionManagerService:
    return QuestionManagerService(
        question_repository=question_repository,
        question_builder=QuestionBuilder,
        notification_service=notification_service,
        template_loader=template_loader,
        user_repository=user_repository,
    )


def get_register_question_handler(
    question_service: Annotated[
        QuestionManagerService, Depends(get_question_manager_service)
    ],
) -> RegisterQuestionHandler:
    return RegisterQuestionHandler(question_service=question_service)


def get_get_question_by_id_handler(
    question_repository: Annotated[
        QuestionRepository, Depends(get_question_repository)
    ],
) -> GetQuestionByIdHandler:
    return GetQuestionByIdHandler(question_repository=question_repository)


def get_update_question_handler(
    question_repository: Annotated[
        QuestionRepository, Depends(get_question_repository)
    ],
) -> UpdateQuestionHandler:
    return UpdateQuestionHandler(question_repository=question_repository)


def get_get_questions_by_level_handler(
    question_repository: Annotated[
        QuestionAssessmentRepository, Depends(get_questions_cache_repository)
    ],
) -> GetQuestionsByLevelHandler:
    return GetQuestionsByLevelHandler(question_repository=question_repository)


def get_get_questions_by_category_handler(
    question_repository: Annotated[
        QuestionAssessmentRepository, Depends(get_questions_cache_repository)
    ],
) -> GetQuestionsByCategoryHandler:
    return GetQuestionsByCategoryHandler(question_repository=question_repository)


def get_assessment_service(
    question_repository: Annotated[
        QuestionAssessmentRepository, Depends(get_questions_cache_repository)
    ],
    assessment_repository: Annotated[
        AssessmentRepository, Depends(get_assessment_repository)
    ],
) -> GetAssessmentService:
    return GetAssessmentService(
        question_repository=question_repository,
        assessment_repository=assessment_repository,
    )


def get_get_assessment_handler(
    get_assessment_service: Annotated[
        GetAssessmentService, Depends(get_assessment_service)
    ],
) -> GetAssessmentHandler:
    return GetAssessmentHandler(get_assessment_service=get_assessment_service)


@lru_cache()
def get_model_selector_service() -> ModelSelectorService:
    return OpencodeModelsManagerProxy()


@lru_cache()
def get_qualifier_service(
    model_selector_service: Annotated[
        ModelSelectorService, Depends(get_model_selector_service)
    ],
) -> QualifierService:
    model = model_selector_service.get_selected_model(AvailableProcesses.QUALIFIER)
    return OpencodeQualifierService(model)


@lru_cache()
def get_classification_service(
    model_selector_service: Annotated[
        ModelSelectorService, Depends(get_model_selector_service)
    ],
) -> ClassificationService:
    model = model_selector_service.get_selected_model(AvailableProcesses.CLASSIFIER)
    return OpenCodeClassificationService(model_id=model)


def get_evaluate_assessment_service() -> EvaluateAssessmentService:
    return EvaluateAssessmentService()


@lru_cache()
def get_sqs_connection(
    evaluate_contract: Annotated[
        EvaluateAssessmentContract, Depends(get_evaluate_assessment_service)
    ],
) -> SqsConnection:
    sqs_manager_service = SqsManagerService(evaluate_contract=evaluate_contract)
    sqs_connection_factory = sqs_manager_service.create_connection_factory()
    return sqs_connection_factory.create_connection()


def get_qualify_publisher_service(
    sqs_connection: Annotated[SqsConnection, Depends(get_sqs_connection)],
) -> PublisherService:
    return EvaluateAssessmentPublishAdapter(sqs_client=sqs_connection)


def get_save_assessment_answers_service(
    assessment_repository: Annotated[
        AssessmentRepository, Depends(get_assessment_repository)
    ],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    evaluator_service: Annotated[
        EvaluateAssessmentService, Depends(get_evaluate_assessment_service)
    ],
    publisher_service: Annotated[
        PublisherService, Depends(get_qualify_publisher_service)
    ],
) -> SaveAssessmentsAnswersService:
    return SaveAssessmentsAnswersService(
        assessment_repository=assessment_repository,
        user_repository=user_repository,
        evaluator_service=evaluator_service,
        publisher_service=publisher_service,
    )


def get_save_assessment_answers_handler(
    service: Annotated[
        SaveAssessmentsAnswersService, Depends(get_save_assessment_answers_service)
    ],
) -> SaveAssessmentsAnswersHandler:
    return SaveAssessmentsAnswersHandler(assessment_service=service)


def get_get_assessment_by_topic_handler(
    get_assessment_service: Annotated[
        GetAssessmentService, Depends(get_assessment_service)
    ],
) -> GetAssessmentByTopicHandler:
    return GetAssessmentByTopicHandler(get_assessment_service=get_assessment_service)


def get_get_question_categories_handler(
    question_repository: Annotated[
        QuestionRepository, Depends(get_question_repository)
    ],
) -> GetQuestionCategoriesHandler:
    return GetQuestionCategoriesHandler(question_repository=question_repository)


def get_get_all_questions_handler(
    questions_repository: Annotated[
        QuestionRepository, Depends(get_question_repository)
    ],
) -> GetAllQuestionsHandler:
    return GetAllQuestionsHandler(questions_repository=questions_repository)


def get_get_pending_approval_questions_handler(
    questions_repository: Annotated[
        QuestionRepository, Depends(get_question_repository)
    ],
) -> GetPendingApprovalQuestionsHandler:
    return GetPendingApprovalQuestionsHandler(question_repository=questions_repository)


def get_review_question_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    question_repository: Annotated[
        QuestionRepository, Depends(get_question_repository)
    ],
) -> ReviewQuestionService:
    return ReviewQuestionService(
        user_repository=user_repository,
        question_repository=question_repository,
    )


def get_save_review_question_handler(
    review_service: Annotated[
        ReviewQuestionService, Depends(get_review_question_service)
    ],
) -> SaveReviewQuestionHandler:
    return SaveReviewQuestionHandler(review_service=review_service)


def get_get_assessment_result_handler(
    assessment_repository: Annotated[
        AssessmentRepository, Depends(get_assessment_repository)
    ],
) -> GetAssessmentResultHandler:
    return GetAssessmentResultHandler(assessment_repository=assessment_repository)


def get_get_qualification_status_handler(
    assessment_repository: Annotated[
        AssessmentRepository, Depends(get_assessment_repository)
    ],
) -> GetQualificationStatusHandler:
    return GetQualificationStatusHandler(assessment_repository=assessment_repository)


def get_get_questions_topics_handler(
    questions_repository: Annotated[
        QuestionRepository, Depends(get_question_repository)
    ],
) -> GetQuestionsTopicsHandler:
    return GetQuestionsTopicsHandler(questions_repository=questions_repository)


def get_update_question_status_handler(
    question_repository: Annotated[
        QuestionRepository, Depends(get_question_repository)
    ],
) -> UpdateQuestionStatusHandler:
    return UpdateQuestionStatusHandler(question_repository=question_repository)


def get_get_quantity_of_assessments_handler(
    assessment_repository: Annotated[
        AssessmentRepository, Depends(get_assessment_repository)
    ],
) -> GetQuantityOfAssessmentsHandler:
    return GetQuantityOfAssessmentsHandler(assessment_repository=assessment_repository)


def get_get_assessments_summary_handler(
    assessment_repository: Annotated[
        AssessmentRepository, Depends(get_assessment_repository)
    ],
) -> GetAssessmentsSummaryHandler:
    return GetAssessmentsSummaryHandler(assessment_repository=assessment_repository)


@lru_cache()
def get_models_service() -> ModelExplorerService:
    return OpencodeModelsManagerProxy()


def get_get_available_models_handler(
    explorer_service: Annotated[ModelExplorerService, Depends(get_models_service)],
) -> GetAvailableModelsHandler:
    return GetAvailableModelsHandler(explorer_service=explorer_service)


def get_get_model_selected_handler(
    model_selector_service: Annotated[
        ModelSelectorService, Depends(get_model_selector_service)
    ],
) -> GetModelSelectedHandler:
    return GetModelSelectedHandler(model_selector_service=model_selector_service)


def get_update_model_handler(
    model_selector_service: Annotated[
        ModelSelectorService, Depends(get_model_selector_service)
    ],
    model_explorer_service: Annotated[
        ModelExplorerService, Depends(get_models_service)
    ],
) -> UpdateModelHandler:
    return UpdateModelHandler(
        model_selector_service=model_selector_service,
        model_explorer_service=model_explorer_service,
    )
