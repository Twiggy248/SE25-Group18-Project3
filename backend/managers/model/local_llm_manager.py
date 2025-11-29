from huggingface_hub import HfApi
import os



def getHFModels():
    token = os.getenv("HF_TOKEN")
    hf = HfApi(token=token)

    models = hf.list_models(task="text-generation")
    


# get available models to host locally


# initalize locally hosted model


# query locally hosted model