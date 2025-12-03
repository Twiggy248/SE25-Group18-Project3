from api.services import SERVICE_MODELS

def getAvailableModels() -> dict:
    """
    Consolidates all available Models, both those locally hosted and those through an API
    and returns a all_models dict variable
    """
    all_models = {}
    
    # Get the Models from Available Services
    for service, funcs in SERVICE_MODELS.items():
        serviceInit = funcs[0]
        service_models = serviceInit()
        all_models[service] = service_models

    # Returns the dictionary of all models with is formatted as service: list of model strings
    return all_models




# initalize model
def initModel(service: str, model_name: str):
    """
    Given the service and Model, initalize the model
    """
    match service:
        case "hf":
            funcs = SERVICE_MODELS["hf"]
            initFunc = funcs[1]
            initFunc(model_name)
    pass


# query model
def makeQuery(request: str) -> str:

    # Send the query to the proper service manager overlord (api or local)
        # If no llm made, use default local llm

    pass