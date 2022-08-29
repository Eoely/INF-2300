import socketserver
import threading
from server import MyTCPHandler as HTTPHandler
from http import HTTPStatus
from http.client import HTTPConnection, BadStatusLine
import os
from random import shuffle
import json
"""
Written by: Raymon Skjørten Hansen
Email: raymon.s.hansen@uit.no
Course: INF-2300 - Networking
UiT - The Arctic University of Norway
May 9th, 2019
"""


RANDOM_TESTING_ORDER = True

HOST = "localhost"
PORT = 54321

with open("index.html", "rb") as infile:
    EXPECTED_BODY = infile.read()

with open("server.py", "rb") as infile:
    FORBIDDEN_BODY = infile.read()

messages_file = "messages.json"

class MockServer(socketserver.TCPServer):
    allow_reuse_address = True


server = MockServer((HOST, PORT), HTTPHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()
client = HTTPConnection(HOST, PORT)


def server_returns_valid_response_code():
    """Server returns a valid http-response code."""
    client.request("GET", "/")
    try:
        response = client.getresponse()
        return response.status in [status.value for status in HTTPStatus]
    except BadStatusLine:
        client.close()
        return False


def test_index():
    """GET-request to root returns 'index.html'."""
    client.request("GET", "/")
    body = client.getresponse().read()
    client.close()
    return EXPECTED_BODY == body


def test_content_length():
    """Content-Length header is present."""
    client.request("GET", "/")
    headers = [k.lower() for k in client.getresponse().headers.keys()]
    client.close()
    return "content-length" in headers


def test_valid_content_length():
    """Content-Length is correct."""
    client.request("GET", "/")
    headers = {k.lower(): v for k, v in client.getresponse().headers.items()}
    expected_length = len(EXPECTED_BODY)
    try:
        length = int(headers.get("content-length"))
        return expected_length == length
    except (KeyError, TypeError):
        return False
    finally:
        client.close()


def test_content_type():
    """Content-Type is present."""
    client.request("GET", "/")
    headers = [k.lower() for k in client.getresponse().headers.keys()]
    client.close()
    return "content-type" in headers


def test_valid_content_type():
    """Content type is correct."""
    client.request("GET", "/")
    headers = {k.lower(): v for k, v in client.getresponse().headers.items()}
    expected_type = "text/html"
    try:
        actual_type = headers.get("content-type")
        # Type-field could contain character encoding too.
        # So we just check that the basic type is correct.
        return actual_type.startswith(expected_type)
    except (KeyError, TypeError):
        return False
    finally:
        client.close()


def test_nonexistent_resource_status_code():
    """Server returns 404 on non-existing resource."""
    client.request("GET", "did_not_find_this_file.not")
    response = client.getresponse()
    client.close()
    return response.status == HTTPStatus.NOT_FOUND


def test_forbidden_resource_status_code():
    """Server returns 403 on forbidden resource."""
    client.request("GET", "server.py")
    response = client.getresponse()
    client.close()
    return response.status == HTTPStatus.FORBIDDEN


def test_directory_traversal_exploit():
    """Directory traversal attack returns 403 status code."""
    client.request("GET", "../README.md")
    response = client.getresponse()
    client.close()
    return response.status == HTTPStatus.FORBIDDEN


def test_post_to_non_existing_file_should_create_file():
    """POST-request to non-existing file, should create that file."""
    testfile = "test.txt"
    msg = b'Simple test'
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
        "Content-Length": len(msg),
    }
    if(os.path.exists(testfile)):
        os.remove(testfile)
    client.request("POST", testfile, body=msg, headers=headers)
    client.getresponse()
    client.close()
    return os.path.exists(testfile)


def test_post_to_test_file_should_return_file_content():
    """POST to test-file should append to file and return the file-content."""
    testfile = "test.txt"
    msg = b'text=Simple test'
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
        "Content-Length": len(msg),
    }
    if(os.path.exists(testfile)):
        os.remove(testfile)
    client.request("POST", testfile, body=msg, headers=headers)
    response_body = client.getresponse().read()
    with open(testfile, "rb") as infile:
        filecontent = infile.read()
    client.close()
    return response_body == filecontent


def test_post_to_test_file_should_return_correct_content_length():
    """POST to test-file should respond with correct content_length."""
    testfile = "test.txt"
    msg = b'text=Simple test'
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
        "Content-Length": len(msg),
    }
    if(os.path.exists(testfile)):
        os.remove(testfile)
    client.request("POST", testfile, body=msg, headers=headers)
    expected_content_length = len(client.getresponse().read())
    with open(testfile, "rb") as infile:
        actual_length = len(infile.read())
    client.close()
    return expected_content_length == actual_length

# -------- TESTS FOR MESSAGES API CALLS ---------

def test_messages_get():
    """GET-request to messages returns 'messages.json'."""
    with open(messages_file, "rb") as infile:
        MESSAGES_BODY = infile.read()
    client.request("GET", "/messages")
    body = client.getresponse().read()
    client.close()
    return MESSAGES_BODY == body

def test_messages_post():
    """POST to test-file should respond with correct content_length."""
    test_text ="POST Test text"
    json_object = '{"text": "POST Test text"}'
    msg = bytes(json_object, encoding="utf-8")
    headers = {
        "Content-type": "application/json",
        "Accept": "text/plain",
        "Content-Length": len(msg),
    }

    client.request("POST", "/messages", body=msg, headers=headers)
    response = client.getresponse()
    body = response.read().decode('utf-8')
    # body = client.getresponse().read().decode('utf-8')
    client.close()

    #Confirm last message is test_id
    with open(messages_file) as f:
        result_messages = json.load(f)
        last_message_text = result_messages[-1]["text"]
    return last_message_text == test_text and response.status == HTTPStatus.CREATED

