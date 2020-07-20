FROM archlinux/base

RUN useradd -ms /bin/bash docker
ENV JAVA_HOME=/usr/lib/jvm/default-runtime
ENV PATH="/home/docker/.local/bin:${JAVA_HOME}:${PATH}"
RUN pacman -Syu --noconfirm stack base-devel jdk8-openjdk python wget git maven unzip vim nano emacs
RUN stack upgrade --binary-version 1.9.3

WORKDIR /home/docker
USER docker
RUN wget http://debloating.cs.ucla.edu/dist/jdebloat.tgz -q -O /home/docker/jdebloat.tgz
RUN tar xvzf jdebloat.tgz
RUN rm jdebloat.tgz
RUN cd jdebloat && python jdebloat.py setup 2>/dev/null
ENTRYPOINT ["/bin/bash"]
