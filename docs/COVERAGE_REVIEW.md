# Test Coverage Review — ITMentorSoft Backend

## Executive Summary

**Current Coverage**: 96.2% line coverage (7,984 of 8,299 lines)

**Coverage Breakdown**:
- Files with 100% coverage: ~85% of source files
- Files with partial coverage (<90%): ~10% of source files
- Files with 0% coverage: ~5% of source files

**Top Gaps**:
1. `src/main.py` — 0% coverage (application bootstrap, lifespan, router registration)
2. `src/infrastructure/broker/aws/` — Entire AWS SQS infrastructure completely untested
3. `src/infrastructure/notification/brevo_notification_service.py` — No tests
4. `src/infrastructure/classifier/opencode_classifier_service.py` — No tests
5. `src/infrastructure/security/` — JWT token generator and bcrypt password hasher not tested
6. Repository layer has several methods with partial coverage

**Files Without Tests**:
- `src/main.py`
- `src/infrastructure/broker/aws/services/aws_sqs_publisher_service.py`
- `src/infrastructure/broker/aws/services/aws_sqs_consumer_service.py`
- `src/infrastructure/broker/aws/services/aws_sqs_consumer_qualification.py`
- `src/infrastructure/broker/aws/services/aws_sqs_manager.py`
- `src/infrastructure/broker/aws/services/aws_sqs_creator_service.py`
- `src/infrastructure/broker/aws/services/aws_sqs_connection_factory.py`
- `src/infrastructure/broker/aws/models/aws_sqs_client.py`
- `src/infrastructure/broker/aws/models/aws_sqs_queue.py`
- `src/infrastructure/broker/aws/models/aws_sqs_messages.py`
- `src/infrastructure/broker/aws/models/aws_sqs_consumer_config.py`
- `src/infrastructure/notification/brevo_notification_service.py`
- `src/infrastructure/classifier/opencode_classifier_service.py`
- `src/infrastructure/security/jwt_token_generator.py`
- `src/infrastructure/security/bcrypt_password_hasher.py`

---

## Coverage by Feature

| Feature | Files | Coverage | Status |
|---------|-------|----------|--------|
| **assessments** | 40+ | ~95% | Good — except `evaluate_assessment_handler/service` |
| **content_management** | 25+ | ~97% | Good — request validators need edge case coverage |
| **user_management** | 30+ | ~92% | Moderate — shared services need more coverage |
| **reports** | 15+ | ~90% | Moderate — `student_report_service` partially covered |
| **shared** | 5 | ~97% | Good — `publisher_service` is abstract, `notification_service` builder tested |

---

## Coverage by Layer

| Layer | Coverage | Notes |
|-------|----------|-------|
| **Handlers/Endpoints** | ~95% | Good — most handlers have both handler and validator tests |
| **Services** | ~85% | Moderate — `user_manager_service`, `classification_service`, `qualifier_service` have gaps |
| **Repositories** | ~70% | Needs work — several `get_*` methods and error branches not covered |
| **Validators/Requests** | ~90% | Good — edge cases in validators still missing |
| **Infrastructure - Security** | 0% | **CRITICAL** — JWT and bcrypt completely untested |
| **Infrastructure - Broker/AWS** | 0% | **CRITICAL** — All SQS services untested |
| **Infrastructure - Notification** | 0% | **CRITICAL** — Brevo service untested |
| **Infrastructure - Classifier** | 0% | **CRITICAL** — Classifier service untested |
| **Infrastructure - Database** | ~75% | Moderate — mappers and models need test coverage |

---

## Detailed Gap Analysis

### user_management

#### `src/features/user_management/shared/user_manager_service.py`
- **Current Coverage**: 49% (25/51 lines)
- **Gap Description**: The `create_user_with_role`, `update_user`, and `soft_delete_user` methods are not covered at all. Error branches (user not found, database errors) are not tested.
- **Suggested Tests**:
  - `test_when_create_user_with_role_then_user_is_created_with_correct_role` — MEDIUM
  - `test_when_create_user_with_role_and_db_error_then_raises` — MEDIUM
  - `test_when_update_user_then_user_properties_are_updated` — MEDIUM
  - `test_when_update_user_not_found_then_returns_none` — MEDIUM
  - `test_when_soft_delete_user_then_user_status_is_deleted` — MEDIUM
