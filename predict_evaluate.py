from Recommender.recommender import Recommender

recommender1= Recommender(
    model='gpt2-modelset_token-512/best_model',
    type='token',
    test_path='./modelset_token/test.txt',
    max_new_tokens=8,
    num_ret_seq=1
)

recommender2= Recommender(
    model='gpt2-medium-modelset_token-512/best_model',
    type='token',
    test_path='./modelset_token/test.txt',
    max_new_tokens=8,
    num_ret_seq=1
)

recommender3= Recommender(
    model='gpt2-large-modelset_token-512/best_model',
    type='token',
    test_path='./modelset_token/test.txt',
    max_new_tokens=8,
    num_ret_seq=1
)

recommender4= Recommender(
    model='Salesforce/codegen-350M-mono-modelset_token-512/best_model',
    type='token',
    test_path='./modelset_token/test.txt',
    max_new_tokens=8,
    num_ret_seq=1
)

recommender5= Recommender(
    model='Salesforce/codegen-350M-nl-modelset_token-512/best_model',
    type='token',
    test_path='./modelset_token/test.txt',
    max_new_tokens=8,
    num_ret_seq=1
)

recommender6= Recommender(
    model='Salesforce/codegen-350M-multi-modelset_token-512/best_model',
    type='token',
    test_path='./modelset_token/test.txt',
    max_new_tokens=8,
    num_ret_seq=1
)

recommender7= Recommender(
    model='facebook/opt-350m-modelset_token-512/best_model',
    type='token',
    test_path='./modelset_token/test.txt',
    max_new_tokens=8,
    num_ret_seq=1
)

recommender8= Recommender(
    model='EleutherAI/gpt-neo-125m-modelset_token-512/best_model',
    type='token',
    test_path='./modelset_token/test.txt',
    max_new_tokens=8,
    num_ret_seq=1
)


#recommender1.recommendToken()
#recommender2.recommendToken()
#recommender3.recommendToken()
#recommender4.recommendToken()
#recommender5.recommendToken()
#recommender6.recommendToken()
#recommender7.recommendToken()
recommender8.recommendToken()