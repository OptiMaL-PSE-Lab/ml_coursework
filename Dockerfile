FROM trsav/openfoam_swak4foam:latest

RUN pip install --no-cache --upgrade pip && \
     pip install --no-cache notebook jupyterlab

 ENV HOME /home/

 # Copy contents of repo to home
 COPY . ${HOME}
 USER root
