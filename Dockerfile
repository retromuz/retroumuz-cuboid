# retroumuz/cuboid:0.0.1
FROM retroumuz/cuboid-base:0.0.1
USER cuboid
WORKDIR /home/cuboid
RUN set -eux; \
    ARCH=`uname -m`; \
    python3 -m pip install httpserver requests torch torchvision;
    # git clone https://github.com/CYang0515/NonCuboidRoom.git; \
    # cd NonCuboidRoom; \
    # conda create -n layout python=3.6; \
    # conda activate layout; \
    # conda install pytorch==1.5.0 torchvision==0.6.0 cudatoolkit=10.1 -c pytorch; \

ADD src /home/cuboid/src
