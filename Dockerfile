FROM public.ecr.aws/lambda/python:3.9

COPY pyproject.toml  .
COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}" --timeout 120

COPY ./src/*.py ${LAMBDA_TASK_ROOT}/

CMD [ "main.lambda_handler" ]
