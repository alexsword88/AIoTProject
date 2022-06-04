# Requirement
- python >= 3.8
- [tflite_runtime](https://pypi.org/project/tflite-runtime/) (over 3.9 need build yourself)
- [tflite-support](https://pypi.org/project/tflite-support/)

# tflite_runtime build
```
git clone https://github.com/tensorflow/tensorflow
sudo apt install swig libjpeg-dev zlib1g-dev python3-dev python3-numpy
pip install numpy pybind11
cd tensorflow/tensorflow/lite/tools/pip_package

sh tensorflow/lite/tools/pip_package/build_pip_package_with_cmake.sh
```