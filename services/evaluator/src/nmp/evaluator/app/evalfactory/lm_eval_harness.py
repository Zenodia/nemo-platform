# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import nmp.evaluator.app.evalfactory.labels as ef_labels
import nmp.evaluator.app.jobs.evalfactory.models as ef
from nmp.evaluator.app.evalfactory.convert import augment_online_job
from nmp.evaluator.app.evalfactory.handler import (
    BaseSystemHandler,
    harness_model_type_param,
    hf_token_param,
)
from nmp.evaluator.app.jobs.evalfactory.constants import EvalFactoryModelType
from nmp.evaluator.app.values import Parameter, SystemBenchmark, SystemBenchmarkJob, SystemBenchmarkOnlineJob
from nmp.evaluator.config import settings

# Required tokenizer param for completions-based loglikelihood tasks
tokenizer_param = Parameter(
    name="tokenizer",
    type="string",
    description=(
        "HuggingFace tokenizer for computing context lengths in loglikelihood tasks "
        "(e.g. meta-llama/Llama-3.2-3B-Instruct). Required for completions-based benchmarks."
    ),
)

# Optional params for all LM Eval Harness benchmarks
lm_eval_harness_params = [
    harness_model_type_param,
    Parameter(
        name="tokenizer_backend", type="string", description="The backend to fetch the tokenizer (e.g. huggingface)"
    ),
    Parameter(name="tokenized_requests", type="boolean"),
    Parameter(name="downsampling_ratio", type="number"),
]


