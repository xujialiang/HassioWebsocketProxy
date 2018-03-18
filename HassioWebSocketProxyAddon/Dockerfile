ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8
RUN apk add --no-cache python3
#RUN apk add --no-cache python3-pip
RUN apk add --no-cache jq

# Copy data for add-on
COPY run.sh /
COPY app.py /
RUN pip3 install asyncws
RUN chmod a+x /run.sh

# WORKDIR /data

CMD [ "/run.sh" ]