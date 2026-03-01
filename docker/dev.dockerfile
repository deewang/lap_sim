ARG IMAGE_BASE="ubuntu"
ARG IMAGE_TAG="22.04"

FROM ${IMAGE_BASE}:${IMAGE_TAG}

# Check if the image is Ubuntu or Debian based
RUN cat /etc/os-release | grep -Eqi 'ubuntu|debian' || (echo "Error: Image (${IMAGE_BASE}:${IMAGE_TAG}) is not based on Ubuntu or Debian" && exit 1)

ARG PROJECT
ARG DEBIAN_FRONTEND=noninteractive

# Various arguments and user settings
ARG USERNAME="${PROJECT}"
ARG USERHOME="/home/${USERNAME}"
ARG USERSHELL="bash"
ARG USERSHELLPATH="/bin/${USERSHELL}"
ARG USERSHELLPROFILE="${USERHOME}/.${USERSHELL}rc"

# Install some global dependencies and clean up after
USER root
RUN apt-get update && \
        apt-get install --no-install-recommends -y sudo python3-pip && \
        apt-get clean && apt-get autoremove -y && rm -rf /var/lib/apt/lists/* && \
        apt-get install -y openssh-client

# Add user and grant sudo permission.
ARG USER_UID=1000
ARG USER_GID=1000
ARG USER_GROUPS=""
RUN if getent passwd ${USER_UID}; then \
        userdel -r $(getent passwd ${USER_UID} | cut -d: -f1); \
    fi && \
    useradd --shell /bin/${USERSHELL} --create-home --password "" ${USERNAME} && \
    passwd -d ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/${USERNAME} && \
    chmod 0440 /etc/sudoers.d/${USERNAME} && \
    groupmod -o -g ${USER_GID} ${USERNAME} && \
    usermod -u ${USER_UID} -g ${USER_GID} ${USERNAME} && \
    if [ -n "${USER_GROUPS}" ]; then \
        for g in ${USER_GROUPS}; do \
            getent group $g || groupadd $g; \
            usermod -aG $g ${USERNAME}; \
        done; \
    fi

# Change to the user
USER ${USERNAME}

# Generate SSH key for container user (no passphrase)
RUN mkdir -p ~/.ssh && \
    ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -q && \
    chmod 700 ~/.ssh && chmod 600 ~/.ssh/id_ed25519

ARG CHRONO_BRANCH="release/9.0"
ARG CHRONO_REPO="https://github.com/projectchrono/chrono.git"
ARG CHRONO_DIR="${USERHOME}/chrono"
ARG CHRONO_INSTALL_DIR="${USERHOME}/packages/chrono"
ARG PACKAGE_DIR="${USERHOME}/packages"
RUN mkdir -p ${PACKAGE_DIR}

# This variable will be used by snippets to add cmake options
ENV CMAKE_OPTIONS=""
# This variable is used before building (but in the same RUN command)
# This is useful for setting environment variables that are used in the build process
ENV PRE_BUILD_COMMANDS=""

# Install Chrono dependencies that are required for all modules (or some but are fairly small)
RUN sudo apt update && \
        sudo apt install --no-install-recommends -y \
        libirrlicht-dev \
        libeigen3-dev \
        git \
        cmake \
        build-essential \
        ninja-build \
        swig \
        libxxf86vm-dev \
        freeglut3-dev \
        python3-numpy \
        libglu1-mesa-dev \
        libglew-dev \
        libglfw3-dev \
        libblas-dev \
        liblapack-dev \
        wget \
        unzip \
        xorg-dev && \
        sudo apt clean && sudo apt autoremove -y && sudo rm -rf /var/lib/apt/lists/*

# Clone Chrono before running the snippets
RUN git clone --recursive -b ${CHRONO_BRANCH} ${CHRONO_REPO} ${CHRONO_DIR}

# Install OpenCRG from source using the provided Chrono build script
# OpenCRG is a library for specifying road surfaces in vehicle simulations
ARG OPENCRG_INSTALL_DIR="${PACKAGE_DIR}/opencrg"

RUN set -e && \
    # Run the provided buildOpenCRG.sh script with custom install directory
    cd ${CHRONO_DIR}/contrib/build-scripts/opencrg && \
    sh buildOpenCRG.sh ${OPENCRG_INSTALL_DIR} && \
    # Clean up temporary download directory
    rm -rf download_crg

# Update CMake options to enable OpenCRG and point to installation
ENV CMAKE_OPTIONS="${CMAKE_OPTIONS} \
    -DENABLE_OPENCRG=ON \
    -DOpenCRG_INCLUDE_DIR=${OPENCRG_INSTALL_DIR}/include \
    -DOpenCRG_LIBRARY=${OPENCRG_INSTALL_DIR}/lib/libOpenCRG.1.1.2.a"

# Install Chrono::Irrlicht
RUN sudo apt update && \
        sudo apt install --no-install-recommends -y \
        libirrlicht-dev && \
        sudo apt clean && sudo apt autoremove -y && sudo rm -rf /var/lib/apt/lists/*

# Update CMake options
ENV CMAKE_OPTIONS="${CMAKE_OPTIONS} \
    -DENABLE_MODULE_IRRLICHT=ON"

# Install Chrono::Vehicle
# Update CMake options
ENV CMAKE_OPTIONS="${CMAKE_OPTIONS} \
    -DENABLE_MODULE_VEHICLE=ON \
    -DENABLE_MODULE_VEHICLE_MODELS=ON"

# Install Chrono
RUN ${PRE_BUILD_SCRIPTS} && \
    # Evaluate the cmake options to expand any $(...) commands or variables
    eval "_CMAKE_OPTIONS=\"${CMAKE_OPTIONS}\"" && \
    mkdir ${CHRONO_DIR}/build && \
    cd ${CHRONO_DIR}/build && \
    cmake ../ -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_DEMOS=ON \
        -DBUILD_BENCHMARKING=OFF \
        -DBUILD_TESTING=OFF \
        -DCMAKE_LIBRARY_PATH=$(find /usr/local/cuda/ -type d -name stubs) \
        -DEigen3_DIR=/usr/lib/cmake/eigen3 \
        -DCMAKE_INSTALL_PREFIX=${CHRONO_INSTALL_DIR} \
        -DNUMPY_INCLUDE_DIR=$(python3 -c 'import numpy; print(numpy.get_include())') \
        ${_CMAKE_OPTIONS} \
        && \
    ninja && ninja install


# Update shell config
RUN echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:${CHRONO_INSTALL_DIR}/lib" >> ${USERSHELLPROFILE}

# Change to root user
USER root

# Install dependencies
ARG APT_DEPENDENCIES=""
RUN apt-get update && \
        apt-get install --no-install-recommends -y gnuplot && \
        [ -z "${APT_DEPENDENCIES}" ] || apt-get install --no-install-recommends -y ${APT_DEPENDENCIES} && \
        apt-get clean && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Update apt such that it never runs without --no-install-recommends
RUN apt-config dump | grep -we Recommends -e Suggests | sed s/1/0/ | sudo tee /etc/apt/apt.conf.d/999norecommend

# Update shell config
ARG DEFAULT_SHELL_ADD_ONS="export TERM=xterm-256color"
ARG USER_SHELL_ADD_ONS=""
RUN echo "${DEFAULT_SHELL_ADD_ONS}" >> ${USERSHELLPROFILE} && \
        sed -i 's/#force_color_prompt=yes/force_color_prompt=yes/' ${USERSHELLPROFILE} && \
        [ -z "${USER_SHELL_ADD_ONS}" ] || echo "${USER_SHELL_ADD_ONS}" >> ${USERSHELLPROFILE}

# Sets the user, the work dir, and the command
USER ${USERNAME}
WORKDIR ${USERHOME}
ENV HOME=${USERHOME}
ENV USERSHELLPATH=${USERSHELLPATH}
ENV USERSHELLPROFILE=${USERSHELLPROFILE}

CMD ["sh","-c","$USERSHELLPATH"]
