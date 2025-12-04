from services import SERVICE_MODELS, initDefault
import services.model_details as service

def getAvailableModels() -> dict:
    """
    Consolidates all available Models, both those locally hosted and those through an API
    and returns a all_models dict variable
    """
    all_models = {}
    
    # Get the Models from Available Services
    for service, funcs in SERVICE_MODELS.items():
        getServiceModels = funcs[0]
        service_models = getServiceModels()
        all_models[service] = service_models

    # Returns the dictionary of all models with is formatted as service: list of model strings
    return all_models


# initalize model
def initModel(service: str, model_name: str):
    """
    Given the service and Model, initalize the model
    """

    # Check that the service and model_name is passed properly and if not, use the default model
    if service is None or model_name is None:
        initDefault()

    # If valid, initialize the model and service
    else:
        funcs = SERVICE_MODELS[service]
        initFunc = funcs[1]
        initFunc(model_name)


# query model
def makeQuery(instructionsStr: str, query: str) -> str:

    # Get the current model
    modelService = service.getModelService()

    # If a model hasn't been setup yet, go ahead and get the default one booted up
    if modelService is None:
        initModel()
        modelService = service.getModelService()

    # Make the query based on the service
    funcs = SERVICE_MODELS[modelService]
    queryFunc = funcs[2]
    
    # Make the query
    response = queryFunc(instructionsStr, query)

    # Return the query response
    return response
