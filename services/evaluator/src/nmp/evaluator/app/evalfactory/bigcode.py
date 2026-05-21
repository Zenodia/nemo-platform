# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import nmp.evaluator.app.jobs.evalfactory.models as ef
from nmp.evaluator.app.evalfactory.convert import augment_online_job
from nmp.evaluator.app.evalfactory.handler import (
    BaseSystemHandler,
    harness_model_type_param,
    hf_token_param,
)
from nmp.evaluator.app.evalfactory.labels import LABEL_CODE, new_labels
from nmp.evaluator.app.jobs.evalfactory.constants import EvalFactoryModelType
from nmp.evaluator.app.values import Parameter, SystemBenchmark, SystemBenchmarkJob, SystemBenchmarkOnlineJob
from nmp.evaluator.config import settings

# Common parameters for code generation benchmarks
n_samples_param = Parameter(
    name="n_samples",
    type="integer",
    description="Number of code samples to generate per problem for pass@k benchmarks (default: 10).",
    default=10,
)

do_sample_param = Parameter(
    name="do_sample",
    type="boolean",
    description="Whether to use sampling (True) or greedy decoding (False) for code generation (default: True).",
    default=True,
)

# Shared params for all BigCode benchmarks
bigcode_eval_harness_params = [hf_token_param, harness_model_type_param, n_samples_param, do_sample_param]

_benchmark_name_map = {
    "humaneval-instruct": "humaneval_instruct",
    "mbppplus-nemo": "mbppplus_nemo",
}


