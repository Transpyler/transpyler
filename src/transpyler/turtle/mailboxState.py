from .remoteState import RemoteState

class MailboxState(RemoteState):
    """
    A remote state that uses a multiprocessing.Queue to communicate between
    processes.

    The communication uses an inbox/outbox model. The client puts a message in
    the outbox and the server responds with a message in the inbox.
    """

    def inbox_factory(self):
        return Queue()

    def outbox_factory(self):
        return Queue()

    timeout = 1.0

    def __init__(self, **kwargs):
        # Initialize inbox
        try:
            self.inbox = kwargs['inbox']
        except KeyError:
            if not hasattr(self, 'inbox'):
                self.inbox = self.inbox_factory()

        # Initialize outbox
        try:
            self.outbox = kwargs['outbox']
        except KeyError:
            if not hasattr(self, 'outbox'):
                self.outbox = self.outbox_factory()

        super().__init__(**kwargs)

    def send(self, msg):
        self.put_message(msg)
        return self.get_message()

    def put_message(self, msg):
        """
        Put outgoing message on the outbox
        """
        self.outbox.put(msg)

    def get_message(self):
        """
        Get incoming message from the inbox.
        """
        return self.inbox.get(timeout=self.timeout)

    def draw_line(self, v1, v2):
        pass  # no-op: we broadcast and let the server handle it
