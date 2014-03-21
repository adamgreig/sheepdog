# Quick sample of waiting on a specific request ID, say if you accidentally
# killed the main script. Better hope nothing finished between then and
# starting this though...
import sys
import time
import sheepdog
server = sheepdog.Server()
storage = sheepdog.Storage()
while True:
    n_results = storage.count_results(int(sys.argv[1]))
    sys.stdout.write("{0} results\r".format(n_results))
    sys.stdout.flush()
    time.sleep(5)
