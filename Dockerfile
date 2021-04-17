FROM python:3.7.5

#设置工作目录
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# 添加依赖(利用Docker缓存)
ADD ./requirements.txt /usr/src/app/requirements.txt

# 安装依赖
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 添加应用
ADD . /usr/src/app

# 运行服务
CMD python manage.py runserver -h 0.0.0.0