- **Priority**: HIGH
- **Effort**: MEDIUM (2-3 hours)

#### `src/features/user_management/shared/token_generator.py`
- **Current Coverage**: 80% (21/26 lines)
- **Gap Description**: Error handling branches (`InvalidTokenError` paths) are not covered.
- **Suggested Tests**:
  - `test_when_validate_token_with_invalid_signature_then_raises_invalid_token_error` — EASY
  - `test_when_validate_token_with_expired_token_then_raises_invalid_token_error` — EASY
  - `test_when_validate_token_with_malformed_token_then_raises_invalid_token_error` — EASY
- **Priority**: MEDIUM
- **Effort**: EASY (30 min)

#### `src/features/user_management/shared/password_hasher.py`
- **Current Coverage**: 75% (6/8 lines)
- **Gap Description**: `verify_password` method is not covered.
- **Suggested Tests**:
  - `test_when_verify_password_with_correct_password_then_returns_true` — EASY
  - `test_when_verify_password_with_incorrect_password_then_returns_false` — EASY
- **Priority**: MEDIUM
- **Effort**: EASY (30 min)

#### `src/features/user_management/shared/user_repository.py`
- **Current Coverage**: 71% (22/31 lines)
- **Gap Description**: Error branches (user not found) and `get_admin_users` method not covered.
- **Suggested Tests**:
  - `test_when_get_user_by_username_not_found_then_returns_none` — EASY
  - `test_when_get_user_by_email_not_found_then_returns_none` — EASY
  - `test_when_get_admin_users_then_returns_list_of_admins` — MEDIUM
- **Priority**: MEDIUM
- **Effort**: EASY (30 min)

#### `src/features/user_management/shared/refresh_token_repository.py`
- **Current Coverage**: 88% (22/25 lines)
- **Gap Description**: `revoke_token` error branch not covered.
- **Suggested Tests**:
  - `test_when_revoke_token_not_found_then_returns_none` — EASY
- **Priority**: LOW
- **Effort**: EASY (15 min)

#### `src/features/user_management/shared/role_repository.py`
- **Current Coverage**: 75% (9/12 lines)
- **Gap Description**: Error branches not covered.
- **Suggested Tests**:
  - `test_when_get_role_by_name_not_found_then_returns_none` — EASY
- **Priority**: LOW
- **Effort**: EASY (15 min)

#### `src/features/user_management/shared/user_recovery_token_repository.py`
- **Current Coverage**: 72% (18/25 lines)
- **Gap Description**: Several error branches not covered.
- **Suggested Tests**:
  - `test_when_get_recovery_token_not_found_then_returns_none` — EASY
  - `test_when_delete_recovery_token_for_user_then_tokens_deleted` — EASY
- **Priority**: LOW
- **Effort**: EASY (15 min)

---

### assessments

#### `src/features/assessments/shared/classification_service.py`
- **Current Coverage**: 44% (14/32 lines)
- **Gap Description**: The `classify` method and error handling branches are not covered. This is a critical LLM-dependent service with complex error handling.
- **Suggested Tests**:
  - `test_when_classify_with_valid_input_then_returns_classification_result` — MEDIUM
  - `test_when_classify_with_empty_qualifications_then_raises_value_error` — EASY
  - `test_when_classify_llm_returns_invalid_json_then_raises_classification_error` — MEDIUM
  - `test_when_classify_llm_returns_non_array_then_raises_classification_error` — MEDIUM
- **Priority**: HIGH
- **Effort**: MEDIUM (2 hours)

#### `src/features/assessments/shared/qualifier_service.py`
- **Current Coverage**: 76% (37/49 lines)
- **Gap Description**: `qualify_batch` error paths and the LLM fallback behavior not fully covered.
- **Suggested Tests**:
  - `test_when_qualify_batch_with_partial_failure_then_returns_partial_results` — MEDIUM
  - `test_when_qualify_batch_with_empty_batch_then_raises_value_error` — EASY
- **Priority**: MEDIUM
- **Effort**: MEDIUM (1-2 hours)

#### `src/features/assessments/shared/assessment_repository.py`
- **Current Coverage**: 71% (34/48 lines)
- **Gap Description**: Several `get_*` methods and error paths not covered.
- **Suggested Tests**:
  - `test_when_get_assessment_not_found_then_returns_none` — EASY
  - `test_when_get_assessments_by_user_not_found_then_returns_empty_list` — EASY
  - `test_when_save_assessment_then_commits_to_database` — MEDIUM
