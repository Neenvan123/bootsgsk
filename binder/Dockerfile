FROM intel4coro/base-notebook:20.04-noetic-full-xpra

RUN python --version

#-------------------------------------------------------------------------------------------------------------------------------------------
USER root

RUN conda create -n rasa38 python=3.8 && echo "conda activate rasa38" >> ~/.bashrc

SHELL ["conda", "run", "-n", "rasa38", "/bin/bash", "-c"]
# SHELL ["/bin/bash", "-c", "source ~/.bashrc && conda activate rasa38"]

RUN python --version

RUN pip install rasa && pip install spacy && pip install transformers

# SHELL ["/bin/bash", "-c", "source ~/.bashrc && conda deactivate"]

SHELL ["conda", "run", "-n", "base", "/bin/bash", "-c"]

RUN python --version

USER ${NB_USER}

RUN pip uninstall -y jlab-enhanced-cell-toolbar
RUN pip install https://raw.githubusercontent.com/yxzhan/jupyterlab-rviz/master/dist/jupyterlab_rviz-0.3.2.tar.gz \
  https://raw.githubusercontent.com/yxzhan/extension-examples/main/cell-toolbar/dist/jupyterlab_examples_cell_toolbar-0.1.4.tar.gz
RUN mamba install -y ripgrep
RUN pip install --upgrade \
  sidecar \
  Cython \
  openai \
  jupyterlab-git \
  jupyterlab-unfold \
  jupyter-archive \
  jupyterlab-search-replace \
  jupyter-offlinenotebook \
  jupyter-collaboration \
  jupyter-ai \
  jupyterlab-language-pack-de-DE  \
  jupyterlab_execute_time

# Initiate ROS workspace 
ENV ROS_WS=/home/${NB_USER}/workspace/ros
WORKDIR ${ROS_WS}/src
# A Workaround for fixing the issue of RvizWeb loading meshes with "file:///" path instead of "package:///".
COPY --chown=${NB_USER}:users binder/me ${ROS_WS}/src/me
COPY --chown=${NB_USER}:users binder/noetic.rosinstall /home/${NB_USER}/noetic.rosinstall
RUN wstool merge /home/${NB_USER}/noetic.rosinstall \
  && wstool update
# Clone repos with ssh url in .gitmodules
RUN git clone https://github.com/maltehue/mujoco_robots.git \
  && cd mujoco_robots \
  && perl -i -p -e 's|git@(.*?):|https://\1/|g' .gitmodules \
  && git submodule sync \
  && git submodule update --init --recursive
RUN git clone https://github.com/HoangGiang93/mujoco_world.git \
  && cd mujoco_world \
  && perl -i -p -e 's|git@(.*?):|https://\1/|g' .gitmodules \
  && git submodule sync \
  && git submodule update --init --recursive

# Install dependencies
WORKDIR  ${ROS_WS}
USER root
RUN rosdep update && apt update && apt dist-upgrade -y \
  && rosdep install -y --ignore-src --from-paths ./ -r \
  && rosdep fix-permissions \
  && apt install -y ffmpeg libglfw3 libglfw3-dev
USER ${NB_USER}
RUN pip install -r src/giskardpy/requirements.txt

# Install missing python packages (should be included in src/giskardpy/requirements.txt)
RUN pip install termcolor pydot triangle cython~=0.19

# Building Custom bullet3 from source with Python 3.10 (in a clumsy way)
WORKDIR /home/${NB_USER}
RUN git clone https://github.com/pybind/pybind11.git \
  && cd pybind11 \
  && mkdir build \
  && cd build \
  && cmake .. -DCMAKE_BUILD_TYPE=Release -DPYBIND11_PYTHON_VERSION=3 -DPYBIND11_TEST=OFF
USER root
RUN cd pybind11/build && make install
USER ${NB_USER}

RUN git clone https://github.com/SemRoCo/bullet3.git
COPY --chown=${NB_USER}:users binder/build_cmake_pybullet_3.10_double.sh /home/${NB_USER}/bullet3/
RUN cd bullet3 && ./build_cmake_pybullet_3.10_double.sh
ENV PYTHONPATH=${PYTHONPATH}:/home/${NB_USER}/bullet3/build_cmake/better_python:/home/${NB_USER}/bullet3/examples/pybullet

# Build ROS workspace
WORKDIR  ${ROS_WS}
# Can not build package iai_pr2_donbot and it is not used
RUN rm -rf src/iai_pr2/iai_pr2_donbot
# Upldate rvizweb
RUN cd src/rvizweb && git pull
RUN catkin build

RUN pip install --upgrade \
  jupyter-collaboration \
  openai \
  jupyter-ai

# Chatbot configs
# COPY --chown=${NB_USER}:users binder/jupyter-ai.json /home/${NB_USER}/.local/share/jupyter/jupyter_ai/config.json
# ENV OPENAI_API_BASE="http://192.168.240.1:5002"
# ENV OPENAI_API_KEY="sk-4e6e40294b4da6fd87ddc0a4aae645a4"

# -----------------------------------------------------------------------------
# Initiate BOOTSTRAP workspace 
ENV BOOT_WS=/home/${NB_USER}/workspace/bootstrap
WORKDIR ${BOOT_WS}/src
COPY --chown=${NB_USER}:users binder/bootstrap ${BOOT_WS}/src/

# install the dependencies and packages in the requirements file
RUN pip install --no-cache-dir -r requirements.txt

RUN spacy download en_core_web_sm

