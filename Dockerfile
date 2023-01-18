FROM python:3
USER root
RUN mkdir -p /opt/waterjug
RUN mkdir -p /opt/waterjug/templates
RUN mkdir -p /opt/waterjug/static
ADD waterjug.py /opt/waterjug/waterjug.py
ADD requirements.txt /opt/waterjug/requirements.txt
ADD templates/* /opt/waterjug/templates/
ADD static/* /opt/waterjug/static/
WORKDIR /opt/waterjug
RUN pip install -r requirements.txt
CMD [ "python", "/opt/waterjug/waterjug.py" ]
