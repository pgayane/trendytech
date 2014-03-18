import time

class Counter:

    def __init__(self, rate_limit):
        self.start_time = time.time()
        self.count = 0
        self.time_limit = 3660
        self.rate_limit = rate_limit

    def sleep(self, delta):
        time.sleep(self.time_limit - delta)

    def check_limit(self):
        if (self.count > 0) and (self.count % self.rate_limit == 0):
            delta = time.time() - self.start_time
            if delta < self.time_limit:
                print 'sleep for %f' % (delta)
                self.sleep(delta)
            else:
                print 'not sleeping as delta is %f' % (delta)
            
            self.start_time = time.time()

    def increment(self):
        self.count += 1

