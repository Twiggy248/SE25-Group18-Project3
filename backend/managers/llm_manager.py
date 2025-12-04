from services import SERVICE_MODELS, initDefault
import services.model_details as service

def status() -> bool:
    """
    Checks the current status of the LLM System. If Model Name has been set,
    the LLM has been initalized.
    
    :return: If an LLM has been setup and initalized
    :rtype: bool
    """

    if service.getModelName() is None:
        return False
    return True

def checkService(service: str) -> bool:
    """
    Checks if a service is valid by checking if its in the Service_models array
    which (should) contain all services integrated into the application
    
    :param service: The requested Service to check
    :type service: str
    :return: If Service is supported
    :rtype: bool
    """
    try:
        SERVICE_MODELS[service]
        return True
    except:
        return False

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


def initModel(service: str, api_key: str, model_name: str):
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
def makeQuery(instructionsStr: str, query: str) -> dict[str, str]:
    """
    The Generic Query method used by the project. Pulls the current LLM Service and Model, and queries it as
    defined in that specific LLM's integration code.
    
    :param instructionsStr: The String containing the instructions for the LLM (ex. "You are a chef guiding new students, providing feedback where needed")
    :type instructionsStr: str
    :param query: The String containing the query from the user as well as any context (ex. "How do I know if I've overcooked noodles?")
    :type query: str
    :return: The dict variable of string:string that the LLM returns
    :rtype: dict[str, str]
    """

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
