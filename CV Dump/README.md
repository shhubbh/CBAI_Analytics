# Docker Commands 
- To pull the image, in terminal run:

```docker pull scoobydub/cv_env:V1```
- In Windows Powershell with docker desktop/engine runnning, navigate to your project directory & run:

```docker run -it -p 8888:8888 -p 5000:5000 -v ${PWD}:/home --name your_container_name scoobydub/cv_env:V1```

- To run jupyter-lab, in powershell running container's bash shell, run:

```jupyter lab --ip='0.0.0.0' --port=8888 --no-browser --allow-root --notebook-dir=/home```




