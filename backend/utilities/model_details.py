
MODEL_NAME = ""
MODEL_SERVICE = ""

def setModelName(model: str):
    global MODEL_NAME
    MODEL_NAME = model

def setModelService(service: str):
    global MODEL_SERVICE
    MODEL_SERVICE = service

def getModelName() -> str:
    return MODEL_NAME

def getModelService() -> str:
    return MODEL_SERVICE