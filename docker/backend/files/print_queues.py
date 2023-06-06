diff --git a/backend/run/print_queues.py b/backend/run/print_queues.py
index 849f8f6a..f48d1157 100755
--- a/backend/run/print_queues.py
+++ b/backend/run/print_queues.py
@@ -14,6 +14,7 @@ redis_config = {
     'host': opts['redis_host'],
     'port': opts['redis_port'],
     'db': opts['redis_db'],
+    'password': opts['redis_pwd'],
 }
 
 for i in range(0, NUM_QUEUES):
