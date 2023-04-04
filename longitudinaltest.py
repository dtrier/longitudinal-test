import json

LAST_TEST_RESULT = {}

# modelop.init
def init(job_json):
    global LAST_TEST_RESULT
    job = json.loads(job_json.get("rawJson", {}))
    jobParameters = job.get("jobParameters", {})
    LAST_TEST_RESULT = jobParameters.get("lastTestResult", {})


# modelop.metrics
def metrics(data):
    print("Last Test Result: " + str(LAST_TEST_RESULT))
    results = data.iloc[0].to_dict()
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
