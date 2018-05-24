FROM bojleros/flask:0.0.1
MAINTAINER Bartek R "bojleros@gmail.com"
ENV APP_DIR /app
COPY main.py /app
WORKDIR /app
ENTRYPOINT ["python3"]
CMD ["main.py"]

