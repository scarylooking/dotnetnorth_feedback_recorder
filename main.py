import json
import program
import uuid
import string
import random
import logging


def random_string():
    return ''.join(random.choice(string.ascii_letters) for i in range(100, 250))


def random_rating():
    return random.randint(1, 5)


logging.basicConfig(level=logging.INFO)

body = {
    'session': random_rating(),
    'delivery': random_rating(),
    'knowledge': random_rating(),
    'slides': random_rating(),
    'overall': random_rating(),
    'technical': random_rating(),
    'comments': f'{random_string()}',
}

test_event_body = json.dumps(body)
test_event = {'body': test_event_body}
test_context = type('obj', (object,), {'aws_request_id': str(uuid.uuid4())})()
print(program.lambda_handler(test_event, test_context))