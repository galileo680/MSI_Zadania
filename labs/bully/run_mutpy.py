import sys
from mutpy import commandline

sys.argv = [
    "mutpy",
    "--target", "bully_async",
    "--unit-test", "bully_async_test",
    "--runner", "unittest",
    "--report-html", "report"
]

commandline.main(sys.argv)