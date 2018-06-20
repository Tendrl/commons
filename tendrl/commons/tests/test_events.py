import __builtin__
import maps
from tendrl.commons.event import Event
from tendrl.commons.message import Message


# Event Dummys provide code coverage for the Event constructor
message_new = msg = Message(priority="info", publisher="node_agent",
                            payload={"message": "Test Message"},
                            node_id="Test id")
event_dummy = Event(Message(priority="info", publisher="node_agent", payload={
    "message": "Test Message"}, node_id="Test id"))
event_dummy2 = Event(Message(priority="info", publisher="node_agent", payload={
    "message": TypeError}, node_id="Test id"))

# event_test_write = Event(Message(priority="notice",
# publisher="node_agent", payload={
# "message":  "Test Message"}, node_id="Test id"))


# def test_write():
# event_test_write._write(message_new)

def test_write():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['tags'] = "test"
    NS.publisher_id = "node_context"
    NS.config.data['logging_socket_path'] = "/var/run/tendrl/message.sock"
    event_to_test = Event(Message(priority="info", publisher="node", payload={
        "message": "Test message"}, node_id="Test id"))
    event_to_test._write(message_new)
    event_to_test.socket_path = None
    event_to_test._write(message_new)
    # event_to_test.socket_path = NS.config.data['logging_socket_path']
    # event_to_test._pack_and_send(Message.to_json(message_new))

# def test_start():
#   from tendrl.commons.profiler import start
#   start()
