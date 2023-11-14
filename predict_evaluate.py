from Recommender.recommender import Recommender

# REPEAT THIS FOR EACH MODEL.
recommender1= Recommender(
    model='gpt2-modelset_token-256/best_model',
    type='token',
    test_path='./modelset_token/test.txt',
    max_new_tokens=8,
    num_ret_seq=1
)

recommender2 = Recommender(
    model='gpt2-modelset_line-256/best_model',
    type='line',
    test_path='./modelset_line/test.json',
    max_new_tokens=30,
    num_ret_seq=1
)

recommender3 = Recommender(
    model='gpt2-modelset_token-256/best_model',
    type='class',
    test_path='tests_by_class',
    max_new_tokens=8,
    num_ret_seq=5
)

recommender1.recommendToken()
#recommender2.recommendLine()
#recommender3.recommendByClass()

