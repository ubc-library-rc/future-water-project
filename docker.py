# import logging
# import os
# import sys
#
# sys.path.append(os.getcwd())  # I thought this happened by default?
# from test.test_pipeline_google import main as google_script
#
# # https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
# logging.getLogger("requests").setLevel(logging.WARNING)
# logging.getLogger("urllib3").setLevel(logging.WARNING)
#
# logger = logging.getLogger()
# logger.level = logging.DEBUG
# stream_handler = logging.StreamHandler(sys.stdout)
# logger.addHandler(stream_handler)
#
# logger.info("Runnig Google script")
# os.chdir(os.path.join(
#         os.path.dirname(os.path.realpath(__file__)),
#         'test'
# ))
# google_script()

print("Hello")