from api.services import SERVICE_MODELS


# init api models
def initModels(option: str):
    """
    Initalizes all the Models that are called through the API unless an option string is provided
    """
    if option is None:
        for service, funcs in SERVICE_MODELS.items():
            initModel = funcs[1]
            try:
                initModel()
            except Exception as e:
                continue
    else:
        funcs = SERVICE_MODELS[option]
        initModel = funcs[1]
        try:
            initModel()
        except Exception as e:
            print("Cannot initalize API Model\n")


def getAvailableModels():
    """
    Iterates through currently implemented services and returns the available models
    """

    all_models = {}

    for service, funcs in SERVICE_MODELS.items():
        getModels = funcs[0]
        try:
            models_list = getModels()
            all_models[service] = models_list
        except Exception as e:
            # Implemented service may not be initalized or available, so we can ignore it
            continue

    return all_models

# query api model