# retroumuz/cuboid:0.0.1
FROM retroumuz/cuboid-base:0.0.1
USER cuboid
WORKDIR /home/cuboid
RUN set -eux; \
    export ARCH=`uname -m`; \
    curl -o anaconda.sh https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-${ARCH}.sh; \
    git clone https://github.com/CYang0515/NonCuboidRoom.git;

ADD src /home/cuboid/src

# RUN set -eux; \
    # python3 -m pip install httpserver requests torch torchvision; \
    # conda create -n layout python=3.6; \
    # conda activate layout; \
    # conda install pytorch==1.5.0 torchvision==0.6.0 cudatoolkit=10.1 -c pytorch;

ADD entrypoint.sh /home/cuboid/
ENTRYPOINT bash /home/cuboid/entrypoint.sh
