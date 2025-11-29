import model.api_llm_manager as api_manager

def getAvailableModels() -> dict:
    """
    Consolidates all available Models, both those locally hosted and those through an API
    and returns a all_models dict variable
    """
    all_models = {}
    
    # Get the API Models
    api_models = api_manager.getAvailableModels()
    all_models["api"] = api_models

    # Get the locally hosted Models



    return all_models




# initalize model


# query model