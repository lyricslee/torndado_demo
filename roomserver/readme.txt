
conda env create --file=conda_env.yml
source activate autohw

vim ~/.bashrc
export PATH=/root/anaconda3/bin:$PATH
source ~/.bashrc

/root/anaconda3/envs/autohw/bin/python server.py
