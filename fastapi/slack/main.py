from fastapi import FastAPI
import slack.slack
import eureka

app = FastAPI()


# Register the startup and shutdown event handlers
# app.add_event_handler("startup", startup_event)
# app.add_event_handler("shutdown", shutdown_event)
app.include_router(eureka.router)

# slack
app.include_router(slack.slack.router)