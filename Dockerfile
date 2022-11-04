FROM trsav/openfoam_swak4foam:latest

# install the notebook package
RUN pip install --no-cache --upgrade pip && \
    pip install --no-cache notebook jupyterlab
COPY . ${HOME}
USER root
