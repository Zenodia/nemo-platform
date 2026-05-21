# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Literal

import nmp.evaluator.app.evalfactory.labels as ef_labels
import nmp.evaluator.app.jobs.evalfactory.models as ef
from nemo_evaluator_sdk.values import SecretRef
from nmp.evaluator.app.evalfactory.convert import augment_online_job
from nmp.evaluator.app.evalfactory.handler import (
    BaseSystemHandler,
    JudgeModelParamsInput,
    hf_token_param,
)
from nmp.evaluator.app.jobs.evalfactory.constants import EvalFactoryModelType
from nmp.evaluator.app.values import (
    Parameter,
    SystemBenchmark,
    SystemBenchmarkJob,
    SystemBenchmarkOnlineJob,
)
from nmp.evaluator.config import settings
from pydantic import BaseModel, Field


class SimpleEvalsJudgeModelParamsInput(JudgeModelParamsInput):
    """Input class for Simple Evals judge params with additional fields."""

    backend: Literal["generic", "openai"] | None = Field(
        default=None, description="'openai' for OpenAI compatible judges; 'generic' for direct calls via aiohttp"
    )
    temperature: float | None = Field(default=None, description="Sampling temperature for judge generation.")
    top_p: float | None = Field(default=None, description="Nucleus sampling parameter for judge.")
    max_tokens: int | None = Field(default=None, description="Maximum number of output tokens for judge.")
    max_concurrent_requests: int | None = Field(
        default=None, description="Only used with generic backend, defaults to job.params.parallelism"
    )


class _BaseSimpleEvalsJudgeModelParams(BaseModel):
    backend: Literal["generic", "openai"] = Field(
        default="generic", description="'openai' for OpenAI compatible judges; 'generic' for direct calls via aiohttp"
    )
    request_timeout: int | None = Field(default=None, description="Request timeout (seconds) for judge model requests.")
    max_retries: int | None = Field(default=None, description="Maximum number of retries for failed judge requests.")
    temperature: float | None = Field(default=None, description="Sampling temperature for generation.")
    top_p: float | None = Field(default=None, description="Nucleus sampling parameter.")
    max_tokens: int | None = Field(default=None, description="Maximum number of output sequence tokens.")
    max_concurrent_requests: int | None = Field(
        default=None, description="Only used with generic backend, defaults to job.params.parallelism"
    )


class SimpleEvalsJudgeModelParams(_BaseSimpleEvalsJudgeModelParams):
    url: str
    model_id: str
    api_key: str | None
    api_key_name: str | None


simple_evals_judge_param = Parameter(
    name="judge",
    type="object",
    description="The LLM judge to use for the evaluation.",
    schema_=SimpleEvalsJudgeModelParamsInput.model_json_schema(),
)


