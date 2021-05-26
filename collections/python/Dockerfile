FROM python:3.7
WORKDIR /usr/src/app

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

# Install aria2
RUN apt-get update
#RUN apt-get install -y aria2
RUN apt-get install -y awscli && aws configure set s3.signature_version s3v4
RUN apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
 && locale-gen

ENV LANG en_US.UTF-8
ENV EN_PUNCTUATOR_MODEL_H5=s3://workfit-models/auto-punc/original_cr_fisher_rev_h256_glove_v1.h5
ENV EN_PUNCTUATOR_MODEL_PCL=s3://workfit-models/auto-punc/original_cr_fisher_rev_h256_glove_v1.pcl
ENV EN_TRUECASING_MODEL=s3://workfit-models/auto-punc/en_truecasing_model.obj
ENV ES_PUNCTUATOR_MODEL_H5=s3://workfit-models/auto-punc/es/spanish_mset_v2.h5
ENV ES_PUNCTUATOR_MODEL_PCL=s3://workfit-models/auto-punc/es/spanish_mset_v2.pcl
ENV ES_TRUECASING_MODEL=s3://workfit-models/auto-punc/es/es_wiki_truecaser_model_25000.obj

RUN mkdir models && mkdir models/en && mkdir models/es && \
    aws s3 cp $EN_PUNCTUATOR_MODEL_H5 en/en_punctuator_model.h5 && \
    aws s3 cp $EN_PUNCTUATOR_MODEL_PCL en/en_punctuator_model.pcl && \
    aws s3 cp $EN_TRUECASING_MODEL en/en_truecasing_model.obj && \
    aws s3 cp $ES_PUNCTUATOR_MODEL_H5 es/es_punctuator_model.h5 && \
    aws s3 cp $ES_PUNCTUATOR_MODEL_PCL es/es_punctuator_model.pcl && \
    aws s3 cp $ES_TRUECASING_MODEL es/es_truecasing_model.obj

# araia2 doesn't support s3, temporary disable
#COPY download_models.sh .
#RUN export EN_PUNCTUATOR_MODEL_H5=https://s3-us-west-2.amazonaws.com/workfit-models/auto-punc/original_cr_fisher_rev_h256_glove_v1.h5 && \
#  export EN_PUNCTUATOR_MODEL_PCL=https://s3-us-west-2.amazonaws.com/workfit-models/auto-punc/original_cr_fisher_rev_h256_glove_v1.pcl && \
#  export EN_TRUECASING_MODEL=https://s3-us-west-2.amazonaws.com/workfit-models/auto-punc/en_truecasing_model.obj && \
#  export ES_PUNCTUATOR_MODEL_H5=https://s3-us-west-2.amazonaws.com/workfit-models/auto-punc/es/spanish_mset_v2.h5 && \
#  export ES_PUNCTUATOR_MODEL_PCL=https://s3-us-west-2.amazonaws.com/workfit-models/auto-punc/es/spanish_mset_v2.pcl && \
#  export ES_TRUECASING_MODEL=https://s3-us-west-2.amazonaws.com/workfit-models/auto-punc/es/es_wiki_truecaser_model_25000.obj && \
#  sh download_models.sh
  
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "import nltk; nltk.download('punkt')"
COPY . .
EXPOSE 5000
# Use ENTRYPOINT to set fairly stable default commands and arguments and then
# use CMD to set additional defaults that are more likely to be changed
ENTRYPOINT ["python3.7", "./server.py", "--config", "en_prod.cfg,es_prod.cfg"]
#ENTRYPOINT ["sh"]
