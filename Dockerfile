FROM opencfd/openfoam2106-default:latest
RUN python3 -m pip install --no-cache-dir notebook jupyterlab PyFoam

ARG NB_USER=coursework_user
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}
COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}
RUN mkdir -p $FOAM_RUN
RUN cd "$HOME/OpenFOAM/$USER-$WM_PROJECT_VERSION"
RUN wget "https://github.com/Unofficial-Extend-Project-Mirror/openfoam-extend-swak4Foam-dev/archive/branches/develop.tar.gz" -O swak4Foam.tar.gz
RUN tar -xf swak4Foam.tar.gz
RUN mv openfoam-extend-swak4Foam-dev-branches-develop swak4Foam
RUN cd swak4Foam
RUN ./Allwmake > log.make 2>&1