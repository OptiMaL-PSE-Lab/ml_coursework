FROM opencfd/openfoam2106-default:latest
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}
COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}
RUN apt-get update && apt-get install -y python3.6 python3-distutils python3-pip python3-apt
RUN python3 -m pip install --no-cache-dir notebook jupyterlab PyFoam
RUN wget "https://github.com/Unofficial-Extend-Project-Mirror/openfoam-extend-swak4Foam-dev/archive/branches/develop.tar.gz" -O swak4Foam.tar.gz
RUN tar -xf swak4Foam.tar.gz
RUN mv openfoam-extend-swak4Foam-dev-branches-develop swak4Foam
RUN cd swak4Foam
RUN ./Allwmake