class BigCodeEvaluationHarnessHandler(BaseSystemHandler):
    @classmethod
    def docker_image(cls) -> str:
        return settings.evalfactory.bigcode_evaluation_harness

    @classmethod
    def system_benchmarks(cls) -> list[SystemBenchmark]:
        return cls._system_benchmarks

    def augment_benchmark_job(self, job: SystemBenchmarkJob, output_dir: str) -> ef.EvaluationJob:
        self.validate_supported_benchmark_job_types(job)
        self.validate_params(job.benchmark_params, job.benchmark.required_params, job.benchmark.optional_params)
        self.augment_harness_supported_model_types(job, self.SUPPORTED_MODEL_TYPE.get(job.benchmark.name))

        if not isinstance(job, SystemBenchmarkOnlineJob):
            raise ValueError(
                f"BigCode benchmarks require a SystemBenchmarkOnlineJob (with model), "
                f"but got {type(job).__name__}. Use an online benchmark spec for '{job.benchmark.name}'."
            )
        ef_job = augment_online_job(job, output_dir)

        # BigCode config type may need name mapping
        # Note: We set this on the EF job config, not on the original benchmark to avoid mutating shared state
        if ef_job.config:
            ef_job.config.type = _benchmark_name_map.get(job.benchmark.name, job.benchmark.name)

        return ef_job

    _system_benchmarks = [
        SystemBenchmark(
            name="humaneval",
            description="HumanEval is used to measure functional correctness for synthesizing programs from docstrings. It consists of 164 original programming problems, assessing language comprehension, algorithms, and simple mathematics, with some comparable to simple software interview questions. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="humaneval-instruct",
            description="InstructHumanEval is a modified version of OpenAI HumanEval. For a given prompt, we extracted its signature, its docstring as well as its header to create a flexing setting which would allow to evaluation instruction-tuned LLM. The delimiters used in the instruction-tuning procedure can be use to build and instruction that would allow the model to elicit its best capabilities. Compatible with chat model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="humanevalplus",
            description="HumanEvalPlus is a modified version of HumanEval containing 80x more test cases. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="mbpp",
            description="MBPP consists of Python programming problems, designed to be solvable by entry level programmers, covering programming fundamentals, standard library functionality, and so on. Each problem consists of a task description, code solution and 3 automated test cases. Compatible with both chat and completions model endpoints.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="mbppplus",
            description="MBPP+ is a modified version of MBPP containing 35x more test cases. Compatible with both chat and completions model endpoints.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="mbppplus-nemo",
            description="MBPP+NeMo is a modified version of MBPP+ that uses the NeMo alignment prompt template. Compatible with chat model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-clj",
            description="MultiPL-E Clojure coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-cpp",
            description="MultiPL-E C++ coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-cs",
            description="MultiPL-E C# coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-d",
            description="MultiPL-E D coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-elixir",
            description="MultiPL-E Elixir coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-go",
            description="MultiPL-E Go coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-hs",
            description="MultiPL-E Haskell coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-java",
            description="MultiPL-E Java coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-jl",
            description="MultiPL-E Julia coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-js",
            description="MultiPL-E JavaScript coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-lua",
            description="MultiPL-E Lua coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-ml",
            description="MultiPL-E ML/OCaml coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-php",
            description="MultiPL-E PHP coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-pl",
            description="MultiPL-E Perl coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-r",
            description="MultiPL-E R coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-rb",
            description="MultiPL-E Ruby coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-rkt",
            description="MultiPL-E Racket coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-rs",
            description="MultiPL-E Rust coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-scala",
            description="MultiPL-E Scala coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-sh",
            description="MultiPL-E Bash/Shell coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        SystemBenchmark(
            name="multiple-swift",
            description="MultiPL-E Swift coding tasks translated from HumanEval. Compatible with completions model endpoint.",
            labels=new_labels("bigcode_eval_harness", LABEL_CODE),
            optional_params=bigcode_eval_harness_params,
        ),
        # SystemBenchmark(
        #     name="multiple-ts",
        #     description="MultiPL-E TypeScript coding tasks translated from HumanEval. Compatible with completions model endpoint.",
        #     labels=new_labels("bigcode_eval_harness", LABEL_CODE),
        #     optional_params=bigcode_eval_harness_params,
        # ),
    ]

    SUPPORTED_MODEL_TYPE: dict[str, set[EvalFactoryModelType]] = {
        "humaneval": {EvalFactoryModelType.COMPLETIONS},
        "humaneval-instruct": {EvalFactoryModelType.CHAT},
        "humanevalplus": {EvalFactoryModelType.COMPLETIONS},
        "mbpp": {EvalFactoryModelType.CHAT, EvalFactoryModelType.COMPLETIONS},
        "mbppplus": {EvalFactoryModelType.CHAT, EvalFactoryModelType.COMPLETIONS},
        "mbppplus-nemo": {EvalFactoryModelType.CHAT},
        "multiple-clj": {EvalFactoryModelType.COMPLETIONS},
        "multiple-cpp": {EvalFactoryModelType.COMPLETIONS},
        "multiple-cs": {EvalFactoryModelType.COMPLETIONS},
        "multiple-d": {EvalFactoryModelType.COMPLETIONS},
        "multiple-elixir": {EvalFactoryModelType.COMPLETIONS},
        "multiple-go": {EvalFactoryModelType.COMPLETIONS},
        "multiple-hs": {EvalFactoryModelType.COMPLETIONS},
        "multiple-java": {EvalFactoryModelType.COMPLETIONS},
        "multiple-jl": {EvalFactoryModelType.COMPLETIONS},
        "multiple-js": {EvalFactoryModelType.COMPLETIONS},
        "multiple-lua": {EvalFactoryModelType.COMPLETIONS},
        "multiple-ml": {EvalFactoryModelType.COMPLETIONS},
        "multiple-php": {EvalFactoryModelType.COMPLETIONS},
        "multiple-pl": {EvalFactoryModelType.COMPLETIONS},
        "multiple-r": {EvalFactoryModelType.COMPLETIONS},
        "multiple-rb": {EvalFactoryModelType.COMPLETIONS},
        "multiple-rkt": {EvalFactoryModelType.COMPLETIONS},
        "multiple-rs": {EvalFactoryModelType.COMPLETIONS},
        "multiple-scala": {EvalFactoryModelType.COMPLETIONS},
        "multiple-sh": {EvalFactoryModelType.COMPLETIONS},
        "multiple-swift": {EvalFactoryModelType.COMPLETIONS},
        # "multiple-ts": {EvalFactoryModelType.COMPLETIONS},
    }
