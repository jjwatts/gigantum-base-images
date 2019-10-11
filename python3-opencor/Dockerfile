# Copyright (c) Gigantum

# Note, some docker commands taken from/inspired by the standard docker-stacks maintained
# by the Jupyter team: https://github.com/jupyter/docker-stacks/
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Start Image Def
FROM ubuntu:18.04
LABEL maintainer="Jared Watts <j.watts@digital-science.com>"
ENV DEBIAN_FRONTEND noninteractive

# Install system level dependencies
RUN apt-get update \
    && apt-get install -yq --no-install-recommends \
        wget \
        bzip2 \
        ca-certificates \
        gcc \
        g++ \
        make \
        locales \
        fonts-liberation \
        gosu \
        tzdata \
        git \
    && apt-get clean

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

# Setup environment variables
ENV CONDA_DIR=/opt/conda \
    GIGANTUM_SHARE=/mnt/share \
    GIGANTUM_WORKDIR=/mnt/labbook \
    SHELL=/bin/bash \
    MINICONDA_VERSION=4.1.11 \
    MINICONDA_MD5=874dbb0d3c7ec665adf7231bbb575ab2 \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8
ENV PATH=$CONDA_DIR/bin:$PATH \
    JUPYTER_RUNTIME_DIR=$GIGANTUM_SHARE/jupyter/runtime

# Install conda, python, and jupyter
RUN cd /tmp && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh && \
    echo "$MINICONDA_MD5 *Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh" | md5sum -c - && \
    /bin/bash Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh -f -b -p $CONDA_DIR && \
    rm Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh
RUN conda update --quiet --yes conda && \
    conda config --system --prepend channels conda-forge && \
    conda config --system --remove channels defaults && \
    conda config --system --append channels anaconda && \
    conda config --system --set auto_update_conda false && \
    conda config --system --set show_channel_urls true
    # conda update --all --quiet --yes

    # notebook 5.3 through 5.7.1 have security holes
    # Pillow 6.0 breaks things like pytorch, so we install it pre-emptively

RUN conda install --quiet --yes -c conda-forge jupyterlab 'notebook<5.8' pillow && \
    # This is currently installed by default by conda, but it's mission
    # critical so we make it explicit
    conda install pip && \
    # We pin the version of nodejs so we can be sure to re-install the same
    # version later - avoiding jupyterlab extension rebuilds and generally
    # improving compatability
    conda install --quiet --yes nodejs==10.15.3 && \
    pip install nbresuse && \
    # unlcear from statusbar docs if this is necessary for jupyterlab, but doesn't hurt
    jupyter serverextension enable --py nbresuse && \
    jupyter labextension install @jupyterlab/toc && \
    #jupyter labextension install @jupyterlab/statusbar && \
    npm cache clean --force && \
    rm -rf $CONDA_DIR/share/jupyter/lab/staging && \
    rm -rf /root/.cache/yarn && \
    rm -rf /root/.node-gyp && \
    conda remove --quiet --yes nodejs && \
    conda clean --all

RUN conda install --quiet --yes python=3.5.2

RUN apt-get update \
        && apt-get install -yq --no-install-recommends \
            # These are needed by some conda-installed packages, such as opencv
            # Note that since our R bases use apt, this gets taken care of
            # automatically there
            libfontconfig1 \
            libfreetype6 \
            libpulse-mainloop-glib0	\
            libx11-6 \
            libx11-xcb1 \
            libxrender1 \
            libxext6 \
            libgl1-mesa-glx \
            libxslt1.1 \
            openssh-server \
            sqlite3 \
        && apt-get clean

RUN mkdir /opencor
RUN cd /opencor && wget https://github.com/dbrnz/opencor/releases/download/snapshot-2019-06-11/OpenCOR-2019-06-11-Linux.tar.gz
RUN cd /opencor && tar -xvzf OpenCOR-2019-06-11-Linux.tar.gz && rm OpenCOR-2019-06-11-Linux.tar.gz
RUN cd /opt/conda/share/jupyter/kernels && mkdir OpenCOR && cd OpenCOR && touch kernel.json
RUN echo '{"argv":["/opencor/OpenCOR-2019-06-11-Linux/OpenCOR", "-c", "JupyterKernel::kernel", "{connection_file}"],"display_name":"OpenCOR","language":"python"}' > /opt/conda/share/jupyter/kernels/OpenCOR/kernel.json

RUN mkdir /opt/gigantum-fix && mkdir /opt/gigantum-fix/bin
ENV PATH=/opt/gigantum-fix/bin:$PATH
COPY __init__.py /opt/gigantum-fix
COPY jupyter /opt/gigantum-fix/bin
RUN chmod +x /opt/gigantum-fix/bin/jupyter

COPY OpenCOR /opencor/OpenCOR-2019-06-11-Linux
RUN chmod +x /opencor/OpenCOR-2019-06-11-Linux/OpenCOR

# Expose port for jupyterlab
EXPOSE 8888

# Set working dir
WORKDIR $GIGANTUM_WORKDIR

# CMD may be updated during final image assembly, but this keeps a container alive.
CMD ["tail", "-f", "/dev/null"]
