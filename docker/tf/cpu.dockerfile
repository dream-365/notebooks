# 基于 TensorFlow 官方 Jupyter 镜像
FROM tensorflow/tensorflow:2.5.1-jupyter

# 安装额外的包和依赖
RUN apt-get update && \
    apt-get install -y git wget unzip && \
    rm -rf /var/lib/apt/lists/*

# 使用 pip 安装额外的 Python 包
RUN pip install --no-cache-dir deepmatch tqdm pandas scikit-learn faiss-cpu==1.7.2