class LMEvalHarnessHandler(BaseSystemHandler):
    @classmethod
    def docker_image(cls) -> str:
        return settings.evalfactory.lm_eval_harness

    @classmethod
    def system_benchmarks(cls) -> list[SystemBenchmark]:
        return cls._system_benchmarks

    def augment_benchmark_job(self, job: SystemBenchmarkJob, output_dir: str) -> ef.EvaluationJob:
        self.validate_supported_benchmark_job_types(job)
        self.validate_params(job.benchmark_params, job.benchmark.required_params, job.benchmark.optional_params)
        self.augment_harness_supported_model_types(job, self.SUPPORTED_MODEL_TYPE.get(job.benchmark.name))

        if not isinstance(job, SystemBenchmarkOnlineJob):
            raise ValueError(
                f"LM Eval Harness benchmarks require a SystemBenchmarkOnlineJob (with model), "
                f"but got {type(job).__name__}. Use an online benchmark spec for '{job.benchmark.name}'."
            )
        ef_job = augment_online_job(job, output_dir)

        # LM Eval Harness config type uses underscores instead of hyphens
        # Note: We set this on the EF job config, not on the original benchmark to avoid mutating shared state
        if ef_job.config:
            ef_job.config.type = job.benchmark.name.replace("-", "_")

        return ef_job

    _system_benchmarks = [
        SystemBenchmark(
            name="gpqa",
            description="Advanced Reasoning. The GPQA (Graduate-Level Google-Proof Q&A) benchmark is a challenging dataset of 448 multiple-choice questions in biology, physics, and chemistry. It is designed to be extremely difficult for both humans and AI, ensuring that questions cannot be easily answered using web searches. Compatible with completions model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_ADVANCED_REASONING),
            required_params=[hf_token_param, tokenizer_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="gpqa-diamond-cot",
            description="Advanced Reasoning (GPQA-Diamond-CoT). The GPQA (Graduate-Level Google-Proof Q&A) benchmark is a challenging dataset of 448 multiple-choice questions in biology, physics, and chemistry. It is designed to be extremely difficult for both humans and AI, ensuring that questions cannot be easily answered using web searches. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_ADVANCED_REASONING),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="ifeval",
            description='Instruction Following: IFEval is a dataset designed to test a model\'s ability to follow explicit instructions, such as "include keyword x" or "use format y." The focus is on the model\'s adherence to formatting instructions rather than the content generated, allowing for the use of strict and rigorous benchmarks. Compatible with chat model endpoint.',
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_INSTRUCTION_FOLLOWING),
            required_params=[hf_token_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="mmlu",
            description="The MMLU (Massive Multitask Language Understanding) benchmark is designed to measure the knowledge acquired during pretraining by evaluating models in zero-shot and few-shot settings. It covers 57 subjects across various fields, testing both world knowledge and problem-solving abilities. Compatible with completions model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param, tokenizer_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="mmlu-instruct",
            description="The MMLU (Massive Multitask Language Understanding) benchmark is designed to measure the knowledge acquired during pretraining by evaluating models in zero-shot and few-shot settings. It covers 57 subjects across various fields, testing both world knowledge and problem-solving abilities. This variant defaults to zero-shot evaluation and instructs the model to produce a single letter response. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="mmlu-pro",
            description="MMLU-Pro: MMLU-Pro is a refined version of the MMLU dataset, which has been a standard for multiple-choice knowledge assessment. Recent research identified issues with the original MMLU, such as noisy data (some unanswerable questions) and decreasing difficulty due to advances in model capabilities and increased data contamination. MMLU-Pro addresses these issues by presenting models with 10 choices instead of 4, requiring reasoning on more questions, and undergoing expert review to reduce noise. As a result, MMLU-Pro is of higher quality and currently more challenging than the original. Compatible with completions model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param, tokenizer_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="mmlu-pro-instruct",
            description="MMLU-Pro-instruct: MMLU-Pro is a refined version of the MMLU dataset, which has been a standard for multiple-choice knowledge assessment. Recent research identified issues with the original MMLU, such as noisy data (some unanswerable questions) and decreasing difficulty due to advances in model capabilities and increased data contamination. MMLU-Pro addresses these issues by presenting models with 10 choices instead of 4, requiring reasoning on more questions, and undergoing expert review to reduce noise. As a result, MMLU-Pro is of higher quality and currently more challenging than the original. This variant applies a chat template and defaults to zero-shot evaluation. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="mmlu-redux",
            description="MMLU-Redux is a subset of 3,000 manually re-annotated questions across 30 MMLU subjects. Compatible with completions model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param, tokenizer_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="mmlu-redux-instruct",
            description="MMLU-Redux is a subset of 3,000 manually re-annotated questions across 30 MMLU subjects. This variant applies a chat template and defaults to zero-shot evaluation. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="gsm8k",
            description="GSM8K: The GSM8K benchmark evaluates the arithmetic reasoning of large language models using 1,319 grade school math word problems. Compatible with completions model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_MATH),
            required_params=[hf_token_param, tokenizer_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="gsm8k-cot-instruct",
            description="GSM8K-instruct: The GSM8K benchmark evaluates the arithmetic reasoning of large language models using 1,319 grade school math word problems. This variant defaults to chain-of-thought zero-shot evaluation with custom instructions. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_MATH),
            required_params=[hf_token_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="mgsm",
            description="MGSM: The Multilingual Grade School Math (MGSM) benchmark evaluates the reasoning abilities of large language models in multilingual settings. It consists of 250 grade-school math problems from the GSM8K dataset, translated into ten diverse languages, and tests models using chain-of-thought prompting. Compatible with completions model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_MATH),
            required_params=[hf_token_param, tokenizer_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="mgsm-cot",
            description="MGSM-CoT: The Multilingual Grade School Math (MGSM) benchmark evaluates the reasoning abilities of large language models in multilingual settings. It consists of 250 grade-school math problems from the GSM8K dataset, translated into ten diverse languages, and tests models using chain-of-thought prompting. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_MATH),
            required_params=[hf_token_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="wikilingua",
            description="The WikiLingua benchmark is a large-scale, multilingual dataset designed for evaluating cross-lingual abstractive summarization systems. It includes approximately 770,000 article-summary pairs in 18 languages, extracted from WikiHow, with gold-standard alignments created by matching images used to describe each how-to step in an article. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_LANGUAGE_UNDERSTANDING),
            required_params=[hf_token_param],
            optional_params=lm_eval_harness_params,
        ),
        # Exclude benchmarks until NIM supports logprobs or we identify hosted models that support it for testing and documentation
        # SystemBenchmark(
        #     name="winogrande",
        #     description="WinoGrande is a collection of 44k problems, inspired by Winograd Schema Challenge (Levesque, Davis, and Morgenstern 2011), but adjusted to improve the scale and robustness against the dataset-specific bias. Formulated as a fill-in-a-blank task with binary options, the goal is to choose the right option for a given sentence which requires commonsense reasoning. Compatible with completions model endpoint.",
        #     labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_ADVANCED_REASONING),
        #     required_params=[hf_token_param, tokenizer_param],
        #     optional_params=[
        #         *lm_eval_harness_params,
        #         Parameter(name="num_fewshot", type="integer", description="Number of examples in few-shot context."),
        #     ],
        # ),
        # SystemBenchmark(
        #     name="arc-challenge",
        #     description='The ARC dataset consists of 7,787 science exam questions drawn from a variety of sources, including science questions provided under license by a research partner affiliated with AI2. These are text-only, English language exam questions that span several grade levels as indicated in the files. Each question has a multiple choice structure (typically 4 answer options). The questions are sorted into a Challenge Set of 2,590 "hard" questions (those that both a retrieval and a co-occurrence method fail to answer correctly) and an Easy Set of 5,197 questions. Compatible with completions model endpoint.',
        #     labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_ADVANCED_REASONING),
        #     required_params=[hf_token_param, tokenizer_param],
        #     optional_params=lm_eval_harness_params,
        # ),
        # SystemBenchmark(
        #     name="arc-challenge-chat",
        #     description='ARC Challenge-instruct: The ARC dataset consists of 7,787 science exam questions drawn from a variety of sources, including science questions provided under license by a research partner affiliated with AI2. These are text-only, English language exam questions that span several grade levels as indicated in the files. Each question has a multiple choice structure (typically 4 answer options). The questions are sorted into a Challenge Set of 2,590 "hard" questions (those that both a retrieval and a co-occurrence method fail to answer correctly) and an Easy Set of 5,197 questions. This variant applies a chat template and defaults to zero-shot evaluation. Compatible with chat model endpoint.',
        #     labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_ADVANCED_REASONING),
        #     required_params=[hf_token_param],
        #     optional_params=lm_eval_harness_params,
        # ),
        # SystemBenchmark(
        #     name="hellaswag",
        #     description="The HellaSwag benchmark tests a language model's commonsense reasoning by having it choose the most logical ending for a given story. Compatible with completions model endpoint.",
        #     labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_ADVANCED_REASONING),
        #     required_params=[hf_token_param, tokenizer_param],
        #     optional_params=[
        #         *lm_eval_harness_params,
        #         Parameter(name="num_fewshot", type="integer", description="Number of examples in few-shot context."),
        #     ],
        # ),
        # SystemBenchmark(
        #     name="truthfulqa",
        #     description="The TruthfulQA benchmark measures the truthfulness of language models in generating answers to questions. It consists of 817 questions across 38 categories, such as health, law, finance, and politics, designed to test whether models can avoid generating false answers that mimic common human misconceptions. Compatible with completions model endpoint.",
        #     labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_QUESTION_ANSWERING),
        #     required_params=[hf_token_param, tokenizer_param],
        #     optional_params=lm_eval_harness_params,
        # ),
        SystemBenchmark(
            name="bbh",
            description="The BIG-Bench Hard (BBH) benchmark is a part of the BIG-Bench evaluation suite, focusing on 23 particularly difficult tasks that current language models struggle with. These tasks require complex, multi-step reasoning, and the benchmark evaluates models using few-shot learning and chain-of-thought prompting techniques. Compatible with completions model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_ADVANCED_REASONING),
            required_params=[hf_token_param, tokenizer_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="bbh-instruct",
            description="The BIG-Bench Hard (BBH) benchmark is a part of the BIG-Bench evaluation suite, focusing on 23 particularly difficult tasks that current language models struggle with. These tasks require complex, multi-step reasoning, and the benchmark evaluates models using few-shot learning and chain-of-thought prompting techniques. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_ADVANCED_REASONING),
            required_params=[hf_token_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="musr",
            description="The MuSR (Multistep Soft Reasoning) benchmark evaluates the reasoning capabilities of large language models through complex, multistep tasks specified in natural language narratives. It introduces sophisticated natural language and complex reasoning challenges to test the limits of chain-of-thought prompting. Compatible with completions model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_ADVANCED_REASONING),
            required_params=[hf_token_param, tokenizer_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="frames-naive",
            description="Frames Naive uses the prompt as input without additional context. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_RAG),
            required_params=[hf_token_param],
        ),
        SystemBenchmark(
            name="frames-naive-with-links",
            description="Frames Naive with Links provides the prompt and relevant Wikipedia article links. Compatible with chat model endpoint.",
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_RAG),
            required_params=[hf_token_param],
            optional_params=lm_eval_harness_params,
        ),
        SystemBenchmark(
            name="frames-oracle",
            description='Frames Oracle (long context) provides prompts and relevant text from curated and processed Wikipedia articles from "parasail-ai/frames-benchmark-wikipedia. Compatible with chat model endpoint.',
            labels=ef_labels.new_labels("lm_eval_harness", ef_labels.LABEL_RAG),
            required_params=[hf_token_param],
            optional_params=lm_eval_harness_params,
        ),
    ]

    SUPPORTED_MODEL_TYPE: dict[str, set[EvalFactoryModelType]] = {
        "mmlu": {EvalFactoryModelType.COMPLETIONS},
        "mmlu-instruct": {EvalFactoryModelType.CHAT},
        "ifeval": {EvalFactoryModelType.CHAT},
        "mmlu-pro": {EvalFactoryModelType.COMPLETIONS},
        "mmlu-pro-instruct": {EvalFactoryModelType.CHAT},
        "mmlu-redux": {EvalFactoryModelType.COMPLETIONS},
        "mmlu-redux-instruct": {EvalFactoryModelType.CHAT},
        "gsm8k": {EvalFactoryModelType.COMPLETIONS},
        "gsm8k-cot-instruct": {EvalFactoryModelType.CHAT},
        "mgsm": {EvalFactoryModelType.COMPLETIONS},
        "mgsm-cot": {EvalFactoryModelType.CHAT},
        "wikilingua": {EvalFactoryModelType.CHAT},
        # Exclude benchmarks until NIM supports logprobs or we identify hosted models that support it for testing and documentation
        # "winogrande": {EvalFactoryModelType.COMPLETIONS},
        # "arc-challenge": {EvalFactoryModelType.COMPLETIONS},
        # "arc-challenge-chat": {EvalFactoryModelType.CHAT},
        # "hellaswag": {EvalFactoryModelType.COMPLETIONS},
        # "truthfulqa": {EvalFactoryModelType.COMPLETIONS},
        "bbh": {EvalFactoryModelType.COMPLETIONS},
        "bbh-instruct": {EvalFactoryModelType.CHAT},
        "musr": {EvalFactoryModelType.COMPLETIONS},
        "gpqa": {EvalFactoryModelType.COMPLETIONS},
        "gpqa-diamond-cot": {EvalFactoryModelType.CHAT},
        "frames-naive": {EvalFactoryModelType.CHAT},
        "frames-naive-with-links": {EvalFactoryModelType.CHAT},
        "frames-oracle": {EvalFactoryModelType.CHAT},
    }
