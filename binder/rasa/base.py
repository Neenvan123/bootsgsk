# rasa run --enable-api --debug
import Python_Queries.preprocessors
import Python_Queries.call_rasa
import Python_Queries.postprocessings
from Python_Queries import test
def main():
    user_input = input("Enter an NL instruction: ")
    print("You entered:", user_input.lower())
    
    compound_props = Python_Queries.preprocessors.preprocessing(user_input.lower())
    # print("processsed input: ",compound_props['compounded_text'])

    try:
        rasa_out = Python_Queries.call_rasa.query_rasa(user_input.lower())
        # if rasa_out['intent']['name'] in ['pick_up','drop','put_down']:
        print("RASA output: ", rasa_out)
        # else:
        print("Intent: ", rasa_out['intent']['name'])
    except:
        print("RASA server is not up and running")
        # return

    # test.testingExtraction(rasa_out)
    try:
        instance = Python_Queries.postprocessings.postprocess(rasa_out, compound_props)
        if instance is not None:
            # print("Final Output")
            instance.print_params()
        else:
            print("Post processed instance is None")
    except:
        print("Post Process error")

if __name__ == "__main__":
    main()