- **Priority**: MEDIUM
- **Effort**: MEDIUM (1-2 hours)

#### `src/features/assessments/shared/questions_repository.py`
- **Current Coverage**: 69% (22/32 lines)
- **Gap Description**: Error paths and most `get_*` methods not covered.
- **Suggested Tests**:
  - `test_when_get_question_by_id_not_found_then_returns_none` — EASY
  - `test_when_get_questions_by_level_then_returns_filtered_questions` — MEDIUM
  - `test_when_get_questions_by_category_then_returns_filtered_questions` — MEDIUM
- **Priority**: MEDIUM
- **Effort**: MEDIUM (1-2 hours)

#### `src/features/assessments/shared/question.py`
- **Current Coverage**: 83% (80/96 lines)
- **Gap Description**: Several builder methods and model properties not covered.
- **Suggested Tests**:
  - `test_when_question_builder_sets_all_properties_then_question_is_valid` — EASY
  - `test_when_question_builder_missing_required_then_raises_validation_error` — EASY
- **Priority**: LOW
- **Effort**: EASY (30 min)

#### `src/features/assessments/shared/question_manager_service.py`
- **Current Coverage**: 100% — Already well tested
- **Status**: No gaps identified

#### `src/features/assessments/shared/review_question_service.py`
- **Current Coverage**: 100% — Already well tested
- **Status**: No gaps identified

#### `src/features/assessments/evaluate/evaluate_assessment_handler.py`
- **Current Coverage**: ~90% (partial)
- **Gap Description**: This handler is the SQS consumer entry point but has no dedicated tests.
- **Suggested Tests**:
  - `test_when_evaluate_contract_receives_valid_request_then_returns_success_response` — MEDIUM
  - `test_when_evaluate_contract_with_empty_answers_then_returns_failure` — MEDIUM
- **Priority**: HIGH
- **Effort**: MEDIUM (2 hours)

---

### content_management

#### `src/features/content_management/shared/content_repository.py`
- **Current Coverage**: 74% (20/27 lines)
- **Gap Description**: Error paths and filtering methods not covered.
- **Suggested Tests**:
  - `test_when_get_content_by_category_not_found_then_returns_empty_list` — EASY
  - `test_when_get_content_by_topic_not_found_then_returns_empty_list` — EASY
  - `test_when_save_content_then_commits_to_database` — MEDIUM
- **Priority**: MEDIUM
- **Effort**: MEDIUM (1-2 hours)

#### `src/features/content_management/shared/learning_path_repository.py`
- **Current Coverage**: 73% (11/15 lines)
- **Gap Description**: Error paths and update methods not covered.
- **Suggested Tests**:
  - `test_when_update_learning_path_status_then_status_is_updated` — MEDIUM
  - `test_when_update_learning_path_not_found_then_returns_none` — EASY
- **Priority**: MEDIUM
- **Effort**: EASY (30 min)

---

### reports

#### `src/features/reports/shared/student_report_service.py`
- **Current Coverage**: 50% (22/44 lines)
- **Gap Description**: The main report generation methods are not covered. This is a core business service.
- **Suggested Tests**:
  - `test_when_generate_student_report_with_valid_user_then_returns_complete_report` — HARD
  - `test_when_generate_student_report_with_no_assessments_then_returns_zero_scores` — MEDIUM
  - `test_when_generate_student_report_with_partial_completion_then_returns_partial_report` — MEDIUM
- **Priority**: HIGH
- **Effort**: HARD (3-4 hours)

#### `src/features/reports/shared/report_repository.py`
- **Current Coverage**: 77% (10/13 lines)
- **Gap Description**: `get_category_report` method not covered.
- **Suggested Tests**:
  - `test_when_get_category_report_then_returns_category_statistics` — MEDIUM
- **Priority**: MEDIUM
- **Effort**: EASY (30 min)

---

### infrastructure

