from Recommender.recommender import Recommender

###############################
## BASELINE GPT2 RANDOM INIT ##
##       TOKEN LEVEL         ##
###############################
recommender00 = Recommender(
    model='gpt2rand-modelset_token-512/best_model',
    type='token',
    test_path='./modelset_token/test.txt',
    max_new_tokens=8,
    num_ret_seq=1
)

recommender000 = Recommender(
    model='gpt2rand-medium-modelset_token-512/best_model',
    type='token',
    test_path='./modelset_token/test.txt',
    max_new_tokens=8,
    num_ret_seq=1
)

###############################
## BASELINE GPT2 RANDOM INIT ##
##        LINE LEVEL         ##
###############################
recommender01 = Recommender(
    model='gpt2rand-modelset_line-512/best_model',
    type='line',
    test_path='./modelset_line/test.json',
    max_new_tokens=30,
    num_ret_seq=1
)

recommender001 = Recommender(
    model='gpt2rand-medium-modelset_line-512/best_model',
    type='line',
    test_path='./modelset_line/test.json',
    max_new_tokens=30,
    num_ret_seq=1
)

###############################
## BASELINE GPT2 RANDOM INIT ##
##       TOKEN LEVEL         ##
###############################
recommender02 = Recommender(
    model='gpt2rand-modelset_token-512/best_model',
    type='class',
    test_path='tests_by_class',
    max_new_tokens=8,
    num_ret_seq=10
)

recommender002 = Recommender(
    model='gpt2rand-medium-modelset_token-512/best_model',
    type='class',
    test_path='tests_by_class',
    max_new_tokens=8,
    num_ret_seq=10
)

##########################
## BASELINE PREDICTIONS ##
##########################
#recommender00.recommend_token()
#recommender01.recommend_line()
#recommender02.recommend_by_class()
#recommender000.recommend_token()
#recommender001.recommend_line()
#recommender002.recommend_by_class()

#######################
## PRETRAINED MODELS ##
##    TOKEN LEVEL    ##
#######################
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


#recommender1.recommend_token()
#recommender2.recommend_token()
#recommender3.recommend_token()
#recommender4.recommend_token()
#recommender5.recommend_token()
#recommender6.recommend_token()
#recommender7.recommend_token()
#recommender8.recommend_token()

#######################
## PRETRAINED MODELS ##
##    LINE LEVEL    ##
#######################
recommender9= Recommender(
    model='gpt2-modelset_line-512/best_model',
    type='line',
    test_path='./modelset_line/test.json',
    max_new_tokens=30,
    num_ret_seq=1
)

recommender10= Recommender(
    model='gpt2-medium-modelset_line-512/best_model',
    type='line',
    test_path='./modelset_line/test.json',
    max_new_tokens=30,
    num_ret_seq=1
)

recommender11= Recommender(
    model='gpt2-large-modelset_line-512/best_model',
    type='line',
    test_path='./modelset_line/test.json',
    max_new_tokens=30,
    num_ret_seq=1
)

recommender12= Recommender(
    model='Salesforce/codegen-350M-mono-modelset_line-512/best_model',
    type='line',
    test_path='./modelset_line/test.json',
    max_new_tokens=30,
    num_ret_seq=1
)

recommender13= Recommender(
    model='Salesforce/codegen-350M-nl-modelset_line-512/best_model',
    type='line',
    test_path='./modelset_line/test.json',
    max_new_tokens=30,
    num_ret_seq=1
)

recommender14= Recommender(
    model='Salesforce/codegen-350M-multi-modelset_line-512/best_model',
    type='line',
    test_path='./modelset_line/test.json',
    max_new_tokens=30,
    num_ret_seq=1
)

recommender15= Recommender(
    model='facebook/opt-350m-modelset_line-512/best_model',
    type='line',
    test_path='./modelset_line/test.json',
    max_new_tokens=30,
    num_ret_seq=1
)

recommender16= Recommender(
    model='EleutherAI/gpt-neo-125m-modelset_line-512/best_model',
    type='line',
    test_path='./modelset_line/test.json',
    max_new_tokens=30,
    num_ret_seq=1
)

#recommender9.recommend_line()
#.recommend_line()
#recommender11.recommend_line()
#recommender12.recommend_line()
#recommender13.recommend_line()
#recommender14.recommend_line()
#recommender15.recommend_line()
#recommender16.recommend_line()


