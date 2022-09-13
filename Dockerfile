FROM trsav/openfoam_swak4foam
CMD ["/bin/bash"]
WORKDIR "root"
RUN git clone https://github.com/OptiMaL-PSE-Lab/ml_coursework.git