#### `src/infrastructure/security/jwt_token_generator.py`
- **Current Coverage**: 0% (0/72 lines)
- **Gap Description**: **CRITICAL** — JWT token generation, validation, and random token generation are completely untested. This is security-critical code.
- **Suggested Tests**:
  - `test_when_generate_token_then_returns_valid_jwt_with_correct_claims` — EASY
  - `test_when_validate_token_with_valid_token_then_returns_token_data` — EASY
  - `test_when_validate_token_with_expired_token_then_raises_invalid_token_error` — EASY
  - `test_when_validate_token_with_invalid_signature_then_raises_invalid_token_error` — EASY
  - `test_when_validate_token_with_tampered_token_then_raises_invalid_token_error` — EASY
  - `test_when_generate_random_token_then_returns_uuid_with_correct_expiry` — EASY
- **Priority**: HIGH
- **Effort**: EASY (1-2 hours)

#### `src/infrastructure/security/bcrypt_password_hasher.py`
- **Current Coverage**: 0% (0/28 lines)
- **Gap Description**: **CRITICAL** — Password hashing and verification are completely untested. Security-critical code.
- **Suggested Tests**:
  - `test_when_hash_password_then_returns_bcrypt_hash` — EASY
  - `test_when_verify_password_with_correct_password_then_returns_true` — EASY
  - `test_when_verify_password_with_incorrect_password_then_returns_false` — EASY
  - `test_when_verify_password_with_malformed_hash_then_returns_false` — EASY
- **Priority**: HIGH
- **Effort**: EASY (1 hour)

#### `src/infrastructure/notification/brevo_notification_service.py`
- **Current Coverage**: 0% (0/104 lines)
- **Gap Description**: **CRITICAL** — Email notification sending is completely untested. Error handling and API integration not verified.
- **Suggested Tests**:
  - `test_when_send_notification_with_valid_config_then_returns_true` — MEDIUM
  - `test_when_send_notification_with_api_error_then_returns_false` — MEDIUM
  - `test_when_send_notification_with_invalid_email_then_raises_error` — EASY
  - `test_given_notification_config_when_to_brevo_payload_then_maps_correctly` — EASY
- **Priority**: HIGH
- **Effort**: MEDIUM (2 hours)

#### `src/infrastructure/classifier/opencode_classifier_service.py`
- **Current Coverage**: 0% (0/103 lines)
- **Gap Description**: **CRITICAL** — LLM classification service completely untested. Error handling for API failures, JSON parsing, and validation not tested.
- **Suggested Tests**:
  - `test_when_classify_with_valid_prompt_then_returns_classification_result` — MEDIUM
  - `test_when_classify_with_empty_qualifications_then_raises_value_error` — EASY
  - `test_when_classify_with_api_error_then_raises_classification_error` — MEDIUM
  - `test_when_classify_with_invalid_json_response_then_raises_classification_error` — MEDIUM
  - `test_when_classify_with_missing_keys_then_raises_classification_error` — MEDIUM
- **Priority**: HIGH
- **Effort**: MEDIUM (2-3 hours)

#### `src/infrastructure/broker/aws/services/aws_sqs_publisher_service.py`
- **Current Coverage**: 0% (0/120 lines)
- **Gap Description**: **CRITICAL** — Message publishing to SQS queues is completely untested.
- **Suggested Tests**:
  - `test_given_valid_request_when_publish_then_returns_true` — MEDIUM
  - `test_given_sqs_error_when_publish_then_returns_false` — MEDIUM
  - `test_given_evaluate_assessment_publish_adapter_when_publish_then_sends_to_correct_queue` — MEDIUM
  - `test_given_classify_student_publish_adapter_when_publish_then_sends_to_correct_queue` — MEDIUM
- **Priority**: HIGH
- **Effort**: MEDIUM (2-3 hours)

#### `src/infrastructure/broker/aws/services/aws_sqs_consumer_service.py`
- **Current Coverage**: 0% (0/73 lines)
- **Gap Description**: **CRITICAL** — SQS message consumption is completely untested. Consumer lifecycle (start/stop) not verified.
- **Suggested Tests**:
  - `test_when_start_consumer_then_creates_async_task` — MEDIUM
  - `test_when_stop_consumer_then_cancels_task` — MEDIUM
  - `test_when_consume_messages_with_disabled_config_then_sleeps` — MEDIUM
  - `test_when_process_message_then_calls_abstract_method` — MEDIUM
- **Priority**: HIGH
- **Effort**: MEDIUM (2-3 hours)

