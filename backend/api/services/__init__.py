# Treating api/services as a package

import openai_api

# This must be updated whenever a new service is added
SERVICE_MODELS = {
    "openai": [openai_api.getModels, openai_api.initalizeModel, openai_api.query]
}