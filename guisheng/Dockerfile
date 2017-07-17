FROM python:2.7

ENV DEPLOY_PATH /guisheng

RUN mkdir -p $DEPLOY_PATH
WORKDIR $DEPLOY_PATH

Add requirements.txt requirements.txt
RUN pip install --index-url http://pypi.doubanio.com/simple/ -r requirements.txt --trusted-host=pypi.doubanio.com

VOLUME /var/run/mysqld:/var/run/mysqld
EXPOSE 3306
Add . .