RUN python -m nltk.downloader punkt && python -m nltk.downloader wordnet
# -----------------------------------------------------------------------------
# Initiate RASA workspace 
ENV RASA_WS=/home/${NB_USER}/workspace/rasa
WORKDIR ${RASA_WS}/src
COPY --chown=${NB_USER}:users binder/rasa ${RASA_WS}/src/
# RUN pip install rasa==3.6.0

# install the dependencies and packages in the requirements file
# RUN pip install --no-cache-dir -r requirements.txt
# -----------------------------------------------------------------------------

# Copy the giskard tmp meshes to skip the converting step
COPY --chown=${NB_USER}:users binder/giskard_decomposed_obj ${ROS_WS}/src/giskardpy/tmp
# The giskard standalone does not publish tf messaages by default set it to true for rvizweb
RUN sed -i 's/publish_tf: bool = False/publish_tf: bool = True/g' ${ROS_WS}/src/giskardpy/src/giskardpy/configs/behavior_tree_config.py
# Copy contents of the repo into the image
COPY --chown=${NB_USER}:users . /home/${NB_USER}/giskard_examples
WORKDIR /home/${NB_USER}/giskard_examples
RUN git config --global --add safe.directory ${PWD}
# Soft link the ROS workspace directory to the working directory
RUN ln -s ${ROS_WS} ${PWD}/ROS_WS
# jupyterlab interface configuration
COPY --chown=${NB_USER}:users binder/webapps.json ${ROS_WS}/src/rvizweb/webapps/app.json
COPY --chown=${NB_USER}:users binder/jupyter-settings.json /opt/conda/share/jupyter/lab/settings/overrides.json
COPY --chown=${NB_USER}:users binder/entrypoint.sh /
# ENTRYPOINT ["/entrypoint.sh"]
# CMD ["start-notebook.sh"]


RUN cd ${ROS_WS}/src/rvizweb && git pull

RUN pip install --upgrade --force-reinstall flask-sqlalchemy sqlalchemy

RUN cd ${ROS_WS}/src/mujoco_robots && git pull

# -------------------------------------------------------

SHELL ["/bin/bash", "-c"] 

USER root

#copy stage 1 files
# WORKDIR /home/rasaenv

# COPY --from=stage1 --chown=${NB_USER}:users /rasaenv/venv /home/rasaenv/venv

RUN apt update --fix-missing
RUN apt install -y git m4 wget
# RUN apt install -y git m4 python python3-pip wget
RUN apt install -y python3-catkin-pkg-modules python3-rospkg-modules libffi-dev
RUN apt update
RUN apt install -y nodejs npm

USER ${NB_USER}
# Install and set path for python dependencies
ENV PYTHONPATH=/opt/ros/noetic/lib/python3/dist-packages:/home/${NB_USER}/ros/devel/lib/python3/dist-packages:$PYTHONPATH
RUN pip install jupyter
RUN pip install jupyterlab

USER root
# Install jupyter-ros
WORKDIR /home/ros
RUN git clone https://github.com/RoboStack/jupyter-ros.git
WORKDIR /home/ros/jupyter-ros
# RUN sudo apt update
# RUN sudo apt install -y nodejs npm
RUN pip install -e .
USER ${NB_USER}
RUN pip install numpy --upgrade
RUN jupyter nbextension install --py --symlink --sys-prefix jupyros
RUN jupyter nbextension enable --py --sys-prefix jupyros

# Install jupyter-zethus
RUN python -m pip install jupyterlab-zethus

# Install Knowrob kernel 
RUN pip install git+https://github.com/sasjonge/jupyter-knowrob.git
WORKDIR ~/.local/share/jupyter/kernels/
USER root
RUN mkdir jknowrob
USER ${NB_USER}
RUN wget https://raw.githubusercontent.com/sasjonge/jupyter-knowrob/master/kernel.json -P ~/.local/share/jupyter/kernels/jknowrob

RUN pip install --upgrade jupyter-server

# We need the json_prolog_msgs to communicate with KnowRob
USER root
WORKDIR /home/ros/src
RUN /usr/bin/python3 /opt/ros/noetic/bin/catkin_init_workspace
RUN source /opt/ros/noetic/setup.bash
RUN git clone https://github.com/code-iai/iai_common_msgs.git

WORKDIR /home/ros
# Build the catkin workspace
ENV CMAKE_PREFIX_PATH=/home/${NB_USER}/knowrob_ws/devel:/opt/ros/noetic
RUN /opt/ros/noetic/bin/catkin_make -DPYTHON_EXECUTABLE=/usr/bin/python3

WORKDIR /home/ros/lectures

# Configure container startup
COPY --chown=${NB_USER}:users binder/knowrob/run_notebook.sh /home/ros/lectures/run_notebook.sh
RUN chmod +x /home/ros/lectures/run_notebook.sh
COPY --chown=${NB_USER}:users binder/knowrob/knowrob_cloud /home/ros/src/knowrob_cloud

RUN pip install --upgrade \
  sidecar \
  Cython \
  openai \
  jupyterlab-git \
  jupyterlab-unfold \
  jupyter-archive \
  jupyterlab-search-replace \
  jupyter-offlinenotebook \
  jupyter-collaboration \
  jupyter-ai \
  jupyterlab-language-pack-de-DE  \
  jupyterlab_execute_time

WORKDIR /home/${NB_USER}/giskard_examples
CMD ["conda", "run", "-n", "base", "python"]