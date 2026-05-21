# SafeSynthesizer

## Jobs

Types:

```python
from nemo_platform.types.safe_synthesizer import (
    ClassifyConfig,
    Column,
    ColumnActions,
    DataParameters,
    DifferentialPrivacyHyperparams,
    EvaluationParameters,
    GenerateParameters,
    GlinerConfig,
    Globals,
    NERConfig,
    PIIReplacerConfig,
    Row,
    RowActions,
    SafeSynthesizerJob,
    SafeSynthesizerJobConfig,
    SafeSynthesizerJobRequest,
    SafeSynthesizerJobsListFilter,
    SafeSynthesizerJobsPage,
    SafeSynthesizerJobsSortField,
    SafeSynthesizerParameters,
    StepDefinition,
    TimeSeriesParameters,
    TrainingHyperparams,
    ValidationParameters,
)
```

Methods:

- <code title="post /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs">client.safe_synthesizer.jobs.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/jobs.py">create</a>(\*, workspace, \*\*<a href="src/nemo_platform/types/safe_synthesizer/job_create_params.py">params</a>) -> <a href="./src/nemo_platform/types/safe_synthesizer/safe_synthesizer_job.py">SafeSynthesizerJob</a></code>
- <code title="get /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs/{name}">client.safe_synthesizer.jobs.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/jobs.py">retrieve</a>(name, \*, workspace) -> <a href="./src/nemo_platform/types/safe_synthesizer/safe_synthesizer_job.py">SafeSynthesizerJob</a></code>
- <code title="get /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs">client.safe_synthesizer.jobs.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/jobs.py">list</a>(\*, workspace, \*\*<a href="src/nemo_platform/types/safe_synthesizer/job_list_params.py">params</a>) -> <a href="./src/nemo_platform/types/safe_synthesizer/safe_synthesizer_job.py">SyncDefaultPagination[SafeSynthesizerJob]</a></code>
- <code title="delete /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs/{name}">client.safe_synthesizer.jobs.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/jobs.py">delete</a>(name, \*, workspace) -> None</code>
- <code title="post /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs/{name}/cancel">client.safe_synthesizer.jobs.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/jobs.py">cancel</a>(name, \*, workspace) -> <a href="./src/nemo_platform/types/safe_synthesizer/safe_synthesizer_job.py">SafeSynthesizerJob</a></code>
- <code title="get /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs/{name}/logs">client.safe_synthesizer.jobs.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/jobs.py">get_logs</a>(name, \*, workspace, \*\*<a href="src/nemo_platform/types/safe_synthesizer/job_get_logs_params.py">params</a>) -> <a href="./src/nemo_platform/types/shared/platform_job_log.py">SyncLogsPagination[PlatformJobLog]</a></code>
- <code title="get /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs/{name}/status">client.safe_synthesizer.jobs.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/jobs.py">get_status</a>(name, \*, workspace) -> <a href="./src/nemo_platform/types/shared/platform_job_status_response.py">PlatformJobStatusResponse</a></code>

### Results

Types:

```python
from nemo_platform.types.safe_synthesizer.jobs import SafeSynthesizerSummary, SafeSynthesizerTiming
```

Methods:

- <code title="get /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs/{job}/results/{name}">client.safe_synthesizer.jobs.results.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/results.py">retrieve</a>(name, \*, workspace, job) -> <a href="./src/nemo_platform/types/shared/platform_job_result_response.py">PlatformJobResultResponse</a></code>
- <code title="get /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs/{name}/results">client.safe_synthesizer.jobs.results.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/results.py">list</a>(name, \*, workspace) -> <a href="./src/nemo_platform/types/shared/platform_job_list_result_response.py">PlatformJobListResultResponse</a></code>
- <code title="get /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs/{job}/results/{name}/download">client.safe_synthesizer.jobs.results.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/results.py">download</a>(name, \*, workspace, job) -> BinaryAPIResponse</code>
- <code title="get /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs/{job}/results/adapter/download">client.safe_synthesizer.jobs.results.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/results.py">download_adapter</a>(job, \*, workspace) -> BinaryAPIResponse</code>
- <code title="get /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs/{job}/results/evaluation-report/download">client.safe_synthesizer.jobs.results.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/results.py">download_evaluation_report</a>(job, \*, workspace) -> BinaryAPIResponse</code>
- <code title="get /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs/{job}/results/summary/download">client.safe_synthesizer.jobs.results.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/results.py">download_summary</a>(job, \*, workspace) -> <a href="./src/nemo_platform/types/safe_synthesizer/jobs/safe_synthesizer_summary.py">SafeSynthesizerSummary</a></code>
- <code title="get /apis/safe-synthesizer/v2/workspaces/{workspace}/jobs/{job}/results/synthetic-data/download">client.safe_synthesizer.jobs.results.<a href="./src/nemo_platform/resources/safe_synthesizer/jobs/results.py">download_synthetic_data</a>(job, \*, workspace) -> BinaryAPIResponse</code>
