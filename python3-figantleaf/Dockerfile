FROM gigantum/python3-data-science:87c90e7834-2019-07-19
LABEL maintainer="Jared Watts <j.watts@digital-science.com>"

RUN apt-get update
RUN apt-get -y --no-install-recommends install biber libfreetype6-dev libx11-dev openssh-server texlive-bibtex-extra texlive-xetex xfonts-base libxml2-dev
RUN pip install GitPython==3.0.3 && pip install dimcli==0.5.8.1 && pip install gender_guesser==0.4.0 && pip install pybtex==0.22.2 && pip install pylatex==1.3.1 && pip install python-twitter==3.5

COPY *.py /opt/conda/lib/python3.7/site-packages/