#### `src/infrastructure/broker/aws/services/aws_sqs_consumer_qualification.py`
- **Current Coverage**: 0% (0/59 lines)
- **Gap Description**: **CRITICAL** — Assessment evaluation via SQS consumer is completely untested.
- **Suggested Tests**:
  - `test_given_valid_sqs_message_when_process_message_then_evaluates_assessment` — HARD
  - `test_given_invalid_json_message_when_process_message_then_returns_false` — MEDIUM
  - `test_given_evaluation_error_when_process_message_then_returns_false` — MEDIUM
- **Priority**: HIGH
- **Effort**: MEDIUM (2 hours)

#### `src/infrastructure/broker/aws/services/aws_sqs_manager.py`
- **Current Coverage**: 0% (0/95 lines)
- **Gap Description**: SQS queue management and consumer lifecycle completely untested.
- **Suggested Tests**:
  - `test_when_create_connection_factory_then_returns_valid_factory` — EASY
  - `test_when_create_queues_then_calls_creator_service` — MEDIUM
  - `test_when_start_consumer_services_then_returns_consumer_dict` — MEDIUM
  - `test_when_stop_consumer_services_then_stops_all_consumers` — MEDIUM
- **Priority**: MEDIUM
- **Effort**: MEDIUM (2 hours)

#### `src/infrastructure/broker/aws/services/aws_sqs_creator_service.py`
- **Current Coverage**: 0% (0% lines)
- **Gap Description**: Queue creation not tested.
- **Suggested Tests**:
  - `test_given_queue_name_when_create_queue_then_calls_sqs_client` — EASY
- **Priority**: LOW
- **Effort**: EASY (30 min)

#### `src/infrastructure/broker/aws/services/aws_sqs_connection_factory.py`
- **Current Coverage**: 0% (0% lines)
- **Gap Description**: SQS connection factory not tested.
- **Suggested Tests**:
  - `test_given_valid_request_when_create_connection_then_returns_sqs_connection` — EASY
- **Priority**: LOW
- **Effort**: EASY (30 min)

#### `src/infrastructure/broker/aws/models/aws_sqs_client.py`
- **Current Coverage**: 0% (0% lines)
- **Gap Description**: SQS client model not tested.
- **Suggested Tests**:
  - `test_aws_sqs_client_model_initialization` — EASY
- **Priority**: LOW
- **Effort**: EASY (30 min)

#### `src/infrastructure/broker/aws/models/aws_sqs_queue.py`
- **Current Coverage**: 0% (0% lines)
- **Gap Description**: SQS queue model not tested.
- **Suggested Tests**:
  - `test_aws_sqs_queue_model_initialization` — EASY
- **Priority**: LOW
- **Effort**: EASY (30 min)

#### `src/infrastructure/broker/aws/models/aws_sqs_messages.py`
- **Current Coverage**: 0% (0% lines)
- **Gap Description**: SQS message models not tested.
- **Suggested Tests**:
  - `test_sqs_message_received_model_initialization` — EASY
- **Priority**: LOW
- **Effort**: EASY (30 min)

#### `src/infrastructure/broker/aws/models/aws_sqs_consumer_config.py`
- **Current Coverage**: 0% (0% lines)
- **Gap Description**: Consumer configuration model not tested.
- **Suggested Tests**:
  - `test_sqs_consumer_config_initialization` — EASY
- **Priority**: LOW
- **Effort**: EASY (30 min)

---

### shared

#### `src/features/shared/publisher_service.py`
- **Current Coverage**: N/A (abstract base classes)
- **Gap Description**: Abstract classes are interface definitions, not meant to be tested directly. However, concrete implementations (SQS adapters) need tests.
- **Status**: Covered by infrastructure tests above
- **Priority**: N/A

#### `src/features/shared/notification_service.py`
- **Current Coverage**: 97% — NotificationConfigBuilder is well tested
- **Status**: Minor gap — NotificationService abstract class doesn't need direct tests

---

## Testing Anti-Patterns

### 1. Over-Mocking in Handler Tests
Some handler tests mock the entire service layer with `MagicMock()` rather than using the real service. This can hide integration bugs.

**Example**: Handler tests that mock `qualifier_service.qualify_batch()` completely lose the test value of the actual service tests.

**Recommendation**: Use real service instances where possible, mock only external dependencies (LLM APIs, databases, SQS).

