FROM opencfd/openfoam2106-default:latest
COPY . ${HOME}
RUN apt-get update && apt-get install -y python3.6 python3-distutils python3-pip python3-apt
RUN python3 -m pip install --no-cache-dir notebook jupyterlab PyFoam
RUN wget "https://github.com/Unofficial-Extend-Project-Mirror/openfoam-extend-swak4Foam-dev/archive/branches/develop.tar.gz" -O swak4Foam.tar.gz
RUN tar -xf swak4Foam.tar.gz
RUN mv openfoam-extend-swak4Foam-dev-branches-develop swak4Foam
RUN cd swak4Foam
SHELL ["/bin/bash", "-c"]
RUN ./Allwmake 