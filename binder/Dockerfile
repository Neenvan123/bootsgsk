FROM intel4coro/base-notebook:20.04-noetic-full-xpra

#------------------------------------------rasa38 Conda Env (Python 3.8) for rasa packages------------------------------------------
USER root

RUN conda create -n rasa38 python=3.8 && echo "conda activate rasa38" >> ~/.bashrc

SHELL ["conda", "run", "-n", "rasa38", "/bin/bash", "-c"]

# USER ${NB_USER}

RUN pip install rasa && pip install rasa[spacy] && pip install transformers && pip install nltk

RUN python -m spacy download en_core_web_sm && python -m nltk.downloader punkt && python -m nltk.downloader wordnet

# Initiate RASA workspace 
COPY --chown=${NB_USER}:users binder/rasa.sh /home/${NB_USER}/rasa.sh
RUN chmod +x /home/${NB_USER}/rasa.sh

ENV RASA_WS=/home/${NB_USER}/workspace/rasa
WORKDIR ${RASA_WS}/src
COPY --chown=${NB_USER}:users binder/rasa ${RASA_WS}/src/
RUN chmod -R a+rwx ${PWD}

RUN ls -l
# SHELL ["conda", "run", "-n", "rasa38", "/bin/bash", "-c"]

RUN python --version

USER ${NB_USER}

RUN rasa train nlu

# SHELL ["conda", "run", "-n", "base", "/bin/bash", "-c"]

# RUN python --version

#------------------------------------------Switch to base Conda Env (Python 3.10)------------------------------------------
USER root

SHELL ["conda", "run", "-n", "base", "/bin/bash", "-c"]

USER ${NB_USER}

RUN pip uninstall -y jlab-enhanced-cell-toolbar
RUN pip install https://raw.githubusercontent.com/yxzhan/jupyterlab-rviz/master/dist/jupyterlab_rviz-0.3.2.tar.gz \
  https://raw.githubusercontent.com/yxzhan/extension-examples/main/cell-toolbar/dist/jupyterlab_examples_cell_toolbar-0.1.4.tar.gz
RUN mamba install -y ripgrep

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
USER root
RUN chmod +x /home/${NB_USER}/bullet3/build_cmake_pybullet_3.10_double.sh
RUN cd bullet3 && ./build_cmake_pybullet_3.10_double.sh
USER ${NB_USER}
ENV PYTHONPATH=${PYTHONPATH}:/home/${NB_USER}/bullet3/build_cmake/better_python:/home/${NB_USER}/bullet3/examples/pybullet

# Build ROS workspace
WORKDIR  ${ROS_WS}
# Can not build package iai_pr2_donbot and it is not used
RUN rm -rf src/iai_pr2/iai_pr2_donbot
# Upldate rvizweb
RUN cd src/rvizweb && git pull
RUN catkin build

# RUN pip install --upgrade \
#   jupyter-collaboration \
#   openai \
#   jupyter-ai

# Chatbot configs
# COPY --chown=${NB_USER}:users binder/jupyter-ai.json /home/${NB_USER}/.local/share/jupyter/jupyter_ai/config.json
# ENV OPENAI_API_BASE="http://192.168.240.1:5002"
# ENV OPENAI_API_KEY="sk-4e6e40294b4da6fd87ddc0a4aae645a4"

# -----------------------------------------------------------------------------
# ENV BOOT_WS=/home/${NB_USER}/workspace/bootstrap
# WORKDIR ${BOOT_WS}/src
# COPY --chown=${NB_USER}:users binder/bootstrap/requirements.txt ${BOOT_WS}/src/requirements.txt

# # install the dependencies and packages in the requirements file
# RUN pip install --no-cache-dir -r requirements.txt

# RUN spacy download en_core_web_sm

# RUN python -m nltk.downloader punkt && python -m nltk.downloader wordnet
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------

# Copy the giskard tmp meshes to skip the converting step
COPY --chown=${NB_USER}:users binder/giskard_decomposed_obj ${ROS_WS}/src/giskardpy/tmp
# The giskard standalone does not publish tf messaages by default set it to true for rvizweb
RUN sed -i 's/publish_tf: bool = False/publish_tf: bool = True/g' ${ROS_WS}/src/giskardpy/src/giskardpy/configs/behavior_tree_config.py
# Copy contents of the repo into the image
COPY --chown=${NB_USER}:users . /home/${NB_USER}/bootstrapping_giskard
WORKDIR /home/${NB_USER}/bootstrapping_giskard
RUN git config --global --add safe.directory ${PWD}
# Soft link the ROS workspace directory to the working directory
RUN ln -s ${ROS_WS} ${PWD}/ROS_WS
RUN ln -s ${RASA_WS}/src ${PWD}/Rasa
# jupyterlab interface configuration
COPY --chown=${NB_USER}:users binder/webapps.json ${ROS_WS}/src/rvizweb/webapps/app.json
COPY --chown=${NB_USER}:users binder/jupyter-settings.json /opt/conda/share/jupyter/lab/settings/overrides.json

RUN cd ${ROS_WS}/src/rvizweb && git pull

RUN pip install --upgrade --force-reinstall flask-sqlalchemy sqlalchemy

RUN cd ${ROS_WS}/src/mujoco_robots && git pull

# ------------------Training RASA model-------------------------------------

# WORKDIR /home/${NB_USER}/bootstrapping_giskard/binder/rasa
# USER root
# RUN chmod -R a+rwx ${PWD}
# USER ${NB_USER}
# RUN ls -l
# SHELL ["conda", "run", "-n", "rasa38", "/bin/bash", "-c"]

# RUN python --version

# RUN rasa train nlu

# SHELL ["conda", "run", "-n", "base", "/bin/bash", "-c"]

# RUN python --version

# -------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------------------------

RUN pip install --upgrade \
  sidecar \
  Cython \
  openai \
  # jupyterlab-git \
  jupyterlab-unfold \
  jupyter-archive \
  jupyterlab-search-replace \
  jupyter-offlinenotebook \
  jupyter-collaboration \
  jupyter-ai \
  jupyterlab-language-pack-de-DE  \
  jupyterlab_execute_time

RUN pip install --upgrade \
  jupyter-collaboration \
  openai \
  jupyter-ai

WORKDIR /home/${NB_USER}/bootstrapping_giskard/
