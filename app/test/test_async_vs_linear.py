import time
from app.views import vt, list_to_string, q
from test_hashes import hash_1_25, hash_26_50, hash_51_75

__author__ = 'Josh Maine'


def print_vt_query(this_hash):
    response = vt.get_file_report(list_to_string(this_hash))
    error = vt.handle_response_status_code(response)
    if error:
        print error
    else:
        pass
        # print ujson.dumps(response.content)
        # print response.status_code
    return True


def linear_test():
    print_vt_query(hash_1_25)
    print_vt_query(hash_1_25)
    print_vt_query(hash_1_25)


def async_test():
    job1 = q.enqueue(print_vt_query, hash_1_25)
    # print job1.result
    job2 = q.enqueue(print_vt_query, hash_26_50)
    # print job2.result
    job3 = q.enqueue(print_vt_query, hash_51_75)
    # print job3.result
    while not job1.result:
        pass
    while not job2.result:
        pass
    while not job3.result:
        pass


def run_test(interations=30):
    lin_list = []
    async_list = []
    for i in range(interations):
        #: LINEAR
        start_lin = time.time()
        linear_test()
        end_lin = time.time()
        # print "LINEAR TIME +++++++++++++++++++++++++++"
        lin_list.append((end_lin - start_lin))
        # print end_lin - start_lin

        #: ASYNC
        start_as = time.time()
        async_test()
        end_as = time.time()
        # print "Async TIME +++++++++++++++++++++++++++"
        async_list.append((end_as - start_as))
        # print end_as - start_as

    print "LINEAR AVG TIME =========================="
    print reduce(lambda x, y: x + y, lin_list) / len(lin_list)
    print "Async AVG TIME ==========================="
    print reduce(lambda x, y: x + y, async_list) / len(async_list)