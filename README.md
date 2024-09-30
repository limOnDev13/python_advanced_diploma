# Twitter clone
- Description
- Demo
- Technologies
- Installation
## Demo
![Alt text](demo.gif)
## Description
The project is a corporate microblogging service (a very simplified version of Twitter).
The service allows you to create tweets, attach images to them, subscribe to other bloggers,
read tweets from people you follow, and like tweets. The service does not have user registration
(this is a corporate network and users are created from the outside). 
The frontend is provided by the Skillbox training platform (https://skillbox.ru/).
All server handles have been tested by pytest, all code has been verified using mypy, flake8, black and isort
## Technologies
- Python
- asyncio
- SQLAlchemy
- aiofiles
- FastAPI
- NGINX
- Docker
## Installation
To deploy the service, you just need to assemble the container using docker-compose in the root of the project. 
When starting the container, you can go to http://localhost:8080/ (if the container is running on the local machine)
to see how the site is working. To demonstrate the work of the project, two test users are created at startup
with the api-key test and test2. Their IDs are 1 and 2, respectively. To subscribe one user to another,
it is recommended to use Swagger (documentation is located at http://localhost:5000/docs),
since the ability to search for other users has not yet been added.