#######################
## PRETRAINED MODELS ##
##      BY CLASS     ##
#######################

recommender17= Recommender(
    model='gpt2-modelset_token-512/best_model',
    type='class',
    test_path='tests_by_class',
    max_new_tokens=8,
    num_ret_seq=10
)

recommender18= Recommender(
    model='gpt2-medium-modelset_token-512/best_model',
    type='class',
    test_path='tests_by_class',
    max_new_tokens=8,
    num_ret_seq=10
)

recommender19= Recommender(
    model='gpt2-large-modelset_token-512/best_model',
    type='class',
    test_path='tests_by_class',
    max_new_tokens=8,
    num_ret_seq=10
)

recommender20= Recommender(
    model='Salesforce/codegen-350M-mono-modelset_token-512/best_model',
    type='class',
    test_path='tests_by_class',
    max_new_tokens=8,
    num_ret_seq=10
)

recommender21= Recommender(
    model='Salesforce/codegen-350M-nl-modelset_token-512/best_model',
    type='class',
    test_path='tests_by_class',
    max_new_tokens=8,
    num_ret_seq=10
)

recommender22= Recommender(
    model='Salesforce/codegen-350M-multi-modelset_token-512/best_model',
    type='class',
    test_path='tests_by_class',
    max_new_tokens=8,
    num_ret_seq=10
)

recommender23= Recommender(
    model='facebook/opt-350m-modelset_token-512/best_model',
    type='class',
    test_path='tests_by_class',
    max_new_tokens=8,
    num_ret_seq=10
)

recommender24= Recommender(
    model='EleutherAI/gpt-neo-125m-modelset_token-512/best_model',
    type='class',
    test_path='tests_by_class',
    max_new_tokens=8,
    num_ret_seq=10
)

#recommender17.recommend_by_class()
#recommender18.recommend_by_class()
#recommender19.recommend_by_class()
#recommender20.recommend_by_class()
#recommender21.recommend_by_class()
#recommender22.recommend_by_class()
#recommender23.recommend_by_class()
#recommender24.recommend_by_class()


## EVALUACION

#.evaluate_token()
#recommender01.evaluate_line()
#recommender02.mrr_by_class(10)
#recommender000.evaluate_token()
#recommender001.evaluate_line()
#recommender002.mrr_by_class(10)
#recommender1.evaluate_token()
#recommender2.evaluate_token()
#recommender3.evaluate_token()
#recommender4.evaluate_token()
#recommender5.evaluate_token()
#recommender6.evaluate_token()
#recommender7.evaluate_token()
#recommender8.evaluate_token()

#recommender1.evaluate_token_by_class()
#recommender2.evaluate_token_by_class()
#recommender3.evaluate_token_by_class()
#recommender4.evaluate_token_by_class()
#recommender5.evaluate_token_by_class()
#recommender6.evaluate_token_by_class()
#recommender7.evaluate_token_by_class()
#recommender8.evaluate_token_by_class()

#recommender9.evaluate_line()
#recommender10.evaluate_line()
#recommender11.evaluate_line()
#recommender12.evaluate_line()
#recommender13.evaluate_line()
#recommender14.evaluate_line()
#recommender15.evaluate_line()kdjkvbhvjushgdhfgbnhghfrtghuikdfasdfh
#recommender16.evaluate_line()

recommender002.mrr_by_class(3)
#recommender17.mrr_by_class(10)
recommender18.mrr_by_class(3)
#recommender19.mrr_by_class(10)
recommender20.mrr_by_class(3)
recommender21.mrr_by_class(3)
recommender22.mrr_by_class(3)
#recommender23.mrr_by_class(10)
#recommender24.mrr_by_class(10)

recommender002.mrr_by_class(5)
#recommender17.mrr_by_class(10)
recommender18.mrr_by_class(5)
#recommender19.mrr_by_class(10)
recommender20.mrr_by_class(5)
recommender21.mrr_by_class(5)
recommender22.mrr_by_class(5)
#recommender23.mrr_by_class(10)
#recommender24.mrr_by_class(10)

recommender002.mrr_by_class(10)
#recommender17.mrr_by_class(10)
recommender18.mrr_by_class(10)
#recommender19.mrr_by_class(10)
recommender20.mrr_by_class(10)
recommender21.mrr_by_class(10)
recommender22.mrr_by_class(10)
#recommender23.mrr_by_class(10)
#recommender24.mrr_by_class(10)