def test_messages_put_edit():
    """PUT to messages should edit existing object, assume first message has id "1"."""

    json_object = '{"id": "1", "text": "put test message"}'
    msg = bytes(json_object, encoding="utf-8")
    headers = {
        "Content-type": "application/json",
        "Accept": "text/plain",
        "Content-Length": len(msg),
    }

    client.request("PUT", "/messages", body=msg, headers=headers)
    response = client.getresponse()
    client.close()

    #Confirm last message is test_id
    with open(messages_file) as data_file:
        messages = json.load(data_file)

    return messages[0] == json.loads(json_object) and response.status == HTTPStatus.OK

def test_messages_put_create():
    """PUT with non-existing ID, should NOT create message."""
    test_id = "new id put test"

    #Perfrom request
    json_object = '{"id": "new id put test", "text": "put test message"}'
    msg = bytes(json_object, encoding="utf-8")
    headers = {
        "Content-type": "application/json",
        "Accept": "text/plain",
        "Content-Length": len(msg),
    }

    client.request("PUT", "/messages", body=msg, headers=headers)
    response = client.getresponse()
    client.close()

    return response.status == HTTPStatus.NOT_FOUND

def test_messages_delete():
    """DELETE to messages json file, verifies that last object changes after delete"""

    with open(messages_file, 'r') as f:
        original_messages = json.loads(f.read())
        last_id_start = original_messages[-1]["id"]

    msg = bytes(str(original_messages[-1]).replace("'", '"'), encoding="utf-8")
    headers = {
        "Content-type": "application/json",
        "Accept": "text/plain",
        "Content-Length": len(msg),
    }

    client.request("DELETE", "/messages", body=msg, headers=headers)
    response = client.getresponse()
    client.close()

    with open(messages_file, 'r') as f:
        result_messages = json.load(f)
        last_id_result = result_messages[-1]["id"]
    
    return last_id_start != last_id_result and response.status == HTTPStatus.NO_CONTENT

# -------- SPECIAL CASES ---------

def test_messages_pizza():
    '''PIZZA to messages json file, should not crash and return bad request'''
    client.request("PIZZA", "/messages")
    response = client.getresponse()
    client.close()
    return response.status == HTTPStatus.BAD_REQUEST

def post_server_forbidden():
    '''POST to server.py, should return unauthorized'''
    client.request("POST", "server.py")
    response = client.getresponse()
    client.close()
    return response.status == HTTPStatus.FORBIDDEN

def delete_not_existing_message():
    '''Attempt to DELETE message which is not contained in json file'''
    json_object = '{"id": "unique id given number of chars", "text": "irrelevant"}'
    msg = bytes(json_object, encoding="utf-8")
    headers = {
        "Content-type": "application/json",
        "Accept": "text/plain",
        "Content-Length": len(msg),
    }

    client.request("DELETE", "/messages", body=msg, headers=headers)
    response = client.getresponse()
    client.close()
    return response.status == HTTPStatus.NOT_FOUND

def empty_request():
    '''POST request to messages without id or text'''
    client.request("POST", "/messages")
    post_response = client.getresponse()
    client.close()
    client.request("PUT", "/messages")
    put_response = client.getresponse()
    client.close()
    client.request("DELETE", "/messages")
    delete_response = client.getresponse()
    client.close()
    return post_response.status == delete_response.status == put_response.status == HTTPStatus.BAD_REQUEST

def put_no_id():
    '''PUT request without defining ID to edit'''
    json_object = '{"text": "irrelevant"}'
    msg = bytes(json_object, encoding="utf-8")
    headers = {
        "Content-type": "application/json",
        "Accept": "text/plain",
        "Content-Length": len(msg),
    }
    client.request("PUT", "/messages", body=msg, headers=headers)
    response = client.getresponse()
    client.close()
    return response.status == HTTPStatus.BAD_REQUEST

test_functions = [
    server_returns_valid_response_code,
    test_index,
    test_content_length,
    test_valid_content_length,
    test_content_type,
    test_valid_content_type,
    test_nonexistent_resource_status_code,
    test_forbidden_resource_status_code,
    test_directory_traversal_exploit,
    test_post_to_non_existing_file_should_create_file,
    test_post_to_test_file_should_return_file_content,
    test_post_to_test_file_should_return_correct_content_length,
    test_messages_get,
    test_messages_post,
    test_messages_put_edit,
    test_messages_put_create,
    test_messages_delete,
    test_messages_pizza,
    post_server_forbidden,
    delete_not_existing_message,
    empty_request,
    put_no_id,
]


def run_tests(all_tests, random=False):
    passed = 0
    num_tests = len(all_tests)
    skip_rest = False
    for test_function in all_tests:
        if not skip_rest:
            result = test_function()
            if result:
                passed += 1
            else:
                skip_rest = True
            print('result test', result)
            print(("FAIL", "PASS")[result] + "\t" + test_function.__doc__)
        else:
            print("SKIP\t" + test_function.__doc__)
    percent = round((passed / num_tests) * 100, 2)
    print(f"\n{passed} of {num_tests}({percent}%) tests PASSED.\n")
    if passed == num_tests:
        return True
    else:
        return False


def run():
    print("Running tests in sequential order...\n")
    sequential_passed = run_tests(test_functions)
    # We only allow random if all tests pass sequentially
    if RANDOM_TESTING_ORDER and sequential_passed:
        print("Running tests in random order...\n")
        shuffle(test_functions)
        run_tests(test_functions, True)
    elif RANDOM_TESTING_ORDER and not sequential_passed:
        print("Tests should run in sequential order first.\n")


run()
server.shutdown()