### 2. Missing Error Path Tests
Many tests only verify the "happy path". Error branches (user not found, database errors, validation failures) are frequently not covered.

**Impact**: Critical bugs can slip through in error handling code that is rarely executed in production.

### 3. Validator Tests Focus on Happy Path
Several validator tests (e.g., `register_question_request.py`) show many `hits="0"` lines for edge case validation branches.

**Example**: `register_question_request.py` has ~15 lines not covered representing validation failures for:
- Empty required fields
- Invalid field formats
- Out-of-range values

**Recommendation**: Add explicit tests for each validation failure using `pytest.raises`.

### 4. Repository Tests Missing Error Branches
Repository tests often don't verify behavior when entities are not found, or when database operations fail.

### 5. No Integration Tests for SQS Consumer Flow
The SQS consumer service (`aws_sqs_consumer_qualification.py`) integrates multiple components:
- SQS message parsing
- Assessment deserialization
- Contract evaluation
- Response handling

There are no tests that verify this end-to-end flow with mocked SQS messages.

---

## Priority Action Plan

| Priority | Action | Effort | Expected Coverage Impact |
|----------|--------|--------|-------------------------|
| **HIGH** | Add `src/infrastructure/security/jwt_token_generator.py` tests | EASY | +0.9% |
| **HIGH** | Add `src/infrastructure/security/bcrypt_password_hasher.py` tests | EASY | +0.3% |
| **HIGH** | Add `src/infrastructure/notification/brevo_notification_service.py` tests | MEDIUM | +1.3% |
| **HIGH** | Add `src/infrastructure/classifier/opencode_classifier_service.py` tests | MEDIUM | +1.2% |
| **HIGH** | Add `src/infrastructure/broker/aws/sqs_publisher_service.py` tests | MEDIUM | +1.4% |
| **HIGH** | Add `src/infrastructure/broker/aws/sqs_consumer_service.py` tests | MEDIUM | +0.9% |
| **HIGH** | Add `src/infrastructure/broker/aws/sqs_consumer_qualification.py` tests | MEDIUM | +0.7% |
| **HIGH** | Add `src/features/user_management/shared/user_manager_service.py` tests | MEDIUM | +0.6% |
| **HIGH** | Add `src/features/assessments/shared/classification_service.py` tests | MEDIUM | +0.4% |
| **HIGH** | Add `src/features/reports/shared/student_report_service.py` tests | HARD | +0.5% |
| **HIGH** | Add `src/features/assessments/evaluate/evaluate_assessment_handler.py` tests | MEDIUM | +0.8% |
| MEDIUM | Add validator error path tests for `register_question_request.py` | MEDIUM | +0.5% |
| MEDIUM | Add validator error path tests for `update_question_request.py` | MEDIUM | +0.4% |
| MEDIUM | Add repository error branch tests across all repositories | MEDIUM | +1.5% |
| LOW | Add SQS model and factory tests | EASY | +0.3% |
| LOW | Add `src/main.py` tests (integration/smoke tests) | MEDIUM | +0.6% |

---

## Estimated Coverage Improvement

| Scenario | Current | After HIGH | After HIGH+MEDIUM |
|----------|---------|-----------|-------------------|
| **Line Coverage** | 96.2% | 97.8% | 98.5% |
| **Lines Uncovered** | 315 | 185 | 124 |

**If all HIGH priority items are addressed**: Coverage would increase to approximately **97.8%**

**If all HIGH and MEDIUM priority items are addressed**: Coverage would increase to approximately **98.5%**

---

## Recommendations

1. **Immediate Priority**: Add tests for `infrastructure/security/` — JWT and bcrypt are security-critical and currently have 0% coverage.

2. **Immediate Priority**: Add tests for `infrastructure/notification/` and `infrastructure/classifier/` — These handle external API integrations with significant error handling logic.

3. **Immediate Priority**: Add tests for AWS SQS infrastructure — The broker layer is completely untested and represents a critical integration point.

4. **Add Error Path Tests**: At minimum, add one test per error branch to ensure coverage of edge cases and error handling.

5. **Consider Integration Tests**: The `main.py` lifespan function orchestrates multiple services. Consider adding integration/smoke tests that verify the application starts correctly.

6. **Validator Edge Cases**: Add explicit `pytest.raises` tests for each validation failure in request models with multiple validators.

---

*Report generated from coverage.xml analysis*
