import threading
import queue

class ThreadEventManager:
    def __init__(self, window):
        self.events = []
        self.window = window
        self.result_queue = queue.Queue()

    def add_event(self, event_id, func, kwargs=None, completion_functions=None):
        event = {
            'id': event_id,
            'function': func,
            'kwargs': kwargs if kwargs else {},
            'completion_functions': completion_functions if completion_functions else [],
            "result_queue": queue.Queue()
        }
        self.events.append(event)
        self.start_event(event)

    def start_event(self, event):
        thread = threading.Thread(target=self._run_event, args=(event,))
        thread.start()
        self._main_thread_loop(event)

    def _run_event(self, event):
        result = event['function'](**event['kwargs'])
        event["result_queue"].put(result)

    def _main_thread_loop(self, event):
        if not event['result_queue'].empty():
            result = event['result_queue'].get()
            self._process_result(result, event)
        self.window.after(500, self._main_thread_loop, event)

    def _process_result(self, result, event):
        # Assuming result is a dictionary with keys 'message_func' and 'message_args'
        # where both can be None for no message
        message_func, message_args = result.get('message_func'), result.get('message_args')
        if message_func:
            message_func(*message_args)
        for completion_func in event['completion_functions']:
            completion_func()
        # Remove the event from the list of events
        self.events.remove(event)


