import sys
from mutpy import commandline

sys.argv = [
    "mutpy",
    "--target", "bully",
    "--unit-test", "bully_test_improved",
    "--runner", "unittest",
    "--report-html", "report"
]

commandline.main(sys.argv)