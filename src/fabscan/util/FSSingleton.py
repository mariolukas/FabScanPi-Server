import threading

# Based on tornado.ioloop.IOLoop.instance() approach.
# See https://github.com/facebook/tornado
class SingletonMixin(object):
	__singleton_lock = threading.Lock()
	__singleton_instance = None

	@classmethod
	def instance(cls, *args, **kwgs):
		if not cls.__singleton_instance:
			with cls.__singleton_lock:
				if not cls.__singleton_instance:
					cls.__singleton_instance = cls(*args, **kwgs)
		return cls.__singleton_instance


