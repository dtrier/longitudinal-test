import json
import modelop.monitors.performance as performance
import modelop.monitors.stability as stability
import modelop.schema.infer as infer
import modelop.stats.diagnostics as diagnostics
import modelop.utils as utils
from modelop_sdk.utils import dashboard_utils as dashboard_utils

DEPLOYABLE_MODEL = {}
JOB = {}
MODEL_METHODOLOGY = ""
LAST_TEST_RESULT = {}

# modelop.init
def init(job_json):
    global LAST_TEST_RESULT
    global DEPLOYABLE_MODEL
    global JOB
    global MODEL_METHODOLOGY
    job = json.loads(job_json.get("rawJson", {}))
    jobParameters = job.get("jobParameters", {})
    LAST_TEST_RESULT = jobParameters.get("lastTestResult", {})
    
    DEPLOYABLE_MODEL = job["referenceModel"]
    MODEL_METHODOLOGY = DEPLOYABLE_MODEL.get("storedModel", {}).get("modelMetaData", {}).get("modelMethodology", "")

    JOB = job_json
    infer.validate_schema(job_json)


# modelop.metrics
def metrics(comparator):
    
    execution_errors_array = []
    results = calculate_performance(comparator, execution_errors_array)
    
    print("Last Test Result: " + str(LAST_TEST_RESULT))

    results["deviation_auc"] = percentDeviation(LAST_TEST_RESULT.get("auc", None), results.get("auc", None))
    results["deviation_precision"] = percentDeviation(LAST_TEST_RESULT.get("precision", None), results.get("precision", None))
    yield results  
    
def percentDeviation(a, b) :
    print("calculating deviation: " + str(a) + " and " + str(b))
    if a is None:
        return 0
    if b is None:
        return -100
    return int(((b - a) * 100) / a)

def calculate_performance(comparator, execution_errors_array):
    try:
        dashboard_utils.assert_df_not_none_and_not_empty(
            comparator, "Required comparator"
        )
        model_evaluator = performance.ModelEvaluator(dataframe=comparator, job_json=JOB)
        if "regression" in MODEL_METHODOLOGY.casefold():
            return model_evaluator.evaluate_performance(
                pre_defined_metrics="regression_metrics"
            )
        else:
            return model_evaluator.evaluate_performance(
                pre_defined_metrics="classification_metrics"
            )
    except Exception as ex:
        error_message = f"Error occurred calculating performance metrics: {str(ex)}"
        print(error_message)
        execution_errors_array.append(error_message)
        return {"auc": -99, "r2_score": 99}