class SimpleEvalsHandler(BaseSystemHandler):
    @classmethod
    def docker_image(cls) -> str:
        return settings.evalfactory.simple_evals

    @classmethod
    def system_benchmarks(cls) -> list[SystemBenchmark]:
        return cls._system_benchmarks

    def benchmark_job_secrets(self, job: SystemBenchmarkJob) -> dict[str, SecretRef]:
        """Job secrets for the benchmark. Returns a dictionary of environment variables to the secret reference"""
        # Special handling for Simple Evals where judge.model.api_key_secret can't be easily represented
        # by Parameter
        secrets = super().benchmark_job_secrets(job)
        judge_raw_param = job.benchmark_params.get("judge")
        if judge_raw_param:
            judge = SimpleEvalsJudgeModelParamsInput.model_validate(judge_raw_param)
            if judge.model.api_key_secret:
                secrets["judge_api_key_secret"] = judge.model.api_key_secret
        return secrets

    def augment_benchmark_job(self, job: SystemBenchmarkJob, output_dir: str) -> ef.EvaluationJob:
        self.validate_supported_benchmark_job_types(job)
        self.validate_params(job.benchmark_params, job.benchmark.required_params, job.benchmark.optional_params)
        assert isinstance(job, SystemBenchmarkOnlineJob)
        self.augment_harness_supported_model_types(job, self.SUPPORTED_MODEL_TYPE.get(job.benchmark.name))

        # Validate judge model
        if job.benchmark.name in self._require_judge:
            judge_raw_param = job.benchmark_params.get("judge")
            if not judge_raw_param:
                raise ValueError(
                    f"job.benchmark_params.judge.model is required for evaluation with benchmark {job.benchmark.name}"
                )
            judge = SimpleEvalsJudgeModelParamsInput.model_validate(judge_raw_param)
            augmented_judge = SimpleEvalsJudgeModelParams(
                **judge.model_dump(exclude_none=True, exclude={"model", "inference", "system_prompt", "reasoning"}),
                url=judge.model.url,
                model_id=judge.model.name,
                # Use the env var name (must match key in secrets() method) - the Jinja template adds the $ prefix
                api_key="judge_api_key_secret" if judge.model.api_key_secret else None,
                api_key_name="judge_api_key_secret" if judge.model.api_key_secret else None,
            )
            job.benchmark_params["judge"] = augmented_judge.model_dump(exclude_none=True)

        ef_job = augment_online_job(job, output_dir)

        # Simple Evals config type uses underscores and special casing
        # Note: We set this on the EF job config, not on the original benchmark to avoid mutating shared state
        if ef_job.config:
            config_type = job.benchmark.name.replace("-", "_")
            _benchmark_name_map = {
                "aa_aime_2024": "AA_AIME_2024",
                "aa_math_test_500": "AA_math_test_500",
                "aime_2024": "AIME_2024",
                "aime_2025": "AIME_2025",
            }
            ef_job.config.type = _benchmark_name_map.get(config_type, config_type)

        return ef_job

    _require_judge = {
        "aa-aime-2024",
        "aa-math-test-500",
        "aime-2024",
        "aime-2025",
        "math-test-500",
        "simpleqa",
    }

    _system_benchmarks = [
        SystemBenchmark(
            name="aa-aime-2024",
            description="AIME 2024 questions, math, using Artificial Analysis's setup. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_MATH),
            required_params=[simple_evals_judge_param],
            optional_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="aa-math-test-500",
            description="Open AI math test 500, using Artificial Analysis's setup. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_MATH),
            required_params=[simple_evals_judge_param],
            optional_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="aime-2024",
            description="AIME 2024 questions, math. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_MATH),
            required_params=[simple_evals_judge_param],
            optional_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="aime-2025",
            description="AIME 2025 questions, math. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_MATH),
            required_params=[simple_evals_judge_param],
            optional_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="gpqa-diamond",
            description="gpqa_diamond 0-shot CoT. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_ADVANCED_REASONING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="gpqa-extended",
            description="gpqa_extended 0-shot CoT. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_ADVANCED_REASONING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="gpqa-main",
            description="gpqa_main 0-shot CoT. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_ADVANCED_REASONING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="math-test-500",
            description="Open AI math test 500. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_MATH),
            required_params=[simple_evals_judge_param],
            optional_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-am",
            description="Global-MMLU 0-shot CoT in Amharic (am). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-ar",
            description="Global-MMLU 0-shot CoT in Arabic (ar). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-bn",
            description="Global-MMLU 0-shot CoT in Bengali (bn). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-cs",
            description="Global-MMLU 0-shot CoT in Czech (cs). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-de",
            description="Global-MMLU 0-shot CoT in German (de). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-el",
            description="Global-MMLU 0-shot CoT in Greek (el). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-en",
            description="Global-MMLU 0-shot CoT in English (en). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-es",
            description="Global-MMLU 0-shot CoT in Spanish (es). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-fa",
            description="Global-MMLU 0-shot CoT in Persian (fa). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-fil",
            description="Global-MMLU 0-shot CoT in Filipino (fil). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-fr",
            description="Global-MMLU 0-shot CoT in French (fr). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-ha",
            description="Global-MMLU 0-shot CoT in Hausa (ha). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-he",
            description="Global-MMLU 0-shot CoT in Hebrew (he). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-hi",
            description="Global-MMLU 0-shot CoT in Hindi (hi). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-id",
            description="Global-MMLU 0-shot CoT in Indonesian (id). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-ig",
            description="Global-MMLU 0-shot CoT in Igbo (ig). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-it",
            description="Global-MMLU 0-shot CoT in Italian (it). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-ja",
            description="Global-MMLU 0-shot CoT in Japanese (ja). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-ko",
            description="Global-MMLU 0-shot CoT in Korean (ko). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-ky",
            description="Global-MMLU 0-shot CoT in Kyrgyz (ky). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-lt",
            description="Global-MMLU 0-shot CoT in Lithuanian (lt). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-mg",
            description="Global-MMLU 0-shot CoT in Malagasy (mg). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-ms",
            description="Global-MMLU 0-shot CoT in Malay (ms). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-ne",
            description="Global-MMLU 0-shot CoT in Nepali (ne). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-nl",
            description="Global-MMLU 0-shot CoT in Dutch (nl). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-ny",
            description="Global-MMLU 0-shot CoT in Nyanja (ny). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-pl",
            description="Global-MMLU 0-shot CoT in Polish (pl). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-pt",
            description="Global-MMLU 0-shot CoT in Portuguese (pt). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-ro",
            description="Global-MMLU 0-shot CoT in Romanian (ro). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-ru",
            description="Global-MMLU 0-shot CoT in Russian (ru). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-si",
            description="Global-MMLU 0-shot CoT in Sinhala (si). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-sn",
            description="Global-MMLU 0-shot CoT in Shona (sn). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-so",
            description="Global-MMLU 0-shot CoT in Somali (so). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-sr",
            description="Global-MMLU 0-shot CoT in Serbian (sr). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-sv",
            description="Global-MMLU 0-shot CoT in Swedish (sv). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-sw",
            description="Global-MMLU 0-shot CoT in Swahili (sw). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-te",
            description="Global-MMLU 0-shot CoT in Telugu (te). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-tr",
            description="Global-MMLU 0-shot CoT in Turkish (tr). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-uk",
            description="Global-MMLU 0-shot CoT in Ukrainian (uk). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-vi",
            description="Global-MMLU 0-shot CoT in Vietnamese (vi). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="mmlu-yo",
            description="Global-MMLU 0-shot CoT in Yoruba (yo). Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="aime-2025-nemo",
            description="AIME 2025 questions, math, using NeMo's alignment template. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_MATH),
            optional_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="aime-2024-nemo",
            description="AIME 2024 questions, math, using NeMo's alignment template. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_MATH),
            optional_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="math-test-500-nemo",
            description="math_test_500 questions, math, using NeMo's alignment template. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_MATH),
            optional_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="gpqa-diamond-nemo",
            description="gpqa_diamond questions, reasoning, using NeMo's alignment template. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_ADVANCED_REASONING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="simpleqa",
            description="A factuality benchmark called SimpleQA that measures the ability for language models to answer short, fact-seeking questions. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("simple_evals", ef_labels.LABEL_QUESTION_ANSWERING),
            optional_params=[hf_token_param],
        ),
    ]

    SUPPORTED_MODEL_TYPE: dict[str, set[EvalFactoryModelType]] = {
        "aa-aime-2024": {EvalFactoryModelType.CHAT},  # passes. Uses judge.
        "aa-math-test-500": {EvalFactoryModelType.CHAT},  # passes. Uses judge.
        "aime-2024": {EvalFactoryModelType.CHAT},  # passes. Uses judge.
        "aime-2025": {EvalFactoryModelType.CHAT},  # passes. Uses judge.
        "gpqa-diamond": {EvalFactoryModelType.CHAT},  # gated dataset 'Idavidrein/gpqa'. passes.
        "gpqa-extended": {EvalFactoryModelType.CHAT},  # gated dataset 'Idavidrein/gpqa'. passes.
        "gpqa-main": {EvalFactoryModelType.CHAT},  # gated dataset 'Idavidrein/gpqa'. passes.
        "math-test-500": {EvalFactoryModelType.CHAT},  # passes. Uses judge.
        "mmlu-am": {EvalFactoryModelType.CHAT},  # passes. No judge.
        "mmlu-ar": {EvalFactoryModelType.CHAT},
        "mmlu-bn": {EvalFactoryModelType.CHAT},
        "mmlu-cs": {EvalFactoryModelType.CHAT},
        "mmlu-de": {EvalFactoryModelType.CHAT},
        "mmlu-el": {EvalFactoryModelType.CHAT},
        "mmlu-en": {EvalFactoryModelType.CHAT},
        "mmlu-es": {EvalFactoryModelType.CHAT},
        "mmlu-fa": {EvalFactoryModelType.CHAT},
        "mmlu-fil": {EvalFactoryModelType.CHAT},
        "mmlu-fr": {EvalFactoryModelType.CHAT},
        "mmlu-ha": {EvalFactoryModelType.CHAT},
        "mmlu-he": {EvalFactoryModelType.CHAT},
        "mmlu-hi": {EvalFactoryModelType.CHAT},
        "mmlu-id": {EvalFactoryModelType.CHAT},
        "mmlu-ig": {EvalFactoryModelType.CHAT},
        "mmlu-it": {EvalFactoryModelType.CHAT},
        "mmlu-ja": {EvalFactoryModelType.CHAT},
        "mmlu-ko": {EvalFactoryModelType.CHAT},
        "mmlu-ky": {EvalFactoryModelType.CHAT},
        "mmlu-lt": {EvalFactoryModelType.CHAT},
        "mmlu-mg": {EvalFactoryModelType.CHAT},
        "mmlu-ms": {EvalFactoryModelType.CHAT},
        "mmlu-ne": {EvalFactoryModelType.CHAT},
        "mmlu-nl": {EvalFactoryModelType.CHAT},
        "mmlu-ny": {EvalFactoryModelType.CHAT},
        "mmlu-pl": {EvalFactoryModelType.CHAT},
        "mmlu-pt": {EvalFactoryModelType.CHAT},
        "mmlu-ro": {EvalFactoryModelType.CHAT},
        "mmlu-ru": {EvalFactoryModelType.CHAT},
        "mmlu-si": {EvalFactoryModelType.CHAT},
        "mmlu-sn": {EvalFactoryModelType.CHAT},
        "mmlu-so": {EvalFactoryModelType.CHAT},
        "mmlu-sr": {EvalFactoryModelType.CHAT},
        "mmlu-sv": {EvalFactoryModelType.CHAT},
        "mmlu-sw": {EvalFactoryModelType.CHAT},
        "mmlu-te": {EvalFactoryModelType.CHAT},
        "mmlu-tr": {EvalFactoryModelType.CHAT},
        "mmlu-uk": {EvalFactoryModelType.CHAT},
        "mmlu-vi": {EvalFactoryModelType.CHAT},
        "mmlu-yo": {EvalFactoryModelType.CHAT},
        "aime-2025-nemo": {EvalFactoryModelType.CHAT},  # passes. No judge.
        "aime-2024-nemo": {EvalFactoryModelType.CHAT},  # passes. No judge.
        "math-test-500-nemo": {EvalFactoryModelType.CHAT},  # passes. No judge.
        "gpqa-diamond-nemo": {EvalFactoryModelType.CHAT},  # gated dataset 'Idavidrein/gpqa'
        "simpleqa": {EvalFactoryModelType.CHAT},  # passes. Uses judge.
    }
